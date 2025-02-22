# csv_loader.py
from pathlib import Path
from typing import Any, Dict, Optional, Set

import pandas as pd

from .base_loader import BaseLoader


class CSVLoader(BaseLoader):
    """Load and save CSV files using pandas."""

    SUPPORTED_LOAD_CONFIG = {
        "sep",  # str: Delimiter to use
        "header",  # int, list[int]: Row number(s) to use as column names
        "encoding",  # str: File encoding
        "usecols",  # list[str]: List of columns to use
        "dtype",  # dict: Column dtypes
        "na_values",  # scalar, list, dict: Additional NA/NaN strings
        "nrows",  # int: Number of rows to read
    }

    SUPPORTED_SAVE_CONFIG = {
        "sep",  # str: Delimiter to use
        "encoding",  # str: File encoding
        "index",  # bool: Whether to write row names
        "header",  # bool: Whether to write column names
        "na_rep",  # str: Missing data representation
        "float_format",  # str: Format string for float values
    }

    def load(self, file_path: Path, loader_config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Load a CSV file with optional configuration.

        Args:
            file_path (Path): Path to the CSV file
            loader_config (Optional[Dict]): Configuration options for pd.read_csv

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
        self._warn_unused_config(config, used_keys, "CSVLoader")

        return pd.read_csv(file_path, **kwargs)

    def save(self, file_path: Path, data: pd.DataFrame, loader_config: Optional[Dict[str, Any]] = None) -> None:
        """Save a dataframe to CSV with optional configuration.

        Args:
            file_path (Path): Where to save the CSV file
            data (pd.DataFrame): DataFrame to save
            loader_config (Optional[Dict]): Configuration options for to_csv
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Start with default kwargs
        kwargs: Dict[str, Any] = {"index": False}

        # Extract supported arguments from config
        for key in self.SUPPORTED_SAVE_CONFIG:
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "CSVLoader")

        data.to_csv(file_path, **kwargs)
