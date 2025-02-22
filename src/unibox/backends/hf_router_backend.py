# unibox/backends/hf_router_backend.py
import logging
from pathlib import Path
from typing import Optional, List

from .base_backend import BaseBackend
from .hf_api_backend import HuggingFaceApiBackend

logger = logging.getLogger(__name__)


class HuggingFaceRouterBackend(BaseBackend):
    """A router backend that handles both dataset and file operations for HuggingFace.
    Routes to either HuggingFaceApiBackend (for files) or HuggingFaceDatasetsBackend (for datasets)
    based on the URI structure.
    """

    def __init__(self):
        super().__init__()
        self.api_backend = HuggingFaceApiBackend()

    def _is_file_path(self, path: str) -> bool:
        """Determine if a path refers to a file (has extension) or dataset."""
        return "." in Path(path).name

    def download(self, uri: str, target_dir: Optional[str] = None):
        """Download from HuggingFace, routing between file and dataset backends."""
        if self._is_file_path(uri):
            return self.api_backend.download(uri, target_dir)

        # do nothing, let loader handle it (load dataset as hf://.../)
        return uri  

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload to HuggingFace, routing between file and dataset backends.

        Args:
            local_path: Path to local file or dataset directory
            uri: Target HuggingFace URI
        """
        if self._is_file_path(uri):
            return self.api_backend.upload(local_path, uri)
        
        else:
            raise NotImplementedError("Upload not supported for HuggingFace URIs")

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        return self.api_backend.ls(uri, exts, relative_unix, debug_print, **kwargs)