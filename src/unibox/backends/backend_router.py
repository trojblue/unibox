# unibox/backends/backend_router.py
from unibox.utils.utils import is_hf_uri, is_s3_uri, is_url

from .base_backend import BaseBackend
from .hf_hybrid_backend import HuggingfaceHybridBackend
from .http_backend import HTTPBackend
from .local_backend import LocalBackend
from .s3_backend import S3Backend


def get_backend_for_uri(uri: str) -> BaseBackend:
    """Get the appropriate backend for the given URI.

    Args:
        uri (str): The URI to check. Can be a local path, S3 URI, Hugging Face URI, or URL.
    """
    if is_s3_uri(uri):
        return S3Backend()

    if is_hf_uri(uri):
        return HuggingfaceHybridBackend()

    if is_url(uri):
        # Use HTTPBackend for HTTP/HTTPS URLs
        return HTTPBackend()

    return LocalBackend()
