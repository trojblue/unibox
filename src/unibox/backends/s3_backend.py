# s3_backend.py
import tempfile
from pathlib import Path
from typing import List
import os

from unibox.utils.s3_client import S3Client
from unibox.utils.globals import GLOBAL_TMP_DIR

from .base_backend import BaseBackend


class S3Backend(BaseBackend):
    def __init__(self):
        self._client = S3Client()

    def download(self, uri: str, target_dir: str = None) -> Path:
        """
        Download the file from S3. If target_dir is given, place it there,
        else use your global or stable temp directory.
        """
        if not target_dir:
            from unibox.utils.globals import GLOBAL_TMP_DIR
            target_dir = GLOBAL_TMP_DIR
        
        os.makedirs(target_dir, exist_ok=True)

        local_path = self._client.download(uri, target_dir)
        return Path(local_path)

    def upload(self, local_path: Path, uri: str) -> None:
        self._client.upload(str(local_path), uri)

    def ls(self, uri: str) -> List[str]:
        # Implementation that calls s3_client walk or traverse
        return list(self._client.traverse(uri, debug_print=False))
