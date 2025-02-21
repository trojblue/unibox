# unibox.py
import os
import tempfile
import timeit
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd  # <--- you'll need this import if not present
from tqdm.auto import tqdm

from .backends.backend_router import get_backend_for_uri
from .backends.local_backend import LocalBackend
from .loaders.loader_router import get_loader_for_suffix
from .utils.df_utils import generate_dataset_readme
from .utils.globals import GLOBAL_TMP_DIR
from .utils.logger import UniLogger
from .utils.s3_client import S3Client

s3_client = S3Client()
logger = UniLogger()


def _get_type_info(obj: Any) -> str:
    obj_module, obj_name = type(obj).__module__, type(obj).__name__
    return str(obj_module), str(obj_name)


### CHANGED ###
def _parse_hf_uri(uri: str):
    # likely duplicate of hf_datasets_backend.py impl
    """Args:
        uri: A URI in the format 'hf://owner/repo/some_file', or 'hf://owner/repo' for a dataset.

    Returns:
        repo_id: The repo ID 'owner/repo' from 'hf://owner/repo/...'.
        subpath: The remaining part ('' if None or some_file)
    """
    trimmed = uri.replace("hf://", "", 1)
    parts = trimmed.split("/", 2)  # Split into at most three parts
    if len(parts) < 2:
        raise ValueError(f"Invalid Hugging Face URI format: {uri}")

    repo_id = f"{parts[0]}/{parts[1]}"  # First two parts make up the repo ID
    subpath = parts[2] if len(parts) > 2 else ""  # Remaining part is the subpath

    return repo_id, subpath


def load_file(uri: Union[str, Path], debug_print: bool = True, **kwargs) -> str:
    """Return a local file path (downloading if needed) without parsing."""
    import os
    import timeit

    start_time = timeit.default_timer()
    uri_str = str(uri)
    backend = get_backend_for_uri(uri_str)

    if isinstance(backend, LocalBackend):
        local_path = Path(uri_str).absolute()
    else:
        rand_dir = GLOBAL_TMP_DIR / str(os.getpid())
        rand_dir.mkdir(parents=True, exist_ok=True)
        local_path = backend.download(uri_str, target_dir=rand_dir)

    end_time = timeit.default_timer()
    if debug_print:
        logger.info(f'File available at "{local_path}" in {end_time - start_time:.2f}s')
    return str(local_path)


def loads(uri: Union[str, Path], file: bool = False, debug_print: bool = True, **kwargs) -> Any:
    """Loads data from a given URI.
    If file=True, just returns the local path, no parsing.
    Otherwise:
      - If HF with no subpath => treat as entire dataset => .load_dataset()
      - Else do normal "download then suffix-based loader."

    some kwargs:
        split: str = "train"  (for HF dataset load)
        streaming: bool = False  (for HF dataset load)
    """
    if file:
        return load_file(uri, debug_print=debug_print, **kwargs)

    start_time = timeit.default_timer()
    uri_str = str(uri)
    backend = get_backend_for_uri(uri_str)

    ### CHANGED - HuggingFace dataset logic ###
    if uri_str.startswith("hf://"):
        repo_id, subpath = _parse_hf_uri(uri_str)
        # If there's no subpath, that means "hf://owner/repo" => dataset
        if not subpath:
            # call backend.load_dataset
            # requires that the backend is our HF Router or old HFBackend
            # We'll assume it implements .load_dataset
            # here: split, streaming is passed into load_dataset
            res = (
                backend.ds_backend.load_dataset(repo_id, **kwargs)
                if hasattr(backend, "ds_backend")
                else backend.load_dataset(repo_id, **kwargs)
            )
            # done
            end_time = timeit.default_timer()
            if debug_print:
                mod, cls = _get_type_info(res)
                logger.info(f'{cls} LOADED from "{uri_str}" in {end_time - start_time:.2f}s')
            return res
        # else we fall back to the normal "download + suffix loader" below

    # Normal approach: download => loader => parse
    rand_dir = GLOBAL_TMP_DIR / str(os.getpid())
    rand_dir.mkdir(parents=True, exist_ok=True)
    if isinstance(backend, LocalBackend):
        local_path = Path(uri_str)
    else:
        local_path = backend.download(uri_str, target_dir=rand_dir)

    suffix = local_path.suffix.lower()
    loader = get_loader_for_suffix(suffix)
    if loader is None:
        raise ValueError(f"No loader found for suffix: {suffix}")

    res = loader.load(local_path, **kwargs)

    # if remote => remove temp
    if not isinstance(backend, LocalBackend):
        try:
            os.remove(local_path)
        except OSError:
            pass

    end_time = timeit.default_timer()
    if debug_print:
        mod, cls = _get_type_info(res)
        logger.info(f'{cls} LOADED from "{uri_str}" in {end_time - start_time:.2f}s')

    return res


def saves(data: Any, uri: Union[str, Path], debug_print: bool = True, **kwargs) -> None:
    """Saves data to local or remote. Special-case:
    - If HF with no extension => interpret as dataset push
    - Otherwise, do suffix-based local or single-file approach

    some kwargs:
        split: str = "train"  (for HF dataset push)
        private: bool = True  (for HF dataset push)
    """
    start_time = timeit.default_timer()
    uri_str = str(uri)
    backend = get_backend_for_uri(uri_str)
    suffix = Path(uri_str).suffix.lower()

    # 1) The HF dataset push block
    if uri_str.startswith("hf://") and suffix == "":
        # Means something like "hf://owner/repo" => push entire dataset
        repo_id, _ = _parse_hf_uri(uri_str)

        # if hasattr(backend, "ds_backend"):
        # If router-based, do: ds_backend.data_to_hub
        dataset_split = kwargs.get("split", "train")
        backend.ds_backend.data_to_hub(
            data,
            repo_id=repo_id,
            private=kwargs.get("private", True),
            split=dataset_split,
        )
        # else:
        #     print("OLD STYLE; code removed; see version ~0.7")

        # 2) (NEW) Update README in the HF repo, overwriting any existing version.
        #    We'll assume the new method is on "api_backend" or the router has an "api_backend".
        #    If your `backend` is a HuggingFaceRouterBackend, you have `backend.api_backend`.
        #    Or you can just instantiate a new HuggingFaceApiBackend() directly here.
        #    We'll do: backend.api_backend.update_readme(...).
        #    Also, only do this if data is a DataFrame (so we can do len, columns, etc.)

        if isinstance(data, pd.DataFrame):
            readme_text = generate_dataset_readme(data, repo_id, backend)
            backend.api_backend.update_readme(repo_id, readme_text, repo_type="dataset")

        # End-of-process for HF dataset push
        end_time = timeit.default_timer()
        if debug_print:
            _, data_cls = _get_type_info(data)
            logger.info(f'{data_cls} saved (HF dataset) to "{uri_str}" in {end_time - start_time:.2f}s')
        return

    # Otherwise, the existing logic for normal single-file suffix-based saving:
    loader = get_loader_for_suffix(suffix)
    if loader is None:
        raise ValueError(f"No loader found for extension {suffix}")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmpf:
        temp_path = Path(tmpf.name)

    try:
        loader.save(temp_path, data)
        backend.upload(temp_path, uri_str)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    end_time = timeit.default_timer()
    if debug_print:
        _, data_cls = _get_type_info(data)
        logger.info(f'{data_cls} saved to "{uri_str}" in {end_time - start_time:.2f}s')


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


def peeks(data: Any, n=3, console_print=False) -> Dict[str, Any]:
    peeker = UniPeeker(n, console_print)
    return peeker.peeks(data)


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
