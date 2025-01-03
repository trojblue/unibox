# base_loader.py
from pathlib import Path
from typing import Any

class BaseLoader:
    def load(self, local_path: Path) -> Any:
        raise NotImplementedError

    def save(self, local_path: Path, data: Any) -> None:
        raise NotImplementedError
