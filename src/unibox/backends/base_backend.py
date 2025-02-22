# base_backend.py
import warnings
from pathlib import Path
from typing import List, Optional


class BaseBackend:
    """Interface for storage backends (local, S3, etc.)."""

    def download(self, uri: str, target_dir: Optional[str] = None) -> Path:
        """Download the resource identified by `uri` to a local temp path.

        Args:
            uri: URI of the resource to download
            target_dir: Optional directory to download to. If None, uses a temp directory.

        Returns:
            Path: Local path to the downloaded resource
        """
        raise NotImplementedError

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload local_path to the specified `uri`."""
        raise NotImplementedError

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """List files under `uri` with optional extension filtering.

        Args:
            uri: A string representing a directory path or location.
            exts: A list of file extensions to include (['.txt', '.csv']).
            relative_unix: Return relative paths with forward slashes if True.
            debug_print: Show progress bar.
            **kwargs: Additional arguments for compatibility (ignored by default).

        Returns:
            List[str]: A list of file paths.
        """
        include_extensions = kwargs.pop("include_extensions", None)
        if include_extensions is not None:
            warnings.warn(
                "`include_extensions` is deprecated; use `exts` instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            exts = include_extensions

        # By default, raise NotImplementedError.
        # LocalBackend or other backends can override with real logic.
        raise NotImplementedError("ls() is not implemented in BaseBackend.")
