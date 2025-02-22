"""basic loader class"""

# base_loader.py
from pathlib import Path
from typing import Any, Dict, Optional, Union


class BaseLoader:
    def load(self, local_path: Union[str, Path], loader_config: Optional[Dict] = None) -> Any:
        """Load data from the given path with optional loader-specific configuration.

        Args:
            local_path (Union[str, Path]): Path or URI to load from
            loader_config (Optional[Dict]): Loader-specific configuration options

        Returns:
            Any: The loaded data
        """
        raise NotImplementedError

    def save(self, local_path: Union[str, Path], data: Any, loader_config: Optional[Dict] = None) -> None:
        """Save data to the given path with optional loader-specific configuration.

        Args:
            local_path (Union[str, Path]): Path or URI where to save the data
            data (Any): Data to save
            loader_config (Optional[Dict]): Loader-specific configuration options
        """
        raise NotImplementedError

    def _warn_unused_config(self, config: Dict, used_keys: set, loader_name: str) -> None:
        """Warn about unused configuration keys.

        Args:
            config (Dict): The provided configuration dictionary
            used_keys (set): Set of keys that were actually used
            loader_name (str): Name of the loader for the warning message
        """
        unused_keys = set(config.keys()) - used_keys
        if unused_keys:
            import warnings

            warnings.warn(f"{loader_name}: Ignoring unknown arguments: {', '.join(unused_keys)}")
