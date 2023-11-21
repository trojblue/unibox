from __future__ import annotations

import os
import tempfile
import requests
from urllib.parse import urlparse

from pathlib import Path
from typing import Union, List, Dict, Any

from .utils.uni_loader import UniLoader
from .utils.uni_logger import UniLogger
from .utils.uni_saver import UniSaver
from .utils.uni_traverser import UniTraverser
from .utils.uni_traverser import traverses as _onestep_traverse
from .utils.uni_resizer import UniResizer
from .utils.uni_merger import UniMerger
from .utils.s3_client import S3Client
from .utils import constants  # from unibox.constants import IMG_FILES


def is_s3_uri(uri: str) -> bool:
    """Check if the URI is an S3 URI."""
    parsed = urlparse(uri)
    return parsed.scheme == 's3'


def is_url(path: str) -> bool:
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except:
        return False

def loads(file_path: str | Path, debug_print=True) -> any:
    """
    Loads arbitrary data from the given file path, using UniLoader.loads() method.
    :param file_path: Path to the file to load.
    :param debug_print: Whether to print debug messages. (advised to turn off if loading many files)

    example:
    >>> df = unibox.loads("data.csv")
    >>> json_dict_list = unibox.loads("data.jsonl")
    >>> pil_iimage = unibox.loads("image.png")
    """
    loader = UniLoader(debug_print=debug_print)

    if is_s3_uri(str(file_path)):
        s3_client = S3Client()
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = Path(s3_client.download(str(file_path), tmp_dir))
            return loader.loads(local_path)
    elif is_url(str(file_path)):
        response = requests.get(file_path)
        response.raise_for_status()  # Ensure the request was successful
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(response.content)
            return loader.loads(tmp_file.name)
    else:
        return loader.loads(file_path)

def saves(data: Any, file_path: Path | str) -> None:
    """
    Saves arbitrary data to the given file path, using the UniSaver.saves() method.
    :param data: The data to saves.
    :param file_path: Path to the file to saves.

    example:
    >>> json_dict = {"name": "John", "age": 30}
    >>> unibox.saves(json_dict, "data.json")
    >>> json_dict_list = [{"name": "John", "age": 30}, {"name": "Doe", "age": 40}]
    >>> unibox.saves(json_dict_list, "data.jsonl")
    >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> unibox.saves(df, "data.parquet")
    >>> pil_image = Image.new('RGB', (60, 30), color='red')
    >>> unibox.saves(pil_image, "image.png")
    """
    saver = UniSaver()
    saver.saves(data, file_path)


def traverses(root_dir: str, include_extensions: List[str] = None,
              exclude_extensions: List[str] = None, relative_unix=False):
    """

    Args:
        root_dir: the root dir to traverse
        include_extensions: list of extensions that will be included in the traversal (.txt .jpg .webp)
        exclude_extensions: list of extensions that will be excluded in the traversal (.txt .jpg .webp)
        relative_unix: whether to give a relative path or not (default False gives absolute path)

    Returns:
        list of files that were traversed
    """
    return _onestep_traverse(root_dir, include_extensions, exclude_extensions, relative_unix)


def merges(*data: Union[str, Dict, List[Any], Any]) -> Any:
    """
    Merges arbitrary data using UniMerger.merges() method.
    :param data: A variable number of data entries to merge. Each entry can be a dictionary, a list, a dataframe, or a string representing a file path.
    :param debug_print: Whether to print debug messages. (advised to turn off if merging many data entries)
    :return: Merged data
    example:
    >>> merged_dict = merges(dict1, dict2, dict3)
    >>> merged_df = merges(df1, df2, df3)
    >>> merged_data_from_files = merges("data1.csv", "data2.json", "data3.parquet")
    """
    merger = UniMerger()
    return merger.merges(*data)
