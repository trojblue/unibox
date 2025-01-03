# unibox

[![ci](https://github.com/trojblue/unibox/workflows/ci/badge.svg)](https://github.com/trojblue/unibox/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://trojblue.github.io/unibox/)
[![pypi version](https://img.shields.io/pypi/v/unibox.svg)](https://pypi.org/project/unibox/)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#unibox:gitter.im)

unibox provides unified interface for common file operations

## Installation

```bash
pip install unibox
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv tool install unibox
```

If you're not using python 3.13, it's also recommended to install pandas[performance]:

```bash
pip install "pandas[performance]"
```


to update or remove project dependencies:

```bash

uv add requests

uv remove requests

# after adding new package: rerun
make setup
```

to get a coverage report, run:
```bash
pytest --cov=src/unibox --cov-report=term-missing tests
```