"""unibox package.

unibox provides unified interface for common file operations
"""

from __future__ import annotations

__all__: list[str] = []

from .utils.constants import *
from .utils.logger import UniLogger
from .unibox import loads, ls, saves
