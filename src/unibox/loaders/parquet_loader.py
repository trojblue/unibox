# parquet_loader.py
from pathlib import Path

import pandas as pd

from .base_loader import BaseLoader


class ParquetLoader(BaseLoader):
    """Load and save Parquet files using pandas."""

    def load(self, file_path: Path) -> pd.DataFrame:
        return pd.read_parquet(file_path)

    def save(self, file_path: Path, data: pd.DataFrame) -> None:
        data.to_parquet(file_path)
