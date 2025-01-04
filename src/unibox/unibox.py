# ub.py
import os
import timeit
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from tqdm.auto import tqdm

from .backends.backend_router import LocalBackend, get_backend_for_uri
from .backends.hf_backend import HuggingFaceBackend
from .loaders.loader_router import get_loader_for_suffix
from .nb_helpers.uni_peeker import UniPeeker
from .utils.globals import GLOBAL_TMP_DIR
from .utils.logger import UniLogger
from .utils.s3_client import S3Client

s3_client = S3Client()

logger = UniLogger()


def _get_type_info(obj: Any) -> str:
    obj_module, obj_name = type(obj).__module__, type(obj).__name__
    return str(obj_module), str(obj_name)


def loads(uri: Union[str, Path], debug_print: bool = True, **kwargs) -> Any:
    start_time = timeit.default_timer()
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
        loader = None  # to work with debug print
        res = backend.load_dataset(repo_id, split="train")

    else:
        # Otherwise, do the normal "download + suffix-based loader" approach:

        # get a random directory name to download the file to, under the global temp directory
        rand_dir = GLOBAL_TMP_DIR / str(os.getpid())
        local_path = backend.download(str(uri), target_dir=rand_dir)  # returns Path
        suffix = local_path.suffix.lower()
        loader = get_loader_for_suffix(suffix)
        if loader is None:
            raise ValueError(f"No loader found for {suffix}")

        # res = loader.load(local_path, **kwargs)
        res = loader.load(local_path)

        if not isinstance(backend, LocalBackend):
            # remove the downloaded file if it's from remote;
            # could break if it's memory-mapped, like PIL or feather
            os.remove(local_path)

    end_time = timeit.default_timer()
    if debug_print:
        backend_name = backend.__class__.__name__
        loader_name = loader.__class__.__name__ if loader else "None"
        res_module, res_name = _get_type_info(res)
        # log_str = f'{res_name} LOADED from "{uri}" in {end_time-start_time:.2f} seconds\n    [{backend_name}:{loader_name} -> {res_module}.{res_name}]'
        log_str = f'{res_name} LOADED from "{uri}" in {end_time-start_time:.2f} seconds'
        logger.info(log_str)

    return res


def saves(data: Any, uri: Union[str, Path], debug_print: bool = True, **kwargs) -> None:
    start_time = timeit.default_timer()
    backend = get_backend_for_uri(str(uri))
    suffix = Path(uri).suffix.lower()
    loader = get_loader_for_suffix(suffix)

    if isinstance(backend, LocalBackend):
        # Save directly to final path
        if loader:
            loader.save(Path(uri), data)
        else:
            raise ValueError(f"No loader found for {suffix}")

    # BYPASS: if it's saving dataframe to a HF dataset (hf://username/repo_name with no extension)
    # We can skip the local file save and directly upload the dataset.
    # Internal logics are handled by the HF backend.
    elif isinstance(backend, HuggingFaceBackend) and suffix == "":
        backend.data_to_hub(data, str(uri))

    else:
        # Non-local backend (S3, HF, etc.)
        # If HF with no extension & data is DF => skip local file?
        # But let's keep consistent logic for now, we can pass it anyway.

        # If there's no loader (e.g. the user didn't provide an extension
        # for an HF dataset push?), loader might be None.
        # So let's handle that:
        import tempfile

        if loader is not None:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                temp_path = Path(tmp.name)
            # Save data to local
            loader.save(temp_path, data)
            # Upload
            backend.upload(temp_path, str(uri))
            os.remove(temp_path)
        else:
            raise ValueError(f"No loader found for {suffix}")

    end_time = timeit.default_timer()
    if debug_print:
        backend_name = backend.__class__.__name__
        loader_name = loader.__class__.__name__
        data_module, data_name = _get_type_info(data)
        # log_str = f'{data_name} saved successfully to "{uri}" in {end_time-start_time:.2f} seconds\n    [{data_module}.{data_name} -> {backend_name}:{loader_name}]'
        log_str = f'{data_name} saved successfully to "{uri}" in {end_time-start_time:.2f} seconds'
        logger.info(log_str)


