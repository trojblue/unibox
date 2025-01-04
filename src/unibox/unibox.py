# ub.py
import os
import timeit
from pathlib import Path
from typing import Any, Union

from .backends.backend_router import LocalBackend, get_backend_for_uri
from .backends.hf_backend import HuggingFaceBackend
from .loaders.loader_router import get_loader_for_suffix
from .utils.globals import GLOBAL_TMP_DIR
from .utils.logger import UniLogger

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


def ls(uri: Union[str, Path]) -> list[str]:
    backend = get_backend_for_uri(str(uri))
    return backend.ls(str(uri))
