from pathlib import Path
from typing import Any
import tomli
import tomli_w

from .base_loader import BaseLoader


class TOMLLoader(BaseLoader):
    """Load and save TOML files."""

    def load(self, file_path: Path) -> Any:
        with open(file_path, "rb") as f:
            return tomli.load(f)

    def save(self, file_path: Path, data: Any) -> None:
        with open(file_path, "wb") as f:
            tomli_w.dump(data, f)
