# unibox

[![ci](https://github.com/trojblue/unibox/workflows/ci/badge.svg)](https://github.com/trojblue/unibox/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://trojblue.github.io/unibox/)
[![pypi version](https://img.shields.io/pypi/v/unibox.svg)](https://pypi.org/project/unibox/)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#unibox:gitter.im)

**A unified interface for seamless file operations across local, S3, and Hugging Face ecosystems.**

`unibox` simplifies loading, saving, and exploring data—whether it's a local CSV, an S3-hosted image, or an entire Hugging Face dataset. With a single API, you can handle diverse file types and storage backends effortlessly.

## Installation

```bash
pip install unibox
```

Or with `uv`:

```bash
uv tool install unibox
```



## Quick Start

Load anything, anywhere:

```python
import unibox as ub

# Local parquet file
df = ub.loads("data/sample.parquet")

# S3-hosted text file
lines = ub.loads("s3://my-bucket/notes.txt")

# Hugging Face dataset
dataset = ub.loads("hf://user/repo")
```

Save with ease:

```python
ub.saves(df, "s3://my-bucket/processed.parquet")
ub.saves(dataset, "hf://my-org/new-dataset")
```

List files or peek at data:

```python
# List all JPGs in an S3 folder
images = ub.ls("s3://bucket/images", exts=[".jpg"])

# Preview a dataset
ub.peeks(dataset)
```



## Why unibox?

- **Versatile**: Handles CSVs, images, datasets, and more—locally or remotely.
- **Simple**: One function call to load or save, no matter the source.
- **Transformative**: From quick data peeks to concurrent downloads, it scales with your needs.



Explore the full power in our [documentation](https://trojblue.github.io/unibox/).



## Contributing

Love unibox? Join us! Check out [CONTRIBUTING.md]() to get started.

Extra dev notes: see [README_dev.md](./README_dev.md).
