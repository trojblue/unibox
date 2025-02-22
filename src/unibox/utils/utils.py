import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def to_relaive_unix_path(absolute_path: str, root_dir: str, convert_slash=True):
    relative_path = os.path.relpath(absolute_path, root_dir)
    if convert_slash:
        relative_path = relative_path.replace("\\", "/")
    return relative_path


def is_s3_uri(uri: str) -> bool:
    """Check if the URI is an S3 URI."""
    parsed = urlparse(uri)
    return parsed.scheme == "s3"


def is_url(path: str) -> bool:
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_hf_uri(uri: str) -> bool:
    """Check if the URI is a Hugging Face URI."""
    return uri.startswith("hf://")


def parse_hf_uri(uri: str) -> tuple[str, str]:
    """Parse a Hugging Face URI into repo_id and path.

    Args:
        uri: A URI in format 'hf://owner/repo/path/to/nested/file.ext'
             or 'hf://owner/repo' for a dataset

    Returns:
        tuple[str, str]: (repo_id, subpath) where:
            - repo_id is 'owner/repo'
            - subpath is the full remaining path after repo (may contain multiple '/')
            - subpath is '' if no path specified (dataset case)
    """
    if not uri.startswith("hf://"):
        raise ValueError("URI must start with 'hf://'")

    # Remove prefix and normalize slashes
    # This handles both hf://owner/repo and hf:///owner/repo
    trimmed = uri[5:].strip("/")
    parts = trimmed.split("/", 2)  # Split into owner, repo, and rest

    if len(parts) < 2:
        raise ValueError(f"Invalid Hugging Face URI format: {uri}. Must contain at least owner/repo.")

    # First two parts form the repo_id
    repo_id = f"{parts[0]}/{parts[1]}"

    # Everything after owner/repo is the subpath (may contain multiple '/')
    subpath = parts[2] if len(parts) > 2 else ""

    return repo_id, subpath


def merge_dicts(*dicts):
    """Merge dictionaries, raising warnings for overlapping keys and data type mismatches.

    Args:
        *dicts: Dictionaries to merge.
        logger: Logger instance for warnings (default: None).

    Returns:
        dict: Merged dictionary.
    """
    assert all(isinstance(d, dict) for d in dicts), "All inputs must be dictionaries."

    result = {}
    for d in dicts:
        for key, value in d.items():
            if key in result:
                logger.warning(f"Overlapping key '{key}' detected. Existing value: {result[key]}, New value: {value}")
                if type(result[key]) != type(value):
                    logger.warning(
                        f"Data type mismatch for key '{key}': {type(result[key])} vs {type(value)}.",
                    )
            result[key] = value

    return result
