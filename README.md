# unibox

![Python](https://img.shields.io/badge/python-3.8-blue.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg) 
[![PyPI Version](https://img.shields.io/pypi/v/unibox.svg)](https://pypi.python.org/pypi/unibox)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

unibox provides unified interface for common file operations.



## Quick Start

```python
# pip install unibox
import unibox as ub
```

some common use cases of unibox includes:

<br>

**loading various file types in the same way:**

- supports json, txt, images, parquet, csv, feather, ....
- uses appropriate best practices (such as `orjson` package for json) for speed ups

```python
some_dict = ub.loads("some_file.json")    # json → dict
some_list = ub.loads("some_file.txt")     # txt  → list[str]
some_img  = ub.loads("some_image.jpg")    # webp/jpg/png/..etc → PIL.Image
some_df   = ub.loads("some_data.parquet") # parquet/csv/feather → pd.Dataframe
# .... for more: see uni_loader.py#L40
```

<br>

**saving various python data structure in the same way**:

- similar as `ub.loads` but also for saving files

```python
# mostly similar as above
ub.saves(some_dict, "some_file.json")
ub.saves(some_df, "some_df.parquet")
```

<br>

**list s3 or local directories in the same way:**

- default optional params: `relative_unix=True, debug_print=True`
- optimized `s3 ls` speed compared to boto3 

```python
files_under_dir = ub.traverses("/home/ubuntu/data")  # list local file

# needs to have `aws configure` pre-configured
files_under_s3  = ub.traverses("s3://dataset-pixiv/resized_1572864") # list s3 files
```

<br>

**simplified logger class for easier debug**:

- a logger with functionalities pre-configured
- includes caller frame info, emoji warnings, datetime, and more

```python
logger = ub.UniLogger()
logger.info("....") 
logger.warn("....")
logger.error("....")
```

<br>

**resizing millions of images efficiently**:

- (pre-configured omitted here for simplicity)
- also able to resize by minimum or maximum of side lengths,

```python
# Initialize resizer
resizer = ub.UniResizer(root_dir, dst_dir,
    target_pixels=int(1024 * 1024 * 1.5),
)

# Resize the images
images_to_resize = resizer.get_resize_jobs()
resizer.execute_resize_jobs(images_to_resize)
```



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



## [OLD DOC] Features

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
- `unibox.saves(data, filepath)`: saves arbitrary data to a file, with automatic detection of file type

