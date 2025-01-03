from pathlib import Path
from typing import Any, Union

from .backends.backend_router import get_backend_for_uri, LocalBackend
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

    # 2) Determine the file extension and get the loader
    suffix = Path(uri).suffix.lower()
    loader = get_loader_for_suffix(suffix)
    if not loader:
        raise ValueError(f"No loader found for {suffix}")

    # 3) If local backend, save directly to the final path
    #    Otherwise, write to a temp file and then upload.
    if isinstance(backend, LocalBackend):
        # Directly save to `uri`
        loader.save(Path(uri), data)
    else:
        # Use temp file and then upload
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            temp_path = Path(tmp.name)

        loader.save(temp_path, data)
        backend.upload(temp_path, str(uri))

def ls(uri: Union[str, Path]) -> list[str]:
    backend = get_backend_for_uri(str(uri))
    return backend.ls(str(uri))