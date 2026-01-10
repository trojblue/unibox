import logging
import os
from dataclasses import dataclass
from typing import Optional
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


HF_REPO_TYPE_PREFIXES = {
    "dataset": "dataset",
    "datasets": "dataset",
    "model": "model",
    "models": "model",
    "space": "space",
    "spaces": "space",
}


@dataclass(frozen=True)
class HfUriParts:
    repo_id: str
    path_in_repo: str
    revision: Optional[str]
    repo_type: str

    # Backwards-compatible tuple-like behavior for repo_id/path_in_repo.
    def __iter__(self):
        yield self.repo_id
        yield self.path_in_repo

    def __len__(self) -> int:
        return 2

    def __getitem__(self, idx: int):
        return (self.repo_id, self.path_in_repo)[idx]


def parse_hf_uri(uri: str) -> HfUriParts:
    """Parse a Hugging Face URI into repo_id/path/revision/repo_type.

    Args:
        uri: A URI in format 'hf://owner/repo/path/to/nested/file.ext'
             or 'hf://owner/repo' for a dataset

    Returns:
        HfUriParts: Parsed components where:
            - repo_id is 'owner/repo'
            - path_in_repo is the remaining path after repo (may contain multiple '/')
            - revision is optional (from hf://owner/repo@revision)
            - repo_type defaults to "model" unless prefixed (e.g., hf://datasets/owner/repo)
    """
    if not uri.startswith("hf://"):
        raise ValueError("URI must start with 'hf://'")

    # Remove prefix and normalize slashes; handles both hf://owner/repo and hf:///owner/repo
    trimmed = uri[len("hf://") :].strip("/")
    if not trimmed:
        raise ValueError(f"Invalid Hugging Face URI format: {uri}. Must contain at least owner/repo.")

    raw_parts = trimmed.split("/")
    repo_type = "model"
    if raw_parts[0] in HF_REPO_TYPE_PREFIXES:
        repo_type = HF_REPO_TYPE_PREFIXES[raw_parts[0]]
        raw_parts = raw_parts[1:]

    if len(raw_parts) < 2:
        raise ValueError(f"Invalid Hugging Face URI format: {uri}. Must contain at least owner/repo.")

    owner = raw_parts[0]
    repo_and_revision = raw_parts[1]
    path_in_repo = "/".join(raw_parts[2:]) if len(raw_parts) > 2 else ""

    revision = None
    if "@" in repo_and_revision:
        repo_name, revision = repo_and_revision.split("@", 1)
        if not repo_name:
            raise ValueError(f"Invalid Hugging Face URI format: {uri}. Repo name is missing.")
        if revision == "":
            revision = None
    else:
        repo_name = repo_and_revision

    if not repo_name:
        raise ValueError(f"Invalid Hugging Face URI format: {uri}. Repo name is missing.")

    repo_id = f"{owner}/{repo_name}"
    return HfUriParts(repo_id=repo_id, path_in_repo=path_in_repo, revision=revision, repo_type=repo_type)


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
