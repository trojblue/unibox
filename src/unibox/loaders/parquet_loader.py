# parquet_loader.py
from pathlib import Path
from typing import Dict, Optional, Set

import pandas as pd

from .base_loader import BaseLoader


class ParquetLoader(BaseLoader):
    """Load and save Parquet files using pandas."""

    SUPPORTED_LOAD_CONFIG = {
        "columns",  # List[str]: Columns to load
        "engine",  # str: 'pyarrow' or 'fastparquet'
        "filters",  # List: Rows filter pushdown
        "use_nullable_dtypes",  # bool: Use nullable dtypes
    }

    SUPPORTED_SAVE_CONFIG = {
        "engine",  # str: 'pyarrow' or 'fastparquet'
        "compression",  # str or None: Compression method
        "index",  # bool: Whether to save index
    }

    def load(self, file_path: Path, loader_config: Optional[Dict] = None) -> pd.DataFrame:
        """Load a parquet file with optional configuration.

        Args:
            file_path (Path): Path to the parquet file
            loader_config (Optional[Dict]): Configuration options for pd.read_parquet

        Returns:
            pd.DataFrame: The loaded dataframe
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
        self._warn_unused_config(config, used_keys, "ParquetLoader")

        return pd.read_parquet(file_path, **kwargs)

    def save(self, file_path: Path, data: pd.DataFrame, loader_config: Optional[Dict] = None) -> None:
        """Save a dataframe to parquet with optional configuration.

        Args:
            file_path (Path): Where to save the parquet file
            data (pd.DataFrame): DataFrame to save
            loader_config (Optional[Dict]): Configuration options for to_parquet
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
        self._warn_unused_config(config, used_keys, "ParquetLoader")

        data.to_parquet(file_path, **kwargs)
