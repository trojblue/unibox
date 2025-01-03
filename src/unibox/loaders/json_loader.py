# json_loader.py
from pathlib import Path
from typing import Any, List, Dict
import orjson

from .base_loader import BaseLoader

class JSONLoader(BaseLoader):
    """Load and save JSON files."""

    def load(self, file_path: Path) -> Any:
        with open(file_path, "rb") as f:
            file_content = f.read()
            if not file_content:
                return None
            return orjson.loads(file_content)

    def save(self, file_path: Path, data: Any) -> None:
        # Decide how you want to handle e.g. dict vs list
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(data))
