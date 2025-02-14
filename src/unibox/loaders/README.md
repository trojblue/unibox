# Loaders

naming convention: use `{extension}_loader.py`

each loader inherits from `base_loader.py` and implements:

```python
    def load(self, local_path: Path) -> Any:
        raise NotImplementedError

    def save(self, local_path: Path, data: Any) -> None:
        raise NotImplementedError
```


## Adding a new loader

1. Create a new file in `src/unibox/loaders/` with the name `{extension}_loader.py`
2. Implement the `load` and `save` methods
3. Add the loader to the `src/unibox/loaders/loader_router.py` file
4. test that the new loader works
