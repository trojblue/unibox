from typing import List, Callable
from tqdm import tqdm
import os

from typing import List, Callable, Optional
from tqdm import tqdm
import os


class UniTraverser:
    """
    Universal directory traverser that handles traversal with optional file extension filtering.

    Attributes:
        root_dir: The root directory to traverse.
        include_extensions: Optional list of file extensions to include.
        exclude_extensions: Optional list of file extensions to exclude.
        pre_process: Optional function to call before traversal.
        post_process: Optional function to call after traversal.
        error_handler: Optional function to handle errors during traversal.
    """

    def __init__(self, root_dir: str, include_extensions: List[str] = None,
                 exclude_extensions: List[str] = None, pre_process: Callable[[], None] = None,
                 post_process: Callable[[], None] = None, error_handler: Callable[[Exception], None] = None):
        self.root_dir = root_dir
        self.include_extensions = tuple(include_extensions) if include_extensions else None
        self.exclude_extensions = tuple(exclude_extensions) if exclude_extensions else None
        self.pre_process = pre_process
        self.post_process = post_process
        self.error_handler = error_handler
        self.traversed_files = []

    def _files_to_traverse(self):
        for root, _, files in os.walk(self.root_dir):
            for file_name in files:
                extension = os.path.splitext(file_name)[1]
                if (self.include_extensions is None or extension in self.include_extensions) and \
                        (self.exclude_extensions is None or extension not in self.exclude_extensions):
                    yield os.path.join(root, file_name)
    def traverse(self, file_handler: Callable[[str], None]) -> None:
        """
        Traverses the directory tree and applies the given file handler to each file.

        Args:
            file_handler: A function that takes a file path and performs the desired action.
        """
        if self.pre_process:
            self.pre_process()

        with tqdm(desc="Traversing files", leave=False, unit="files", total=None) as pbar:
            for file_path in self._files_to_traverse():
                try:
                    file_handler(file_path)
                except Exception as e:
                    if self.error_handler:
                        self.error_handler(e)
                    else:
                        raise e
                pbar.update(1)
                self.traversed_files.append(file_path)

        if self.post_process:
            self.post_process()


# example code
def pre_process():
    print("Starting traversal...")


def post_process():
    print("Finished traversal.")


def error_handler(e: Exception):
    print(f"An error occurred: {e}")


def print_txt_file(file_path: str):
    # demo file handler; does nothing but traversed file is in traverser.traversed_files
    pass


if __name__ == '__main__':
    root_dir = r"E:\Datasets\bp"
    include_extensions = [".txt"]
    traverser = UniTraverser(root_dir, include_extensions=include_extensions,
                             pre_process=pre_process, post_process=post_process,
                             error_handler=error_handler)
    traverser.traverse(print_txt_file)

    print(f"traversed {len(traverser.traversed_files)} files")
    print("Done")
