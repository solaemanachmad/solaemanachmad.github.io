#!/usr/bin/env python3
"""Membuat _includes/publications-jsonld.html dari data/publications.yml.

Isinya <script type="application/ld+json"> berupa ItemList berisi ScholarlyArticle,
supaya Google memahami daftar publikasi di halaman Publications.
Dijalankan otomatis sebelum render (project.pre-render di _quarto.yml).
File hasilnya jangan diedit manual; edit data/publications.yml saja.

Field opsional per entri di publications.yml:
  authors: daftar nama penulis (list atau string dipisah koma).
           Jika kosong, dipakai pemilik situs (Achmad Solaeman).
  doi:     DOI tanpa prefix https://doi.org/ (opsional).
"""
import json
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "publications.yml")
OUT = os.path.join(ROOT, "_includes", "publications-jsonld.html")

SITE = "https://solaemanachmad.github.io"
OWNER = {
    "@type": "Person",
    "@id": SITE + "/#person",
    "name": "Achmad Solaeman",
    "url": SITE + "/",
    "sameAs": ["https://orcid.org/0009-0002-9620-7411"],
}


def authors_of(entry):
    raw = entry.get("authors")
    if not raw:
        return [OWNER]
    if isinstance(raw, str):
        raw = [a.strip() for a in raw.split(",") if a.strip()]
    people = []
    for name in raw:
        name = str(name).strip()
        if name.lower() == OWNER["name"].lower():
            people.append(OWNER)
        else:
            people.append({"@type": "Person", "name": name})
    return people


def article(entry):
    item = {"@type": "ScholarlyArticle", "name": str(entry.get("title", "")).strip()}
    item["headline"] = item["name"][:110]
    if entry.get("url"):
        item["url"] = str(entry["url"]).strip()
    if entry.get("year"):
        item["datePublished"] = str(entry["year"]).strip()
    item["author"] = authors_of(entry)
    if entry.get("venue"):
        kind = str(entry.get("kind", "")).lower()
        venue_type = "Periodical" if ("journal" in kind or "review" in kind) else "PublicationEvent"
        if venue_type == "Periodical":
            item["isPartOf"] = {"@type": "Periodical", "name": str(entry["venue"]).strip()}
        else:
            # Prosiding konferensi
            item["isPartOf"] = {"@type": "CreativeWork", "name": str(entry["venue"]).strip() + " Proceedings"}
    if entry.get("publisher"):
        item["publisher"] = {"@type": "Organization", "name": str(entry["publisher"]).strip()}
    if entry.get("summary"):
        item["abstract"] = str(entry["summary"]).strip()
    if entry.get("kind"):
        item["genre"] = str(entry["kind"]).strip()
    if entry.get("doi"):
        doi = str(entry["doi"]).strip()
        item["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": doi}
        item.setdefault("sameAs", "https://doi.org/" + doi)
    return item


def main():
    with open(SRC, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    items = [e for e in entries if isinstance(e, dict) and e.get("title")]
    data = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Publications by Achmad Solaeman",
        "url": SITE + "/publications.html",
        "numberOfItems": len(items),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "item": article(e)}
            for i, e in enumerate(items, start=1)
        ],
    }
    # "</" di-escape agar teks judul/abstrak tidak bisa menutup tag <script>.
    body = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    html = (
        "<!-- DIBUAT OTOMATIS oleh scripts/build_jsonld.py dari data/publications.yml. Jangan diedit manual. -->\n"
        '<script type="application/ld+json">\n' + body + "\n</script>\n"
    )
    old = None
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = f.read()
    if old != html:  # tulis hanya jika berubah, supaya quarto preview tidak render ulang terus
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(html)
    print(f"build_jsonld: {len(items)} publications -> {os.path.relpath(OUT, ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
