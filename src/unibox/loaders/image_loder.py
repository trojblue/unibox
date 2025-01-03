from pathlib import Path

from PIL import Image

from .base_loader import BaseLoader


class ImageLoader(BaseLoader):
    """Load and (optionally) save images using PIL."""

    def load(self, file_path: Path) -> Image.Image:
        with Image.open(file_path) as img:
            # Return the loaded image object (still efficient, no copy needed)
            return img

    def save(self, file_path: Path, data: Image.Image) -> None:
        # Ensure the image is loaded in memory
        if data.fp is not None:
            data.load()
        data.save(file_path)
