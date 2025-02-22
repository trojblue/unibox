# jsonl_loader.py
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import orjson

from .base_loader import BaseLoader


class JSONLLoader(BaseLoader):
    """Load and save JSONL files using orjson."""

    SUPPORTED_LOAD_CONFIG = {
        "encoding",  # str: File encoding for reading lines
        "skip_errors",  # bool: Whether to skip lines that can't be parsed
        "replace_nan",  # bool: Whether to replace NaN with null
        "default",  # Callable: Function to handle unknown types
    }

    SUPPORTED_SAVE_CONFIG = {
        "encoding",  # str: File encoding for writing lines
        "option",  # int: orjson option flags
        "default",  # Callable: Function to handle unknown types
    }

    def load(self, file_path: Path, loader_config: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Load a JSONL file with optional configuration.

        Args:
            file_path (Path): Path to the JSONL file
            loader_config (Optional[Dict]): Configuration options for JSONL loading

        Returns:
            List[Any]: List of parsed JSON objects
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Handle config options
        encoding = config.get("encoding", "utf-8")
        if "encoding" in config:
            used_keys.add("encoding")

        skip_errors = config.get("skip_errors", True)
        if "skip_errors" in config:
            used_keys.add("skip_errors")

        replace_nan = config.get("replace_nan", True)
        if "replace_nan" in config:
            used_keys.add("replace_nan")

        # Handle default function if specified
        kwargs = {}
        if "default" in config:
            kwargs["default"] = config["default"]
            used_keys.add("default")

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "JSONLLoader")

        data = []
        with open(file_path, "rb") as f:
            for line in f:
                line_str = line.decode(encoding, errors="replace")
                if replace_nan and "NaN" in line_str:
                    line_str = re.sub(r"\bNaN\b", "null", line_str)
                try:
                    data.append(orjson.loads(line_str, **kwargs))
                except orjson.JSONDecodeError:
                    if not skip_errors:
                        raise
        return data

    def save(self, file_path: Path, data: List[Any], loader_config: Optional[Dict[str, Any]] = None) -> None:
        """Save a list of objects to a JSONL file with optional configuration.

        Args:
            file_path (Path): Where to save the JSONL file
            data (List[Any]): Objects to save
            loader_config (Optional[Dict]): Configuration options for JSONL saving
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}
        for key in self.SUPPORTED_SAVE_CONFIG - {"encoding"}:
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Handle encoding
        encoding = config.get("encoding", "utf-8")
        if "encoding" in config:
            used_keys.add("encoding")

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "JSONLLoader")

        with open(file_path, "wb") as f:
            for item in data:
                line = orjson.dumps(item, **kwargs)
                if encoding != "utf-8":
                    line = line.decode("utf-8").encode(encoding)
                f.write(line + b"\n")
