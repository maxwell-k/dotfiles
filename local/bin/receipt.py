#!/usr/bin/env -S uv run
"""Scan a receipt, process it and save as a PDF.

Process means:

1. remove a trailing blank block
2. detect a rectangle
3. rotate so the rectangle is vertical and
4. crop to the width of the rectangle.
"""

# /// script
# dependencies = [
#   "img2pdf",
#   "numpy",
#   "opencv-python",
# ]
# requires-python = ">=3.13"
# ///

# local/bin/receipt.py
# Copyright 2026 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

import logging
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from doctest import ELLIPSIS, testmod
from os import environ
from pathlib import Path
from shlex import join
from subprocess import DEVNULL, Popen, run
from textwrap import dedent

import cv2
import img2pdf
import numpy as np

DPI = 300
SCANIMAGE = "/usr/bin/scanimage"
VIEWER = "/usr/bin/google-chrome-stable"
EXCLUDED = {".jp2"}
BLANK = 250
ENVRC = {"SANE_CONFIG_DIR": str(Path("~/.config/adf").expanduser())}
CACHE = Path("cache.pnm")

logger = logging.getLogger(__name__)


def main(_args: list[str] | None = None) -> int:
    """Scan a receipt, process it and save as a PDF."""
    args = parse_args(_args)

    setup_logging(debug=args.debug)
    logger.debug("command line arguments: %s", args)

    if args.test:
        results = testmod(optionflags=ELLIPSIS)
        logger.info("test results: %s", results)
        return max(0, min(results.failed, 1))

    env = environ.copy()
    env.update(ENVRC)

    if CACHE.is_file():
        logger.debug("%s exists, using cached scan", CACHE)
        scan = CACHE.read_bytes()
    else:
        error_if_scanner_missing("brother5", env)
        cmd = (
            SCANIMAGE,
            "--format=pnm",
            f"--resolution={DPI}",
            "--mode=True Gray",
            "--source=Automatic Document Feeder(center aligned)",
            *args.options,
        )
        result = run(cmd, capture_output=True, check=True, env=env)
        logger.debug("returncode %s from `%s`", result.returncode, join(cmd))
        scan = result.stdout

    img = cv2.imdecode(np.frombuffer(scan, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        msg = "Failed to read image from scanner."
        raise RuntimeError(msg)

    if args.keep and not CACHE.is_file():
        write("cache.pnm", img)

    stop = img.shape[0] - np.argmax(np.any(img[::-1] < BLANK, axis=1))
    img = img[:stop, :]
    if args.debug:
        write("debug0.png", img)

    if not any("-x" in i for i in args.options):
        contour = largest(img)
        if args.debug:
            debug = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(debug, [contour], -1, (0, 0, 255), 2)
            write("debug1.png", debug)

        rect = cv2.minAreaRect(contour)
        rotation = cv2.getRotationMatrix2D(rect[0], rect[-1] + 90.0, 1.0)
        size = (img.shape[1], img.shape[0])
        img = cv2.warpAffine(img, rotation, size, flags=cv2.INTER_CUBIC)

        (centre, _), (_, width), _ = rect
        left = int(centre - width / 2)
        img = img[:, left : int(left + width)]

    write(args.output, img, args.compression)
    view(args.output)

    return 0


def view(name: str) -> None:
    """Open a file in viewier."""
    path = Path(name)
    if path.suffix in EXCLUDED:
        return
    cmd = (VIEWER, path.absolute())
    Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)


def write(name: str, img: np.ndarray, compression: int = 20) -> None:
    """Write an image to a file."""
    path = Path(name)
    if path.suffix.lower() == ".pdf":
        params = [cv2.IMWRITE_JPEG2000_COMPRESSION_X1000, compression]
        success, encoded = cv2.imencode(".jp2", img, params)
        if not success:
            msg = "JPEG 2000 encoding failed."
            raise RuntimeError(msg)
        img2pdf.default_dpi = DPI
        with path.open("wb") as outputstream:
            img2pdf.convert(encoded.tobytes(), outputstream=outputstream)
    else:
        cv2.imwrite(name, img)
    logger.debug("wrote %s", name)


def largest(img: np.ndarray) -> np.ndarray:
    """Return the largest contour."""
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return sorted(contours, key=cv2.contourArea, reverse=True)[0]


def error_if_scanner_missing(name: str, env: dict[str, str]) -> None:
    """Raise a RuntimeError if the named scanner is not present."""
    cmd = (SCANIMAGE, "-L")
    result = run(cmd, capture_output=True, check=True, env=env)
    logger.debug("standard output from `%s`: %s", join(cmd), result.stdout)
    if name.encode() not in result.stdout:
        msg = f"scanner {name} not found"
        raise RuntimeError(msg)


def parse_args(args: list[str] | None) -> Namespace:
    """Parse command line arguments.

    >>> parse_args(['output.pnm']).output
    'output.pnm'

    >>> parse_args(['output.pnm'])
    Namespace(... options=[], debug=False, keep=False, compression=20, test=False)

    >>> parse_args(['output.pnm', "--compression=10"])
    Namespace(... options=[], debug=False, keep=False, compression=10, test=False)

    >>> args = parse_args(['--debug', 'example.pdf'])
    >>> args.debug, args.keep
    (True, True)

    >>> parse_args(['example.pdf', '--', '-x100']).options
    ['-x100']
    """
    name = Path(__file__).name
    epilog = dedent(f"""
    If the automatic width detection fails specify the width manually, for
    example:

        {name} output.pdf -- -x100

    """)
    parser = ArgumentParser(
        description=__doc__,
        epilog=epilog,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="output file name",
    )
    parser.add_argument(
        "options",
        nargs="*",
        help="additional options to pass to scanimage.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="show debug logging.",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help=f"keep '{CACHE}'.",
    )
    parser.add_argument(
        "--compression",
        default=20,
        type=int,
        help="target compression ratio 1 to 1,000.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="run doctest against this file.",
    )
    parsed = parser.parse_args(args)
    if parsed.debug:
        parsed.keep = True
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
    raise SystemExit(main())
