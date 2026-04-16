#!/usr/bin/env -S uv run --script
"""Convert PNM files to JPEG 2000 images in a PDF."""

# /// script
# dependencies = [
#   "img2pdf",
#   "pillow",
# ]
# requires-python = ">=3.13"
# ///

# local/bin/jpeg2000.py
# Copyright 2026 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

import logging
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from doctest import testmod
from io import BytesIO
from pathlib import Path
from stat import S_IXUSR
from subprocess import DEVNULL, Popen

import img2pdf
from PIL import Image

DPI = 300
VIEWER = Path("/usr/bin/google-chrome-stable")

logger = logging.getLogger(__name__)


def _main(_args: list[str] | None = None) -> int:
    args = parse_args(_args)

    setup_logging(debug=args.debug)
    logger.debug("command line arguments: %s", args)

    if args.test:
        results = testmod()
        logger.info("Test results: %s", results)
        return max(0, min(results.failed, 1))
    paths = list(Path().glob("*.pbm"))
    images = [_convert(Image.open(i), args.compression) for i in paths]

    img2pdf.default_dpi = DPI
    with args.output.open("wb") as outputstream:
        img2pdf.convert(images, outputstream=outputstream)

    size = args.output.stat().st_size
    logger.info("Wrote %s bytes to %s", f"{size:,}", args.output)

    if VIEWER.is_file() and VIEWER.stat().st_mode & S_IXUSR:
        cmd = (VIEWER, args.output.absolute())
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)

    return 0


def _convert(img: Image.Image, compression: int) -> BytesIO:
    result = BytesIO()
    img.save(result, format="JPEG2000", quality_layers=[compression])
    result.seek(0)
    return result


def parse_args(args: list[str] | None) -> Namespace:
    """Parse command line arguments.

    Supports --compression:

    >>> parse_args(['example.pdf']).output
    PosixPath('example.pdf')

    Supports --compression:

    >>> parse_args(['example.pdf']).compression
    20
    >>> parse_args(['example.pdf', '--compression=40']).compression
    40

    Supports --test which defaults off:

    >>> parse_args(['example.pdf']).test
    False
    >>> parse_args(['example.pdf', '--test']).test
    True

    Supports --debug which defaults off:

    >>> parse_args(['example.pdf']).debug
    False
    >>> parse_args(['example.pdf', '--debug']).debug
    True

    """
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="output file name",
        type=Path,
    )
    parser.add_argument(
        "--compression",
        default=20,
        type=int,
        help="approximate rate of size reduction.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="run doctest against this file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="show debug logging.",
    )
    parsed = parser.parse_args(args)
    if parsed.output is None and not parsed.test:
        msg = "'output' is required unless using --test"
        parser.error(msg)
    return parsed


def setup_logging(*, debug: bool = False) -> None:
    """Set up logging."""
    level = logging.DEBUG if debug else logging.INFO
    format_ = "%(levelname)s:%(name)s:%(asctime)s:" if debug else ""
    format_ += "%(message)s"
    logging.basicConfig(level=level, format=format_)


if __name__ == "__main__":
    raise SystemExit(_main())
