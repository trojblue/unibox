# json_loader.py
from pathlib import Path
from typing import Any, Dict, Optional, Set

import orjson

from .base_loader import BaseLoader


class JSONLoader(BaseLoader):
    """Load and save JSON files using orjson."""

    SUPPORTED_LOAD_CONFIG = {
        "encoding",  # str: File encoding (if not binary)
        "default",  # Callable: Function to handle unknown types
    }

    SUPPORTED_SAVE_CONFIG = {
        "option",  # int: orjson option flags (e.g., orjson.OPT_INDENT_2)
        "default",  # Callable: Function to handle unknown types
    }

    def load(self, file_path: Path, loader_config: Optional[Dict[str, Any]] = None) -> Any:
        """Load a JSON file with optional configuration.

        Args:
            file_path (Path): Path to the JSON file
            loader_config (Optional[Dict]): Configuration options for JSON loading

        Returns:
            Any: The loaded JSON data
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Handle encoding if specified
        if "encoding" in config:
            used_keys.add("encoding")
            with open(file_path, encoding=config["encoding"]) as f:
                file_content = f.read().encode()
        else:
            with open(file_path, "rb") as f:
                file_content = f.read()

        if not file_content:
            return None

        # Handle default function if specified
        kwargs = {}
        if "default" in config:
            kwargs["default"] = config["default"]
            used_keys.add("default")

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "JSONLoader")

        return orjson.loads(file_content, **kwargs)

    def save(self, file_path: Path, data: Any, loader_config: Optional[Dict[str, Any]] = None) -> None:
        """Save data to a JSON file with optional configuration.

        Args:
            file_path (Path): Where to save the JSON file
            data (Any): Data to save
            loader_config (Optional[Dict]): Configuration options for JSON saving
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}
        for key in self.SUPPORTED_SAVE_CONFIG:
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "JSONLoader")

        with open(file_path, "wb") as f:
            f.write(orjson.dumps(data, **kwargs))
