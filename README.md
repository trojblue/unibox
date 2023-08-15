# Unibox

![Python](https://img.shields.io/badge/python-3.10-blue.svg) 
[![PyPI Version](https://img.shields.io/pypi/v/unibox.svg)](https://pypi.python.org/pypi/unibox)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Unibox is a tool that aims to provide a unified interface for various common daily operations.

## Features

**CLI**:
- `unibox resize <dir>`: resizes a directory of images using either `pillow` or `libvips`
  - customizable size / quality / encoding (png / webp / jpeg)
- `unibox copy <dir>`: an awscli-like tool for copying files with certain suffix to a new dir, keeping the same directory structure. 
  - bypasses windows explorer so it's much faster.
- `unibox move <dir>`: like `copy`, but moves instead

**utils**:
- `UniLogger`: uniformed logger class
- `UniLoader`: uniformed data loader class (`unibox.loads(<any file>)`)
- `UniSaver`: uniformed data saver class (`unibox.saves(<any file>)`)
- `UniTraverser`: uniformed directory traverser class, with 

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
