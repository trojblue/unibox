# unibox/backends/hf_datasets_backend.py

from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from datasets import Dataset, load_dataset

from ..utils.logger import UniLogger
from .base_backend import BaseBackend

logger = UniLogger()

HF_PREFIX = "hf://"


def parse_hf_uri(uri: str):
    """Given 'hf://username/repo_name/subpath...' -> (repo_id='username/repo_name', subpath='subpath...')."""
    if not uri.startswith(HF_PREFIX):
        raise ValueError(f"Not an HF URI: {uri}")
    trimmed = uri[len(HF_PREFIX) :]
    parts = trimmed.split("/", maxsplit=1)
    repo_id = parts[0]
    subpath = parts[1] if len(parts) > 1 else ""
    return repo_id, subpath


class HuggingFaceDatasetsBackend(BaseBackend):
    """A backend that handles HF *datasets* usage:
    - load_dataset() from a repo
    - push entire Dataset to a repo
    """

    def download(self, uri: str, target_dir: str = None) -> Path:
        """For a dataset-based approach, we usually don't do single-file 'download()'.
        We'll raise NotImplemented if we ever get here for single-file usage.
        """
        raise NotImplementedError("HuggingFaceDatasetsBackend does not handle single-file download.")

    def upload(self, local_path: Path, uri: str) -> None:
        """Expects the user is pushing a Dataset => must handle separately. Use data_to_hub()."""
        raise NotImplementedError("HuggingFaceDatasetsBackend expects entire dataset push (see data_to_hub).")

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """List sub-files or splits in a HF dataset repo? Currently not implemented."""
        raise NotImplementedError("Listing HF dataset contents is not implemented here.")

    # -- Additional helper for dataset loading:
    def load_dataset(
        self,
        repo_id: str,
        split: Optional[str] = "train",
        revision: str = "main",
        to_pandas: bool = False,
    ) -> Dataset:
        """Load a dataset from the HF Hub and return a `datasets.Dataset`.

        Args:
            repo_id: Repository ID ("org/repo_name").
            split: Split name to load (default: "train").
            revision: Branch/tag name (default: "main").
            to_pandas: Convert to pandas DataFrame before returning (default: False).
        """
        if to_pandas:
            return load_dataset(repo_id, split=split, revision=revision).to_pandas()
        return load_dataset(repo_id, split=split, revision=revision)

    # -- Additional helper for pushing data frames or Datasets:
    def data_to_hub(self, data: pd.DataFrame | Dataset | Any, repo_id: str, private: bool = True, **kwargs) -> None:
        """Upload a DataFrame or HF Dataset to HF as a dataset repo.

        kwargs:
            eg. `split` for Dataset.from_pandas()
        """
        logger.info(f"Uploading dataset to HF repo {repo_id}")
        if isinstance(data, Dataset):
            ds = data
        elif isinstance(data, pd.DataFrame):
            ds = Dataset.from_pandas(data, **kwargs)
        else:
            # attempt to convert
            ds = Dataset.from_pandas(pd.DataFrame(data), **kwargs)

        # create_repo(repo_id, private=private, exist_ok=True)
        ds.push_to_hub(repo_id, private=private)
