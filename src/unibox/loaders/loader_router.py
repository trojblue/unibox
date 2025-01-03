# loader_router.py
from pathlib import Path
from typing import Optional
from .csv_loader import CSVLoader
from .image_loder import ImageLoader
from .json_loader import JSONLoader
from .jsonl_loader import JSONLLoader
from .parquet_loader import ParquetLoader
# ... etc

from ..utils.constants import IMG_FILES

def get_loader_for_suffix(suffix: str):
    suffix = suffix.lower()
    if suffix == ".csv":
        return CSVLoader()
    elif suffix in IMG_FILES:
        return ImageLoader()
    elif suffix == ".json":
        return JSONLoader()
    elif suffix == ".jsonl":
        return JSONLLoader()
    elif suffix == ".parquet":
        return ParquetLoader()
    # ...
    return None
