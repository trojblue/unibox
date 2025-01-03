from pathlib import Path

from PIL import Image

from .base_loader import BaseLoader


class ImageLoader(BaseLoader):
    """Load and (optionally) save images using PIL."""

    def load(self, file_path: Path) -> Image.Image:
        return Image.open(file_path)

    def save(self, file_path: Path, data: Image.Image) -> None:
        # Ensure the image is loaded in memory
        if data.fp is not None:
            data.load()
        data.save(file_path)
