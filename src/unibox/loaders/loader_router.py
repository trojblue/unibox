# loader_router.py
# ... etc
from ..utils.constants import IMG_FILES
from .csv_loader import CSVLoader
from .image_loder import ImageLoader
from .json_loader import JSONLoader
from .jsonl_loader import JSONLLoader
from .parquet_loader import ParquetLoader


def get_loader_for_suffix(suffix: str):
    suffix = suffix.lower()
    if suffix == ".csv":
        return CSVLoader()
    if suffix in IMG_FILES:
        return ImageLoader()
    if suffix == ".json":
        return JSONLoader()
    if suffix == ".jsonl":
        return JSONLLoader()
    if suffix == ".parquet":
        return ParquetLoader()
    # ...
    return None
