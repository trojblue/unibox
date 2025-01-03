# ub.py
from pathlib import Path
from typing import Any, Union
import pandas as pd
import timeit

from .utils.logger import UniLogger
from .backends.backend_router import get_backend_for_uri, LocalBackend
from .backends.hf_backend import HuggingFaceBackend
from .loaders.loader_router import get_loader_for_suffix

logger = UniLogger()

def _get_type_info(obj: Any) -> str:
    obj_module, obj_name = type(obj).__module__, type(obj).__name__
    return str(obj_module), str(obj_name)

def loads(uri: Union[str, Path], debug_print:bool=True, **kwargs) -> Any:
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
        loader = None # to work with debug print
        res = backend.load_dataset(repo_id, split="train")

    else:
        # Otherwise, do the normal "download + suffix-based loader" approach:
        local_path = backend.download(str(uri))  # returns Path
        suffix = local_path.suffix.lower()
        loader = get_loader_for_suffix(suffix)
        if loader is None:
            raise ValueError(f"No loader found for {suffix}")
        
        # res = loader.load(local_path, **kwargs)
        res = loader.load(local_path)

    end_time = timeit.default_timer()
    if debug_print:
        backend_name = backend.__class__.__name__
        loader_name = loader.__class__.__name__ if loader else "None"
        res_module, res_name = _get_type_info(res)
        logger.info(f"{res_name} LOADED from \"{uri}\" in {end_time-start_time:.2f} seconds   [{backend_name}:{loader_name} -> {res_module}.{res_name}]")

    return res

def saves(data: Any, uri: Union[str, Path], debug_print:bool=True, **kwargs) -> None:
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
    # This is a special case for HF, but we can generalize it later.
    # For now, let's keep the logic consistent.
    elif isinstance(backend, HuggingFaceBackend) and suffix == "":
        if isinstance(data, pd.DataFrame):
            # If it's a DataFrame, we can upload it directly to HF as a dataset
            # without saving it to a local file first.
            # We can pass a dummy local_path or None
            backend.df_to_hub(data, str(uri))  

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
            backend.upload(temp_path, str(uri), data=data)
        else:
            # Possibly the user is doing "hf://myuser/myrepo" with no extension => entire dataset
            # We can pass a dummy local_path or None
            backend.upload(None, str(uri), data=data)
    
    end_time = timeit.default_timer()
    if debug_print:
        backend_name = backend.__class__.__name__
        loader_name = loader.__class__.__name__
        data_module, data_name = _get_type_info(data)
        logger.info(f"{data_name} saved successfully to \"{uri}\" in {end_time-start_time:.2f} seconds   [{data_module}.{data_name} -> {backend_name}:{loader_name}]")


def ls(uri: Union[str, Path]) -> list[str]:
    backend = get_backend_for_uri(str(uri))
    return backend.ls(str(uri))