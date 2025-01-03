import os
import click
from typing import List

from unibox import UniTraverser
# Assuming UniTraverser is already defined above

class FileRenamer:
    """
    File renamer class to perform file renaming based on given criteria.

    Attributes:
        root_dir: Root directory.
        suffix: The suffix to add to the file names.
        include_extensions: Optional list of file extensions to include.
        exclude_extensions: Optional list of file extensions to exclude.
    """

    def __init__(self, root_dir: str, suffix: str, include_extensions: List[str] = None,
                 exclude_extensions: List[str] = None):
        self.root_dir = root_dir
        self.suffix = suffix
        self.include_extensions = include_extensions
        self.exclude_extensions = exclude_extensions

    def rename_files(self):
        """
        Renames the files in the root directory based on the given criteria.
        """
        def file_handler(file_path: str):
            dir_path, filename = os.path.split(file_path)
            name, extension = os.path.splitext(filename)
            new_name = f"{name}{self.suffix}{extension}"
            os.rename(file_path, os.path.join(dir_path, new_name))

        traverser = UniTraverser(self.root_dir, include_extensions=self.include_extensions,
                                 exclude_extensions=self.exclude_extensions)
        traverser.traverse(file_handler)

@click.command()
@click.argument('root_dir')
@click.argument('suffix')
@click.option('--include', '-i', default=None, type=str,
              help='File extensions to include (e.g., ".txt .jpg .webp").')
@click.option('--exclude', '-e', default=None, type=str,
              help='File extensions to exclude (e.g., ".txt .jpg .webp").')
def rename(root_dir, suffix, include, exclude):
    include_extensions = include.split() if include else None
    exclude_extensions = exclude.split() if exclude else None
    renamer = FileRenamer(root_dir, suffix, include_extensions, exclude_extensions)
    renamer.rename_files()
    print(f'Renamed files in {root_dir} with suffix {suffix}')

if __name__ == '__main__':
    rename()
