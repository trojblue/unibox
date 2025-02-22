from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Union

from PIL import Image

from .base_loader import BaseLoader

if TYPE_CHECKING:
    import numpy as np


class ImageLoader(BaseLoader):
    """Load and save images using PIL."""

    SUPPORTED_LOAD_CONFIG = {
        "mode",  # str: Mode to convert image to (e.g., 'RGB', 'L')
        "size",  # Tuple[int, int]: Size to resize to
        "as_array",  # bool: Convert to numpy array
    }

    SUPPORTED_SAVE_CONFIG = {
        "format",  # str: Image format (e.g., 'PNG', 'JPEG')
        "quality",  # int: JPEG quality (1-95)
        "optimize",  # bool: Whether to optimize
        "dpi",  # Tuple[int, int]: DPI setting
    }

    def load(self, file_path: Path, loader_config: Optional[Dict[str, Any]] = None) -> Union[Image.Image, "np.ndarray"]:
        """Load an image with optional configuration.

        Args:
            file_path (Path): Path to the image file
            loader_config (Optional[Dict]): Configuration options for image loading

        Returns:
            Union[Image.Image, np.ndarray]: The loaded image
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Load the image
        img = Image.open(file_path)

        # Handle mode conversion
        if "mode" in config:
            img = img.convert(config["mode"])
            used_keys.add("mode")

        # Handle resizing
        if "size" in config:
            img = img.resize(config["size"])
            used_keys.add("size")

        # Handle numpy conversion
        if config.get("as_array", False):
            import numpy as np

            img = np.array(img)
            used_keys.add("as_array")

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "ImageLoader")

        return img

    def save(self, file_path: Path, data: Image.Image, loader_config: Optional[Dict[str, Any]] = None) -> None:
        """Save an image with optional configuration.

        Args:
            file_path (Path): Where to save the image
            data (Image.Image): Image to save
            loader_config (Optional[Dict]): Configuration options for image saving
        """
        config = loader_config or {}
        used_keys: Set[str] = set()

        # Ensure the image is loaded in memory
        if data.fp is not None:
            data.load()

        # Extract supported arguments from config
        kwargs = {}
        for key in self.SUPPORTED_SAVE_CONFIG:
            if key in config:
                kwargs[key] = config[key]
                used_keys.add(key)

        # Warn about unused config options
        self._warn_unused_config(config, used_keys, "ImageLoader")

        data.save(file_path, **kwargs)
