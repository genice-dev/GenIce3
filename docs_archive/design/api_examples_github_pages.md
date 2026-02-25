# Strategy: Publishing examples/api as GitHub Pages

**Update:** Plan 2 (MkDocs Material) was adopted. The old `docs/` content was moved to `docs_archive/`. The live manual is built from `docs/` with MkDocs; `docs/api-examples/` uses symlinks to `examples/api/*/README.md`. See `mkdocs.yml` and `.github/workflows/mkdocs.yml`.

---

## Current state (at design time)

- **GitHub Pages**: Already used (source: `docs/`, theme: `jekyll-theme-minimal`).
- **Manual URL**: https://genice-dev.github.io/GenIce3
- **examples/api**: README.md at root + one README per subdir (basic, cif_io, doping, guest_occupancy, polarization, unitcell_transform, topological_defects, tools). No Jekyll/MkDocs in examples/api.

## Goals

- Publish the **examples/api** structure and READMEs as browsable pages under GitHub Pages.
- Prefer a single source of truth (the READMEs in examples/api) and minimal duplicate content.
- Optionally link to or show the example scripts (.py) from the same pages.

---

## Option 1: Jekyll only – sync READMEs into `docs/` (recommended)

**Idea:** Keep using the existing Jekyll site. Add an **API Examples** section under `docs/` whose content is **generated from** `examples/api/**/README.md`.

**Steps:**

1. Add a small script (e.g. `scripts/sync_api_docs.py` or under `examples/api/tools/`) that:
   - Copies `examples/api/README.md` → `docs/api-examples/index.md` (or `api-examples.md`).
   - Copies each `examples/api/<name>/README.md` → `docs/api-examples/<name>.md`.
   - Optionally adds Jekyll front matter (e.g. `title`, `layout`) so the theme renders them correctly.

2. Run this script:
   - Manually before committing doc changes, or
   - In CI (e.g. GitHub Actions) before building Jekyll, so that the published site always reflects the current READMEs.

3. Add a link from the main docs index (if you have one) to `api-examples/` so users can reach the examples from the manual.

**Pros:** Reuses current setup; single source of truth (examples/api); no new dependencies.  
**Cons:** Need to run the sync step (or automate it in CI).

---

## Option 2: MkDocs (Material) for the whole manual + examples

**Idea:** Switch the published site from Jekyll to **MkDocs** (e.g. with **mkdocs-material**). Use MkDocs’ nav to mirror the examples/api structure; doc sources can be the READMEs (via symlinks or a sync script).

**Steps:**

1. Add `mkdocs.yml` at repo root and optional dependency `mkdocs-material`.
2. Set `docs_dir` to a directory that contains:
   - Existing design/ and other docs (moved or copied),
   - An `api-examples/` tree: either symlinks to `examples/api/*/README.md` or copies produced by a script.
3. Configure `nav` so that “API examples” appears as a section with subpages (basic, cif_io, doping, …).
4. Build with `mkdocs build` and deploy the `site/` output to GitHub Pages (e.g. push to `gh-pages` or use `mkdocs gh-deploy` / GitHub Actions).

**Pros:** Nice navigation, search, and code highlighting; one tool for all docs.  
**Cons:** Replaces or duplicates the current Jekyll workflow; need to migrate existing `docs/` content and adjust CI.

---

## Option 3: Jekyll + “include” or data from examples/api

**Idea:** Keep Jekyll, but avoid copying READMEs: let Jekyll **read** the Markdown from `examples/api` at build time (e.g. with a plugin or a custom Liquid include that reads files from the repo).

**Steps:**

1. Use a Jekyll plugin that can include content from arbitrary paths (e.g. `jekyll-readme-index` or a small custom plugin), or generate a Jekyll “collection” from examples/api in a pre-build step.
2. Build the site so that each examples/api subdir is rendered as a page.

**Pros:** No duplicate README files.  
**Cons:** Relies on plugin or custom logic; GitHub Pages only allows a limited set of Jekyll plugins unless you use a custom Actions workflow.

---

## Recommendation

- **Short term / minimal change:** **Option 1** (sync script + Jekyll). You keep the current theme and URL; only add a sync step and a new `docs/api-examples/` section. Easy to revert and no new stack.
- **Long term / better UX:** If you want a richer manual (navigation, search, code tabs), consider **Option 2** (MkDocs) and migrate the rest of `docs/` into it; then examples/api can be a first-class section with the same look and feel.

If you tell me which option you prefer (e.g. “Option 1 with a sync script”), I can outline the exact file layout and a minimal `sync_api_docs.py` (or equivalent) step by step.
