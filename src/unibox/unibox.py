# ub.py
from pathlib import Path
from typing import Any, Union

from .backends.backend_router import get_backend_for_uri, LocalBackend
from .backends.hf_backend import HuggingFaceBackend
from .loaders.loader_router import get_loader_for_suffix

def loads(uri: Union[str, Path]) -> Any:
    backend = get_backend_for_uri(str(uri))

    # For HF entire dataset approach:
    if isinstance(backend, HuggingFaceBackend):
        # If we pass "hf://username/repo_name" with no file extension,
        # we can parse out "username/repo_name" after "hf://"
        # and call `backend.load_dataset()`.
        
        # 1) Extract the repo part from the URI
        # e.g. "hf://username/repo_name" -> "username/repo_name"
        repo_id = str(uri).replace("hf://", "").rstrip("/")
        
        # 2) Possibly parse out a split if you want
        # For now, default "train"
        ds = backend.load_dataset(repo_id, split="train")
        return ds

    # Otherwise, do the normal "download + suffix-based loader" approach:
    local_path = backend.download(str(uri))  # returns Path
    suffix = local_path.suffix.lower()
    loader = get_loader_for_suffix(suffix)
    if loader is None:
        raise ValueError(f"No loader found for {suffix}")
    return loader.load(local_path)

def saves(data: Any, uri: Union[str, Path]) -> None:
    backend = get_backend_for_uri(str(uri))

    # If it's a HFBackend, possibly do something special,
    # e.g. push to huggingface dataset. This is up to you.
    if isinstance(backend, HuggingFaceBackend):
        # ...
        raise NotImplementedError("Push to HF not implemented yet.")

    # Otherwise do the local or remote approach
    suffix = Path(uri).suffix.lower()
    loader = get_loader_for_suffix(suffix)
    if not loader:
        raise ValueError(f"No loader found for {suffix}")

    if isinstance(backend, LocalBackend):
        loader.save(Path(uri), data)
    else:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            temp_path = Path(tmp.name)
        loader.save(temp_path, data)
        backend.upload(temp_path, str(uri))

def ls(uri: Union[str, Path]) -> list[str]:
    backend = get_backend_for_uri(str(uri))
    return backend.ls(str(uri))