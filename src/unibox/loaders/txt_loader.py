from pathlib import Path
from typing import List

from .base_loader import BaseLoader


class TxtLoader(BaseLoader):
    """Load and (optionally) save text files."""

    def load(self, file_path: Path, encoding: str = "utf-8") -> List[str]:
        """
        Load a text file and return a list of stripped lines.

        Args:
            file_path (Path): The path to the text file.
            encoding (str): The file encoding. Defaults to 'utf-8'.

        Returns:
            List[str]: A list of lines with leading and trailing whitespace removed.
        """
        with open(file_path, "r", encoding=encoding) as f:
            return [line.strip() for line in f.readlines()]

    def save(self, file_path: Path, data: List[str], encoding: str = "utf-8") -> None:
        """
        Save a list of strings to a text file.

        Args:
            file_path (Path): The path to the text file.
            data (List[str]): The list of strings to write to the file.
            encoding (str): The file encoding. Defaults to 'utf-8'.
        """
        with open(file_path, "w", encoding=encoding) as f:
            f.writelines(f"{line}\n" for line in data)
