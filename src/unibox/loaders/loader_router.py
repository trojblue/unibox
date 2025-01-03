# loader_router.py
from pathlib import Path
from typing import Optional
from .csv_loader import CSVLoader
from .jsonl_loader import JSONLoader
from .parquet_loader import ParquetLoader
# ... etc

def get_loader_for_suffix(suffix: str):
    suffix = suffix.lower()
    if suffix == ".csv":
        return CSVLoader()
    elif suffix == ".json":
        return JSONLoader()
    elif suffix == ".parquet":
        return ParquetLoader()
    # ...
    return None
