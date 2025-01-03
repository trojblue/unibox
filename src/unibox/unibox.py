# ub.py
from pathlib import Path
from typing import Any, Union

from .backends.backend_router import get_backend_for_uri
from .loaders.loader_router import get_loader_for_suffix


def loads(uri: Union[str, Path]) -> Any:
    # 1) Determine the backend
    backend = get_backend_for_uri(str(uri))

    # 2) Download to local
    local_path = backend.download(str(uri))  # returns Path

    # 3) Determine file extension
    suffix = local_path.suffix.lower()

    # 4) Get the loader
    loader = get_loader_for_suffix(suffix)
    if loader is None:
        raise ValueError(f"No loader found for {suffix}")

    # 5) Load
    return loader.load(local_path)


def saves(data: Any, uri: Union[str, Path]) -> None:
    # 1) Determine the backend
    backend = get_backend_for_uri(str(uri))

    # 2) Create a local temp path
    suffix = Path(uri).suffix.lower()  # guess from the final name
    loader = get_loader_for_suffix(suffix)
    if not loader:
        raise ValueError(f"No loader found for {suffix}")

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        temp_path = Path(tmp.name)

    # 3) Save data locally first
    loader.save(temp_path, data)

    # 4) Upload to final destination
    backend.upload(temp_path, str(uri))


def ls(uri: Union[str, Path]) -> list[str]:
    backend = get_backend_for_uri(str(uri))
    return backend.ls(str(uri))
