# s3_backend.py
import os
import re
import warnings
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from unibox.utils.s3_client import S3Client

from ..utils.constants import BLACKLISTED_PATHS
from .base_backend import BaseBackend


class S3Backend(BaseBackend):
    # Blacklisted directories and files
    BLACKLISTED_PATHS = BLACKLISTED_PATHS

    def __init__(self):
        self._client = S3Client()

    def _validate_s3_uri(self, uri: str) -> str:
        """Strictly validate S3 URIs to prevent path traversal and injection attacks."""
        uri = uri.strip()

        if not uri.startswith("s3://"):
            raise ValueError(f"Not a valid S3 URI: {uri}")

        parsed = urlparse(uri)
        bucket = parsed.netloc
        path = parsed.path.lstrip("/")  # Normalize path by removing leading slashes

        # Ensure bucket name follows AWS naming rules
        if not re.match(r"^[a-zA-Z0-9.\-_]{3,63}$", bucket):
            raise ValueError(f"Invalid S3 bucket name: {bucket}")

        # Prevent directory traversal (e.g., "s3://my-bucket/../../etc/passwd")
        if ".." in path or path.startswith("/"):
            raise ValueError(f"Suspicious S3 path detected: {path}")

        return uri

    def download(self, uri: str, target_dir: str | None = None) -> Path:
        """Download the file from S3. If target_dir is given, place it there,
        else use your global or stable temp directory.
        """
        uri = self._validate_s3_uri(uri)
        from unibox.utils.globals import GLOBAL_TMP_DIR

        _target_dir = target_dir or GLOBAL_TMP_DIR

        abs_target_dir = Path(_target_dir).resolve()

        # Fix: Ensure blacklisted directories and their subdirectories are blocked
        for blocked in BLACKLISTED_PATHS:
            blocked_path = Path(blocked).resolve()
            if abs_target_dir == blocked_path or str(abs_target_dir).startswith(str(blocked_path) + os.sep):
                raise PermissionError(f"Download blocked: {abs_target_dir} is a restricted path.")

        os.makedirs(_target_dir, exist_ok=True)
        local_path = self._client.download(uri, _target_dir)

        return Path(local_path)

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload the local file to S3."""
        uri = self._validate_s3_uri(uri)
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

        uri = self._validate_s3_uri(uri)
        return self._client.traverse(
            s3_uri=uri,
            include_extensions=exts,
            exclude_extensions=exclude_extensions,
            relative_unix=relative_unix,
            debug_print=debug_print,
        )
