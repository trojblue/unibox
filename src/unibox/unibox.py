# unibox.py
import os
import warnings
from collections.abc import Iterable, Mapping
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from tqdm.auto import tqdm

from .backends.backend_router import get_backend_for_uri
from .backends.http_backend import HTTPBackend
from .loaders.loader_router import get_loader_for_path, load_data
from .utils.df_utils import coerce_json_like_to_df
from .utils.logger import UniLogger
from .utils.s3_client import S3Client

s3_client = None
logger = UniLogger()
HTTP_DOWNLOAD_KWARGS = {"target_dir", "timeout", "retries", "retry_backoff", "chunk_size", "headers"}
NON_HTTP_DOWNLOAD_KWARGS = HTTP_DOWNLOAD_KWARGS - {"target_dir"}


def _resolve_downloaded_path(local_path: Union[str, Path]) -> Path:
    resolved_path = Path(local_path).resolve(strict=False)
    if not (resolved_path.exists() or os.path.lexists(str(resolved_path))):
        raise FileNotFoundError(f"File not found: {resolved_path}")
    return resolved_path


def _load_from_local_path(local_path: Union[str, Path], loader_config: Optional[Dict[str, Any]] = None) -> Any:
    resolved_path = _resolve_downloaded_path(local_path)
    loader = get_loader_for_path(resolved_path)
    if loader is None:
        raise ValueError(f"No loader found for path: {resolved_path}")
    return loader.load(resolved_path, loader_config=loader_config or {})


def _split_http_download_kwargs(kwargs: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    download_kwargs = {key: value for key, value in kwargs.items() if key in HTTP_DOWNLOAD_KWARGS}
    loader_kwargs = {key: value for key, value in kwargs.items() if key not in HTTP_DOWNLOAD_KWARGS}
    return download_kwargs, loader_kwargs


def _is_http_uri(uri: Union[str, Path]) -> bool:
    return str(uri).startswith(("http://", "https://"))


def _raise_if_unsupported_non_http_download_kwargs(kwargs: Dict[str, Any], context: str) -> None:
    unsupported = sorted(key for key in kwargs if key in NON_HTTP_DOWNLOAD_KWARGS)
    if unsupported:
        joined = ", ".join(unsupported)
        raise ValueError(f"{joined} {context} only supported for HTTP/HTTPS URIs.")


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
    resolved_path = _resolve_downloaded_path(local_path)

    # Load the file contents
    with open(resolved_path, encoding="utf-8") as f:
        return f.read()


def loads(uri: Union[str, Path], file: bool = False, debug_print: bool = True, **kwargs) -> Any:
    """Load data from a file or dataset.

    For HuggingFace URIs:
    - hf://owner/repo => loads as dataset
    - hf://owner/repo/path/to/file.ext => loads as file

    Args:
        uri: Path or URI to load from
        file: If True, return the local file path instead of parsing.
            For HTTP/HTTPS URIs, you can pass download options like
            `target_dir`, `timeout`, `retries`, `retry_backoff`,
            `chunk_size`, and `headers`.
        debug_print: Whether to print debug info
        **kwargs: Additional arguments passed to loader
            For HF datasets: split, streaming, revision, etc.
            For files: loader-specific arguments
    """
    if debug_print:
        logger.info(f"Loading from {uri}")

    # If file=True, just get the local path
    if file:
        backend = get_backend_for_uri(str(uri))
        if backend is None:
            raise ValueError(f"No backend found for URI: {uri}")
        if not isinstance(backend, HTTPBackend):
            _raise_if_unsupported_non_http_download_kwargs(kwargs, "are")
        local_path = backend.download(str(uri), **kwargs)
        return _resolve_downloaded_path(local_path)

    if _is_http_uri(uri):
        backend = get_backend_for_uri(str(uri))
        if not isinstance(backend, HTTPBackend):
            raise ValueError(f"No HTTP backend found for URI: {uri}")
        download_kwargs, loader_kwargs = _split_http_download_kwargs(kwargs)
        local_path = backend.download(str(uri), **download_kwargs)
        return _load_from_local_path(local_path, loader_config=loader_kwargs)

    # Use the loader router to handle both dataset and file loading
    return load_data(uri, loader_config=kwargs)


def saves(
    data: Any,
    uri: Union[str, Path],
    debug_print: bool = True,
    create_dir: bool = True,
    **kwargs,
) -> None:
    """Save data to a file or dataset.

    For HuggingFace URIs:
    - hf://owner/repo => saves as dataset
    - hf://owner/repo/path/to/file.ext => saves as file

    Args:
        data: Data to save
        uri: Path or URI to save to
        debug_print: Whether to print debug info
        create_dir: Whether to create parent directories for local file paths
        **kwargs: Additional arguments passed to loader
            For HF datasets: split, private, etc.
            For files: loader-specific arguments
    """
    if debug_print:
        logger.info(f"Saving to {uri}")

    if create_dir and "://" not in str(uri):
        Path(uri).expanduser().parent.mkdir(parents=True, exist_ok=True)

    # Get the appropriate loader
    loader = get_loader_for_path(uri)
    if loader is None:
        raise ValueError(f"No loader found for path: {uri}")

    # Save using the loader (it will handle both dataset and file cases)
    loader.save(uri, data, loader_config=kwargs)


def to_df(
    data: Any,
    dict_key_column: str = "DICT_KEY",
    value_column: str = "VALUE",
    flatten_sep: str = "__",
    max_depth: int = 2,
) -> pd.DataFrame:
    """Convert JSON-like input to a pandas DataFrame.

    Supports dict, list of dicts, list of scalars, or a DataFrame.
    """
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, (dict, list, tuple)):
        return coerce_json_like_to_df(
            data,
            dict_key_column=dict_key_column,
            value_column=value_column,
            flatten_sep=flatten_sep,
            max_depth=max_depth,
        )
    raise ValueError("to_df expects a dict, list/tuple, or DataFrame")


