---
description: File formats supported by unibox and their loaders.
---

# Supported formats

Unibox routes files by extension and URI scheme. This page summarizes the current mapping.

## File types by extension

| Type | Extensions | Loader | Notes |
| --- | --- | --- | --- |
| Tabular | `.csv` | CSVLoader | Loads to DataFrame |
| Tabular | `.parquet` | ParquetLoader | Loads to DataFrame |
| JSON | `.json` | JSONLoader | Loads to dict/list |
| JSONL | `.jsonl` | JSONLLoader | Loads to list of dicts |
| Text | `.txt`, `.md`, `.markdown` | TxtLoader | Loads to string |
| Images | common image types | ImageLoader | Returns PIL images or arrays |
| Config | `.yaml`, `.yml` | YAMLLoader | Loads to dict |
| Config | `.toml` | TOMLLoader | Loads to dict |

!!! note
    Image extensions are defined in `src/unibox/utils/constants.py`.

## Hugging Face URIs

- `hf://owner/repo` (no file extension) is treated as a **dataset**.
- `hf://owner/repo/path/file.ext` is treated as a **file** and uses the extension mapping above.

## JSON-like saves to Hugging Face

When saving to a dataset URI, `ub.saves` also accepts JSON-like inputs:
- dict
- list of dicts (JSONL-style)
- list of scalars

These are converted into a DataFrame and then uploaded as a dataset.

## Next steps

- Learn dataset vs file semantics and save options. [→ Hugging Face guide](guides_hugging_face.md)
- Load and save common formats from S3. [→ S3 guide](guides_s3.md)
- Task‑oriented snippets using these formats. [→ Recipes](recipes.md)
