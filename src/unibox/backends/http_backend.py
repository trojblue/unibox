import hashlib
import os
import shutil
import threading
import time
import uuid
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from tqdm.auto import tqdm

from ..utils.constants import BLACKLISTED_PATHS
from ..utils.logger import UniLogger
from .base_backend import BaseBackend


class HTTPBackend(BaseBackend):
    """Backend for downloading files from HTTP/HTTPS URLs."""

    BLACKLISTED_PATHS = BLACKLISTED_PATHS
    _LOCKS: dict[str, threading.Lock] = {}
    _LOCKS_GUARD = threading.Lock()

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
        url_hash = hashlib.md5(uri.encode()).hexdigest()[:8]

        # Get filename from path
        filename = Path(path).name

        # If no filename or extension, generate one based on URL hash
        if not filename or "." not in filename:
            extension = self._guess_extension_from_uri(uri)
            filename = f"http_download_{url_hash}{extension}"
        else:
            suffix = "".join(Path(filename).suffixes)
            stem = filename[: -len(suffix)] if suffix else filename
            filename = f"{stem}_{url_hash}{suffix}"

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

    @classmethod
    def _get_lock(cls, local_path: Path) -> threading.Lock:
        key = str(local_path.resolve(strict=False))
        with cls._LOCKS_GUARD:
            lock = cls._LOCKS.get(key)
            if lock is None:
                lock = threading.Lock()
                cls._LOCKS[key] = lock
            return lock

    def _resolve_target_dir(self, target_dir: Optional[str]) -> Path:
        from unibox.utils.globals import GLOBAL_TMP_DIR

        _target_dir = target_dir or GLOBAL_TMP_DIR
        abs_target_dir = Path(_target_dir).resolve()

        for blocked in self.BLACKLISTED_PATHS:
            blocked_path = Path(blocked).resolve()
            if abs_target_dir == blocked_path or str(abs_target_dir).startswith(str(blocked_path) + os.sep):
                raise PermissionError(f"Download blocked: {abs_target_dir} is a restricted path.")

        abs_target_dir.mkdir(parents=True, exist_ok=True)
        return abs_target_dir

    def _download_once(
        self,
        uri: str,
        local_path: Path,
        timeout: float,
        chunk_size: int,
        headers: Optional[Dict[str, str]],
    ) -> None:
        request = Request(uri, headers=headers or {})
        temp_path = local_path.with_name(f".{local_path.name}.{uuid.uuid4().hex}.part")
        try:
            with urlopen(request, timeout=timeout) as response, temp_path.open("wb") as output_file:
                shutil.copyfileobj(response, output_file, length=chunk_size)
            temp_path.replace(local_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def download(
        self,
        uri: str,
        target_dir: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 2,
        retry_backoff: float = 0.5,
        chunk_size: int = 1024 * 1024,
        headers: Optional[Dict[str, str]] = None,
    ) -> Path:
        """Download a file from HTTP/HTTPS URL to local storage.

        Args:
            uri: HTTP/HTTPS URL of the file to download
            target_dir: Optional directory to download to. If None, uses global temp directory.

        Returns:
            Path: Local path to the downloaded file
        """
        uri = self._validate_http_uri(uri)
        abs_target_dir = self._resolve_target_dir(target_dir)

        # Generate local filename
        filename = self._get_filename_from_uri(uri)
        local_path = abs_target_dir / filename

        # Check if file already exists (simple caching)
        if local_path.exists():
            self.logger.debug(f"File already exists locally: {local_path}")
            return local_path

        lock = self._get_lock(local_path)
        with lock:
            if local_path.exists():
                self.logger.debug(f"File already exists locally: {local_path}")
                return local_path

            self.logger.debug(f"Downloading {uri} to {local_path}")
            last_error: Optional[Exception] = None
            for attempt in range(retries + 1):
                try:
                    self._download_once(
                        uri=uri,
                        local_path=local_path,
                        timeout=timeout,
                        chunk_size=chunk_size,
                        headers=headers,
                    )
                    if not local_path.exists():
                        raise FileNotFoundError(f"Download failed: {local_path} was not created")

                    self.logger.info(f"Successfully downloaded {uri}")
                    return local_path
                except Exception as e:
                    last_error = e
                    if local_path.exists():
                        local_path.unlink()
                    if attempt == retries:
                        break
                    time.sleep(retry_backoff * (2**attempt))

            raise RuntimeError(f"Failed to download {uri}: {last_error}")

    def download_many(
        self,
        uris: List[str],
        num_workers: int = 8,
        debug_print: bool = True,
        **kwargs: Any,
    ) -> List[Optional[Path]]:
        """Download multiple HTTP/HTTPS URLs concurrently."""
        results: List[Optional[Path]] = [None] * len(uris)
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_idx = {executor.submit(self.download, uri, **kwargs): idx for idx, uri in enumerate(uris)}
            futures_iter = as_completed(future_to_idx)
            if debug_print:
                futures_iter = tqdm(futures_iter, total=len(uris), desc="Downloading HTTP")

            for future in futures_iter:
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    self.logger.error(f"Exception downloading {uris[idx]}: {e}")

        return results

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

        raise NotImplementedError(
            "HTTP backend does not support directory listing. HTTP URLs point to individual files, not directories.",
        )
