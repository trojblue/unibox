# unibox

![Python](https://img.shields.io/badge/python-3.8-blue.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg) 
[![PyPI Version](https://img.shields.io/pypi/v/unibox.svg)](https://pypi.python.org/pypi/unibox)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

unibox provides unified interface for common file operations.

## Features

The package is designed to be running with python 3.10, but targets 3.8+ for compatibility:


**CLI**:
- `unibox resize <dir>`: resizes a directory of images using either `pillow` or `libvips`
  - customizable size / quality / encoding (png / webp / jpeg)
- `unibox copy <dir>`: an awscli-like tool for copying files with certain suffix to a new dir, keeping the same directory structure. 
  - bypasses windows explorer so it's much faster.
- `unibox move <dir>`: like `copy`, but moves instead

**utils**:
- `UniLogger`: uniformed logger class (`logger = unibox.UniLogger()`, and use `logger.info(...)`)
- `UniLoader`: uniformed data loader class (`unibox.loads(<filename>)`)
- `UniSaver`: uniformed data saver class (`unibox.saves(<data>, <filename>)`)
- `UniTraverser`: uniformed directory traverser class, with callbacks in multiple stages
- `UniResizer`: uniformed image resizer class, with callbacks in multiple stages

**callables**:
- `unibox.traverses(dir, include, exclude, relative_unix)`: traverse a directory using specified exclude / include extensions, and return a list of files
- `unibox.loads(filepath)`: load arbitrary data from a file into suitable formats, with automatic detection of file type
  - supported formats: see UniLoader class implementation
- `unibox.saves(data, filepath)`: save arbitrary data to a file, with automatic detection of file type

## Install

install from pypi:
```bash
pip install unibox
```

build from source:
```bash
git clone https://github.com/trojblue/unibox

# pip install poetry
poetry install
poetry build
pip install dist/unibox-<version number>.whl
```
