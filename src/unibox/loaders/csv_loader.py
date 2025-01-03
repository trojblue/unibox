# csv_loader.py
import pandas as pd
from pathlib import Path
from typing import Any
from .base_loader import BaseLoader

class CSVLoader(BaseLoader):
    def load(self, local_path: Path) -> pd.DataFrame:
        return pd.read_csv(local_path)

    def save(self, local_path: Path, data: pd.DataFrame) -> None:
        data.to_csv(local_path, index=False)
