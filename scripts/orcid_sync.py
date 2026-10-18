#!/usr/bin/env python3
"""Append new works from ORCID to data/publications.yml.

Fetches the public works list of an ORCID iD and, for every work whose DOI
(or normalised title) is not yet in data/publications.yml, appends a new entry
as plain text (the existing file and its comments are never rewritten).
Running it again adds nothing (idempotent).

Usage:
  python3 scripts/orcid_sync.py               # update data/publications.yml
  python3 scripts/orcid_sync.py --dry-run     # only print what would be added
  python3 scripts/orcid_sync.py --input works.json --dry-run   # offline test

Stdlib only (uses PyYAML for reading if it is installed, else a simple scan).
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ORCID_ID = "0009-0002-9620-7411"
API = "https://pub.orcid.org/v3.0/{id}/works"
ROOT = Path(__file__).resolve().parent.parent
PUBS = ROOT / "data" / "publications.yml"

KIND = {
    "conference-paper": "Conference paper",
    "journal-article": "Journal article",
    "book-review": "Book review",
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
        headers={"Accept": "application/json",
                 "User-Agent": "orcid_sync.py (personal website)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


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
    return (
        "# TODO: added from ORCID — review summary/publisher\n"
        f"- year: {year}\n"
        f"  title: {q(w['title'])}\n"
        f"  url: {q(w['url'])}\n"
        f"  venue: {q(w['venue'])}\n"
        f"  kind: {q(w['kind'])}\n"
        f"  publisher: \"\"\n"
        f"  summary: \"\"\n"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="print new entries, do not modify the file")
    ap.add_argument("--orcid", default=ORCID_ID, help="ORCID iD")
    ap.add_argument("--input", help="read ORCID works JSON from a file (offline/testing)")
    ap.add_argument("--file", default=str(PUBS), help="publications YAML to update")
    a = ap.parse_args()

    path = Path(a.file)
    text = path.read_text(encoding="utf-8")
    data = json.loads(Path(a.input).read_text(encoding="utf-8")) if a.input else fetch(a.orcid)

    dois, titles = existing_keys(text)
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
