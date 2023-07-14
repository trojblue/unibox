from __future__ import annotations

from pathlib import Path

from .utils.uni_loader import UniLoader
from .utils.uni_logger import UniLogger

def loads(file_path: Path | str):
    Loader = UniLoader()
    return Loader.loads(file_path)