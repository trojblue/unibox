import os
from urllib.parse import urlparse
def to_relaive_unix_path(absolute_path:str, root_dir:str, convert_slash=True):
    relative_path = os.path.relpath(absolute_path, root_dir)
    if convert_slash:
        relative_path = relative_path.replace("\\", "/")
    return relative_path


def is_s3_uri(uri: str) -> bool:
    """Check if the URI is an S3 URI."""
    parsed = urlparse(uri)
    return parsed.scheme == 's3'

def is_url(path: str) -> bool:
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except:
        return False