# Unibox File Handling Reference

## Doc map (local)

Use these files under `/local/yada/dev/unibox/docs` for authoritative examples:
- `docs/getting_started_quickstart.md`: core `ub.loads`, `ub.saves`, `ub.ls` patterns.
- `docs/guides_s3.md`: S3 load/save/list and IAM notes.
- `docs/guides_hugging_face.md`: HF dataset vs file URIs, splits, save options.
- `docs/supported_formats.md`: extension routing and JSON/JSONL behavior.
- `docs/recipes.md`: quick snippets (peek, concurrent loads, list by extension).
- `docs/utilities.md`: `ub.to_df`, `ub.presigns`, galleries, helper utilities.

## Docs (web)

Use these pages for user-facing docs and examples:
- https://trojblue.github.io/unibox/
- https://trojblue.github.io/unibox/getting_started_quickstart/
- https://trojblue.github.io/unibox/supported_formats/
- https://trojblue.github.io/unibox/guides_hugging_face/
- https://trojblue.github.io/unibox/guides_s3/
- https://trojblue.github.io/unibox/recipes/

## Supported formats and I/O behavior

- CSV (`.csv`): loads to `pandas.DataFrame`; saving expects a DataFrame and writes CSV.
- Parquet (`.parquet`): loads to `pandas.DataFrame`; saving expects a DataFrame and writes Parquet.
- JSON (`.json`): loads to `dict` or `list`; returns None if the file is empty; saving writes JSON bytes.
- JSONL (`.jsonl`): loads to `list[Any]` (often dicts); saving writes one JSON object per line.
- Text (`.txt`, `.md`, `.markdown`): loads to `list[str]` (default strips whitespace); saving expects `list[str]` and writes one line per item.
- YAML/TOML (`.yaml`, `.yml`, `.toml`): loads to a dict-like object; saving writes YAML/TOML.
- Images (common extensions): loads to `PIL.Image.Image` by default, or numpy array when `as_array=True`.
- Hugging Face dataset URI (`hf://owner/repo`): loads to `datasets.Dataset` for the `split` (default `"train"`); use `to_pandas=True` for DataFrame conversion.
- Hugging Face file URI (`hf://owner/repo/path/file.ext`): uses extension-based loaders above.

## Core operations

### Load

```python
import unibox as ub

local_df = ub.loads("data/sample.parquet")
s3_df = ub.loads("s3://my-bucket/data/sample.csv")
hf_ds = ub.loads("hf://my-org/my-dataset")

# Optional: HF split or DataFrame conversion
hf_train_df = ub.loads("hf://my-org/my-dataset", split="train", to_pandas=True)
```

**Behavior notes:**
- `ub.loads(...)` raises on failure (no backend/loader, missing file, or parse errors). It does not return None on failure.
- `ub.loads(..., file=True)` returns a resolved local `Path` to the downloaded file.
- `ub.loads`, `ub.saves`, and `ub.ls` print status messages by default; set `debug_print=False` for tight loops.

### Save

```python
import unibox as ub

ub.saves(local_df, "data/processed.parquet")
ub.saves(s3_df, "s3://my-bucket/data/processed.parquet")
ub.saves(hf_ds, "hf://my-org/my-new-dataset")

# HF save options
ub.saves(hf_train_df, "hf://my-org/my-dataset", split="train", private=True)
```

**Behavior notes:**
- `ub.saves(...)` returns None; errors propagate.
- HF saves accept `DataFrame`, `datasets.Dataset`, `DatasetDict`, or JSON-like (dict/list/tuple) which is converted to a DataFrame before upload.

### List

```python
import unibox as ub

files = ub.ls("s3://my-bucket/data", exts=[".parquet", ".csv"])
```

Use `ub.IMG_FILES` to target images (list is defined in `src/unibox/utils/constants.py`).

**Behavior notes:**
- `ub.ls(...)` returns `list[str]` and raises if no backend is found.

## JSON-like saves to Hugging Face

```python
import unibox as ub

ub.saves({"a": 1, "b": {"c": 2}}, "hf://me/my-ds")
ub.saves([{"id": 1}, {"id": 2}], "hf://me/my-ds")
ub.saves(["foo", "bar"], "hf://me/my-ds")
```

If you need explicit conversion:

```python
import unibox as ub

df = ub.to_df([{"id": 1}, {"id": 2}])
ub.saves(df, "hf://me/my-ds")
```

## Common recipes

### Upload JSONL to Hugging Face dataset

```python
import unibox as ub

data_dict = ub.loads("/data/nyanko/naifu-flux/hpsv3/testset-hpdv3.json")
ub.saves(data_dict, "hf://incantor/hpdv3-nyanko-testset-json")
```

### Count image files under S3

```python
import unibox as ub

image_files = ub.ls("s3://my-bucket/images", exts=ub.IMG_FILES)
count = len(image_files)
```

### Preview data

```python
import unibox as ub

peek = ub.peeks(ub.loads("hf://my-org/my-ds"))
```

**Behavior notes:**
- `ub.peeks(...)` returns a dict with type/shape/head for DataFrames, or head/length for lists and dicts.
- For other inputs, it returns `{"type": type_name, "value": str(data)}`.

### Concurrent loads

```python
import unibox as ub

uris = [
    "s3://my-bucket/data/a.parquet",
    "s3://my-bucket/data/b.parquet",
]
items = ub.concurrent_loads(uris, num_workers=8)
```

**Behavior notes:**
- `ub.concurrent_loads(...)` returns a list aligned to input order.
- If a load fails for a specific URI, that index is None; errors are logged and a warning is emitted if any are missing.

## URI semantics

- `hf://owner/repo` is a dataset.
- `hf://owner/repo/path/file.ext` is a file.
- Add `split=...` to target a split when loading or saving datasets.

## Helpers worth knowing

- `ub.presigns("s3://bucket/key", expiration=3600)` for temporary S3 URLs.
- `ub.IMG_FILES` / `ub.IMAGE_FILES` for image extension lists.
- `ub.peeks(..., console_print=True)` for compact console previews.

## Credentials reminders

- S3 access requires AWS credentials (boto3-compatible).
- HF access requires a token in the environment or HF config.
