# jsonl_loader.py
import re
import orjson
from pathlib import Path
from typing import Any, List

from .base_loader import BaseLoader

class JSONLLoader(BaseLoader):
    """Load and save JSONL files."""

    def load(self, file_path: Path) -> List[Any]:
        data = []
        with open(file_path, "rb") as f:
            for line in f:
                line_str = line.decode("utf-8", errors="replace")
                if "NaN" in line_str:
                    line_str = re.sub(r'\bNaN\b', 'null', line_str)
                try:
                    data.append(orjson.loads(line_str))
                except orjson.JSONDecodeError:
                    # handle errors if you want
                    pass
        return data

    def save(self, file_path: Path, data: List[Any]) -> None:
        with open(file_path, "wb") as f:
            for item in data:
                f.write(orjson.dumps(item) + b"\n")
