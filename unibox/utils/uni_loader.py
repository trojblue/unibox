# Adding the _load_csv and _load_parquet methods to the UniLoader class

from __future__ import annotations

import json
import timeit

import tomli
import pandas as pd
from PIL import Image
from pathlib import Path
from omegaconf import OmegaConf

from .uni_logger import UniLogger


class UniLoader:
    """A simple utility class for loading various file types.
    Data cleaning should be done in the class that uses this loader.
    """

    def __init__(self, logger=None, debug_print=True):
        if not logger:
            self.logger = UniLogger(file_suffix="UniLoader")
        else:
            self.logger = logger

        self.debug_print = debug_print

        # Mapping of file extensions to loader functions
        self.loaders = {
            '.json': self._load_json,
            '.jsonl': self._load_jsonl,  # Added '.jsonl' to the loaders dictionary
            '.txt': self._load_txt,
            '.html': self._load_txt,
            '.csv': self._load_csv,
            '.png': self._load_image,
            '.jpg': self._load_image,
            '.webp': self._load_image,
            '.jpeg': self._load_image,
            '.toml': self._load_toml,
            '.yaml': self._load_yaml,
            '.parquet': self._load_parquet,
        }

    def loads(self, file_path: Path | str, encoding="utf-8"):
        """Load data from the given file path.

        The type of data returned depends on the file extension.
        """
        start_time = timeit.default_timer()
        if isinstance(file_path, str):
            file_path = Path(file_path)

        file_type = file_path.suffix.lower()

        if not file_path.exists():
            self.logger.warning(f'{file_type} DOES NOT EXIST at "{file_path}"')
            return None

        if file_type not in self.loaders:
            self.logger.error(f'Unsupported file type "{file_type}"')
            return None

        try:
            result = self.loaders[file_type](file_path, encoding)
            if self.debug_print:
                self.logger.info(f'{file_type} LOADED from "{file_path}" in {timeit.default_timer() - start_time:.2f}s')
            return result
        except Exception as e:
            self.logger.error(f'{file_type} LOAD ERROR at "{file_path}": {e}')
            return None

    def _load_json(self, file_path: Path, encoding):
        with open(file_path, "r", encoding=encoding) as f:
            return json.load(f)

    def _load_jsonl(self, file_path: Path, encoding):
        """Load data from a .jsonl file and return it as a list of dictionaries."""
        with open(file_path, "r", encoding=encoding) as f:
            return [json.loads(line) for line in f]

    def _load_txt(self, file_path: Path, encoding):
        with open(file_path, "r", encoding=encoding) as f:
            raw_lines = f.readlines()
            return [line.strip() for line in raw_lines]

    def _load_csv(self, file_path: Path, encoding):
        return pd.read_csv(file_path, delimiter=',')

    def _load_image(self, file_path: Path, encoding):
        return Image.open(file_path)

    def _load_toml(self, file_path: Path, encoding):
        with open(file_path, "r", encoding=encoding) as f:
            return tomli.load(f)

    def _load_yaml(self, file_path: Path, encoding):
        with open(file_path, "r", encoding=encoding) as f:
            return OmegaConf.load(f)

    def _load_parquet(self, file_path: Path, encoding):
        return pd.read_parquet(file_path)


if __name__ == "__main__":
    # Usage example
    logger = UniLogger("logs", file_suffix="data_loader")
    data_loader = UniLoader(logger)
    json_data = data_loader.loads("example.json")  # string
    txt_data = data_loader.loads(Path("example.txt"))  # path
    csv_data = data_loader.loads(Path("example.csv"))
    image_data = data_loader.loads(Path("example.png"))
    toml_data = data_loader.loads(Path("example.toml"))
    yaml_data = data_loader.loads(Path("example.yaml"))
    parquet_data = data_loader.loads(Path("example.parquet"))
