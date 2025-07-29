"""Module that contains the command line application."""

# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m unibox` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `unibox.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `unibox.__main__` in `sys.modules`.

from __future__ import annotations

import argparse
import sys
from typing import Any

from unibox import debug
from unibox.utils.credentials_manager import apply_credentials as _apply_credentials


class _DebugInfo(argparse.Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        debug.print_debug_info()
        sys.exit(0)


def apply_credentials(*services: str) -> None:
    """Apply credentials for AWS and Hugging Face.

    This function is called when the program starts.
    It hides the credentials for AWS and Hugging Face in a hidden directory.
    """
    if not services:
        services = ["aws", "huggingface"]
    try:
        print(f"Applying credentials: {services}")
        _apply_credentials(*services)
    except Exception as e:
        print(f"Error applying credentials: {e}")
        sys.exit(1)


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""
    parser = argparse.ArgumentParser(prog="unibox")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {debug.get_version()}")
    parser.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")

    subparsers = parser.add_subparsers(dest="command", required=False)

    # Add `apply-cred` command
    subparsers.add_parser("apply-cred", help="Apply credentials for AWS and Hugging Face. Hides them if not hidden")
    subparsers.add_parser("ac", help="Alias for apply-cred")

    return parser


def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `unibox` or `python -m unibox`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)

    if opts.command in ("apply-cred", "ac"):
        apply_credentials()
        return 0
    if opts.command is None:
        # No command provided - show help and return 0 (expected by test)
        parser.print_help()
        return 0

    # Unknown command
    parser.print_help()
    return 1
