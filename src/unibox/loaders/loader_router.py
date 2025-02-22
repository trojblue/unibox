# loader_router.py
# ... etc
import warnings
from pathlib import Path
from typing import Optional, Union, Any

from ..utils.constants import IMG_FILES
from ..utils.logger import UniLogger as logger
from .base_loader import BaseLoader
from .csv_loader import CSVLoader
from .hf_dataset_loader import HFDatasetLoader
from .image_loder import ImageLoader
from .json_loader import JSONLoader
from .jsonl_loader import JSONLLoader
from .parquet_loader import ParquetLoader
from .toml_loader import TOMLLoader
from .txt_loader import TxtLoader
from .yaml_loader import YAMLLoader


def _parse_hf_uri(uri: str) -> tuple[str, str]:
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


def get_loader_for_path(path: Union[str, Path]) -> Optional[BaseLoader]:
    """Get appropriate loader for a given path.

    Args:
        path (Union[str, Path]): File path or URI to load

    Returns:
        Optional[BaseLoader]: Appropriate loader instance or None if no loader found
    """
    path_str = str(path).lower()

    # Handle HuggingFace URIs
    if path_str.startswith("hf://"):
        repo_id, subpath = _parse_hf_uri(path_str)
        # If no subpath or no extension in subpath, treat as dataset
        if not subpath or "." not in subpath:
            return HFDatasetLoader()
        # If there's a subpath with extension, treat as file and use appropriate loader
        path_str = subpath

    # For other URIs (s3://, etc.), extract the filename part
    elif "://" in path_str:
        # Get the last part of the path (filename)
        path_str = path_str.split("/")[-1]
        if not path_str:
            return None

    # Handle file extensions
    suffix = Path(path_str).suffix.lower()
    if suffix == ".csv":
        return CSVLoader()
    if suffix in IMG_FILES:
        return ImageLoader()
    if suffix == ".json":
        return JSONLoader()
    if suffix == ".jsonl":
        return JSONLLoader()
    if suffix == ".parquet":
        return ParquetLoader()
    if suffix == ".txt":
        return TxtLoader()
    if suffix == ".toml":
        return TOMLLoader()
    if suffix == ".yaml" or suffix == ".yml":
        return YAMLLoader()

    return None


def get_loader_for_suffix(suffix: str) -> Optional[BaseLoader]:
    """DEPRECATED: Use get_loader_for_path instead.
    
    This function is kept for backward compatibility and will be removed in a future version.
    """
    warnings.warn(
        "get_loader_for_suffix is deprecated and will be removed in a future version. "
        "Use get_loader_for_path instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Create a fake path with the given suffix to reuse the logic
    return get_loader_for_path(f"file{suffix}")


def load_data(path: Union[str, Path], loader_config: Optional[dict] = None) -> Any:
    """High-level function to load data using the appropriate loader.
    
    Args:
        path (Union[str, Path]): Path to the file or dataset to load
        loader_config (Optional[dict]): Configuration options for the loader
        
    Returns:
        Any: The loaded data
        
    Raises:
        ValueError: If no appropriate loader is found
    """
    path_str = str(path)
    loader = get_loader_for_path(path_str)
    if loader is None:
        raise ValueError(f"No loader found for path: {path_str}")
    
    # Don't convert URIs to Path objects as it normalizes slashes
    if "://" in path_str:
        return loader.load(path_str, loader_config=loader_config or {})
    
    # For local files, use Path
    return loader.load(Path(path_str), loader_config=loader_config or {})
