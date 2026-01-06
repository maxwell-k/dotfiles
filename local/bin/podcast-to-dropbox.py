#!/usr/bin/env -S uv run --script
"""Move podcast files to Dropbox with rclone."""

# local/bin/podcast-to-dropbox.py
# Copyright 2026 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "rclone-python",
# ]
# ///


import argparse
from pathlib import Path

from rclone_python.rclone import move

DESTINATION = "dropbox:Podcasts"


def _main() -> int:
    args = _parse_args()
    for file in args.file:
        move(file, DESTINATION)
    return 0


def _parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    description = f"Move .mp3 and .m4a files to {DESTINATION}"
    parser = argparse.ArgumentParser(description=description)
    help_ = "podcast to move to dropbox"
    parser.add_argument("file", nargs="+", type=_podcast, help=help_)
    return parser.parse_args(args)


def _podcast(value: str) -> Path:
    """Check a podcast argument.

    >>> import tempfile
    >>> from contextlib import chdir

    >>> with tempfile.TemporaryDirectory() as d, chdir(d):
    ...     Path('file.mp3').touch()
    ...     _podcast('file.mp3')
    PosixPath('file.mp3')

    >>> with tempfile.TemporaryDirectory() as d, chdir(d):
    ...     Path('file.m4a').touch()
    ...     _podcast('file.m4a')
    PosixPath('file.m4a')

    >>> with tempfile.TemporaryDirectory() as d, chdir(d):
    ...     Path('file.webm').touch()
    ...     _podcast('file.webm')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: 'file.webm' does not end in .mp3 or .m4a.

    >>> _podcast('not-a-file.mp3')
    Traceback (most recent call last):
    ...
    argparse.ArgumentTypeError: 'not-a-file.mp3' is not a file.

    """
    result = Path(value)
    if not result.is_file():
        msg = f"'{result}' is not a file."
        raise argparse.ArgumentTypeError(msg)
    if result.suffix not in (".m4a", ".mp3"):
        msg = f"'{result}' does not end in .mp3 or .m4a."
        raise argparse.ArgumentTypeError(msg)
    return result


if __name__ == "__main__":
    raise SystemExit(_main())
