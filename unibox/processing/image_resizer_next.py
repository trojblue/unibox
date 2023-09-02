import os
import math
import shutil
from PIL import Image
from pathlib import Path
from tqdm.auto import tqdm

import unibox
from unibox import UniLoader

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple


class ImageResizer:
    # value to which the shorter side will be rounded down after scaling
    TRUNCATE_MULTIPLIER = 32
    WEBP_QUALITY = 98
    EXTENSION = ".webp"  # file extension (.webp)

    def __init__(self, root_dir: str, dst_dir: str,
                 min_dim: int = None, max_dim: int = None, target_pixels: int = None,
                 keep_hierarchy: bool = True, ):
        """
        :param min_dim: minimum dimension of the shorter side
        :param max_dim: maximum dimension of the longer side (higher priority than min_dim)
        :param target_pixels: target number of pixels (truncate short side to a multiple of TRUNCATE_MULTIPLIER; higher priority than max_dim)
        """
        self.root_dir = root_dir
        self.dst_dir = dst_dir

        self.min_dim = min_dim
        self.max_dim = max_dim
        self.target_pixels = target_pixels
        self.keep_hierarchy = keep_hierarchy
        pass

    @staticmethod
    def _get_new_dimensions(width: int, height: int, target_side: int, resize_by_longer_side: bool = False) -> tuple:
        """
        Calculates new dimensions based on the target for either the shorter or longer side while maintaining aspect ratio.

        :param width: original width of the image
        :param height: original height of the image
        :param target_side: target dimension for the side specified
        :param resize_by_longer_side: if True, resize by longer side; otherwise, by shorter side
        :return: tuple containing new dimensions (new_width, new_height)
        """
        if target_side == -1:
            return int(width), int(height)

        if any(x <= 0 or type(x) != int for x in [width, height, target_side]):
            raise ValueError("width, height and target_side must be positive integers")

        # Determine shorter and longer side
        shorter_side, longer_side = min(width, height), max(width, height)

        if resize_by_longer_side:
            target_longer_side = target_side
            new_longer_side = target_longer_side
            new_shorter_side = round(new_longer_side * (shorter_side / longer_side))
        else:
            target_shorter_side = target_side
            new_shorter_side = target_shorter_side
            new_longer_side = round(new_shorter_side * (longer_side / shorter_side))

        # Assign new dimensions based on original orientation (portrait or landscape)
        if width > height:
            return new_longer_side, new_shorter_side
        else:
            return new_shorter_side, new_longer_side

    def _get_dst_path(self, og_rel_image_path: str, create_dir: bool = True) -> Path:
        """
        :param og_rel_image_path: original relative image path
        :param create_dir: if True, create the destination directory if it doesn't exist
        """
        assert self.EXTENSION.startswith(".") and self.EXTENSION != ".", "extension must start with a dot"

        og_rel_path = Path(og_rel_image_path)
        rel_resized_path = og_rel_path.with_name(f"{og_rel_path.stem}_resized{self.EXTENSION}")

        if self.keep_hierarchy:
            dst_file_path = Path(self.dst_dir) / rel_resized_path
            if create_dir:
                dst_file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            dst_file_path = Path(self.dst_dir) / rel_resized_path.name

        return dst_file_path

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        输入PIL Image对象，输出resize之后的 PIL Image

        :param image: PIL.Image.Image object to be resized
        :return: PIL.Image.Image object after resizing
        """

        width, height = image.size
        new_width, new_height = width, height

        # Define the need_resize variable
        need_resize = (self.min_dim is not None and min(width, height) < self.min_dim) or \
                      (self.max_dim is not None and max(width, height) > self.max_dim)

        # Priority 1: Resize based on target_pixels
        if self.target_pixels is not None:
            scale_factor = math.sqrt(self.target_pixels / (width * height))
            target_shorter_side = round(
                (min(width, height) * scale_factor) // self.TRUNCATE_MULTIPLIER) * self.TRUNCATE_MULTIPLIER
            new_width, new_height = self._get_new_dimensions(width, height, target_shorter_side)

        # Priority 2: Resize based on max_dim
        elif self.max_dim is not None and need_resize:
            new_width, new_height = self._get_new_dimensions(width, height, self.max_dim, resize_by_longer_side=True)

        # Priority 3: Resize based on min_dim
        elif self.min_dim is not None and need_resize:
            new_width, new_height = self._get_new_dimensions(width, height, self.min_dim)

        # If resizing is not needed, return the original image
        elif not need_resize:
            return image

        # Perform the resize operation
        return image.resize((new_width, new_height), Image.LANCZOS)

    def _resize_single_image_task(self, og_rel_image_path: str) -> None:
        loader = UniLoader(debug_print=False)
        image = loader.loads(os.path.join(self.root_dir, og_rel_image_path))
        image = self._resize_image(image)

        # Handle save path
        dst_file_path = self._get_dst_path(og_rel_image_path)

        # Save
        try:
            with open(dst_file_path, "wb") as f:
                image.save(f, "webp", quality=95)
        except OSError:
            print(f"Error saving image {dst_file_path}. Skipping...")

    def _execute_resize_tasks(self, tasks: List[Tuple]):
        """
        Execute tasks using ProcessPoolExecutor
        """
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(task, *args) for task, *args in tasks]
            list(tqdm(as_completed(futures), total=len(tasks), desc="Resizing images"))

    def resizer_sketch(self):

        image_files = unibox.traverses(self.root_dir, include_extensions=unibox.constants.IMG_FILES, relative_unix=True)

        tasks = [(self._resize_single_image_task, og_rel_image_path) for og_rel_image_path in image_files]

        self._execute_resize_tasks(tasks)



if __name__ == '__main__':
    root_dir = r"E:\_benchmark\1k"
    dst_dir = r"E:\_benchmark\1k_resized"

    min_dim = 512
    max_dim = int(1024 * 3)
    target_pixels = int(1024 * 1024 * 1.25)

    resizer = ImageResizer(root_dir, dst_dir, min_dim=min_dim, max_dim=max_dim, target_pixels=target_pixels,
                           keep_hierarchy=False)
    resizer.resizer_sketch()