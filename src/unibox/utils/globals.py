"""create a global temporary directory that is cleaned up when the program exits.

When accessing files that's not local, they have to be downloaded first;

having a global temporary dir ensures that the files can be properly cleaned up when the program exits.

"""

import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Define a fixed name for the temporary directory
_default_tmp_dir = Path(tempfile.gettempdir()) / "unibox_temp"
GLOBAL_TMP_DIR = Path(os.environ.get("UNIBOX_TEMP_DIR", _default_tmp_dir))
print(f"Using global temporary directory: {GLOBAL_TMP_DIR}")

# cleanup previous runs
# shutil.rmtree(GLOBAL_TMP_DIR, ignore_errors=True)

# Create the directory if it doesn't exist
GLOBAL_TMP_DIR.mkdir(parents=True, exist_ok=True)

# @atexit.register
# def cleanup_global_tmp_dir():
#     shutil.rmtree(GLOBAL_TMP_DIR, ignore_errors=True)
