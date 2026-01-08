---
name: file-handling
description: Unibox-based file I/O and dataset handling for local paths, S3, and Hugging Face. Use when asked to load/save with ub.loads/ub.saves, upload JSON/JSONL to HF datasets, list or count files in buckets/prefixes (especially image files via ub.IMG_FILES), preview datasets, or work with hf:// and s3:// URIs using unibox. Refer to /local/yada/dev/unibox/docs for authoritative examples.
---

# File Handling (Unibox)

## Overview

Use unibox as ub to load, save, list, and preview data across local files, S3, and Hugging Face. Keep answers short and copy-pasteable, and lean on the bundled reference file for canonical snippets and doc pointers.

## Quick start

Use the core three operations and add options as needed:

```python
import unibox as ub

data = ub.loads("s3://my-bucket/data/sample.csv")
ub.saves(data, "hf://my-org/my-dataset")
files = ub.ls("s3://my-bucket/images", exts=ub.IMG_FILES)
```

Note: `ub.loads`, `ub.saves`, and `ub.ls` print status messages by default; set `debug_print=False` when calling them in tight loops.

## Supported formats (load/save behavior)

- CSV/Parquet: `ub.loads` returns a pandas DataFrame; `ub.saves` expects a DataFrame.
- JSON: `ub.loads` returns dict/list (or None if the file is empty).
- JSONL: `ub.loads` returns a list of parsed objects (often dicts).
- Text (.txt/.md/.markdown): `ub.loads` returns a list of strings; `ub.saves` expects a list of strings (one per line).
- YAML/TOML: `ub.loads` returns a dict-like object.
- Images: `ub.loads` returns `PIL.Image.Image` (or numpy array with `as_array=True`).
- Hugging Face dataset URI (`hf://owner/repo`): `ub.loads` returns a `datasets.Dataset` for the `split` (default `"train"`), or a DataFrame when `to_pandas=True`.

## Common tasks

### Upload JSONL to Hugging Face dataset

Use the JSONL load + save pattern verbatim unless the user asks for changes:

```python
import unibox as ub

data_dict = ub.loads("/data/nyanko/naifu-flux/hpsv3/testset-hpdv3.json")
ub.saves(data_dict, "hf://incantor/hpdv3-nyanko-testset-json")
```

### Count image files under S3 (or any prefix)

Filter by image extensions and count the returned list:

```python
import unibox as ub

image_files = ub.ls("s3://my-bucket/images", exts=ub.IMG_FILES)
count = len(image_files)
```

### Handle HF dataset vs file URIs

Treat `hf://owner/repo` as a dataset and `hf://owner/repo/path/file.ext` as a file. Add `split=...` or `to_pandas=True` only when needed.

## Return values and failure behavior

- `ub.loads(...)`: returns the parsed object above; raises on failures (no backend/loader, missing file, parse errors). It does not return None on failure.
- `ub.loads(..., file=True)`: returns a resolved local `Path` to the downloaded file.
- `ub.saves(...)`: returns None; raises on failure.
- `ub.concurrent_loads(uris)`: returns a list aligned to input order; any failed item is None and errors are logged.
- `ub.ls(...)`: returns `list[str]`; raises if no backend is found.
- `ub.peeks(data, n=3)`: returns a dict with type/shape/head; prints JSON when `console_print=True`.

## References

Load `references/unibox-file-handling.md` for detailed patterns, behaviors, and doc pointers (including the web docs).
