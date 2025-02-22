from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .base_loader import BaseLoader


class TxtLoader(BaseLoader):
    """Load and save text files."""

    SUPPORTED_LOAD_CONFIG = {
        "encoding",  # str: File encoding
        "strip",  # bool: Whether to strip whitespace from lines
        "skip_empty",  # bool: Whether to skip empty lines
    }

    SUPPORTED_SAVE_CONFIG = {
        "encoding",  # str: File encoding
        "newline",  # str: Line ending to use
        "append",  # bool: Whether to append to file
    }

    def load(self, file_path: Path, loader_config: Optional[Dict[str, Any]] = None) -> List[str]:
        """Load a text file and return a list of lines.

        Args:
            file_path (Path): Path to the text file
            loader_config (Optional[Dict]): Configuration options for text loading

        Returns:
            List[str]: A list of lines from the file
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Handle encoding
        encoding = config.get("encoding", "utf-8")
        if "encoding" in config:
            used_keys.add("encoding")

        # Handle line processing options
        strip = config.get("strip", True)
        if "strip" in config:
            used_keys.add("strip")

        skip_empty = config.get("skip_empty", False)
        if "skip_empty" in config:
            used_keys.add("skip_empty")

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "TxtLoader")

        with open(file_path, encoding=encoding) as f:
            lines = [line.strip() if strip else line.rstrip("\n") for line in f]
            if skip_empty:
                lines = [line for line in lines if line]
            return lines

    def save(self, file_path: Path, data: List[str], loader_config: Optional[Dict[str, Any]] = None) -> None:
        """Save a list of strings to a text file.

        Args:
            file_path (Path): Where to save the text file
            data (List[str]): Lines to write to the file
            loader_config (Optional[Dict]): Configuration options for text saving
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Handle encoding
        encoding = config.get("encoding", "utf-8")
        if "encoding" in config:
            used_keys.add("encoding")

        # Handle write mode
        mode = "a" if config.get("append", False) else "w"
        if "append" in config:
            used_keys.add("append")

        # Handle line ending
        newline = config.get("newline", "\n")
        if "newline" in config:
            used_keys.add("newline")

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "TxtLoader")

        with open(file_path, mode, encoding=encoding, newline=newline) as f:
            f.writelines(f"{line}{newline}" for line in data)
