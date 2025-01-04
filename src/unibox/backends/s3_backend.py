# s3_backend.py
import os
from pathlib import Path
from typing import List

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

    def download(self, uri: str, target_dir: str = None) -> Path:
        """Download the file from S3. If target_dir is given, place it there,
        else use your global or stable temp directory.
        """
        uri = self._ensure_s3_uri(uri)
        if not target_dir:
            from unibox.utils.globals import GLOBAL_TMP_DIR

            target_dir = GLOBAL_TMP_DIR

        os.makedirs(target_dir, exist_ok=True)

        local_path = self._client.download(uri, target_dir)
        return Path(local_path)

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload the local file to S3."""
        uri = self._ensure_s3_uri(uri)
        self._client.upload(str(local_path), s3_uri=uri)

    def ls(self, uri: str) -> List[str]:
        """Implementation that calls s3_client walk or traverse"""
        uri = self._ensure_s3_uri(uri)
        return list(self._client.traverse(uri, debug_print=False))
