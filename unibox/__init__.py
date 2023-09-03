from __future__ import annotations

from pathlib import Path
from typing import Any, List, Callable, Optional

from .utils.uni_loader import UniLoader
from .utils.uni_logger import UniLogger
from .utils.uni_saver import UniSaver
from .utils.uni_traverser import UniTraverser
from .utils.uni_traverser import traverses as _onestep_traverse
from .utils.uni_resizer import UniResizer
from .utils import constants #  from unibox.constants import IMG_FILES


def loads(file_path: Path | str, debug_print=True) -> any:
    """
    Loads arbitrary data from the given file path, using UniLoader.loads() method.
    :param file_path: Path to the file to load.
    :param debug_print: Whether to print debug messages. (advised to turn off if loading many files)
    example:
    >>> df = unibox.loads("data.csv")
    >>> json_dict_list = unibox.loads("data.jsonl")
    >>> pil_iimage = unibox.loads("image.png")
    """
    Loader = UniLoader(debug_print=debug_print)
    return Loader.loads(file_path)


def saves(data: Any, file_path: Path | str) -> None:
    """
    Saves arbitrary data to the given file path, using the UniSaver.save() method.
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