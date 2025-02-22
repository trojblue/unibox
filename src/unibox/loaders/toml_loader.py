from pathlib import Path
from typing import Any, Dict, Optional, Set

import tomli
import tomli_w

from .base_loader import BaseLoader


class TOMLLoader(BaseLoader):
    """Load and save TOML files using tomli/tomli_w."""

    SUPPORTED_LOAD_CONFIG = {
        "multiline_strings",  # bool: Parse multiline strings
    }

    SUPPORTED_SAVE_CONFIG = {
        "indentation",  # str: Indentation string
        "multiline_strings",  # bool: Use multiline strings
    }

    def load(self, file_path: Path, loader_config: Optional[Dict[str, Any]] = None) -> Any:
        """Load a TOML file with optional configuration.

        Args:
            file_path (Path): Path to the TOML file
            loader_config (Optional[Dict]): Configuration options for TOML loading

        Returns:
            Any: The loaded TOML data
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Extract supported arguments from config
        kwargs = {}
        for key in self.SUPPORTED_LOAD_CONFIG:
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "TOMLLoader")

        with open(file_path, "rb") as f:
            return tomli.load(f, **kwargs)

    def save(self, file_path: Path, data: Any, loader_config: Optional[Dict[str, Any]] = None) -> None:
        """Save data to a TOML file with optional configuration.

        Args:
            file_path (Path): Where to save the TOML file
            data (Any): Data to save
            loader_config (Optional[Dict]): Configuration options for TOML saving
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
        self._warn_unused_config(config, used_keys, "TOMLLoader")

        with open(file_path, "wb") as f:
            tomli_w.dump(data, f, **kwargs)
