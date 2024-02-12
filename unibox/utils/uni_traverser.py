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

    def __init__(self,
                 root_dir: str,
                 include_extensions: List[str] = None,
                 exclude_extensions: List[str] = None,
                 pre_process: Callable[[], None] = None,
                 post_process: Callable[[], None] = None,
                 error_handler: Callable[[Exception], None] = None):

        # Expand user and variable paths
        self.root_dir = os.path.expanduser(os.path.expandvars(root_dir))
        self.include_extensions = tuple(include_extensions) if include_extensions else None
        self.exclude_extensions = tuple(exclude_extensions) if exclude_extensions else None
        self.pre_process = pre_process
        self.post_process = post_process
        self.error_handler = error_handler
        self.traversed_files = []

    def _files_to_traverse(self):
        for root, _, files in os.walk(self.root_dir):
            for file_name in files:
                extension = os.path.splitext(file_name)[1].lower()
                if (self.include_extensions is None or extension in self.include_extensions) and \
                        (self.exclude_extensions is None or extension not in self.exclude_extensions):
                    yield os.path.join(root, file_name)

    def traverse(self, file_handler: Callable[[str], None] = None, debug_print: bool = True) -> None:
        """
        Traverses the directory tree and applies the given file handler to each file.

        Args:
            file_handler: A function that takes a file path and performs the desired action.
            debug_print: Whether to print debug messages such as tqdm. (turn off if traversing many files)
        """
        if not file_handler:
            file_handler = lambda x: x  # do nothing; only get the file paths

        if self.pre_process:
            self.pre_process()

        # Conditionally initialize tqdm based on debug_print
        pbar = tqdm(desc="Traversing files", leave=False, unit="files", total=None, disable=not debug_print) if debug_print else None

        for file_path in self._files_to_traverse():
            try:
                file_handler(file_path)
            except Exception as e:
                if self.error_handler:
                    self.error_handler(e)
                else:
                    raise e
            if debug_print:
                pbar.update(1)
            self.traversed_files.append(file_path)

        if pbar is not None:  # Ensure the progress bar is closed if it was used
            pbar.close()

        if self.post_process:
            self.post_process()


    def to_relative_unix_path(self, absolute_path: str, convert_slash: bool = True) -> str:
        """
        Converts the absolute Windows path to a relative path with respect to the root directory.
        Optionally, converts the backslashes to forward slashes for cross-platform compatibility.

        Args:
            absolute_path: The absolute Windows path to convert.
            convert_slash: Whether to convert backslashes to forward slashes.

        Returns:
            The relative Linux-like path.
        """
        # Expand user and variable paths
        absolute_path = os.path.expanduser(os.path.expandvars(absolute_path))

        relative_path = os.path.relpath(absolute_path, self.root_dir)
        if convert_slash:
            relative_path = relative_path.replace("\\", "/")
        return relative_path

    def get_traversed_files(self, relative_unix=False):
        if relative_unix:
            return [self.to_relative_unix_path(file_path) for file_path in self.traversed_files]
        else:
            return self.traversed_files


def traverses(root_dir: str, include_extensions: List[str] = None,
              exclude_extensions: List[str] = None, relative_unix=False, debug_print=True):
    """

    Args:
        root_dir: the root s3_uri to traverse
        include_extensions: list of extensions that will be included in the traversal (.txt .jpg .webp)
        exclude_extensions: list of extensions that will be excluded in the traversal (.txt .jpg .webp)
        relative_unix: whether to give a relative path or not (default False gives absolute path)

    Returns:
        list of files that were traversed
    """
    traverser = UniTraverser(root_dir, include_extensions, exclude_extensions)
    traverser.traverse(debug_print=debug_print)
    files = traverser.get_traversed_files(relative_unix=relative_unix)
    return files


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
