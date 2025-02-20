from pathlib import Path
from typing import Any

import yaml

from .base_loader import BaseLoader


class YAMLLoader(BaseLoader):
    """Load and save YAML files."""

    def load(self, file_path: Path) -> Any:
        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save(self, file_path: Path, data: Any) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False)
