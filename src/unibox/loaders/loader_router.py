# loader_router.py
# ... etc
from ..utils.constants import IMG_FILES
from .csv_loader import CSVLoader
from .image_loder import ImageLoader
from .json_loader import JSONLoader
from .jsonl_loader import JSONLLoader
from .parquet_loader import ParquetLoader
from .txt_loader import TxtLoader
from .toml_loader import TOMLLoader
from .yaml_loader import YAMLLoader


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
    if suffix == ".txt":
        return TxtLoader()
    if suffix == ".toml":
        return TOMLLoader()
    if suffix == ".yaml" or suffix == ".yml":
        return YAMLLoader()        
    return None
