# base_backend.py
from pathlib import Path
from typing import List


class BaseBackend:
    """Interface for storage backends (local, S3, etc.)."""

    def download(self, uri: str, target_dir: str = None) -> Path:
        """Download the resource identified by `uri` to a local temp path. Return local Path."""
        raise NotImplementedError

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload local_path to the specified `uri`."""
        raise NotImplementedError

    def ls(self, uri: str) -> List[str]:
        """List files/folders at `uri`."""
        raise NotImplementedError
