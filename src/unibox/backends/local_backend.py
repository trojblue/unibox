# local_backend.py
import os
import warnings
from pathlib import Path
from typing import List, Optional
import shutil

from tqdm.auto import tqdm

from .base_backend import BaseBackend


class LocalBackend(BaseBackend):
    def download(self, uri: str, target_dir: str = None) -> Path:
        # local path is the URI itself, so just return Path(uri)
        return Path(uri)

    def upload(self, local_path: Path, uri: str) -> None:
        """Ensure the final path has the saved file."""
        dest = Path(uri)
        if dest != local_path:
            # Copy the temp file to the final path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(local_path), str(dest))

    def _traverse_local_dir(
        self,
        root_dir: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
    ) -> List[str]:
        """Traverses the local directory tree and returns a list of files matching the criteria.

        Args:
            root_dir (str): The root directory to traverse.
            exts (List[str], optional): List of file extensions to include. Defaults to None.
            relative_unix (bool, optional): Whether to return relative Unix-style paths. Defaults to False.
            debug_print (bool, optional): Whether to display a progress bar. Defaults to True.

        Returns:
            List[str]: List of file paths.
        """
        abs_root = Path(os.path.expanduser(os.path.expandvars(root_dir))).resolve()
        found_files = []

        # Precompute extensions as a tuple for faster filtering
        exts = tuple(exts) if exts else None

        # Initialize tqdm progress bar
        pbar = tqdm(desc="Listing local files", leave=False, unit="files", disable=not debug_print)

        for dirpath, _, filenames in os.walk(abs_root):
            for file_name in filenames:
                # Filter files based on extensions
                if exts is None or file_name.endswith(exts):
                    full_path = Path(dirpath) / file_name

                    if relative_unix:
                        rel_path = full_path.relative_to(abs_root).as_posix()
                        found_files.append(str(rel_path))
                    else:
                        found_files.append(str(full_path))

                    pbar.update(1)

        pbar.close()  # Close the progress bar
        return found_files

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """Lists files in the local directory with optional extension filtering.

        Args:
            uri (str): Directory URI to list.
            exts (List[str], optional): List of extensions to include. Defaults to None.
            relative_unix (bool, optional): Whether to return relative Unix-style paths. Defaults to False.
            debug_print (bool, optional): Whether to display a progress bar. Defaults to True.

        Returns:
            List[str]: List of file paths.
        """
        # Handle backward compatibility for `include_extensions`
        include_extensions = kwargs.pop("include_extensions", None)
        if include_extensions is not None:
            warnings.warn(
                "`include_extensions` is deprecated; use `exts` instead.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            exts = include_extensions

        return self._traverse_local_dir(
            root_dir=uri,
            exts=exts,
            relative_unix=relative_unix,
            debug_print=debug_print,
        )
