# loader_router.py
# ... etc
import warnings
from pathlib import Path
from typing import Optional, Union

from ..utils.constants import IMG_FILES
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


def get_loader_for_path(path: Union[str, Path]) -> Optional[BaseLoader]:
    """Get appropriate loader for a given path.

    Args:
        path (Union[str, Path]): File path or URI to load

    Returns:
        Optional[BaseLoader]: Appropriate loader instance or None if no loader found
    """
    path_str = str(path).lower()

    # Handle URI-style paths first
    if path_str.startswith("hf://"):
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
        stacklevel=2
    )
    # Create a fake path with the given suffix to reuse the logic
    return get_loader_for_path(f"file{suffix}")
