import concurrent.futures
import multiprocessing
import os
from pathlib import Path
from PIL import Image
from tqdm.auto import tqdm


try:
    import pyvips

    # Try to create a small image using libvips to check if it's working.
    pyvips.Image.black(1, 1)
    HAS_PYVIPS = True
except ImportError:
    HAS_PYVIPS = False
except pyvips.error.Error:
    HAS_PYVIPS = False

SUPPORTED_FORMATS = {"jpg", "webp", "png"}


# Updated ImageResizer class

class ImageResizer:
    def __init__(self, src_dir: str, dst_dir: str, min_side: int = 768, format: str = "webp", quality: int = 95, exist_ok: bool = False):
        """
        Initialize an instance of ImageResizer.
        """
        self.src_dir = Path(src_dir)
        self.dst_dir = Path(dst_dir)
        self.min_side = min_side
        self.format = self._validate_format(format)
        self.quality = quality
        self.exist_ok = exist_ok
        self.num_processes = multiprocessing.cpu_count()

    def _validate_format(self, format: str) -> str:
        """
        Validate the provided image format.
        """
        if format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format '{format}'. Supported formats are {SUPPORTED_FORMATS}.")
        return format

    def _resize_image(self, file_path: Path, relative_path: Path):
        """
        Resize a single image and save the result.
        """
        dst_path = self.dst_dir / relative_path.with_suffix(f".{self.format}")

        # Ensure the destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if HAS_PYVIPS:
            image = self._resize_with_pyvips(file_path)
        else:
            image = self._resize_with_pil(file_path)

        # Image might not need resizing but still needs to be saved in new format
        if image is None:
            if HAS_PYVIPS:
                image = pyvips.Image.new_from_file(str(file_path), access="sequential")
            else:
                image = Image.open(file_path)

        self._save_image(image, dst_path)

    def _resize_with_pil(self, image_path: Path) -> Image:
        """
        Resize an image using PIL.
        """
        try:
            image = Image.open(image_path)
        except IOError:
            print(f"Error opening image {image_path}. Skipping...")
            return None

        width, height = image.size
        min_dim = min(width, height)

        if min_dim <= self.min_side:
            return None

        scale = self.min_side / min_dim
        new_width = round(width * scale)
        new_height = round(height * scale)

        return image.resize((new_width, new_height), Image.LANCZOS)

    def _resize_with_pyvips(self, image_path: Path):
        """
        Resize an image using pyvips.
        """
        try:
            image = pyvips.Image.new_from_file(str(image_path), access="sequential")
        except pyvips.error.Error:
            print(f"Error opening image {image_path} with pyvips. Skipping...")
            return None

        min_dim = min(image.width, image.height)

        if min_dim <= self.min_side:
            return None

        scale = self.min_side / min_dim
        return image.resize(scale)

    def _task(self, file_path, relative_path):
        self._resize_image(file_path, relative_path)

    def _save_image(self, image, dst_path: Path):
        """
        Save an image in the specified format.
        """
        save_methods = {
            "jpg": {"pil": "JPEG", "pyvips": "jpegsave", "params": {"Q": self.quality}},
            "webp": {"pil": "WEBP", "pyvips": "webpsave", "params": {"Q": self.quality}},
            "png": {"pil": "PNG", "pyvips": "pngsave", "params": {}}
        }

        method_map = save_methods[self.format]
        try:
            if HAS_PYVIPS:
                getattr(image, method_map["pyvips"])(str(dst_path), **method_map["params"])
            else:
                image.save(dst_path, method_map["pil"], **method_map["params"])
        except Exception as e:
            print(f"Error saving image {dst_path}. Skipping...\n{str(e)}")

    def _execute_resize(self, tasks):
        """
        Execute tasks using ProcessPoolExecutor
        """
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            futures = [executor.submit(task, *args) for task, *args in tasks]
            list(tqdm(concurrent.futures.as_completed(futures), total=len(tasks),
                      desc=f"Resizing images to min_side={self.min_side}"))

    def resize_images(self):
        """
        Resize all supported images in the source directory.
        """
        tasks = []

        self._print_debug_string()

        for file_path in self.src_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix[1:].lower() in SUPPORTED_FORMATS:
                relative_path = file_path.relative_to(self.src_dir)
                dst_path = self.dst_dir / relative_path.with_suffix(f".{self.format}")

                # Check if the destination file exists and exist_ok is True
                if not self.exist_ok or not dst_path.exists():
                    tasks.append((self._task, file_path, relative_path))

        self._execute_resize(tasks)

    def _print_debug_string(self):
        """
        prints debug message once resize_images is called
        """
        debug_string = ""
        if HAS_PYVIPS:
            debug_string += "Resizing with libvips: "
        else:
            debug_string += "Resizing with PIL: "
        debug_string += f"num_processes = {self.num_processes}, src_dir={self.src_dir}, dst_dir={self.dst_dir}, " \
                        f"min_side={self.min_side}, format={self.format}, quality={self.quality}," \
                        f"exist_ok={self.exist_ok}"
        print(debug_string)


if __name__ == "__main__":
    # Define the source and destination directories and the minimum side length for resizing
    src_dir = input("dir path:")

    dst_dir = f"{src_dir}_768webp"
    min_side = 64

    # Create an instance of the ImageResizer class
    resizer = ImageResizer(src_dir, dst_dir, min_side)

    # Get a list of image files from the source directory
    resizer.resize_images()