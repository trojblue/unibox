# backend_router.py
from .base_backend import BaseBackend
from .local_backend import LocalBackend
from .s3_backend import S3Backend
# from .hf_backend import HuggingFaceBackend  # if you have it
from unibox.utils.utils import is_s3_uri, is_hf_uri, is_url

def get_backend_for_uri(uri: str) -> BaseBackend:
    if is_s3_uri(uri):
        return S3Backend()
    # elif is_hf_uri(uri):
    #     return HuggingFaceBackend()
    elif is_url(uri):
        # Possibly treat URL as a “local” after http download or a new “HTTPBackend”
        # Or just do your logic outside
        return LocalBackend()
    else:
        # Assume local
        return LocalBackend()
