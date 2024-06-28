# Adding the _load_csv and _load_parquet methods to the UniLoader class

from __future__ import annotations

import json
import timeit

import re
import os
import mimetypes
import tempfile
import requests
import orjson

import tomli
import pandas as pd

from PIL import Image
from pathlib import Path
from omegaconf import OmegaConf

from unibox.utils.uni_logger import UniLogger
from unibox.utils.s3_client import S3Client
from unibox.utils.utils import is_url, is_s3_uri


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
            '.feather': self._load_feather,
            ".har": self._load_json,
        }

    def _load_from_s3(self, s3_uri: str):
        """Download a file from an S3 URI and load its content."""
        s3_client = S3Client()
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                local_path = Path(s3_client.download(s3_uri, tmp_dir))
                return self.loads(local_path)
        except Exception as e:
            self.logger.error(f'Error loading from S3 at "{s3_uri}": {e}')
            return None

    def _load_from_url(self, url: str):
        """Download a file from a URL and load its content."""
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful

        _, url_suffix = os.path.splitext(url)
        if url_suffix == '':
            content_type = response.headers.get('content-type')
            mime_suffix = mimetypes.guess_extension(content_type)
            suffix = mime_suffix if mime_suffix else ''
        else:
            suffix = url_suffix

        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                tmp_file_path = tmp_file.name
                # tmp_file.close()
                return self.loads(tmp_file_path)
        except Exception as e:
            self.logger.error(f'Error loading from URL at "{url}": {e}')
            return None

    def loads(self, file_path: Path | str, encoding="utf-8"):
        """Load data from the given file path.

        The type of data returned depends on the file extension.
        """
        start_time = timeit.default_timer()

        # check if is s3 uri or url (downloads the file)
        if isinstance(file_path, str):
            if is_s3_uri(file_path):
                return self._load_from_s3(file_path)

            elif is_url(file_path):
                return self._load_from_url(file_path)

        # is a local file
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
            # read the file using loader function
            result = self.loaders[file_type](file_path, encoding)
            if self.debug_print:
                self.logger.info(f'{file_type} LOADED from "{file_path}" in {timeit.default_timer() - start_time:.2f}s')
            return result
        except Exception as e:
            self.logger.error(f'{file_type} LOAD ERROR at "{file_path}": {e}')
            return None

    def _load_json(self, file_path: Path, encoding='utf-8'):
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
                # Check if the file content is empty
                if not file_content:
                    self.logger.error(f'{file_path} is empty or zero-length.')
                    return None  # or {} depending on how you want to handle this case
                return orjson.loads(file_content)
        except orjson.JSONDecodeError as e:
            self.logger.error(f'JSON LOAD ERROR at "{file_path}": {e}')
            return None
        except Exception as e:
            self.logger.error(f'Unexpected error loading JSON at "{file_path}": {e}')
            return None


    def _load_jsonl(self, file_path: Path, encoding='utf-8'):
        """
        Load data from a .jsonl file and return it as a list of dictionaries.
        Attempts to handle "NaN" gracefully by replacing them with "null".
        """
        data = []
        with open(file_path, "rb") as f:
            for i, line in enumerate(f, start=1):
                try:
                    # Attempt to decode the line using UTF-8
                    line = line.decode(encoding)
                except UnicodeDecodeError as e:
                    self.logger.error(f"Unicode decode error on line {i}: {e}\nContent: {line}")
                    continue
                try:
                    # Try loading the JSON directly
                    data.append(orjson.loads(line))
                except orjson.JSONDecodeError as initial_error:
                    # If there's a JSON error, check and replace NaN with null
                    if 'NaN' in line:
                        self.logger.warning(f"NaN found and replaced with null on line {i}")
                        line = re.sub(r'\bNaN\b', 'null', line)
                        try:
                            data.append(orjson.loads(line))
                        except orjson.JSONDecodeError as e:
                            self.logger.error(f"JSON decode error on line {i} after replacing NaN: {e}\nContent: {line}")
                    else:
                        self.logger.error(f"JSON decode error on line {i}: {initial_error}\nContent: {line}")
        return data

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

    def _load_feather(self, file_path: Path, encoding):
        return pd.read_feather(file_path)

def sample_usage():
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


def debug_url():
    loader = UniLoader()
    img = loader.loads("https://cdn.donmai.us/sample/8e/ea/__karyl_princess_connect_drawn_by_maxwelzy__sample-8eea944690c0c0b27e303420cb1e65bd.jpg")

    print(type(img))


def debug_jsonl():
    loader = UniLoader()
    # /rmtrain/quail/sdxl_qft/sdxl_qft_v5.jsonl
    data = loader.loads("/home/ubuntu/dev/unibox/noteooks/sdxl_qft_v5.jsonl")
    print(data)


if __name__ == "__main__":
    debug_jsonl()

