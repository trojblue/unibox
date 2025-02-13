# unibox/backends/hf_router_backend.py

from pathlib import Path
from typing import List, Optional

from ..utils.logger import UniLogger
from .base_backend import BaseBackend
from .hf_api_backend import HuggingFaceApiBackend
from .hf_datasets_backend import HuggingFaceDatasetsBackend, parse_hf_uri

logger = UniLogger()


def has_dot_in_final_segment(subpath: str) -> bool:
    """Quick check: if the last path segment has a '.' in it, we treat that
    as a 'file-like' path. e.g. "folder/stuff.bin" or "myfile.parquet"
    """
    seg = subpath.split("/")[-1] if subpath else ""
    return "." in seg


class HuggingFaceRouterBackend(BaseBackend):
    """A meta-backend that tries either dataset or single-file approach:
      - If there's no subpath or the subpath doesn't have a dot => single-file first, fallback dataset
      - If there's a dot => dataset first, fallback single-file
    This matches the original “try one, fallback other” logic you requested.
    """

    def __init__(self):
        super().__init__()
        self.api_backend = HuggingFaceApiBackend()  # single-file
        self.ds_backend = HuggingFaceDatasetsBackend()  # dataset

    def download(self, uri: str, target_dir: str = None) -> Path:
        """We interpret “download” to mean “give me a local file”.
        So if we suspect dataset => not implemented. If we suspect single-file => do it.
        But we can do a fallback approach if that fails.
        """
        repo_id, subpath = parse_hf_uri(uri)
        # no subpath => definitely can't do single-file => or subpath has no dot => single-file first
        if not subpath:
            # no subpath => can't single-file => we do dataset approach? Actually dataset approach
            # doesn't produce a single local file. So “download a dataset” is a mismatch.
            raise NotImplementedError(
                "Cannot download entire dataset to single local file in this router. "
                "Try using unibox.py loads() to load HF dataset, or handle multiple files.",
            )
        # If there's a dot => dataset first, fallback single-file
        # OR if there's no dot => single-file first, fallback dataset
        if has_dot_in_final_segment(subpath):
            # dataset first
            try:
                # But dataset approach's download() is not implemented => we must do something else
                # We'll raise or fallback to single-file?
                raise NotImplementedError("Downloading HF dataset as a single file is not possible in ds_backend.")
            except Exception as e_ds:
                logger.debug(f"Dataset approach failed: {e_ds}, falling back to single-file download.")
                # fallback single-file
                return self.api_backend.download(uri, target_dir)
        else:
            # single-file first
            try:
                return self.api_backend.download(uri, target_dir)
            except Exception as e_file:
                logger.debug(f"Single-file approach failed: {e_file}, trying dataset approach.")
                raise NotImplementedError("No direct single-file => dataset fallback is feasible here.")

    def upload(self, local_path: Path, uri: str) -> None:
        """If subpath has a dot => dataset push first, fallback single-file?
        Or the opposite? Adjust the logic as you see fit.
        In practice, you might check if `local_path` is a single file or if you have
        a `datasets.Dataset` object.
        """
        repo_id, subpath = parse_hf_uri(uri)
        if not subpath:
            # Means “hf://owner/repo” no file => dataset approach
            # We actually do “data_to_hub” in the ds backend
            raise NotImplementedError("For dataset push, call ds_backend.data_to_hub(...) directly.")
        # If there's a dot => likely single-file => let's do the api backend
        self.api_backend.upload(local_path, uri)

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """We can attempt listing from the API backend (which uses list_repo_files).
        If you want to separate “dataset splits” listing from “files listing,”
        you might do that with ds_backend, but here let's just rely on api_backend.
        """
        return self.api_backend.ls(uri, exts=exts, relative_unix=relative_unix, debug_print=debug_print, **kwargs)
