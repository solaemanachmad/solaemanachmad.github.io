# Achmad Solaeman — Personal Academic Website

A personal academic website built with [Quarto](https://quarto.org) for GitHub Pages. The same project also produces a **PDF CV** (via Typst).

## Folder structure

```
cv-site/
├── _quarto.yml              Site configuration: menu, theme, includes
├── index.qmd                About (+ certifications list)
├── research.qmd             Research & final-project topics
├── publications.qmd         Publications  ← data/publications.yml
├── teaching.qmd             Teaching      ← courses/*/index.qmd
├── services.qmd             Services      ← data/services.yml
├── posts.qmd                Blog listing  ← posts/*/index.qmd
│
├── data/                    The data you will edit most often
│   ├── publications.yml
│   ├── services.yml
│   └── certificates.yml
│
├── courses/                 One folder per course
│   ├── _metadata.yml
│   └── <course>/
│       ├── index.qmd        course info (title, code, semester, ...)
│       └── meetings.yml     list of meetings + slide links
│
├── posts/                   Blog posts; reader comments are configured in posts/_metadata.yml
│
├── cv/                      CV: web page + PDF, both built from _sections/
│   ├── index.qmd            → _site/cv/index.html (web CV, Download/View PDF buttons)
│   ├── cv.qmd               → _site/cv/solaemanachmad_cv.pdf
│   ├── _sections/           CV content, one file per section (education, experience, ...)
│   ├── cv-style.typ         PDF styling
│   ├── typst-show.typ       PDF title font & colour
│   └── fonts/               Source Sans 3 (fallback when Segoe UI is unavailable)
│
├── assets/
│   ├── images/profile.jpg
│   └── styles/
│       ├── theme.scss       UGM colours, fonts, all layout rules
│       └── theme-dark.scss  dark-mode colours
│
├── _includes/               HTML snippets inserted into every page
│   ├── profile.html         left profile column + "Follow" button (mobile)
│   ├── deck-viewer.html     preview popup for slides & CV (with Download button)
│   └── view-toggle.html     Grid / List toggle and semester tabs
│
├── _templates/              Listing templates (EJS)
│   ├── course-cards.ejs     course cards grouped by academic year
│   ├── meeting-cards.ejs    meeting cards with preview/download
│   ├── year-cards.ejs       Publications & Services cards grouped by year
│   └── compact-list.ejs     compact one-line list (certifications)
│
└── publish.yml              GitHub Actions workflow → move to .github/workflows/
```

Files and folders starting with `_` are not rendered as pages by Quarto.

## Common tasks

| I want to…                      | Edit                                                              |
|---------------------------------|-------------------------------------------------------------------|
| Add news / grant (What's New)   | write a post in `posts/<yyyy-mm-dd-title>/index.qmd` with `categories: [grant, ...]`; the 5 latest appear in What's New on About |
| Add a publication               | `data/publications.yml` only (CV is generated; new ORCID works arrive as a weekly PR) |
| Add a service (reviewer, TPC)   | `data/services.yml` only                                          |
| Add a certificate               | `data/certificates.yml` only                                      |
| Add/close a thesis topic        | `data/topics.yml` (`status`: available / ongoing / taken / draft = hidden) |
| Booking link (office hours)     | `data-url` of the *Book a meeting* line in `_includes/profile.html` (hidden while empty) |
| Visitor statistics              | `GOATCOUNTER_CODE` in `_includes/analytics.html` (off while empty) |
| Search Console verification     | uncomment the meta tag in `_includes/seo-head.html`               |
| Add slides to a meeting         | `courses/<course>/meetings.yml` → fill in `slides:`               |
| Add a new course                | copy a folder in `courses/`, then edit `index.qmd` & `meetings.yml` |
| Teach a course again            | add a line to `semesters:` in `courses/<course>/index.qmd` (see below) |
| Write a post                    | create `posts/<yyyy-mm-dd-title>/index.qmd` (or via GitHub, see *New post*) |
| Change contacts / profile links | `_includes/profile.html`                                          |
| Change the CV content (web + PDF) | `cv/_sections/*.qmd` (section order: `cv/index.qmd` and `cv/cv.qmd`) |
| Change colours / appearance     | `assets/styles/theme.scss` (dark mode: `theme-dark.scss`)         |

### Publications, services & certificates (single source of truth)
`data/publications.yml`, `data/services.yml` and `data/certificates.yml` are the only place to edit these lists.
Before every full render, `scripts/build_cv_sections.py` (Quarto `pre-render`, needs PyYAML) regenerates
`cv/_sections/{publications,services,certificates}.qmd` for the web CV and the PDF CV — do not edit those files by hand.
Every Monday the **ORCID sync** workflow (`scripts/orcid_sync.py`) checks ORCID 0009-0002-9620-7411 and opens a PR
adding any new works to `data/publications.yml`; fill in `summary`/`publisher` before merging
(enable *Settings → Actions → General → Allow GitHub Actions to create and approve pull requests*).
Test locally with `python3 scripts/orcid_sync.py --dry-run`.

### Search engines & link checking
- `_includes/seo-head.html` adds schema.org `Person` data to every page, plus a placeholder for the Google Search Console verification tag.
- `scripts/build_jsonld.py` (pre-render) turns `data/publications.yml` into `_includes/publications-jsonld.html` (schema.org `ScholarlyArticle` list) for the Publications page. Optional per-entry fields: `authors`, `doi`.
- `robots.txt` points crawlers to `sitemap.xml`, generated by Quarto. Page `description:` fields feed search snippets; `body-classes: description-meta-only` keeps them out of the visible page.
- `.github/workflows/link-check.yml` checks the published site for broken links every Monday 06:00 WIB and opens/updates a "Broken links report" issue. LinkedIn, Instagram and Credly are skipped (they block bots).

### Meeting slides (`courses/<course>/meetings.yml`)

```yaml
- meeting: 2
  title: "Entity-Relationship Modeling"
  description: "Entities, attributes, relationships, and cardinality."
  slides: "https://docs.google.com/presentation/d/XXXX/edit"   # Google Slides / PPTX on Drive
  # or:  "https://drive.google.com/file/d/XXXX/view"
  # or:  "m2-er-modeling.pdf"                                   # PDF inside the course folder
  image: "thumbs/m2.png"                                         # thumbnail (optional)
  semester: "2026/2027"                                          # optional, see below
```

The preview and download buttons appear automatically when `slides` is set. Make sure link sharing is set to *Anyone with the link → Viewer*.

### Courses (`courses/<course>/index.qmd`)

Key fields: `title`, `subtitle` (Indonesian name), `code`, `kind` (Lecture/Lab), `semester` (e.g. `"Odd Semester 2026/2027"`) or `semesters` (a list, see below), `order` (higher numbers appear first), `description`.
The Teaching page groups courses by academic year and adds an Odd/Even tag based on the semester name.

### Teaching a course again in another semester

**Rule: one course = one folder.** Do not copy the folder for each semester. This avoids duplicated material and keeps the course page link you shared with students unchanged.

**1. Add the new semester** in `courses/<course>/index.qmd`. Replace `semester:` (a single value) with `semesters:` (a list):

```yaml
# before
semester: "Even Semester 2025/2026"

# after
semesters:
  - "Even Semester 2026/2027"
  - "Even Semester 2025/2026"
```

On the Teaching page, the course then appears under both **Academic Year 2026/2027** and **2025/2026**, and every card links to the same course page.
Also update the info line under the course page title (`[← All courses · ... ]{.meta}`), e.g. `Even Semester 2025/2026 & 2026/2027`.

**2. Same material?** You are done. No change to `meetings.yml` is needed.

**3. Some slides differ?** Add a `semester` field (academic year) only to the meetings that differ:

```yaml
- meeting: 1
  title: "Introduction to Information Security"
  slides: "https://docs.google.com/.../2026"
  semester: "2026/2027"
- meeting: 1
  title: "Introduction to Information Security"
  slides: "https://docs.google.com/.../2025"
  semester: "2025/2026"
- meeting: 2                      # no `semester` = shown in every semester
  title: "Cryptography Basics"
  slides: "https://docs.google.com/..."
```

As soon as any meeting has a `semester` field, the course page shows **one tab per academic year** (newest first). Each tab lists that semester's meetings plus the meetings shared by all semesters.

**When do you need a new folder?** Only when the course itself changes (new curriculum, different code or content). Use a new folder name, e.g. `courses/information-security-2-k2027/`.

**Order on the Teaching page:** the newest academic year comes first. Within a year, Even semester courses appear before Odd ones, then by `order` (higher first).

### New post (also the source of *What's New* on About)

Every post appears in *Posts*; the 5 newest also appear in the **What's New** box on About.
Its `categories` become clickable hashtags (`posts.html#category=grant`).
Keep tags lowercase and reuse existing ones: grant, research, publication, award, talk,
teaching, service, community-service, student, certification, career.

```yaml
---
title: "Title"
description: "One-sentence summary (shown in What's New and Posts)"
date: 2026-11-01
categories: [grant, research]
---
```

**Posting from the browser (no local render needed).** Every push to `main` is rendered and
published by GitHub Actions (`.github/workflows/publish.yml`), usually within a few minutes.

1. Open the **[New post link](https://github.com/solaemanachmad/solaemanachmad.github.io/new/main?filename=posts/2026-11-01-title/index.qmd&value=---%0Atitle%3A%20%22Title%22%0Adescription%3A%20%22One-sentence%20summary%20%28shown%20in%20What%27s%20New%20and%20Posts%29%22%0Adate%3A%202026-11-01%0Acategories%3A%20%5Bgrant%2C%20research%5D%0A---%0A%0AWrite%20the%20post%20here.%0A)** (bookmark it). It opens GitHub's
   "create file" page with the template above already filled in.
2. Change the folder name in the file path (`posts/<yyyy-mm-dd-title>/index.qmd`), the title,
   date, tags, and text → *Commit changes*.
3. Images: open the new post folder on GitHub → *Add file → Upload files*, then use
   `![caption](photo.jpg)` in the post.
4. Progress: the repository's *Actions* tab. Before editing on your computer again, run `git pull`.

For longer edits, press `.` on the repository page to open the web editor (github.dev).

**Reader comments (giscus / GitHub Discussions)**: setup steps are in `posts/_metadata.yml`;
uncomment the same block in `index.qmd` to show the *Discussion* box on About.

## Running locally

1. Install Quarto ≥ 1.6 (Typst is included) and PyYAML (`pip3 install pyyaml`, used by the pre-render scripts).
2. `quarto preview` for a live preview.
3. `quarto render` to build everything (website + PDF CV) into `_site/`.

## Publishing to GitHub Pages

1. Create a repository named **`solaemanachmad.github.io`** (address: `https://solaemanachmad.github.io`).
2. Move `publish.yml` to `.github/workflows/publish.yml`.
3. Push to the `main` branch:
   ```bash
   git init && git add . && git commit -m "Initial site"
   git branch -M main
   git remote add origin https://github.com/solaemanachmad/solaemanachmad.github.io.git
   git push -u origin main
   ```
4. Once, from your computer: `quarto publish gh-pages`.
5. On GitHub: *Settings → Pages → Deploy from a branch → `gh-pages`*.
   After that, every push to `main` is rendered and published automatically.

## Notes

- The phone number appears only in the PDF CV, not on the website.
- Still to fill in: academic data (NIDN, SINTA, grants, community service) in `cv/_sections/academic.qmd`.
