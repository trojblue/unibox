# loader_router.py
# ... etc
import warnings
from pathlib import Path
from typing import Any, Optional, Union

from ..backends.backend_router import get_backend_for_uri
from ..utils.constants import IMG_FILES
from ..utils.utils import parse_hf_uri
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


def is_hf_dataset_dir(path_str: str) -> bool:
    """Check if the given path is a Hugging Face dataset directory.

    Args:
        path (Path): Path to check
    """
    path = Path(path_str)
    if not path.is_dir():
        return False

    hf_signature_files = ["dataset_dict.json", "dataset_info.json"]
    return any((path / f).is_file() for f in hf_signature_files)


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
        repo_id, subpath = parse_hf_uri(path_str)
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

    if is_hf_dataset_dir(path_str):
        return HFDatasetLoader()

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
        stacklevel=2,
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
    # 1. Which backend?
    backend = get_backend_for_uri(path_str)
    if not backend:
        raise ValueError(f"No backend found for: {path_str}")

    # 2. Download
    local_path = backend.download(path_str)

    # if it's huggingface, let loader load it instead of downloading at backend
    if not str(local_path).startswith("hf://"):
        if not local_path.exists():
            raise FileNotFoundError(f"Downloaded file/folder not found: {local_path}")

    # Otherwise, extension-based logic
    loader = get_loader_for_path(local_path)

    if not loader:
        raise ValueError(f"No loader found for path: {local_path}")

    # 4. Let the loader parse
    return loader.load(local_path, loader_config=loader_config or {})
