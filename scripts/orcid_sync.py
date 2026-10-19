#!/usr/bin/env python3
"""Append new works from ORCID to data/publications.yml.

Fetches the public works list of an ORCID iD and, for every work whose DOI
(or normalised title) is not yet in data/publications.yml, appends a new entry
as plain text (the existing file and its comments are never rewritten).
Running it again adds nothing (idempotent). Works listed in
data/publications-ignore.yml are skipped.

For works with a DOI, the entry is completed from Crossref (api.crossref.org):
authors, venue, publisher, volume, issue, pages, year and type. Only the
`summary` is left for you to write. If Crossref cannot be reached, the entry is
still added with the ORCID data.

Usage:
  python3 scripts/orcid_sync.py               # update data/publications.yml
  python3 scripts/orcid_sync.py --dry-run     # only print what would be added
  python3 scripts/orcid_sync.py --input works.json --dry-run   # offline test
  python3 scripts/orcid_sync.py --no-crossref --dry-run          # ORCID data only
  python3 scripts/orcid_sync.py --input works.json --crossref-input cr.json --dry-run
      # offline test; cr.json = {"<doi>": <Crossref "message" object>, ...}

Stdlib only (uses PyYAML for reading if it is installed, else a simple scan).
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ORCID_ID = "0009-0002-9620-7411"
API = "https://pub.orcid.org/v3.0/{id}/works"
CROSSREF = "https://api.crossref.org/works/{doi}"
UA = "orcid_sync.py (personal website; mailto:achmad.solaeman@ugm.ac.id)"
ROOT = Path(__file__).resolve().parent.parent
PUBS = ROOT / "data" / "publications.yml"

KIND = {
    "conference-paper": "Conference paper",
    "journal-article": "Journal article",
    "book-review": "Book review",
    "book-chapter": "Book chapter",
}
CROSSREF_KIND = {
    "proceedings-article": "Conference paper",
    "journal-article": "Journal article",
    "book-chapter": "Book chapter",
    "posted-content": "Preprint",
}
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>?#]+", re.I)


def norm_title(t):
    return " ".join(re.sub(r"[^0-9a-z]+", " ", (t or "").lower()).split())


def norm_doi(d):
    m = DOI_RE.search(d or "")
    return m.group(0).rstrip(".").lower() if m else ""


def val(d, *path):
    """Safe nested lookup: val(w, "title", "title", "value")."""
    for p in path:
        if not isinstance(d, dict):
            return None
        d = d.get(p)
    return d


def fetch(orcid):
    req = urllib.request.Request(
        API.format(id=orcid),
        headers={"Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_crossref(doi):
    """Crossref "message" object for a DOI, or None if unavailable."""
    req = urllib.request.Request(
        CROSSREF.format(doi=urllib.parse.quote(doi, safe="/")),
        headers={"Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get("message")
    except Exception as e:  # network error, 404, bad JSON ...
        print(f"orcid_sync: Crossref lookup failed for {doi}: {e}", file=sys.stderr)
        return None


def first(x):
    return (x[0] if isinstance(x, list) and x else x) or ""


def enrich(w, m):
    """Fill a work dict with Crossref metadata `m` (keeps ORCID values as fallback)."""
    if not m:
        return w
    authors = []
    for a in m.get("author") or []:
        name = " ".join(p for p in (a.get("given"), a.get("family")) if p) or a.get("name") or ""
        if name:
            authors.append(name.strip())
    year = (val(m, "published", "date-parts") or val(m, "issued", "date-parts") or [[None]])[0][0]
    w.update({
        "authors": authors or w.get("authors", []),
        "venue": " ".join(str(first(m.get("container-title"))).split()) or w["venue"],
        "publisher": (m.get("publisher") or "").strip(),
        "volume": str(m.get("volume") or ""),
        "issue": str(m.get("issue") or ""),
        "pages": str(m.get("page") or ""),
        "year": year or w["year"],
        "kind": CROSSREF_KIND.get(m.get("type") or "", w["kind"]),
        "title": " ".join(str(first(m.get("title"))).split()) or w["title"],
    })
    return w


def existing_keys(text):
    """Return (dois, titles) already present in publications.yml."""
    titles, blobs = set(), []
    try:
        import yaml
        for e in yaml.safe_load(text) or []:
            titles.add(norm_title(str(e.get("title", ""))))
            blobs += [str(e.get("url", "")), str(e.get("doi", ""))]
    except ImportError:
        for m in re.finditer(r"^\s*-?\s*title:\s*(.+)$", text, re.M):
            titles.add(norm_title(m.group(1)))
        blobs.append(text)
    dois = {norm_doi(m.group(0)) for b in blobs for m in DOI_RE.finditer(b)}
    return dois, titles


def works_from(data):
    """Yield one dict per ORCID work group (first/preferred summary)."""
    for g in data.get("group", []) or []:
        summaries = g.get("work-summary") or []
        if not summaries:
            continue
        w = summaries[0]
        ext = (val(w, "external-ids", "external-id") or []) + \
              (val(g, "external-ids", "external-id") or [])
        doi = ""
        for x in ext:
            if (x.get("external-id-type") or "").lower() == "doi":
                doi = norm_doi(x.get("external-id-value") or "") or \
                      norm_doi(val(x, "external-id-url", "value") or "")
                if doi:
                    break
        wtype = (w.get("type") or "").lower()
        year = val(w, "publication-date", "year", "value") or "n.d."
        yield {
            "year": year,
            "title": (val(w, "title", "title", "value") or "").strip(),
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else (val(w, "url", "value") or ""),
            "venue": (val(w, "journal-title", "value") or "").strip(),
            "kind": KIND.get(wtype, wtype.replace("-", " ").title()),
        }


def q(s):
    # A JSON string is a valid YAML double-quoted scalar.
    return json.dumps(s, ensure_ascii=False)


def to_yaml(w):
    year = w["year"] if str(w["year"]).isdigit() else q(str(w["year"]))
    lines = [
        "# TODO: added from ORCID — write the summary, check venue, then remove this line",
        f"- year: {year}",
        f"  title: {q(w['title'])}",
    ]
    if w.get("authors"):
        lines.append("  authors: [" + ", ".join(q(a) for a in w["authors"]) + "]")
    lines += [
        f"  url: {q(w['url'])}",
        f"  venue: {q(w['venue'])}",
        f"  kind: {q(w['kind'])}",
        f"  publisher: {q(w.get('publisher', ''))}",
    ]
    if w.get("doi"):
        lines.append(f"  doi: {q(w['doi'])}")
    for k in ("volume", "issue", "pages"):
        if w.get(k):
            lines.append(f"  {k}: {q(w[k])}")
    lines.append('  summary: ""')
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="print new entries, do not modify the file")
    ap.add_argument("--orcid", default=ORCID_ID, help="ORCID iD")
    ap.add_argument("--input", help="read ORCID works JSON from a file (offline/testing)")
    ap.add_argument("--file", default=str(PUBS), help="publications YAML to update")
    ap.add_argument("--no-crossref", action="store_true",
                    help="do not complete entries from Crossref")
    ap.add_argument("--crossref-input",
                    help="JSON file {doi: crossref message} instead of calling Crossref (testing)")
    a = ap.parse_args()

    path = Path(a.file)
    text = path.read_text(encoding="utf-8")
    data = json.loads(Path(a.input).read_text(encoding="utf-8")) if a.input else fetch(a.orcid)

    dois, titles = existing_keys(text)
    # Publikasi yang sengaja tidak ditampilkan (data/publications-ignore.yml)
    ignore = path.parent / "publications-ignore.yml"
    if ignore.exists():
        d2, t2 = existing_keys(ignore.read_text(encoding="utf-8"))
        dois |= d2
        titles |= t2
    new = []
    for w in works_from(data):
        t = norm_title(w["title"])
        if not t or (w["doi"] and w["doi"] in dois) or t in titles:
            continue
        new.append(w)
        titles.add(t)
        if w["doi"]:
            dois.add(w["doi"])

    if not new:
        print("orcid_sync: no new works.")
        return
    if not a.no_crossref:
        offline = json.loads(Path(a.crossref_input).read_text(encoding="utf-8")) \
            if a.crossref_input else None
        for w in new:
            if w["doi"]:
                m = {k.lower(): v for k, v in offline.items()}.get(w["doi"]) \
                    if offline is not None else fetch_crossref(w["doi"])
                enrich(w, m)
    new.sort(key=lambda w: -int(w["year"]) if str(w["year"]).isdigit() else 0)
    block = "".join(to_yaml(w) for w in new)
    print(f"orcid_sync: {len(new)} new work(s):\n{block}")
    if a.dry_run:
        print("orcid_sync: --dry-run, file not modified.")
        return
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + block, encoding="utf-8")
    print(f"orcid_sync: appended to {path}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as e:
        sys.exit(f"orcid_sync: could not reach ORCID API: {e}")
