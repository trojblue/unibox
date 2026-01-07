---
description: Get up and running with unibox in minutes using local files, S3, and Hugging Face datasets.
---

# Quickstart

Unibox gives you one API for local files, S3, and Hugging Face datasets. This page is a 5-minute tour.

!!! tip
    You can copy-paste these snippets as-is. Replace paths, buckets, and repo IDs with your own.

## Install

```bash
pip install unibox
```

## Load and save in 3 tabs

=== "Local"
    ```python
    import unibox as ub

    # Load a local file
    df = ub.loads("data/sample.parquet")
    print(df.head(3))

    # Save to a new local file
    ub.saves(df, "data/processed.parquet")
    ```

=== "S3"
    ```python
    import unibox as ub

    # Load a file from S3
    df = ub.loads("s3://my-bucket/data/sample.csv")

    # Save back to S3
    ub.saves(df, "s3://my-bucket/data/processed.parquet")
    ```

    !!! note
        You need AWS credentials set up. See the Credentials page.

=== "Hugging Face"
    ```python
    import unibox as ub

    # Load a dataset
    ds = ub.loads("hf://my-org/my-dataset")

    # Save a DataFrame or Dataset to HF
    ub.saves(ds, "hf://my-org/my-new-dataset")
    ```

    !!! note
        Hugging Face dataset URIs use `hf://owner/repo`.

## Peek and list

```python
import unibox as ub

# Peek into a dataset or DataFrame
ub.peeks(ds)

# List files in a folder or bucket prefix
files = ub.ls("s3://my-bucket/data", exts=[".parquet", ".csv"])
print(files[:5])
```

## Next steps

- Set up AWS and Hugging Face access. [→ Credentials](getting_started_credentials.md)
- See which extensions map to which loaders. [→ Supported formats](supported_formats.md)
- Learn splits, revisions, and JSON-like saves. [→ Hugging Face guide](guides_hugging_face.md)
- Explore notebook helpers and image tools. [→ Utilities](utilities.md)
- Try task‑oriented snippets. [→ Recipes](recipes.md)