def ls(
    uri: Union[str, Path, Iterable[Union[str, Path]]],
    exts: Optional[List[str]] = None,
    relative_unix: bool = False,
    debug_print: bool = True,
    **kwargs,
) -> list[str]:
    """List files in one or more directories or datasets."""
    include_extensions = kwargs.pop("include_extensions", None)
    if include_extensions is not None:
        warnings.warn(
            "`include_extensions` is deprecated; use `exts` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        exts = include_extensions

    if isinstance(uri, Mapping):
        raise TypeError("uri must be a string, Path, or iterable of strings/Paths.")

    if not isinstance(uri, (str, bytes, Path)) and isinstance(uri, Iterable):
        files = []
        for item in uri:
            files.extend(
                ls(
                    item,
                    exts=exts,
                    relative_unix=relative_unix,
                    debug_print=debug_print,
                    **kwargs,
                )
            )
        return files

    if debug_print:
        logger.info(f"Listing contents of {uri}")

    # Get the appropriate backend
    backend = get_backend_for_uri(str(uri))
    if backend is None:
        raise ValueError(f"No backend found for URI: {uri}")

    # List the files
    return backend.ls(str(uri), exts=exts, relative_unix=relative_unix, debug_print=debug_print, **kwargs)


def concurrent_loads(
    uris_list: List[Union[str, Path]],
    num_workers: int = 8,
    file: bool = False,
    debug_print: bool = True,
    **kwargs,
) -> List[Any]:
    """Load multiple files concurrently.

    For pure HTTP/HTTPS batches, this uses a thread pool because the workload is
    dominated by network I/O. Other URI types keep the existing process-based
    behavior. For HTTP/HTTPS batches with `file=True`, pass `target_dir` to
    save downloads into a specific directory.
    """
    uris = [str(uri) for uri in uris_list]
    results = [None] * len(uris_list)
    all_http = bool(uris) and all(_is_http_uri(uri) for uri in uris)

    if file and not all_http:
        _raise_if_unsupported_non_http_download_kwargs(kwargs, "are")

    if all_http and file:
        backend = HTTPBackend()
        downloaded = backend.download_many(uris, num_workers=num_workers, debug_print=debug_print, **kwargs)
        results = [_resolve_downloaded_path(path) if path is not None else None for path in downloaded]
        missing = sum(path is None for path in results)
        if missing > 0:
            logger.warning(f"{missing} loads returned None.")
        return results

    executor_cls = ThreadPoolExecutor if all_http else ProcessPoolExecutor
    with executor_cls(max_workers=num_workers) as executor:
        partial_load = partial(loads, file=file, debug_print=False, **kwargs)
        future_to_idx = {executor.submit(partial_load, uri): i for i, uri in enumerate(uris)}

        if debug_print:
            futures_iter = tqdm(as_completed(future_to_idx), total=len(uris), desc="Loading concurrent")
        else:
            futures_iter = as_completed(future_to_idx)

        for future in futures_iter:
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error(f"Exception reading {uris[idx]}: {e}")

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


def presigns(s3_uri: str | list[str], expiration: int = 604800) -> str:
    """Generate a presigned URL for an S3 URI."""
    global s3_client
    if s3_client is None:
        s3_client = S3Client()

    if isinstance(s3_uri, list):
        return [s3_client.generate_presigned_uri(uri, expiration=expiration) for uri in s3_uri]

    return s3_client.generate_presigned_uri(s3_uri, expiration=expiration)
