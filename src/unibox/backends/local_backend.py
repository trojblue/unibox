# local_backend.py
from pathlib import Path
from typing import List

from .base_backend import BaseBackend


class LocalBackend(BaseBackend):
    def download(self, uri: str, target_dir: str = None) -> Path:
        # local path is the URI itself, so just return Path(uri)
        return Path(uri)

    def upload(self, local_path: Path, uri: str) -> None:
        # If you want to handle "move/overwrite" logic, do it here
        # Otherwise do nothing if local_path == uri
        if Path(uri) != local_path:
            # copy or rename
            pass

    def ls(self, uri: str) -> List[str]:
        p = Path(uri)
        if not p.exists():
            return []
        return [str(x) for x in p.iterdir()]
