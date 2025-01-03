"""loads a repo as dataset directly from Huggingface
"""

# hf_backend.py
from pathlib import Path
import tempfile
from typing import List, Optional, Union

from .base_backend import BaseBackend

# Hugging Face libraries
from datasets import load_dataset, Dataset
# If you need huggingface_hub for private files:
# from huggingface_hub import hf_hub_download

class HuggingFaceBackend(BaseBackend):
    """
    A backend to handle URIs like: hf://some_repo  (or variants).
    - If you want to load an entire dataset, we do load_dataset(...)
    - If you want a single file, we might do something else.
    """

    def download(self, uri: str) -> Path:
        """
        1) If this is "hf://repo_name" with no file extension,
           it may not make sense to "download" to a local path
           if your final goal is a `datasets.Dataset`.
           2) If we detect a file-based approach (e.g. 'hf://repo_name/some_file.parquet'),
           we might do a direct HF Hub download of that single file, returning a local Path.
        """
        # Minimal placeholder logic:
        # Suppose 'hf://username/repo_name/data.parquet'
        # you parse out "username/repo_name" and the file 'data.parquet'
        
        # If it's truly just "hf://username/repo_name" with no file extension,
        # we might return a dummy path or skip the suffix-based loader.
        
        # For now, let's say:
        raise NotImplementedError("Use load_dataset() instead of .download() for entire HF datasets.")

    def upload(self, local_path: Path, uri: str) -> None:
        """
        If you want to push data to HF. This might involve:
        - Converting local_path (like a CSV or Parquet) into a huggingface "Dataset.from_pandas(...)"
        - Then calling push_to_hub(...).
        Implementation depends on your flow.
        """
        raise NotImplementedError("Push to HF not implemented yet.")

    def ls(self, uri: str) -> List[str]:
        """
        If you want to list "files" or "splits" in a HF dataset.
        Possibly parse huggingface_hub metadata or an object store.
        """
        raise NotImplementedError("List HF content not implemented yet.")

    def load_dataset(self, repo_id: str, split: Optional[str] = "train") -> Dataset:
        """
        Load a dataset from the HF Hub and return a `datasets.Dataset`.
        """
        ds = load_dataset(repo_id, split=split)
        return ds
