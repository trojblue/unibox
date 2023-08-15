from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils.uni_loader import UniLoader
from .utils.uni_logger import UniLogger
from .utils.uni_saver import UniSaver
from .utils import constants  #  from unibox.constants import IMG_FILES

def loads(file_path: Path | str) -> any:
    """
    Loads arbitrary data from the given file path, using UniLoader.loads() method.
    :param file_path: Path to the file to load.

    example:
    >>> df = unibox.loads("data.csv")
    >>> json_dict_list = unibox.loads("data.jsonl")
    >>> pil_iimage = unibox.loads("image.png")
    """
    Loader = UniLoader()
    return Loader.loads(file_path)


def saves(data: Any, file_path: Path | str) -> None:
    """
    Saves arbitrary data to the given file path, using the uniSaver.save() method.
    :param data: The data to save.
    :param file_path: Path to the file to save.

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
    saver.save(data, file_path)