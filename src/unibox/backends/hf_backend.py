"""loads a repo as dataset directly from Huggingface"""

# hf_backend.py
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from datasets import Dataset, load_dataset
from huggingface_hub import create_repo, upload_file  # or others as needed

from .base_backend import BaseBackend

HF_PREFIX = "hf://"


def parse_hf_uri(uri: str):
    """Given 'hf://username/repo_name/subfolder/file.ext',
    returns (repo_id='username/repo_name', subpath='subfolder/file.ext')
    If there's nothing after repo_name, subpath is ''.
    """
    if not uri.startswith(HF_PREFIX):
        raise ValueError(f"Not a HF URI: {uri}")
    trimmed = uri[len(HF_PREFIX) :]
    parts = trimmed.split("/", maxsplit=1)
    repo_id = parts[0]  # e.g. 'username/repo_name'
    subpath = parts[1] if len(parts) > 1 else ""
    return repo_id, subpath


class HuggingFaceBackend(BaseBackend):
    """A backend that can either:
    - upload a DataFrame to HF as a dataset (if no file extension in the URI).
    - upload a single file to HF if the URI includes a file path.
    """

    def download(self, uri: str) -> Path:
        """If you want to handle single-file downloads from a private or public HF repo,
        you might use `huggingface_hub.hf_hub_download`.
        For an entire dataset, you might skip local download and do `load_dataset`.
        """
        raise NotImplementedError("Download logic for HF single-file not implemented yet.")

    def upload(self, local_path: Path, uri: str, data: Any = None) -> None:
        """Push data to a Hugging Face repo.

        :param local_path: The local file that was saved by your 'loader.save()' logic
                           (might be None or a temp file if the user saved something).
        :param uri: The HF URI: 'hf://username/repo_name...'
        :param data: The original Python object (e.g. DataFrame) from user.
                     We pass it in so we can do special logic if it's a DataFrame
                     and there's no file extension in the HF URI.
        """
        repo_id, subpath = parse_hf_uri(uri)

        # 1) Check if there's a file extension in 'subpath'
        #    If not, and data is a DataFrame, interpret as "Dataset push"
        if not subpath:  # no subpath => no extension => entire dataset
            # We only handle the "DataFrame => push dataset" scenario
            if data is not None and hasattr(data, "to_pandas"):
                # We assume it's a HF "Dataset" or a Pandas DF
                if "pandas" in str(type(data)).lower():
                    # Convert from Pandas to HF Dataset
                    ds = Dataset.from_pandas(data)
                else:
                    # Possibly it's already a HF dataset?
                    ds = data

                # create the HF repo if it doesn't exist
                create_repo(repo_id, private=True, exist_ok=True)

                # push to hub
                ds.push_to_hub(repo_id, private=True)
            else:
                raise NotImplementedError("Can't push non-DataFrame with no file extension URI.")
        else:
            # 2) If there's a file extension, treat as single-file upload
            #    For example, 'hf://username/repo_name/myfile.parquet'
            #    'local_path' is the local file from your temp directory.
            #    We'll upload it into 'repo_id' at path 'subpath'.
            create_repo(repo_id, private=True, exist_ok=True)

            # Perform the file upload
            upload_file(
                path_or_fileobj=str(local_path),
                repo_id=repo_id,
                path_in_repo=subpath,
                repo_type="dataset",  # or "model" if it's a model repo
            )

    def ls(self, uri: str) -> List[str]:
        """Possibly list sub-files or splits in the HF repo if you want.
        For example, call huggingface_hub's repo_info or similar.
        """
        raise NotImplementedError("Listing HF content not implemented yet.")

    def load_dataset(self, repo_id: str, split: Optional[str] = "train") -> Dataset:
        """Load a dataset from the HF Hub and return a `datasets.Dataset`."""
        ds = load_dataset(repo_id, split=split)
        return ds

    def df_to_hub(self, df: pd.DataFrame, uri: str):
        """Upload a DataFrame to HF as a dataset."""
        trimmed = uri[len(HF_PREFIX) :]
        print(f"Uploading DataFrame to HF repo {trimmed}")
        dataset_combined = Dataset.from_pandas(df)

        push_msg = dataset_combined.push_to_hub(trimmed, private=True)
        print(push_msg)
