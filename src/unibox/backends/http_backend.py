# http_backend.py
import hashlib
import os
import warnings
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
from urllib.request import urlretrieve

from ..utils.constants import BLACKLISTED_PATHS
from ..utils.logger import UniLogger
from .base_backend import BaseBackend


class HTTPBackend(BaseBackend):
    """Backend for downloading files from HTTP/HTTPS URLs."""

    BLACKLISTED_PATHS = BLACKLISTED_PATHS

    def __init__(self):
        self.logger = UniLogger()

    def _validate_http_uri(self, uri: str) -> str:
        """Validate HTTP/HTTPS URIs to prevent potential security issues."""
        uri = uri.strip()

        if not (uri.startswith("http://") or uri.startswith("https://")):
            raise ValueError(f"Not a valid HTTP/HTTPS URI: {uri}")

        try:
            parsed = urlparse(uri)
            if not parsed.netloc:
                raise ValueError(f"Invalid URL - missing hostname: {uri}")
            if parsed.scheme not in ["http", "https"]:
                raise ValueError(f"Unsupported scheme: {parsed.scheme}")
        except Exception as e:
            raise ValueError(f"Invalid HTTP URI: {uri}. Error: {e}")

        return uri

    def _get_filename_from_uri(self, uri: str) -> str:
        """Extract filename from URI, or generate one if not available."""
        parsed = urlparse(uri)
        path = parsed.path

        # Get filename from path
        filename = Path(path).name

        # If no filename or extension, generate one based on URL hash
        if not filename or "." not in filename:
            # Create a hash of the URL for a unique filename
            url_hash = hashlib.md5(uri.encode()).hexdigest()[:8]
            extension = self._guess_extension_from_uri(uri)
            filename = f"http_download_{url_hash}{extension}"

        return filename

    def _guess_extension_from_uri(self, uri: str) -> str:
        """Guess file extension from common URL patterns."""
        uri_lower = uri.lower()

        # Common image formats
        if any(ext in uri_lower for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg"]):
            for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg"]:
                if ext in uri_lower:
                    return ext

        # Common document formats
        if any(ext in uri_lower for ext in [".pdf", ".doc", ".docx", ".txt", ".csv", ".json", ".xml"]):
            for ext in [".pdf", ".doc", ".docx", ".txt", ".csv", ".json", ".xml"]:
                if ext in uri_lower:
                    return ext

        # Common video formats
        if any(ext in uri_lower for ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]):
            for ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
                if ext in uri_lower:
                    return ext

        # Default to no extension
        return ""

    def download(self, uri: str, target_dir: Optional[str] = None) -> Path:
        """Download a file from HTTP/HTTPS URL to local storage.

        Args:
            uri: HTTP/HTTPS URL of the file to download
            target_dir: Optional directory to download to. If None, uses global temp directory.

        Returns:
            Path: Local path to the downloaded file
        """
        uri = self._validate_http_uri(uri)

        from unibox.utils.globals import GLOBAL_TMP_DIR

        _target_dir = target_dir or GLOBAL_TMP_DIR
        abs_target_dir = Path(_target_dir).resolve()

        # Security check: ensure target directory is not blacklisted
        for blocked in self.BLACKLISTED_PATHS:
            blocked_path = Path(blocked).resolve()
            if abs_target_dir == blocked_path or str(abs_target_dir).startswith(str(blocked_path) + os.sep):
                raise PermissionError(f"Download blocked: {abs_target_dir} is a restricted path.")

        # Create target directory if it doesn't exist
        os.makedirs(_target_dir, exist_ok=True)

        # Generate local filename
        filename = self._get_filename_from_uri(uri)
        local_path = Path(_target_dir) / filename

        # Check if file already exists (simple caching)
        if local_path.exists():
            self.logger.debug(f"File already exists locally: {local_path}")
            return local_path

        try:
            self.logger.debug(f"Downloading {uri} to {local_path}")

            # Download the file
            urlretrieve(uri, str(local_path))

            if not local_path.exists():
                raise FileNotFoundError(f"Download failed: {local_path} was not created")

            self.logger.info(f"Successfully downloaded {uri}")
            return local_path

        except Exception as e:
            # Clean up partial download if it exists
            if local_path.exists():
                local_path.unlink()
            raise RuntimeError(f"Failed to download {uri}: {e}")

    def upload(self, local_path: Path, uri: str) -> None:
        """HTTP backend does not support upload operations."""
        raise NotImplementedError("HTTP backend does not support upload operations. HTTP URLs are read-only.")

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """HTTP backend does not support directory listing.

        HTTP URLs point to individual files, not directories that can be listed.
        """
        # Handle backward compatibility for include_extensions
        include_extensions = kwargs.pop("include_extensions", None)
        if include_extensions is not None:
            warnings.warn(
                "`include_extensions` is deprecated; use `exts` instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            exts = include_extensions

        raise NotImplementedError(
            "HTTP backend does not support directory listing. HTTP URLs point to individual files, not directories.",
        )
