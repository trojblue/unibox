---
description: Configure Hugging Face and AWS credentials for unibox.
---

# Credentials

Unibox relies on standard credential chains from the underlying SDKs:
- **Hugging Face** via `huggingface_hub`.
- **AWS** via `boto3`.

This page shows the most common setup paths.

## Hugging Face

### Option 1: Login via CLI (recommended)

```bash
huggingface-cli login
```

This stores a token in your HF cache. `huggingface_hub` will pick it up automatically.

### Option 2: Set env var

```bash
export HF_TOKEN="hf_..."
```

!!! note
    `huggingface_hub` also supports `HUGGINGFACE_HUB_TOKEN`. If both exist, it uses the highest-priority token it finds.

### Verify

```python
import unibox as ub

# This should work if your token is valid
ub.loads("hf://huggingface/README")
```

## AWS (S3)

### Option 1: Environment variables

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
```

### Option 2: AWS config files

Most users already have these in:
- `~/.aws/credentials`
- `~/.aws/config`

Boto3 will detect them automatically.

### Verify

```python
import unibox as ub

# Try listing a bucket prefix
ub.ls("s3://my-bucket/data", exts=[".csv"])
```

!!! warning
    If you see permission errors, double-check the bucket policy and IAM permissions.

## Optional: helper

If you already have credentials cached locally, you can apply them with:

```python
from unibox.utils.credentials_manager import apply_credentials

apply_credentials("aws", "hf")
```

This helper loads standard credential locations and exports environment variables for the current process.

## Next steps

<div class="grid cards" markdown>

- __Quickstart__

  ---

  Jump back to the 5‑minute tour.

  [:octicons-arrow-right-24: Quickstart](getting_started_quickstart.md)

- __Hugging Face guide__

  ---

  Load and save datasets and files.

  [:octicons-arrow-right-24: HF Guide](guides_hugging_face.md)

- __S3 guide__

  ---

  Read and write objects from S3.

  [:octicons-arrow-right-24: S3 Guide](guides_s3.md)

</div>
