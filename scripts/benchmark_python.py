"""Benchmark `unibox` performance (ls and concurrent_loads)."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import unibox as ub

DEFAULT_IMG_DIR = Path(
    "/data/yada/data/qfty_celery/dit02-desu_refined_danbooru_50k-100k/output",
)


def benchmark_ls(path: Path) -> None:
    """Run `ub.ls` and print timing and throughput."""
    start = time.perf_counter()
    files = ub.ls(str(path), debug_print=False)
    elapsed = time.perf_counter() - start

    num_files = len(files)
    throughput = num_files / elapsed if elapsed > 0 else float("inf")

    print("=== ls benchmark ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Directory: {path}")
    print(f"Files found: {num_files}")
    print(f"Elapsed: {elapsed:.3f} s")
    print(f"Throughput: {throughput:.1f} files/s")
    print()


def benchmark_concurrent_loads(
    path: Path,
    batch_size: int = 100,
    num_batches: int = 10,
    num_workers: int = 8,
) -> None:
    """Load files concurrently in batches and report timing."""
    print("=== concurrent_loads benchmark ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Directory: {path}")
    print(f"Batch size: {batch_size}, batches: {num_batches}, workers: {num_workers}")

    # List image files once
    all_files = ub.ls(str(path), exts=ub.IMG_FILES, debug_print=False)
    needed = batch_size * num_batches
    if len(all_files) < needed:
        print(
            f"Warning: requested {needed} files but only {len(all_files)} available; "
            "reducing number of batches.",
        )
        num_batches = len(all_files) // batch_size
        if num_batches == 0:
            print("Not enough files to run a single batch.")
            print()
            return
        needed = batch_size * num_batches

    files = all_files[:needed]
    print(f"Total files used: {len(files)}")

    batch_times: list[float] = []
    total_start = time.perf_counter()

    for i in range(num_batches):
        batch = files[i * batch_size : (i + 1) * batch_size]

        start = time.perf_counter()
        ub.concurrent_loads(batch, num_workers=num_workers, debug_print=False)
        elapsed = time.perf_counter() - start

        batch_times.append(elapsed)
        print(f"Batch {i + 1}/{num_batches}: {elapsed:.3f} s")

    total_elapsed = time.perf_counter() - total_start
    mean_batch = sum(batch_times) / len(batch_times)
    total_files = batch_size * num_batches
    throughput = total_files / total_elapsed if total_elapsed > 0 else float("inf")

    print("--- Summary ---")
    print(f"Total time (all batches): {total_elapsed:.3f} s")
    print(f"Mean time per batch: {mean_batch:.3f} s")
    print(f"Total files: {total_files}")
    print(f"Throughput: {throughput:.1f} files/s")
    print()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Benchmark unibox performance (ls and concurrent_loads).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_IMG_DIR),
        help=f"Directory to use (default: {DEFAULT_IMG_DIR})",
    )
    parser.add_argument(
        "--mode",
        choices=("ls", "concurrent", "both"),
        default="both",
        help="Which benchmark to run (default: both).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Files per concurrent_loads call (default: 100).",
    )
    parser.add_argument(
        "--batches",
        type=int,
        default=10,
        help="Number of batches for concurrent_loads (default: 10).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Workers for concurrent_loads (default: 8).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the benchmark script."""
    args = parse_args(argv)
    path = Path(args.path)

    if args.mode in ("ls", "both"):
        benchmark_ls(path)
    if args.mode in ("concurrent", "both"):
        benchmark_concurrent_loads(
            path=path,
            batch_size=args.batch_size,
            num_batches=args.batches,
            num_workers=args.workers,
        )


if __name__ == "__main__":
    main()
