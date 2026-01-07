---
description: Quality-of-life helpers for notebooks, images, dataframes, and quick LLM calls.
---

# Utilities & helpers

Unibox includes small, high‑leverage helpers that make exploration and labeling faster. This page highlights the most useful ones.

## Notebook galleries

### Image gallery

```python
import unibox as ub

ub.gallery(
    ["/path/to/img1.jpg", "/path/to/img2.jpg"],
    labels=["cat", "dog"],
    row_height="200px",
)
```

### Label gallery

```python
import unibox as ub

ub.label_gallery(
    ["/path/to/img1.jpg", "/path/to/img2.jpg"],
    labels=["good", "bad"],
    row_height="150px",
)
```

!!! note
    These functions require IPython/Jupyter. If IPython is not available, they print a warning instead of rendering.

## Image utilities

Helpers for assembling and annotating images live in `unibox.utils.image_utils`:

```python
from unibox.utils.image_utils import (
    add_annotation,
    add_annotations,
    concatenate_images_horizontally,
)
```

### Concatenate images

```python
from PIL import Image

images = [Image.open(p) for p in ["a.jpg", "b.jpg", "c.jpg"]]
combo = concatenate_images_horizontally(images, max_height=512)
combo.save("combo.jpg")
```

### Add annotations

```python
from PIL import Image
from unibox.utils.image_utils import add_annotation

img = Image.open("sample.jpg")
annotated = add_annotation(img, "good", position="top", alignment="center", size="larger")
annotated.save("annotated.jpg")
```

## DataFrame utilities

Useful helpers from `unibox.utils.df_utils`:

```python
from unibox.utils.df_utils import (
    column_memory_usage,
    convert_object_to_category,
    downcast_numerical_columns,
)
```

### JSON-like to DataFrame

If you have dicts or lists and want a DataFrame:

```python
import unibox as ub

df = ub.to_df({"a": 1, "b": {"c": 2}})
```

### Memory usage per column

```python
import pandas as pd

mem = column_memory_usage(df)
print(mem.head())
```

### Reduce memory footprint

```python
# Downcast numeric columns to smaller dtypes
small_df = downcast_numerical_columns(df)

# Convert low-cardinality text columns to categoricals
small_df = convert_object_to_category(small_df, ["country", "segment"])
```

## Quick LLM calls

Lightweight wrappers live in `unibox.utils.llm_api`:

```python
from unibox.utils.llm_api import generate_openai, generate_gemini

text = generate_openai("Summarize this text", api_key="...")
text = generate_gemini("Summarize this text", api_key="...")
```

!!! warning
    These are thin wrappers; handle retries, logging, and rate limits in your own code if needed.

## S3 presigned links

If you need short‑lived URLs for S3 objects:

```python
import unibox as ub

url = ub.presigns("s3://my-bucket/data/file.parquet", expiration=3600)
```

## Next steps

- Task‑oriented snippets using these helpers. [→ Recipes](recipes.md)
- Back to the 5‑minute tour. [→ Quickstart](getting_started_quickstart.md)
- See which file types you can load/save. [→ Supported formats](supported_formats.md)
