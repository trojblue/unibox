---
description: Work with S3 objects using unibox.
---

# S3 guide

Unibox uses boto3 under the hood. If boto3 can access your bucket, unibox will work.

## Load files from S3

```python
import unibox as ub

# CSV to DataFrame
sales = ub.loads("s3://my-bucket/data/sales.csv")

# Parquet to DataFrame
events = ub.loads("s3://my-bucket/data/events.parquet")

# JSON to dict or list
cfg = ub.loads("s3://my-bucket/configs/app.json")
```

## Save files to S3

```python
import unibox as ub

ub.saves(sales, "s3://my-bucket/data/sales_clean.parquet")
ub.saves(cfg, "s3://my-bucket/configs/app_clean.json")
```

## List objects

```python
import unibox as ub

# List only parquet files
files = ub.ls("s3://my-bucket/data", exts=[".parquet"])
print(files[:3])
```

## Tips

!!! tip
    Use `exts` to reduce listing noise for large prefixes.

!!! warning
    If you see AccessDenied errors, check IAM permissions and bucket policy.

## Next steps

- Verify AWS access for your environment. [→ Credentials](getting_started_credentials.md)
- See which file types you can load/save. [→ Supported formats](supported_formats.md)
- Task‑oriented snippets using S3. [→ Recipes](recipes.md)
