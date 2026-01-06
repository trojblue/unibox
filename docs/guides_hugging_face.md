---
description: Load and save Hugging Face datasets and files with unibox.
---

# Hugging Face guide

Unibox supports both **datasets** and **files** hosted on the Hugging Face Hub.

## Dataset vs file URIs

- `hf://owner/repo` -> dataset
- `hf://owner/repo/path/to/file.ext` -> file

!!! tip
    If your path includes a file extension, unibox treats it as a file. Otherwise, it treats it as a dataset.

## Load a dataset

```python
import unibox as ub

# Load the default split (train)
train = ub.loads("hf://my-org/my-dataset")

# Load a specific split
val = ub.loads("hf://my-org/my-dataset", split="validation")

# Load as pandas DataFrame
train_df = ub.loads("hf://my-org/my-dataset", split="train", to_pandas=True)
```

## Save a dataset

```python
import unibox as ub

# Save a DataFrame
ub.saves(train_df, "hf://my-org/my-dataset")

# Save a Dataset or DatasetDict
ub.saves(train, "hf://my-org/my-dataset")
```

### Save options

```python
ub.saves(train_df, "hf://my-org/my-dataset", split="train", private=True)
```

## Save JSON-like inputs

Unibox can convert JSON-like structures into a DataFrame and upload them:

```python
import unibox as ub

# dict input (keys become rows)
ub.saves({"a": 1, "b": {"c": 2}}, "hf://me/my-ds")

# list of dicts (JSONL-style)
ub.saves([{"id": 1}, {"id": 2}], "hf://me/my-ds")

# list of scalars
ub.saves(["foo", "bar"], "hf://me/my-ds")
```

!!! warning
    If the list mixes dicts and non-dicts, unibox will still convert but emits a warning.

## Load a file from HF

```python
import unibox as ub

# Load a JSON file from a dataset repo
cfg = ub.loads("hf://my-org/my-dataset/config.json")
```

## Common pitfalls

- **Auth**: Make sure your token is available (see Credentials).
- **Repo types**: `hf://owner/repo` is assumed to be a dataset.
- **Splits**: If the split does not exist, `datasets` will raise an error.
