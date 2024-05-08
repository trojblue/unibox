import os
import math
from PIL import Image
from pathlib import Path
from tqdm.auto import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple
import unibox
from unibox import UniLogger


def chunk_list(lst, chunk_size):
    """Yield successive chunks of size `chunk_size` from list `lst`."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


class UniResizer:
    TRUNCATE_MULTIPLIER = 32  # the shorter side will be a multiple of 32 after scaling
    WEBP_QUALITY = 98  # quality of the output image (max:100)
    EXTENSION = ".webp"  # file extension (.webp)

    def __init__(self, root_dir: str, dst_dir: str, min_dim: int = None, max_dim: int = None, target_pixels: int = None,
                 keep_hierarchy: bool = True, exist_ok: bool = True, logger: UniLogger = None, max_workers: int = None,
                 chunk_size: int = 10_000, ):
        """
        Resizes images in a directory to a specified size.

        Resolution:
            - by min_dim: resize the shorter side to a specified size
            - by max_dim: resize the longer side to a specified size
            - by target_pixels: resize the shorter side to a specified number of pixels

        Methods:
            - by directory: resize all images in a directory
            - by list: resize a list of images given

        Configs:
            - keep_hierarchy: keep the same directory structure as the source directory
            - exist_ok: skip resizing if the destination file already exists
            - max_workers: number of workers for parallel processing
            - chunk_size: number of images to process in each chunk (to be dispatched to ProcessPoolExecutor each time)
        
        Usage:
        >>> resizer = UniResizer(root_dir, dst_dir, min_dim=min_dim, max_dim=max_dim, target_pixels=target_pixels,
        >>>                   keep_hierarchy=False, exist_ok=True)
        >>> resizer.execute_resize_jobs(resizer.get_resize_jobs())
        """ 
        
        self.root_dir = root_dir
        self.dst_dir = dst_dir
        self.min_dim = min_dim
        self.max_dim = max_dim
        self.target_pixels = target_pixels
        self.keep_hierarchy = keep_hierarchy
        self.exist_ok = exist_ok
        self.logger = logger if logger is not None else UniLogger()
        self.max_workers = int(os.cpu_count() - 1) if max_workers is None else max_workers
        self.chunk_size = chunk_size

    def _get_dst_path(self, og_rel_image_path: str) -> str:
        og_rel_path = Path(og_rel_image_path)
        rel_resized_path = og_rel_path.with_name(f"{og_rel_path.stem}_resized{self.EXTENSION}")
        if self.keep_hierarchy:
            dst_file_path = Path(self.dst_dir) / rel_resized_path
        else:
            dst_file_path = Path(self.dst_dir) / rel_resized_path.name
        return str(dst_file_path)

    def _create_dst_dir(self, dst_file_path: str) -> None:
        Path(dst_file_path).parent.mkdir(parents=True, exist_ok=True)

    def resize_single_image(self, image: Image.Image) -> Image.Image:
        width, height = image.size
        new_width, new_height = width, height

        need_resize = (self.min_dim is not None and min(width, height) < self.min_dim) or \
                      (self.max_dim is not None and max(width, height) > self.max_dim)

        if self.target_pixels is not None:
            if width * height > self.target_pixels:
                scale_factor = math.sqrt(self.target_pixels / (width * height))
                target_shorter_side = round((min(width, height) * scale_factor) // self.TRUNCATE_MULTIPLIER) * self.TRUNCATE_MULTIPLIER
                new_width, new_height = self._get_new_dimensions(width, height, target_shorter_side)

        elif self.max_dim is not None and need_resize:
            new_width, new_height = self._get_new_dimensions(width, height, self.max_dim, resize_by_longer_side=True)

        elif self.min_dim is not None and need_resize:
            new_width, new_height = self._get_new_dimensions(width, height, self.min_dim)

        elif not need_resize:
            return image

        return image.resize((new_width, new_height), Image.LANCZOS)

    @staticmethod
    def _get_new_dimensions(width: int, height: int, target_side: int, resize_by_longer_side: bool = False) -> tuple:
        if target_side == -1:
            return int(width), int(height)
        if any(x <= 0 or type(x) != int for x in [width, height, target_side]):
            raise ValueError("width, height and target_side must be positive integers")
        shorter_side, longer_side = min(width, height), max(width, height)
        if resize_by_longer_side:
            new_longer_side = target_side
            new_shorter_side = round(new_longer_side * (shorter_side / longer_side))
        else:
            new_shorter_side = target_side
            new_longer_side = round(new_shorter_side * (longer_side / shorter_side))
        if width > height:
            return new_longer_side, new_shorter_side
        else:
            return new_shorter_side, new_longer_side

    def _resize_single_image_task(self, og_rel_image_path: str) -> None:
        src_file_path = os.path.join(self.root_dir, og_rel_image_path)
        dst_file_path = self._get_dst_path(og_rel_image_path)
        if self.keep_hierarchy:
            self._create_dst_dir(dst_file_path)
        try:
            with Image.open(src_file_path) as image:
                resized_image = self.resize_single_image(image)
                with open(dst_file_path, "wb") as f:
                    resized_image.save(f, "webp", quality=self.WEBP_QUALITY)
        except OSError as e:
            self.logger.error(f"Error processing image {og_rel_image_path}: {e}. Skipping...")

    @staticmethod
    def _execute_resize_tasks(tasks: List[Tuple], max_workers: int, total_progress: tqdm) -> None:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(task, *args): i for i, (task, *args) in enumerate(tasks)}
            for future in as_completed(future_to_task):
                total_progress.update(1)

    def get_resize_jobs(self) -> List[str]:
        self.logger.info("Getting image paths...")
        todo_image_files = unibox.traverses(self.root_dir, include_extensions=unibox.constants.IMG_FILES, relative_unix=True)
        if self.exist_ok:
            self.logger.info("Checking existing files...")
            existing_files = unibox.traverses(self.dst_dir, include_extensions=unibox.constants.IMG_FILES, relative_unix=False)
            expected_file_set = {self._get_dst_path(rel_path) for rel_path in todo_image_files}
            existing_file_set = set(existing_files)
            needed_files_set = expected_file_set - existing_file_set
            reverse_mapping = {self._get_dst_path(rel_path): rel_path for rel_path in todo_image_files}
            todo_image_files = [reverse_mapping[dst_path] for dst_path in needed_files_set]
        return todo_image_files

    def execute_resize_jobs(self, image_files: List[str], report_interval:float=5) -> None:
        tasks = [(self._resize_single_image_task, og_rel_image_path) for og_rel_image_path in image_files]
        self.logger.info(f"Resizing {len(tasks)} images from {self.root_dir} to {self.dst_dir} | chunk size: {self.chunk_size} | report interval: {report_interval}s")
        
        # creating shared progress bar
        pbar = tqdm(total=len(tasks), 
                    desc=f"[interval={report_interval}] resizing [{self.root_dir}]", 
                    mininterval=report_interval
                    )
        # Process each chunk
        for chunk in chunk_list(tasks, self.chunk_size):
            self._execute_resize_tasks(chunk, self.max_workers, pbar)
        
        pbar.close()

# Example Usage
if __name__ == '__main__':
    root_dir = r"E:\_benchmark\1k"
    dst_dir = r"E:\_benchmark\1k_resized"
    min_dim = 512
    max_dim = int(1024 * 3)
    target_pixels = int(1024 * 1024 * 1.25)
    resizer = UniResizer(root_dir, dst_dir, min_dim=min_dim, max_dim=max_dim, target_pixels=target_pixels, keep_hierarchy=False, exist_ok=True)
    images_to_resize = resizer.get_resize_jobs()
    resizer.execute_resize_jobs(images_to_resize)
