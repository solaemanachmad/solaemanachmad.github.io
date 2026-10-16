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
├── cv/                      PDF CV (PDF only, no web page)
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
| Add a publication               | `data/publications.yml` **and** `cv/_sections/publications.qmd`   |
| Add a service (reviewer, TPC)   | `data/services.yml` **and** `cv/_sections/services.qmd`           |
| Add a certificate               | `data/certificates.yml` **and** `cv/_sections/certificates.qmd`   |
| Add slides to a meeting         | `courses/<course>/meetings.yml` → fill in `slides:`               |
| Add a new course                | copy a folder in `courses/`, then edit `index.qmd` & `meetings.yml` |
| Teach a course again            | add a line to `semesters:` in `courses/<course>/index.qmd` (see below) |
| Write a post                    | create `posts/<yyyy-mm-dd-title>/index.qmd`                       |
| Change contacts / profile links | `_includes/profile.html`                                          |
| Change the PDF CV content       | `cv/_sections/*.qmd`                                              |
| Change colours / appearance     | `assets/styles/theme.scss` (dark mode: `theme-dark.scss`)         |

The website and the PDF CV use separate sources for publications, services, and certificates (web: `data/*.yml`, PDF: `cv/_sections/`), so update both.

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

### New post

```yaml
---
title: "Title"
description: "One-sentence summary"
date: 2026-11-01
categories: [research]
---
```

Reader comments (giscus / GitHub Discussions) can be enabled in `posts/_metadata.yml` once the repository is published.

## Running locally

1. Install Quarto ≥ 1.6 (Typst is included).
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
