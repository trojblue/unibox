# unibox/backends/hf_router_backend.py

from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import pandas as pd
from datasets import Dataset, DatasetDict, load_from_disk
import logging

from ..utils.logger import UniLogger
from .base_backend import BaseBackend
from .hf_api_backend import HuggingFaceApiBackend, parse_hf_uri
from .hf_datasets_backend import HuggingFaceDatasetsBackend

from datasets import load_dataset, Dataset, DatasetDict, IterableDatasetDict, IterableDataset

logger = logging.getLogger(__name__)


def has_dot_in_final_segment(subpath: str) -> bool:
    """Quick check: if the last path segment has a '.' in it, we treat that
    as a 'file-like' path. e.g. "folder/stuff.bin" or "myfile.parquet"
    """
    seg = subpath.split("/")[-1] if subpath else ""
    return "." in seg


class HuggingFaceRouterBackend(BaseBackend):
    """A router backend that handles both dataset and file operations for HuggingFace.
    Routes to either HuggingFaceApiBackend (for files) or HuggingFaceDatasetsBackend (for datasets)
    based on the URI structure."""

    def __init__(self):
        super().__init__()
        self.api_backend = HuggingFaceApiBackend()
        self.datasets_backend = HuggingFaceDatasetsBackend()

    def _is_file_path(self, path: str) -> bool:
        """Determine if a path refers to a file (has extension) or dataset."""
        return "." in Path(path).name

    def download(self, uri: str, target_dir: Optional[str] = None) -> Path|Dataset|DatasetDict|IterableDatasetDict | IterableDataset | str:
        """Download from HuggingFace, routing between file and dataset backends.
        
        Args:
            uri: HuggingFace URI (hf://owner/repo[/path])
            target_dir: Local directory to save to
            
        Returns:
            Path to downloaded content (file or dataset directory)
        """
        repo_id, subpath = parse_hf_uri(uri)
        
        # Convert target_dir to string if provided
        target_dir_str = str(target_dir) if target_dir is not None else ""
        
        # Route based on whether it looks like a file path
        if not self._is_file_path(subpath):
            # For datasets, call load_dataset and return directly (download is handled by datasets lib)
                    # We know this is meant to be a dataset
            
            # TODO: change later for splits or remove it
            # ds = load_dataset(repo_id, split="train")
            # logger.debug(f"Downloaded dataset {repo_id}")
            # return ds  # <-- Return in-memory
            return uri  # do nothing, let loader handle it (load dataset as hf://.../)
        else:
            # For files, use the API backend
            return self.api_backend.download(uri, target_dir_str)


    def upload(self, local_path: Path, uri: str) -> None:
        """Upload to HuggingFace, routing between file and dataset backends.
        
        Args:
            local_path: Path to local file or dataset directory
            uri: Target HuggingFace URI
        """
        repo_id, subpath = parse_hf_uri(uri)
        
        # If uploading a directory or the URI has no extension, treat as dataset
        if local_path.is_dir() or not self._is_file_path(subpath):
            self.datasets_backend.data_to_hub(local_path, repo_id)
            # Update README with dataset statistics
            try:
                stats = self._generate_dataset_stats(local_path)
                self.api_backend.update_readme(repo_id, stats)
            except Exception as e:
                logger.warning(f"Failed to update README with stats: {e}")
        else:
            self.api_backend.upload(local_path, uri)

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """List contents from HuggingFace, using appropriate backend.
        
        Args:
            uri: HuggingFace URI to list
            exts: Optional file extensions to filter by
            relative_unix: Return paths in relative unix format
            debug_print: Whether to print debug info
            
        Returns:
            List of paths/URIs
        """
        repo_id, subpath = parse_hf_uri(uri)
        
        # If looking at a specific file path, use API backend
        if self._is_file_path(subpath):
            return self.api_backend.ls(uri, exts, relative_unix, debug_print, **kwargs)
        
        # For dataset listing, try both backends and combine results
        try:
            dataset_files = self.datasets_backend.ls(uri, exts, relative_unix, debug_print, **kwargs)
        except NotImplementedError:
            dataset_files = []
            
        try:
            api_files = self.api_backend.ls(uri, exts, relative_unix, debug_print, **kwargs)
        except NotImplementedError:
            api_files = []
            
        return list(set(dataset_files + api_files))

    def _generate_dataset_stats(self, dataset_path: Path) -> str:
        """Generate statistics about a dataset for the README.
        
        Args:
            dataset_path: Path to local dataset
            
        Returns:
            Markdown formatted string with dataset statistics
        """
        try:
            ds = load_from_disk(str(dataset_path))
            stats = ["## Dataset Statistics\n"]
            
            # Handle both Dataset and DatasetDict
            if isinstance(ds, DatasetDict):
                # Get first split for stats
                first_split = next(iter(ds.values()))
                ds = cast(Dataset, first_split)
            elif not isinstance(ds, Dataset):
                raise ValueError("Expected Dataset or DatasetDict")
            
            # Basic info
            stats.append(f"- Number of examples: {len(ds)}")
            if hasattr(ds, 'features'):
                stats.append(f"- Features: {list(ds.features.keys())}")
            
            # Column statistics
            df = cast(pd.DataFrame, ds.to_pandas())  # Cast to help type checker
            stats.append("\n### Column Statistics")
            for col in df.columns:
                col_data = df[col]  # Get column data
                stats.append(f"\n#### {col}")
                stats.append(f"- Type: {col_data.dtype}")
                if col_data.dtype in ['int64', 'float64']:
                    stats.append(f"- Mean: {col_data.mean():.2f}")
                    stats.append(f"- Std: {col_data.std():.2f}")
                stats.append(f"- Null values: {col_data.isnull().sum()}")
            
            return "\n".join(stats)
        except Exception as e:
            logger.warning(f"Failed to generate dataset statistics: {e}")
            return "## Dataset Statistics\nFailed to generate statistics."

    def load_dataset(self, repo_id: str, **kwargs) -> Any:
        """Load a dataset from HuggingFace Hub.
        
        Args:
            repo_id: Repository ID (owner/repo)
            **kwargs: Dataset loading options (split, streaming, etc.)
        """
        return self.datasets_backend.load_dataset(repo_id, **kwargs)

    def data_to_hub(self, data: Union[Any, pd.DataFrame], repo_id: str, **kwargs) -> None:
        """Push data to HuggingFace Hub as a dataset.
        
        Args:
            data: Data to push (DataFrame or Dataset)
            repo_id: Target repository ID
            **kwargs: Dataset push options (private, split, etc.)
        """
        self.datasets_backend.data_to_hub(data, repo_id, **kwargs)