def ls(
    uri: Union[str, Path],
    exts: Optional[List[str]] = None,
    relative_unix: bool = False,
    debug_print: bool = True,
    **kwargs,
) -> list[str]:
    backend = get_backend_for_uri(str(uri))
    return backend.ls(str(uri), exts=exts, relative_unix=relative_unix, debug_print=debug_print, **kwargs)


def concurrent_loads(uris_list, num_workers=8, debug_print=True):
    """Loads dataframes concurrently from a list of S3 URIs.

    :param uris_list: list of S3 URIs (or local) to load
    :param num_workers: int, number of concurrent workers
    :param debug_print: bool, whether to print debug information or not
    :return: list of loaded dataframes

    >>> selected_uris = [f"{base_s3_uri}/{i}.merged.parquet" for i in selected_ids]
    >>> dfs = concurrent_loads(selected_uris, num_workers)
    >>> df = pd.concat(dfs, ignore_index=True)
    """
    results = [None] * len(uris_list)  # Initialize a list to store results in correct order
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Use partial to bind debug_print
        partial_loads = partial(loads, debug_print=False)
        future_to_index = {executor.submit(partial_loads, uri): idx for idx, uri in enumerate(uris_list)}

        if debug_print:
            futures_iter = tqdm(
                as_completed(future_to_index),
                total=len(uris_list),
                desc="Loading batches",
                mininterval=3,
            )
        else:
            futures_iter = as_completed(future_to_index)

        for future in futures_iter:
            idx = future_to_index[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"Exception for {uris_list[idx]}: {e}")

    # Filter out any None values if there were exceptions
    empty_count = results.count(None)
    if empty_count > 0:
        logger.warning(f"{empty_count} loadings FAILED and were returned as None")
    # results = [res for res in results if res is not None]

    return results


def traverses(
    uri: Union[str, Path],
    exts: Optional[List[str]] = None,
    relative_unix: bool = False,
    debug_print: bool = True,
    **kwargs,
) -> list[str]:
    """Old name for `ls`, depreciated and kept for compatibility"""
    warnings.warn(
        "`traverses()` is deprecated and WILL BE REMOVED by May.1 2025; use `ls` instead.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    return ls(uri, exts=exts, relative_unix=relative_unix, debug_print=debug_print, **kwargs)


# ===== Other handy tools =====


def peeks(data: Any, n=3, console_print=False) -> Dict[str, Any]:
    """Peeks into arbitrary data using UniPeeker.peeks() method.
    :param data: The data to peek into.
    :param n: The number of entries to peek into.
    :param console_print: Whether to print the peeked information to the console.
    :return: A dictionary containing the metadata and the preview of the data.

    Example:
    >>> json_dict = {"name": "John", "age": 30}
    >>> peeked_dict = peeks(json_dict)
    >>> json_dict_list = [{"name": "John", "age": 30}, {"name": "Doe", "age": 40}]
    >>> peeked_dict_list = peeks(json_dict_list)
    >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    >>> peeked_df = peeks(df)
    """
    peeker = UniPeeker(n, console_print)
    return peeker.peeks(data)


# from .utils.ipython_utils import gallery
try:
    from .nb_helpers.ipython_utils import gallery, label_gallery
except (ImportError, ModuleNotFoundError):
    print("IPython is not available. Gallery function will not work.")

    def gallery(
        paths: list[str],
        labels: list[str] = [],
        row_height="300px",
        num_workers=32,
        debug_print=True,
        thumbnail_size: int = 512,
    ):
        print("IPython is not available. Gallery function will not work.")

    def label_gallery(
        paths: list[str],
        labels: list[str] = [],
        row_height="150px",
        num_workers=32,
        debug_print=True,
        thumbnail_size: int = 512,
    ):
        print("IPython is not available. Gallery function will not work.")


def presigns(s3_uri: str, expiration: Union[int, str] = "1d") -> str:
    """Generate a presigned URL from a given S3 URI.
    :param s3_uri: S3 URI (e.g., 's3://bucket-name/object-key')
        :param expiration: Time in seconds for the presigned URL to remain valid (default: 1 day).
                        Accepts either an integer (seconds) or human-readable strings like "1d", "1mo", "1y".
    :return: Presigned URL as string. If error, returns None.
    """
    return s3_client.generate_presigned_uri(s3_uri, expiration=expiration)
