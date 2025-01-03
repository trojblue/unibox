# backend_router.py
from unibox.utils.utils import is_hf_uri, is_s3_uri, is_url

from .base_backend import BaseBackend
from .hf_backend import HuggingFaceBackend
from .local_backend import LocalBackend
from .s3_backend import S3Backend


def get_backend_for_uri(uri: str) -> BaseBackend:
    if is_s3_uri(uri):
        return S3Backend()
    if is_hf_uri(uri):
        return HuggingFaceBackend()
    if is_url(uri):
        # Possibly treat URL as local after download, or
        # define an HTTPBackend. That depends on your design.
        return LocalBackend()
    return LocalBackend()
