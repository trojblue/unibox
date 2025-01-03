# Loaders

naming convention: use `{extension}_loader.py`

each loader inherits from `base_loader.py` and implements:

```python
    def load(self, local_path: Path) -> Any:
        raise NotImplementedError

    def save(self, local_path: Path, data: Any) -> None:
        raise NotImplementedError
```