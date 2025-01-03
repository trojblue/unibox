# csv_loader.py
from pathlib import Path

import pandas as pd

from .base_loader import BaseLoader


class CSVLoader(BaseLoader):
    def load(self, local_path: Path) -> pd.DataFrame:
        return pd.read_csv(local_path)

    def save(self, local_path: Path, data: pd.DataFrame) -> None:
        data.to_csv(local_path, index=False)
