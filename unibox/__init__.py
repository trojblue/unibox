from __future__ import annotations

from pathlib import Path

from .utils.uni_loader import UniLoader
from .utils.uni_logger import UniLogger

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