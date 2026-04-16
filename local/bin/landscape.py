#!/usr/bin/env python3
"""Scan A4 pages in landscape.

Relies upon the system package manager to install python-sane. Configure ALE
with:

let g:ale_python_pyright_config={'python':{'pythonPath':'/usr/bin/python3.12'}}

"""

import logging
from argparse import ArgumentParser, Namespace
from doctest import testmod
from os import environ
from pathlib import Path

import sane

# /// script
# dependencies = ["python-sane"]
# requires-python = ">=3.12"
# ///

# local/bin/landscape.py
# Copyright 2026 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

environ["SANE_CONFIG_DIR"] = str(Path("~/.config/adf").expanduser())

MODEL = ("Brother", "ADS-1200", "USB scanner")
MODE = "True Gray"
SOURCE = "Automatic Document Feeder(center aligned,Duplex)"
RESOLUTION = 300
A4 = (210, 297)

logger = logging.getLogger(__name__)


def _main(_args: list[str] | None = None) -> int:
    args = parse_args(_args)

    setup_logging(debug=args.debug)
    logger.debug("command line arguments: %s", args)

    if args.test:
        results = testmod()
        logger.info("test results: %s", results)
        return max(0, min(results.failed, 1))

    sane.init()
    device = sane.get_devices(localOnly=True)[0]
    dev = sane.open(device[0])
    logger.debug("using scanner %s", device)

    dev.br_x = args.x
    dev.br_y = args.y
    dev.mode = MODE
    dev.source = SOURCE
    dev.resolution = 300

    dev.start()
    imgs = list(dev.multi_scan())
    dev.close()
    sane.exit()

    for page, img in enumerate(imgs, start=1):
        degrees = -90 if page % 2 == 1 else 90
        filename = f"adf.{page:04}.pbm"
        img.rotate(degrees, expand=True).save(filename)
        print(filename)
    return 0


def parse_args(args: list[str] | None) -> Namespace:
    """Parse command line arguments.

    Check that -x and -y are supported and default to A4:

    >>> args = parse_args([])
    >>> args.x, args.y
    (210, 297)
    >>> args = parse_args(["-x100", "-y200"])
    >>> args.x, args.y
    (100, 200)

    Check that setting --debug and --test are supported and default off

    >>> args = parse_args([])
    >>> args.debug, args.test
    (False, False)
    >>> args = parse_args(['--debug', '--test'])
    >>> args.debug, args.test
    (True, True)


    """
    parser = ArgumentParser()
    parser.add_argument(
        "-x",
        default=A4[0],
        type=int,
        help=f"height in mm (default: {A4[0]})",
    )
    parser.add_argument(
        "-y",
        default=A4[1],
        type=int,
        help=f"width in mm (default: {A4[1]})",
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
    return parser.parse_args(args)


def setup_logging(*, debug: bool = False) -> None:
    """Set up logging."""
    level = logging.DEBUG if debug else logging.INFO
    format_ = "%(levelname)s:%(name)s:%(asctime)s:" if debug else ""
    format_ += "%(message)s"
    logging.basicConfig(level=level, format=format_)


if __name__ == "__main__":
    raise SystemExit(_main())
