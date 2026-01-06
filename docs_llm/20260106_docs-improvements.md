# Documentation Improvement Plan (Revised)

This plan incorporates style and structure cues from the Argilla docs guide while keeping scope appropriate for a smaller project.

## Snapshot: Current Docs
- **README.md**: Short overview + install + quick start.
- **Docs site**: `docs/index.md` embeds README; other pages embed CONTRIBUTING/CHANGELOG/etc.
- **API reference**: Auto-generated via mkdocstrings; no curated guides.
- **Design notes**: Minimal.

## What New Users Struggle With
1) **No onboarding path**: nothing like a “5‑minute quickstart”.
2) **No mental model** of URI routing (local vs S3 vs HF dataset vs HF file).
3) **Missing format matrix**: supported file types and their loaders are not surfaced.
4) **Auth guidance absent**: HF token / S3 credentials are likely the first blocker.
5) **Utility discovery**: `ls`, `peeks`, `concurrent_loads`, gallery helpers are buried.
6) **No task‑oriented recipes**: “I want to…” flows are missing.
7) **No CLI page**: CLI exists but is undocumented.

## Principles (adapted from Argilla docs)
- **Diátaxis‑lite**: keep 4 modes but smaller: Getting Started, Guides, Reference, Recipes.
- **Code‑first**: every section has runnable snippets.
- **Short, focused pages**: avoid monoliths; link between pages.
- **Routing landing pages**: use MkDocs “cards” to direct users.
- **Admonitions**: warnings for auth/credentials, tips for common pitfalls.

## Proposed Structure (small but scalable)
- **Home** (README, but add cards)
- **Getting Started**
  - Quickstart (local + HF + S3)
  - Credentials (HF token + S3 setup)
- **Guides**
  - Local Files
  - S3
  - Hugging Face Datasets
- **Recipes**
  - Preview data with `peeks`
  - Concurrent loads
  - Dataset summary (HF save/readme)
- **Reference** (auto-generated API)
- **CLI** (if applicable)

## High‑Impact Page Drafts
### 1) Quickstart
- 3 minimal examples with expected output (tiny previews).
- Use tabs: Local / S3 / HF dataset.
- End with “Next steps” card links.

### 2) Core Concepts (short)
- One diagram or bullet list for URI routing logic.
- Explicit rules for HF dataset vs HF file path.
- Explain `loader_config` pass‑through.

### 3) Supported Formats
- Table: extension → loader → notes.
- Highlight that JSON/JSONL can be files or HF dataset inputs.

### 4) Hugging Face Guide
- Loading splits/revision/streaming.
- Saving DataFrame/Dataset/DatasetDict.
- JSON‑like save behavior (dict/list of dicts/scalars).
- Common pitfalls (auth, repo existence, split names).

### 5) S3 Guide
- Credential sources (ENV, config files, IAM).
- Examples: load/save + `ls` with extensions.

### 6) CLI Page
- `python -m unibox --help` excerpt.
- Simple examples if CLI supports them.

## Improvements to README
- Add a **mini quickstart** with expected output.
- Add “Why unibox?” bullets + links to Guides.
- Fix CONTRIBUTING link (currently empty).

## Concrete TODOs
1) Add a **Quickstart** page (Getting Started).
2) Add **Credentials** page (HF + S3).
3) Add **Supported Formats** page.
4) Add **Hugging Face** + **S3** guides.
5) Add **Recipes** page for peeks + concurrent loads.
6) Update README with mini quickstart + links.

## Notes
- Keep docs short and actionable; avoid heavy narrative.
- Use MkDocs “cards” on index pages to route users.
- Each page should include at least one runnable snippet.
