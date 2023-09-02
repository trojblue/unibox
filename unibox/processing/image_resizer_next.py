import os
import math
import shutil
from PIL import Image
from pathlib import Path
from tqdm.auto import tqdm

import unibox
from unibox import UniLoader


def get_new_dimensions(width: int, height: int, target_side: int, resize_by_longer_side: bool = False) -> tuple:
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


def resize_image(image: Image.Image, min_dim: int = None, max_dim: int = None,
                 target_pixels: int = None, TRUNCATE_MULTIPLIER: int = 32) -> Image.Image:
    """
    输入PIL Image对象，输出resize之后的 PIL Image

    :param image: PIL.Image.Image object to be resized
    :param min_dim: minimum dimension of the shorter side
    :param max_dim: maximum dimension of the longer side (higher priority than min_dim)
    :param target_pixels: target number of pixels (truncate short side to a multiple of TRUNCATE_MULTIPLIER; higher priority than max_dim)
    :param TRUNCATE_MULTIPLIER: value to which the shorter side will be rounded down after scaling
    :return: PIL.Image.Image object after resizing
    """

    width, height = image.size
    new_width, new_height = width, height

    # Define the need_resize variable
    need_resize = (min_dim is not None and min(width, height) < min_dim) or \
                  (max_dim is not None and max(width, height) > max_dim)

    # Priority 1: Resize based on target_pixels
    if target_pixels is not None:
        scale_factor = math.sqrt(target_pixels / (width * height))
        target_shorter_side = round((min(width, height) * scale_factor) // TRUNCATE_MULTIPLIER) * TRUNCATE_MULTIPLIER
        new_width, new_height = get_new_dimensions(width, height, target_shorter_side)

    # Priority 2: Resize based on max_dim
    elif max_dim is not None and need_resize:
        new_width, new_height = get_new_dimensions(width, height, max_dim, resize_by_longer_side=True)

    # Priority 3: Resize based on min_dim
    elif min_dim is not None and need_resize:
        new_width, new_height = get_new_dimensions(width, height, min_dim)

    # If resizing is not needed, return the original image
    elif not need_resize:
        return image

    # Perform the resize operation
    return image.resize((new_width, new_height), Image.LANCZOS)


def get_dst_path(dst_dir: str, og_rel_image_path: str, extension: str, keep_hierarchy: bool = True,
                 create_dir: bool = True) -> Path:
    """
    :param dst_dir: destination directory
    :param og_rel_image_path: original relative image path
    :param extension: file extension (.webp)
    :param keep_hierarchy: if True, keep the original directory hierarchy
    :param create_dir: if True, create the destination directory if it doesn't exist
    """
    assert extension.startswith(".") and extension != ".", "extension must start with a dot"

    og_rel_path = Path(og_rel_image_path)
    rel_resized_path = og_rel_path.with_name(f"{og_rel_path.stem}_resized{extension}")

    if keep_hierarchy:
        dst_file_path = Path(dst_dir) / rel_resized_path
        if create_dir:
            dst_file_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        dst_file_path = Path(dst_dir) / rel_resized_path.name

    return dst_file_path


def resizer_sketch(root_dir, dst_dir, keep_hierarchy=True):
    min_dim = 512
    max_dim = int(1024 * 3)
    target_pixels = int(1024 * 1024 * 1.25)
    extension = ".webp"

    loader = UniLoader(debug_print=False)
    image_files = unibox.traverses(root_dir, include_extensions=unibox.constants.IMG_FILES, relative_unix=True)


    for og_rel_image_path in tqdm(image_files):
        image = loader.loads(os.path.join(root_dir, og_rel_image_path))
        image = resize_image(image, min_dim=min_dim, max_dim=max_dim, target_pixels=target_pixels)

        # handle save path
        dst_file_path = get_dst_path(dst_dir, og_rel_image_path, extension, keep_hierarchy)

        # save
        try:
            with open(dst_file_path, "wb") as f:
                image.save(f, "webp", quality=98)
        except OSError:
            print(f"Error saving image {dst_file_path}. Skipping...")
            continue

    pass


def driver():
    root_dir = r"E:\_benchmark\small"
    dst_dir = r"E:\_benchmark\small_resized"
    resizer_sketch(root_dir, dst_dir)


if __name__ == '__main__':
    driver()
