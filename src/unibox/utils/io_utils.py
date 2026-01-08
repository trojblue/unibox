from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import os


def fast_copy_files(paths, target_dir, workers=None):
    """
    Copy many files into a single directory efficiently.

    Parameters
    ----------
    paths : list[str | Path]
        List of file paths to copy.
    target_dir : str | Path
        Destination directory.
    workers : int | None
        Number of worker threads. Default uses min(32, cpu_count*2).
    """

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    # Choose a good default worker count for I/O bound work
    if workers is None:
        workers = min(32, (os.cpu_count() or 4) * 2)

    def _copy_one(src):
        src = Path(src)
        dst = target_dir / src.name
        shutil.copy2(src, dst)   # Uses kernel copy when possible
        return src

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_copy_one, p) for p in paths]

        # Force completion & surface exceptions early
        for f in as_completed(futures):
            f.result()

# ---

import os
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from urllib.parse import urlparse

def download_one(url, output_dir, extension=None, timeout=10):
    try:
        parsed = urlparse(url)
        filename = Path(parsed.path).name

        # If URL does not provide a filename, synthesize one
        if not filename:
            filename = "file"

        # If filename has no extension and user provided one, append it
        if extension and not Path(filename).suffix:
            if not extension.startswith("."):
                extension = "." + extension
            filename += extension

        out_path = Path(output_dir) / filename

        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        out_path.write_bytes(r.content)

        return filename, None

    except Exception as e:
        return url, str(e)


def download_all(urls, output_dir, max_workers=16, extension=None):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_one, url, output_dir, extension): url
            for url in urls
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading"):
            filename, error = future.result()
            results.append((filename, error))

    return results

