# backend_router.py
from unibox.utils.utils import is_s3_uri, is_url, is_hf_uri
from .base_backend import BaseBackend
from .local_backend import LocalBackend
from .s3_backend import S3Backend
from .hf_backend import HuggingFaceBackend

def get_backend_for_uri(uri: str) -> BaseBackend:
    if is_s3_uri(uri):
        return S3Backend()
    elif is_hf_uri(uri):
        return HuggingFaceBackend()
    elif is_url(uri):
        # Possibly treat URL as local after download, or 
        # define an HTTPBackend. That depends on your design.
        return LocalBackend()
    else:
        return LocalBackend()
