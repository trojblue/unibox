# unibox/backends/backend_router.py

from unibox.utils.utils import is_hf_uri, is_s3_uri, is_url

from .base_backend import BaseBackend
from .hf_router_backend import HuggingFaceRouterBackend
from .local_backend import LocalBackend
from .s3_backend import S3Backend


def get_backend_for_uri(uri: str) -> BaseBackend:
    if is_s3_uri(uri):
        return S3Backend()
    if is_hf_uri(uri):
        # Our new router that delegates between dataset or single-file
        return HuggingFaceRouterBackend()
    if is_url(uri):
        # Possibly define an HTTPBackend or just treat as local after manual download
        return LocalBackend()
    return LocalBackend()
