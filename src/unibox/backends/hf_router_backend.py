# unibox/backends/hf_router_backend.py

from pathlib import Path
from typing import List, Optional, Any, Union

import pandas as pd

from ..utils.logger import UniLogger
from .base_backend import BaseBackend
from .hf_api_backend import HuggingFaceApiBackend
from .hf_datasets_backend import HuggingFaceDatasetsBackend, parse_hf_uri

logger = UniLogger()


def has_dot_in_final_segment(subpath: str) -> bool:
    """Quick check: if the last path segment has a '.' in it, we treat that
    as a 'file-like' path. e.g. "folder/stuff.bin" or "myfile.parquet"
    """
    seg = subpath.split("/")[-1] if subpath else ""
    return "." in seg


class HuggingFaceRouterBackend(BaseBackend):
    """A meta-backend that routes operations between dataset and file APIs:
    - If there's no subpath or no extension => use dataset API
    - If there's a file extension => use file API
    - For ambiguous cases, try dataset API first, then fall back to file API
    """

    def __init__(self):
        super().__init__()
        self.api_backend = HuggingFaceApiBackend()  # single-file operations
        self.ds_backend = HuggingFaceDatasetsBackend()  # dataset operations

    def download(self, uri: str, target_dir: Optional[str] = None, **kwargs) -> Path:
        """Download from HuggingFace, using either dataset or file API.
        
        Args:
            uri: HuggingFace URI (hf://owner/repo or hf://owner/repo/path/to/file)
            target_dir: Local directory to download to
            **kwargs: Additional arguments:
                For datasets: split, streaming, revision, etc.
                For files: revision, repo_type, etc.
        
        Returns:
            Path: Local path to downloaded file or dataset
        """
        repo_id, subpath = parse_hf_uri(uri)
        
        # Ensure target_dir is a string if provided
        target_dir_str = str(target_dir) if target_dir is not None else None
        
        # Case 1: No subpath or no extension => dataset
        if not subpath or not has_dot_in_final_segment(subpath):
            try:
                return self.ds_backend.download(uri, target_dir=target_dir_str, **kwargs)
            except Exception as e:
                logger.debug(f"Dataset download failed: {e}, trying file API")
                return self.api_backend.download(uri, target_dir=target_dir_str, **kwargs)
        
        # Case 2: Has file extension => file API first
        try:
            return self.api_backend.download(uri, target_dir=target_dir_str, **kwargs)
        except Exception as e:
            logger.debug(f"File download failed: {e}, trying dataset API")
            return self.ds_backend.download(uri, target_dir=target_dir_str, **kwargs)

    def upload(self, local_path: Path, uri: str, **kwargs) -> None:
        """Upload to HuggingFace, using either dataset or file API.
        
        Args:
            local_path: Path to local file or dataset
            uri: Target HuggingFace URI
            **kwargs: Additional arguments:
                For datasets: split, private, etc.
                For files: repo_type, commit_message, etc.
        """
        repo_id, subpath = parse_hf_uri(uri)
        
        # Case 1: No subpath => dataset push
        if not subpath:
            self.ds_backend.upload(local_path, uri, **kwargs)
            return
            
        # Case 2: Has subpath => file upload
        self.api_backend.upload(local_path, uri, **kwargs)

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """List contents in HuggingFace repo.
        
        Args:
            uri: HuggingFace URI to list
            exts: Optional file extensions to filter by
            relative_unix: Return paths with forward slashes
            debug_print: Show progress
            **kwargs: Additional backend-specific arguments
        
        Returns:
            List[str]: List of URIs or paths
        """
        repo_id, subpath = parse_hf_uri(uri)
        
        # Try file API first as it's more reliable for listing
        try:
            return self.api_backend.ls(uri, exts=exts, relative_unix=relative_unix, debug_print=debug_print, **kwargs)
        except Exception as e:
            logger.debug(f"File API listing failed: {e}, trying dataset API")
            return self.ds_backend.ls(uri, exts=exts, relative_unix=relative_unix, debug_print=debug_print, **kwargs)

    def load_dataset(self, repo_id: str, **kwargs) -> Any:
        """Load a dataset using the dataset API.
        
        Args:
            repo_id: Repository ID ("owner/repo")
            **kwargs: Dataset loading options (split, streaming, etc.)
        """
        return self.ds_backend.load_dataset(repo_id, **kwargs)

    def data_to_hub(self, data: Union[Any, pd.DataFrame], repo_id: str, **kwargs) -> None:
        """Push data to hub as a dataset.
        
        Args:
            data: Data to push (DataFrame or Dataset)
            repo_id: Target repository ID
            **kwargs: Dataset push options (private, split, etc.)
        """
        self.ds_backend.data_to_hub(data, repo_id, **kwargs)
