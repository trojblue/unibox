# s3_backend.py
import os
import warnings
from pathlib import Path
from typing import List, Optional

from unibox.utils.s3_client import S3Client

from .base_backend import BaseBackend


class S3Backend(BaseBackend):
    def __init__(self):
        self._client = S3Client()

    def _ensure_s3_uri(self, uri: str) -> str:
        uri = str(uri).strip()
        if not uri.startswith("s3://"):
            raise ValueError(f"Not an S3 URI: {uri}")
        return uri

    def download(self, uri: str, target_dir: str | None = None) -> Path:
        """Download the file from S3. If target_dir is given, place it there,
        else use your global or stable temp directory.
        """
        uri = self._ensure_s3_uri(uri)
        if not target_dir:
            from unibox.utils.globals import GLOBAL_TMP_DIR

            _target_dir = GLOBAL_TMP_DIR

        os.makedirs(_target_dir, exist_ok=True)
        local_path = self._client.download(uri, _target_dir)
        return Path(local_path)

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload the local file to S3."""
        uri = self._ensure_s3_uri(uri)
        self._client.upload(str(local_path), s3_uri=uri)

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """List files in the S3 "directory" with optional extension filtering.

        Args:
            uri (str): S3 directory URI to list.
            exts (Optional[List[str]]): List of file extensions to include. Defaults to None.
            relative_unix (bool): Whether to return relative Unix-style paths. Defaults to False.
            debug_print (bool): Whether to display a progress bar. Defaults to True.
            **kwargs: Additional arguments for backward compatibility.
                      Supports 'include_extensions' (deprecated) and 'exclude_extensions'.

        Returns:
            List[str]: List of file keys or full S3 URIs.
        """
        # Handle backward compatibility for include_extensions.
        include_extensions = kwargs.pop("include_extensions", None)
        if include_extensions is not None:
            warnings.warn(
                "`include_extensions` is deprecated; use `exts` instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            exts = include_extensions

        # Also allow passing 'exclude_extensions' if needed.
        exclude_extensions = kwargs.pop("exclude_extensions", None)

        uri = self._ensure_s3_uri(uri)
        return self._client.traverse(
            s3_uri=uri,
            include_extensions=exts,
            exclude_extensions=exclude_extensions,
            relative_unix=relative_unix,
            debug_print=debug_print,
        )
