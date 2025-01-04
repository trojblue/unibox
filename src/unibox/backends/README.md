# Backends

A `backend` interacts with the underlying file system to handle file operations. Currently it could be either local (no change), S3 (posix-like), or Huggingface 

Huggingface is designed to be duplex: 
- `hf:user/repo` as dataframe store
- or `hf:user/repo/file.ext` as posix-like (not implemented yet)

A backend implements a `BaseBackend`:

```python

class BaseBackend:
    """Interface for storage backends (local, S3, etc.)."""

    def download(self, uri: str, target_dir: str = None) -> Path:
        """Download the resource identified by `uri` to a local temp path. Return local Path."""
        raise NotImplementedError

    def upload(self, local_path: Path, uri: str) -> None:
        """Upload local_path to the specified `uri`."""
        raise NotImplementedError

    def ls(
        self,
        uri: str,
        exts: Optional[List[str]] = None,
        relative_unix: bool = False,
        debug_print: bool = True,
        **kwargs,
    ) -> List[str]:
        """List files under `uri` with optional extension filtering."""
        raise NotImplementedError
```

