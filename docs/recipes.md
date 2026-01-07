---
description: Task-oriented recipes for common unibox workflows.
---

# Recipes

Short, task-oriented snippets for common workflows.

## Quick peek

```python
import unibox as ub

# Works for DataFrames, lists, dicts, and datasets
peek = ub.peeks(ub.loads("hf://my-org/my-ds"))
print(peek)
```

!!! tip
    `peeks(..., console_print=True)` prints a compact JSON preview to stdout.

## Concurrent loads

```python
import unibox as ub

uris = [
    "s3://my-bucket/data/a.parquet",
    "s3://my-bucket/data/b.parquet",
    "s3://my-bucket/data/c.parquet",
]

items = ub.concurrent_loads(uris, num_workers=8)
print(len(items))
```

## List and filter by extension

```python
import unibox as ub

images = ub.ls("s3://my-bucket/images", exts=[".jpg", ".png"])
print(images[:5])
```

## Save JSON-like data to HF

```python
import unibox as ub

# List of dicts
ub.saves([{"id": 1}, {"id": 2}], "hf://me/quick-ds")

# List of strings
ub.saves(["alpha", "beta"], "hf://me/strings-ds")
```

## Next steps

- Notebook helpers and image tools. [→ Utilities](utilities.md)
- Full dataset save/load options. [→ Hugging Face guide](guides_hugging_face.md)
- Load and save files on S3. [→ S3 guide](guides_s3.md)
