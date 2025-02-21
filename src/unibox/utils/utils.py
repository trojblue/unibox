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
