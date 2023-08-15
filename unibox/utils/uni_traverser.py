from typing import List, Callable
from tqdm import tqdm
import os


class UniTraverser:
    """
    Universal directory traverser that handles traversal with optional file extension filtering.

    Attributes:
        root_dir: The root directory to traverse.
        include_extensions: Optional list of file extensions to include.
        exclude_extensions: Optional list of file extensions to exclude.
    """

    def __init__(self, root_dir: str, include_extensions: List[str] = None, exclude_extensions: List[str] = None):
        self.root_dir = root_dir
        self.include_extensions = tuple(include_extensions) if include_extensions else None
        self.exclude_extensions = tuple(exclude_extensions) if exclude_extensions else None

    def traverse(self, file_handler: Callable[[str], None]):
        """
        Traverses the directory tree and applies the given file handler to each file.

        Args:
            file_handler: A function that takes a file path and performs the desired action.
        """
        with tqdm(desc="Traversing files", leave=False, unit="files", total=None) as pbar:
            for root, _, files in os.walk(self.root_dir):
                for file_name in files:
                    extension = os.path.splitext(file_name)[1]
                    if (self.include_extensions is None or extension in self.include_extensions) and \
                            (self.exclude_extensions is None or extension not in self.exclude_extensions):
                        file_path = os.path.join(root, file_name)
                        file_handler(file_path)
                        pbar.update(1)


def print_txt_file(file_path: str):
    # demo file handler
    print(f"Found .txt file: {file_path}")


if __name__ == '__main__':
    root_dir = "/path/to/your/directory"
    include_extensions = [".txt"]
    traverser = UniTraverser(root_dir, include_extensions=include_extensions)
    traverser.traverse(print_txt_file)
