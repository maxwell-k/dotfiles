#!/usr/bin/env python3
# update.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

"""Upate the checksum for deno"""

from argparse import ArgumentParser
from pathlib import Path
from tomllib import load
from urllib.request import urlopen

SUFFIXES = {
    "deno": ".sha256sum",
    "uv": ".sha256",
}


def parse_args(arg_list: list[str] | None):
    parser = ArgumentParser()

    help_ = "item to update"
    parser.add_argument("key", type=str, help=help_)
    help_ = "file to update, default: '%(default)s'"
    parser.add_argument(
        "target",
        nargs="?",
        type=str,
        help=help_,
        default="linux-amd64.toml",
    )
    return parser.parse_args(arg_list)


def main(arg_list: list[str] | None = None) -> int:
    """Update the expected hash in target using the URL plus a suffix"""
    args = parse_args(arg_list)

    path = Path(args.target)
    with path.open("rb") as file:
        item = load(file)[args.key]

    url = item["url"] + SUFFIXES[args.key]
    with urlopen(url) as response:
        content = response.read()
    new = content.decode().split()[0]

    old = item["expected"]
    text = path.read_text().replace(old, new)
    path.write_text(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
