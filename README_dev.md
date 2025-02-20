## Dev Notes

To get a coverage report, run:

```bash
pytest --cov=src/unibox --cov-report=term-missing tests
```

To build the docs:

```bash
make docs host=0.0.0.0

# or in debug mode:
make check-docs
```

To manually release a new version (instead of `make release`):

```bash
# python -m pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```
