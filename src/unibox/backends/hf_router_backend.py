# unibox/backends/hf_router_backend.py

from pathlib import Path
import logging

from .base_backend import BaseBackend

from typing import Optional

logger = logging.getLogger(__name__)



class HuggingFaceRouterBackend(BaseBackend):
    """A router backend that handles both dataset and file operations for HuggingFace.
    Routes to either HuggingFaceApiBackend (for files) or HuggingFaceDatasetsBackend (for datasets)
    based on the URI structure."""

    def __init__(self):
        super().__init__()

    def _is_file_path(self, path: str) -> bool:
        """Determine if a path refers to a file (has extension) or dataset."""
        return "." in Path(path).name

    def download(self, uri: str, target_dir: Optional[str] = None) :
        """Download from HuggingFace, routing between file and dataset backends.
        """

        # TODO:
        """
        if is dataset: let loader load it
        else: download file using HuggingFaceApiBackend
        """
        return uri  # do nothing, let loader handle it (load dataset as hf://.../)


    def upload(self, local_path: Path, uri: str) -> None:
        """Upload to HuggingFace, routing between file and dataset backends.
        
        Args:
            local_path: Path to local file or dataset directory
            uri: Target HuggingFace URI
        """
        raise NotImplementedError("Upload not supported for HuggingFace URIs")
