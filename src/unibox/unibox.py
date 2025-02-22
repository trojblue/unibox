# unibox.py
import os
import tempfile
import timeit
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import pandas as pd  # <--- you'll need this import if not present
from tqdm.auto import tqdm

from .backends.backend_router import get_backend_for_uri
from .backends.local_backend import LocalBackend
from .loaders.loader_router import get_loader_for_path
from .utils.df_utils import generate_dataset_readme
from .utils.globals import GLOBAL_TMP_DIR
from .utils.logger import UniLogger
from .utils.s3_client import S3Client

s3_client = S3Client()
logger = UniLogger()


def _get_type_info(obj: Any) -> str:
    """Get type information for an object."""
    return f"{type(obj).__name__} ({obj.__class__.__module__})"


def _parse_hf_uri(uri: str) -> tuple[str, str]:
    """Parse a Hugging Face URI into repo_id and path."""
    if not uri.startswith("hf://"):
        raise ValueError("URI must start with 'hf://'")
    parts = uri[5:].split("/", 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def load_file(uri: Union[str, Path], debug_print: bool = True, **kwargs) -> str:
    """Load a file's contents as a string."""
    if debug_print:
        logger.info(f"Loading file from {uri}")

    # Get the appropriate backend
    backend = get_backend_for_uri(str(uri))
    if backend is None:
        raise ValueError(f"No backend found for URI: {uri}")

    # Download the file if needed
    local_path = backend.download(str(uri), **kwargs)
    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")

    # Load the file contents
    with open(local_path, "r", encoding="utf-8") as f:
        return f.read()


def loads(uri: Union[str, Path], file: bool = False, debug_print: bool = True, **kwargs) -> Any:
    """Load data from a file or dataset."""
    if debug_print:
        logger.info(f"Loading from {uri}")

    # Get the appropriate backend
    backend = get_backend_for_uri(str(uri))
    if backend is None:
        raise ValueError(f"No backend found for URI: {uri}")

    # Download the file if needed
    local_path = backend.download(str(uri), **kwargs)
    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")

    # If file=True, just return the file path
    if file:
        return local_path

    # Get the appropriate loader
    loader = get_loader_for_path(local_path)
    if loader is None:
        raise ValueError(f"No loader found for file: {local_path}")

    # Load the data
    try:
        return loader.load(local_path, loader_config=kwargs)
    except Exception as e:
        raise ValueError(f"Error loading {uri}: {str(e)}") from e


def saves(data: Any, uri: Union[str, Path], debug_print: bool = True, **kwargs) -> None:
    """Save data to a file or dataset."""
    if debug_print:
        logger.info(f"Saving to {uri}")

    # Get the appropriate backend
    backend = get_backend_for_uri(str(uri))
    if backend is None:
        raise ValueError(f"No backend found for URI: {uri}")

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uri).suffix) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Get the appropriate loader
        loader = get_loader_for_path(tmp_path)
        if loader is None:
            raise ValueError(f"No loader found for file: {tmp_path}")

        # Save the data locally first
        loader.save(tmp_path, data, loader_config=kwargs)

        # Upload the file
        backend.upload(tmp_path, str(uri), **kwargs)
    finally:
        # Clean up
        if tmp_path.exists():
            tmp_path.unlink()


def ls(
    uri: Union[str, Path],
    exts: Optional[List[str]] = None,
    relative_unix: bool = False,
    debug_print: bool = True,
    **kwargs,
) -> list[str]:
    """List files in a directory or dataset."""
    if debug_print:
        logger.info(f"Listing contents of {uri}")

    # Get the appropriate backend
    backend = get_backend_for_uri(str(uri))
    if backend is None:
        raise ValueError(f"No backend found for URI: {uri}")

    # List the files
    return backend.ls(str(uri), exts=exts, relative_unix=relative_unix, **kwargs)


def concurrent_loads(uris_list, num_workers=8, debug_print=True):
    results = [None] * len(uris_list)
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        partial_load = partial(loads, debug_print=False)
        future_to_idx = {executor.submit(partial_load, u): i for i, u in enumerate(uris_list)}

        if debug_print:
            futures_iter = tqdm(as_completed(future_to_idx), total=len(uris_list), desc="Loading concurrent")
        else:
            futures_iter = as_completed(future_to_idx)

        for future in futures_iter:
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"Exception reading {uris_list[idx]}: {e}")

    missing = sum(r is None for r in results)
    if missing > 0:
        logger.warning(f"{missing} loads returned None.")
    return results


def traverses(
    uri: Union[str, Path],
    exts: Optional[List[str]] = None,
    relative_unix: bool = False,
    debug_print: bool = True,
    **kwargs,
) -> list[str]:
    warnings.warn("`traverses()` is deprecated; use `ls()` instead.", DeprecationWarning, stacklevel=2)
    return ls(uri, exts=exts, relative_unix=relative_unix, debug_print=debug_print, **kwargs)


from .nb_helpers.uni_peeker import UniPeeker


def peeks(data: Any, n: int = 3, console_print: bool = False) -> Dict[str, Any]:
    """Peek at the first n items of data in a structured way."""
    result: Dict[str, Any] = {}
    
    if isinstance(data, pd.DataFrame):
        result["type"] = "DataFrame"
        result["shape"] = data.shape
        result["columns"] = list(data.columns)
        result["head"] = data.head(n).to_dict("records")
    elif isinstance(data, (list, tuple)):
        result["type"] = type(data).__name__
        result["length"] = len(data)
        result["head"] = data[:n]
    elif isinstance(data, dict):
        result["type"] = "dict"
        result["length"] = len(data)
        result["keys"] = list(data.keys())[:n]
        result["head"] = dict(list(data.items())[:n])
    else:
        result["type"] = type(data).__name__
        result["value"] = str(data)

    if console_print:
        import json
        print(json.dumps(result, indent=2, default=str))

    return result


def gallery(
    paths: list[str],
    labels: list[str] = [],
    row_height="300px",
    num_workers=32,
    debug_print=True,
    thumbnail_size: int = 512,
):
    try:
        from .nb_helpers.ipython_utils import _gallery

        _gallery(paths, labels, row_height, num_workers, debug_print, thumbnail_size)
    except (ImportError, ModuleNotFoundError):
        print("IPython is not available. Gallery function cannot run.")


def label_gallery(
    paths: list[str],
    labels: list[str] = [],
    row_height="150px",
    num_workers=32,
    debug_print=True,
    thumbnail_size: int = 512,
):
    try:
        from .nb_helpers.ipython_utils import _label_gallery

        _label_gallery(paths, labels, row_height, num_workers, debug_print, thumbnail_size)
    except (ImportError, ModuleNotFoundError):
        print("IPython is not available. label_gallery function cannot run.")


def presigns(s3_uri: str, expiration: int = 604800) -> str:
    return s3_client.generate_presigned_uri(s3_uri, expiration=expiration)
