# unibox/backends/hf_api_backend.py

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Optional

from huggingface_hub import HfApi, hf_hub_download
from .base_backend import BaseBackend

HF_PREFIX = "hf://"


def parse_hf_uri(hf_uri: str):
    """
    Parse the Hugging Face URI in the format "hf://{owner}/{repo}/{path_in_repo}".
    Returns (repo_id, path_in_repo).
    """
    if not hf_uri.startswith(HF_PREFIX):
        raise ValueError(f"Invalid HF URI (no hf:// prefix): {hf_uri}")
    # Remove the "hf://" prefix.
    trimmed = hf_uri[len(HF_PREFIX) :]
    parts = trimmed.split("/", 2)
    if len(parts) < 2:
        # e.g. "hf://username/repo" with no trailing subpath -> path_in_repo=''
        owner, name = parts[0], ""
        repo_id = owner  # Not strictly valid, but let's handle carefully
        path_in_repo = ""
        return repo_id, path_in_repo
    elif len(parts) == 2:
        # e.g. "hf://owner/repo"
        owner, name = parts
        if "/" not in name:
            return f"{owner}/{name}", ""
        # fallback if there's a slash
    # normal case: 3 parts
    owner, name, subpath = parts
    repo_id = f"{owner}/{name}"
    return repo_id, subpath


class HuggingFaceApiBackend(BaseBackend):
    """
    A backend that uses low-level HfApi to handle single-file or folder usage in HF repos.

    It can:
      - download a single file (download)
      - upload a single file (upload)
      - list files in a repo (ls)
    For dataset usage, see `HuggingFaceDatasetsBackend`.
    """

    def __init__(self):
        self.api = HfApi()

    def download(self, uri: str, target_dir: str = None) -> Path:
        """
        Download a single file from a HF repo to `target_dir`.
        If the path_in_repo is actually a folder or there's no final file, we raise NotImplemented.
        """
        if not uri.startswith(HF_PREFIX):
            raise ValueError(f"Invalid HF URI: {uri}")
        repo_id, path_in_repo = parse_hf_uri(uri)
        if not path_in_repo:
            raise ValueError(f"No subpath found in URI: {uri} (cannot do single-file download).")

        if not target_dir:
            target_dir = tempfile.gettempdir()
        os.makedirs(target_dir, exist_ok=True)

        # Download
        revision = "main"  # or read from kwargs if you prefer
        local_path = hf_hub_download(repo_id=repo_id, filename=path_in_repo, revision=revision)
        # Copy from HF cache to target_dir if needed
        filename_only = os.path.basename(path_in_repo)
        final_path = Path(target_dir) / filename_only
        shutil.copy(local_path, final_path)
        return final_path

    def upload(self, local_path: Path, uri: str) -> None:
        """
        Upload a single local file to HF at the given subpath in repo.
        If the subpath is empty => we treat that as 'folder'? Or raise error?
        """
        repo_id, path_in_repo = parse_hf_uri(uri)
        if not path_in_repo or path_in_repo.endswith("/"):
            # user wants a directory push
            path_in_repo = path_in_repo.rstrip("/") + "/" + local_path.name

        # Ensure repo exists
        self.api.create_repo(repo_id=repo_id, private=True, exist_ok=True)
        # Upload
        self.api.upload_file(
            path_or_fileobj=str(local_path),
            path_in_repo=path_in_repo,
            repo_id=repo_id,
        )

    def ls(self, uri: str, exts: Optional[List[str]] = None, relative_unix: bool = False,
           debug_print: bool = True, **kwargs) -> List[str]:
        """
        List all files in the HF repo. If path_in_repo is a subfolder prefix, we can filter.
        For extension filtering or subpath filtering, you'd manually do it. Here we do a simple approach.
        """
        repo_id, path_in_repo = parse_hf_uri(uri)
        files = self.api.list_repo_files(repo_id=repo_id)
        # If path_in_repo is not empty, we can filter by that prefix
        if path_in_repo:
            path_in_repo = path_in_repo.rstrip("/")
            files = [f for f in files if f.startswith(path_in_repo)]

        # If exts is given, filter
        if exts:
            exts = [e.lower() for e in exts]
            files = [f for f in files if any(f.lower().endswith(x) for x in exts)]

        # Possibly convert to relative or restore full "hf://..."
        results = []
        for f in files:
            if relative_unix:
                # show subpath relative
                sub = f[len(path_in_repo) :].lstrip("/") if path_in_repo else f
                sub = sub.replace("\\", "/")
                results.append(sub)
            else:
                # return a full HF URI
                results.append(f"hf://{repo_id}/{f}")
        return results

    # -------- Additional methods (from snippet) if needed. --------

    def load_file(self, hf_uri: str, revision: str = "main") -> str:
        """
        Download a single file from the HF repo and return the local path.
        """
        repo_id, path_in_repo = parse_hf_uri(hf_uri)
        local_path = hf_hub_download(repo_id=repo_id, filename=path_in_repo, revision=revision)
        print(f"load_file {hf_uri} -> {local_path}")
        return local_path

    def cp_to_hf(self, local_file_path: str, hf_uri: str, private: bool = True):
        """
        Copy (upload) a local file to a Hugging Face repository. 
        (Provided for reference; 'upload()' is the simpler approach.)
        """
        repo_id, path_in_repo = parse_hf_uri(hf_uri)
        if hf_uri.endswith("/") or not os.path.basename(path_in_repo):
            path_in_repo = path_in_repo.rstrip("/") + "/" + os.path.basename(local_file_path)
        self.api.create_repo(repo_id=repo_id, private=private, exist_ok=True)
        self.api.upload_file(
            path_or_fileobj=local_file_path,
            path_in_repo=path_in_repo,
            repo_id=repo_id,
        )
        print(f"cp {local_file_path} hf://{repo_id}/{path_in_repo}")

    def cp_to_local(self, hf_uri: str, local_file_path: str, revision: str = "main"):
        """
        Copy (download) a file from a Hugging Face repository to a local path.
        (Provided for reference; 'download()' is the simpler approach.)
        """
        repo_id, path_in_repo = parse_hf_uri(hf_uri)
        if os.path.isdir(local_file_path):
            local_file_path = os.path.join(local_file_path, os.path.basename(path_in_repo))
        cached_file_path = hf_hub_download(repo_id=repo_id, filename=path_in_repo, revision=revision)
        shutil.copy(cached_file_path, local_file_path)
        print(f"cp {hf_uri} {local_file_path}")

    # You can include rm/mv/cp as well if you wish, but omitted here for brevity.
