import os
import shutil
from tqdm.auto import tqdm
from typing import List

from unibox.utils.uni_traverser import UniTraverser


class DirMoverCopier:
    """
    Directory mover/copier class to perform file moving or copying based on given criteria.

    Attributes:
        src_dir: Source directory.
        dst_dir: Destination directory.
        keep_structure: Whether to keep the directory structure.
        include_extensions: Optional list of file extensions to include.
        exclude_extensions: Optional list of file extensions to exclude.
        action: Action to perform ('move' or 'copy').
    """

    def __init__(self, src_dir: str, dst_dir: str, keep_structure: bool, include_extensions: List[str] = None,
                 exclude_extensions: List[str] = None, action: str = 'move'):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.keep_structure = keep_structure
        self.include_extensions = include_extensions
        self.exclude_extensions = exclude_extensions
        self.action = action

        self._print_debug_string()

    def _print_debug_string(self):
        debug_string = f"Processing with action={self.action}: " \
                       f"src_dir={self.src_dir}, dst_dir={self.dst_dir}, " \
                       f"keep_structure={self.keep_structure}, include={self.include_extensions}, " \
                       f"exclude={self.exclude_extensions}"
        print(debug_string)

    def should_include_file(self, file_name):
        extension = os.path.splitext(file_name)[1]
        if self.include_extensions and extension not in self.include_extensions:
            return False
        if self.exclude_extensions and extension in self.exclude_extensions:
            return False
        return True

    def process_files(self):
        """
        Processes the files in the source directory based on the given criteria and action.
        """
        processed_files = 0

        def file_handler(src_file_path: str):
            nonlocal processed_files
            filename = os.path.basename(src_file_path)
            if self.should_include_file(filename):
                dir_path = os.path.dirname(src_file_path)
                dst_file_dir = self.dst_dir if not self.keep_structure else \
                    os.path.join(self.dst_dir, os.path.relpath(dir_path, self.src_dir))
                os.makedirs(dst_file_dir, exist_ok=True)
                dst_file_path = os.path.join(dst_file_dir, filename)
                if self.action == 'move':
                    shutil.move(src_file_path, dst_file_path)
                    processed_files += 1
                elif self.action == 'copy':
                    shutil.copy2(src_file_path, dst_file_path)
                    processed_files += 1

        traverser = UniTraverser(self.src_dir, include_extensions=self.include_extensions,
                                 exclude_extensions=self.exclude_extensions)
        traverser.traverse(file_handler)

        print(f"Processed {processed_files} files")
