from pathlib import Path
from typing import Any, Dict, Optional, Set

import yaml

from .base_loader import BaseLoader


class YAMLLoader(BaseLoader):
    """Load and save YAML files."""

    SUPPORTED_LOAD_CONFIG = {
        "encoding",  # str: File encoding
        "Loader",  # yaml.Loader: Custom YAML loader class
    }

    SUPPORTED_SAVE_CONFIG = {
        "encoding",  # str: File encoding
        "allow_unicode",  # bool: Allow unicode in output
        "indent",  # int: Number of spaces for indentation
        "width",  # int: Max line width
        "sort_keys",  # bool: Sort dictionary keys
    }

    def load(self, file_path: Path, loader_config: Optional[Dict[str, Any]] = None) -> Any:
        """Load a YAML file with optional configuration.

        Args:
            file_path (Path): Path to the YAML file
            loader_config (Optional[Dict]): Configuration options for YAML loading

        Returns:
            Any: The loaded YAML data
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}

        # Handle encoding
        encoding = config.get("encoding", "utf-8")
        if "encoding" in config:
            used_keys.add("encoding")

        # Handle other load options
        for key in self.SUPPORTED_LOAD_CONFIG - {"encoding"}:
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "YAMLLoader")

        with open(file_path, encoding=encoding) as f:
            return yaml.safe_load(f, **kwargs)

    def save(self, file_path: Path, data: Any, loader_config: Optional[Dict[str, Any]] = None) -> None:
        """Save data to a YAML file with optional configuration.

        Args:
            file_path (Path): Where to save the YAML file
            data (Any): Data to save
            loader_config (Optional[Dict]): Configuration options for YAML saving
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}

        # Handle encoding
        encoding = config.get("encoding", "utf-8")
        if "encoding" in config:
            used_keys.add("encoding")

        # Handle other save options
        for key in self.SUPPORTED_SAVE_CONFIG - {"encoding"}:
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "YAMLLoader")

        with open(file_path, "w", encoding=encoding) as f:
            yaml.safe_dump(data, f, **kwargs)
