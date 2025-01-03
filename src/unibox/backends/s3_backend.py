# s3_backend.py
from pathlib import Path
import tempfile
from typing import List
from .base_backend import BaseBackend
from unibox.utils.s3_client import S3Client, parse_s3_url

class S3Backend(BaseBackend):
    def __init__(self):
        self._client = S3Client()

    def download(self, uri: str) -> Path:
        # Create temp dir, download from S3
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = self._client.download(uri, tmp_dir)
            # We can't return a path that vanishes after we leave this scope
            # so we might store it in a stable location or keep a reference
            # For simplicity:
            final_path = Path(tmp_dir) / Path(local_path).name
            return final_path

    def upload(self, local_path: Path, uri: str) -> None:
        self._client.upload(str(local_path), uri)

    def ls(self, uri: str) -> List[str]:
        # Implementation that calls s3_client walk or traverse
        return list(self._client.traverse(uri, debug_print=False))
