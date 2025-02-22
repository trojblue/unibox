# unibox/backends/hf_hybrid_backend.py

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import RepositoryNotFoundError

from .base_backend import BaseBackend

HF_PREFIX = "hf://"
START_MARKER = "<!-- BEGIN unibox_hf_autodoc -->"
END_MARKER = "<!-- END unibox_hf_autodoc -->"

import logging

logger = logging.getLogger(__name__)


def parse_hf_uri(hf_uri: str):
    """Parse the Hugging Face URI in the format "hf://{owner}/{repo}/{path_in_repo}".
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
    if len(parts) == 2:
        # e.g. "hf://owner/repo"
        owner, name = parts
        if "/" not in name:
            return f"{owner}/{name}", ""
        # fallback if there's a slash
    # normal case: 3 parts
    owner, name, subpath = parts
    repo_id = f"{owner}/{name}"
    return repo_id, subpath


class HuggingfaceHybridBackend(BaseBackend):
    """A backend that uses low-level HfApi to handle single-file or folder usage in HF repos.

    It can:
      - download a single file (download)
      - upload a single file (upload)
      - list files in a repo (ls)
    """

    def __init__(self):
        self.api = HfApi()

    def download(self, uri: str, target_dir: str | None = None) -> Path | str:
        """Download a single file from a HF repo to `target_dir`.
        If the path_in_repo is actually a folder or there's no final file, we raise NotImplemented.
        """
        if not uri.startswith(HF_PREFIX):
            raise ValueError(f"Invalid HF URI: {uri}")
        repo_id, path_in_repo = parse_hf_uri(uri)
        if not path_in_repo:
            # do nothing, let loader handle it (load dataset as hf://.../)
            logger.info(f"{uri}: is a Huggingface dataset; skipping download.")
            return uri

        if not target_dir:
            target_dir = tempfile.gettempdir()
        os.makedirs(target_dir, exist_ok=True)

        # Download
        revision = "main"  # or read from kwargs if you prefer

        try:
            local_path = hf_hub_download(repo_id=repo_id, filename=path_in_repo, revision=revision)
        except RepositoryNotFoundError:
            logger.info(f"{uri}: is not a model repo; trying to download as dataset...")
            try:
                local_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=path_in_repo,
                    revision="main",
                    repo_type="dataset",
                )
            except RepositoryNotFoundError:
                raise ValueError(f"File not found in HF repo: {uri}")

        # Copy from HF cache to target_dir if needed
        filename_only = os.path.basename(path_in_repo)
        final_path = Path(target_dir) / filename_only
        shutil.copy(local_path, final_path)
        return final_path

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload a single local file to HF at the given subpath in repo.
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

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """List all files in the HF repo. If path_in_repo is a subfolder prefix, we can filter.
        For extension filtering or subpath filtering, you'd manually do it. Here we do a simple approach.
        """
        repo_id, path_in_repo = parse_hf_uri(uri)
        try:
            files = self.api.list_repo_files(repo_id=repo_id)
        except RepositoryNotFoundError:
            logger.info(f"{uri}: is not a model repo; trying to list as dataset...")
            files = self.api.list_repo_files(repo_id=repo_id, repo_type="dataset")

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
        """Download a single file from the HF repo and return the local path."""
        repo_id, path_in_repo = parse_hf_uri(hf_uri)
        local_path = hf_hub_download(repo_id=repo_id, filename=path_in_repo, revision=revision)
        print(f"load_file {hf_uri} -> {local_path}")
        return local_path

    def cp_to_hf(self, local_file_path: str, hf_uri: str, private: bool = True):
        """Copy (upload) a local file to a Hugging Face repository.
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
        """Copy (download) a file from a Hugging Face repository to a local path.
        (Provided for reference; 'download()' is the simpler approach.)
        """
        repo_id, path_in_repo = parse_hf_uri(hf_uri)
        if os.path.isdir(local_file_path):
            local_file_path = os.path.join(local_file_path, os.path.basename(path_in_repo))
        cached_file_path = hf_hub_download(repo_id=repo_id, filename=path_in_repo, revision=revision)
        shutil.copy(cached_file_path, local_file_path)
        print(f"cp {hf_uri} {local_file_path}")

    # You can include rm/mv/cp as well if you wish, but omitted here for brevity.

    def update_readme(
        self,
        repo_id: str,
        new_stats_content: str,
        commit_message: str = "Update README.md",
        repo_type: str = "dataset",
    ):
        """Overwrite ONLY the 'hfbackend_statistics' region in the existing README.md
        (delimited by <!-- BEGIN ... --> and <!-- END ... -->).

        If the region does not exist, it is appended to the bottom of the non-YAML area.
        The YAML block at the top of the file (---\n...\n---\n) is never overwritten.

        Args:
            repo_id (str): The ID of the repo to update (e.g. "org/repo").
            new_stats_content (str): The text that should appear in the 'statistics' block.
            commit_message (str): The commit message to use for the update.
            repo_type (str): The type of repo ("dataset", "model", or "space").
        """
        logger.info(f"Updating README.md in {repo_id} (repo_type={repo_type})")

        # ------------------------------------------------
        # 1) Try to download the existing README.md content
        # ------------------------------------------------
        try:
            existing_readme_path = hf_hub_download(
                repo_id=repo_id,
                filename="README.md",
                repo_type=repo_type,
            )
            with open(existing_readme_path, encoding="utf-8") as f:
                existing_text = f.read()
        except Exception:
            # If README.md does not exist or fails to download, treat as empty
            existing_text = ""

        # ------------------------------------------------
        # 2) Separate out any YAML front-matter (--- ... ---)
        #    so we never overwrite that automatically generated block.
        # ------------------------------------------------
        # This regex looks for the very first '---' then the next '---', capturing everything in between
        # including newlines. We allow for zero or more lines in the middle.
        yaml_pattern = re.compile(r"^---\s*\n.*?\n---\s*\n", flags=re.DOTALL | re.MULTILINE)

        yaml_match = yaml_pattern.search(existing_text)
        if yaml_match:
            yaml_block = yaml_match.group(0)
            rest_of_file = existing_text[yaml_match.end() :]
        else:
            yaml_block = ""
            rest_of_file = existing_text

        # ------------------------------------------------
        # 3) Build the new block we want to insert/replace
        # ------------------------------------------------
        # For clarity, we create a single string that includes the markers and the user stats content
        statistics_block = f"{START_MARKER}\n{new_stats_content}\n{END_MARKER}"

        # ------------------------------------------------
        # 4) Search in 'rest_of_file' for an existing block with those markers
        # ------------------------------------------------
        block_pattern = re.compile(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            flags=re.DOTALL,
        )
        if block_pattern.search(rest_of_file):
            # Replace whatever is between the existing markers with the new text
            new_rest_of_file = block_pattern.sub(statistics_block, rest_of_file)
        else:
            # Markers don't exist -> append at the end of the rest_of_file
            # (with a little spacing to ensure we start on a new line).
            if not rest_of_file.endswith("\n"):
                rest_of_file += "\n"
            new_rest_of_file = rest_of_file + "\n" + statistics_block + "\n"

        # ------------------------------------------------
        # 5) Reassemble the final text
        # ------------------------------------------------
        updated_readme = yaml_block + new_rest_of_file

        # ------------------------------------------------
        # 6) Write new content to a temp file, then upload to HF
        # ------------------------------------------------
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as tmpf:
            tmpf.write(updated_readme)
            temp_path = tmpf.name

        # Make sure the repo exists
        self.api.create_repo(repo_id=repo_id, private=True, exist_ok=True, repo_type=repo_type)

        # Now upload the new README
        try:
            self.api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type=repo_type,
                commit_message=commit_message,
            )
        finally:
            # Cleanup local file
            if os.path.exists(temp_path):
                os.remove(temp_path)
