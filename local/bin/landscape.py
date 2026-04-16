#!/usr/bin/env python3
"""Scan A4 pages in landscape.

Relies upon the system package manager to install python-sane. Configure ALE
with:

let g:ale_python_pyright_config={'python':{'pythonPath':'/usr/bin/python3.12'}}

"""

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


def _main() -> int:
    sane.init()
    devices = sane.get_devices(localOnly=True)
    if devices[0][1:] != MODEL:
        return 1

    dev = sane.open(devices[0][0])

    dev.mode = MODE
    dev.br_x, dev.br_y = A4
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


if __name__ == "__main__":
    raise SystemExit(_main())
