#!/usr/bin/env python3
"""Generate CV sections from the data/*.yml files (single source of truth).

Writes:
  cv/_sections/publications.qmd  <- data/publications.yml
  cv/_sections/services.qmd      <- data/services.yml
  cv/_sections/certificates.qmd  <- data/certificates.yml
  cv/_sections/courses.qmd       <- data/training.yml   ("Courses & Training")

Runs automatically as Quarto's `pre-render` step (see _quarto.yml), or by hand:
  python3 scripts/build_cv_sections.py
Requires PyYAML (`pip install pyyaml`).
"""
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    sys.exit("build_cv_sections.py: PyYAML is required (pip install pyyaml)")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "cv" / "_sections"
SEP = " · "  # " · "


def header(name):
    return (f"<!-- GENERATED from data/{name}.yml by scripts/build_cv_sections.py"
            f" — do not edit -->\n")


def load(name):
    with open(DATA / f"{name}.yml", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def s(v):
    return "" if v is None else str(v).strip()


def group_by_year(items):
    """Non-numeric years (e.g. "Ongoing") first, then numeric years descending.
    Within a year, YAML order is kept."""
    groups = {}
    for it in items:
        groups.setdefault(s(it.get("year")), []).append(it)

    def key(y):
        try:
            return (1, -int(y))
        except ValueError:
            return (0, 0)

    return sorted(groups.items(), key=lambda kv: key(kv[0]))  # stable sort


def year_block(year, body):
    return ("::: {.year-grid}\n::: {.year}\n"
            f"**{year}**\n:::\n::: {{.entries}}\n{body}:::\n:::\n")


def link(text, url):
    return f"[{text}]({url})" if url else text


def publications():
    blocks = []
    for year, items in group_by_year(load("publications")):
        entries = []
        for p in items:
            e = f"::: {{}}\n**{link(s(p.get('title')), s(p.get('url')))}**\n"
            authors = p.get("authors") or []
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(",")]
            if authors:
                e += "\n" + ", ".join(f"**{a}**" if "solaeman" in a.lower() else a
                                      for a in authors) + "\n"
            pages = f"pp. {s(p.get('pages'))}" if s(p.get("pages")) else ""
            doi = f"[doi:{s(p.get('doi'))}](https://doi.org/{s(p.get('doi'))})" if s(p.get("doi")) else ""
            meta = SEP.join(x for x in (s(p.get("venue")), s(p.get("kind")),
                                        s(p.get("publisher")), pages, doi) if x)
            if meta:
                e += f"\n[{meta}]{{.meta}}\n"
            if s(p.get("summary")):
                e += f"\n{s(p.get('summary'))}\n"
            entries.append(e + ":::\n")
        blocks.append(year_block(year, "\n".join(entries)))
    return header("publications") + "\n".join(blocks)


SERVICE_GROUPS = [  # same order/labels as _templates/service-groups.ejs
    ("program-committee", "Program Committee"),
    ("peer-review", "Peer Review"),
    ("editorial", "Editorial"),
    ("community-service", "Community Service"),
    ("talks", "Invited Talks & Workshops"),
    ("institutional", "Institutional Service"),
    ("membership", "Memberships"),
    ("other", "Other Service"),
]


def services():
    """Grouped by role (like the Services page); inside a group, newest first.
    The left column shows `period` (or `year`)."""
    items = load("services")
    keys = {k for k, _ in SERVICE_GROUPS}
    blocks = []
    for key, label in SERVICE_GROUPS:
        group = [v for v in items if (v.get("role") if v.get("role") in keys else "other") == key]
        if not group:
            continue
        group = [v for _, v in group_by_year_flat(group)]
        entries = []
        for v in group:
            e = f"**{s(v.get('title'))}**\n"
            meta = SEP.join(x for x in (link(s(v.get("venue")), s(v.get("url"))),
                                        s(v.get("kind"))) if x)
            if meta:
                e += f"\n[{meta}]{{.meta}}\n"
            if s(v.get("summary")):
                e += f"\n{s(v.get('summary'))}\n"
            entries.append(year_block(s(v.get("period")) or s(v.get("year")), e))
        blocks.append(f"### {label}\n\n" + "\n".join(entries))
    return header("services") + "\n".join(blocks)


def group_by_year_flat(items):
    """(year, item) pairs, non-numeric years first, then newest first; stable."""
    out = []
    for year, its in group_by_year(items):
        out += [(year, it) for it in its]
    return out


def courses():
    """Courses & Training from data/training.yml, newest first."""
    items = sorted(load("training"), key=lambda t: s(t.get("date")), reverse=True)
    blocks = []
    for t in items:
        e = f"### {s(t.get('title'))}\n"
        when = s(t.get("period")) or s(t.get("date"))[:4]
        meta = SEP.join(x for x in (link(s(t.get("provider")), s(t.get("url"))),
                                    s(t.get("location")), when) if x)
        if meta:
            e += f"\n[{meta}]{{.meta}}\n"
        if s(t.get("summary")):
            e += f"\n{s(t.get('summary'))}\n"
        blocks.append(e)
    return header("training") + "\n".join(blocks)


def certificates():
    lines = []
    for c in load("certificates"):
        url = s(c.get("url"))
        parts = [link(s(c.get("title")), url)]
        if s(c.get("issuer")):
            parts.append(s(c.get("issuer")))
        cid = url.rstrip("/").rsplit("/", 1)[-1] if url else ""
        if cid:
            parts.append(f"ID {cid}")
        lines.append("- " + SEP.join(parts) + "\n")
    return header("certificates") + "".join(lines)


def write(name, text):
    path = OUT / f"{name}.qmd"
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old != text:  # avoid touching mtime (and re-triggering preview) if unchanged
        path.write_text(text, encoding="utf-8")
        print(f"build_cv_sections: wrote {path.relative_to(ROOT)}")


def main():
    write("publications", publications())
    write("services", services())
    write("certificates", certificates())
    write("courses", courses())


if __name__ == "__main__":
    main()
