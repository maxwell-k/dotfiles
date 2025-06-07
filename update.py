#!/usr/bin/env python3
# update.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

"""Upate the checksums in a TOML file."""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from tomllib import load
from urllib.request import urlopen

MODIFIERS = {
    "deno": ".sha256sum",
    "uv": ".sha256",
    "dprint": "SHASUMS256.txt",
}


def _parse_args(arg_list: list[str] | None) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("key", type=str, help="item to update")
    parser.add_argument(
        "target",
        nargs="?",
        type=str,
        help="file to update, default: '%(default)s'",
        default="linux-amd64.toml",
    )
    return parser.parse_args(arg_list)


def main(arg_list: list[str] | None = None) -> int:
    """Update the expected hash in target using the URL plus a suffix."""
    args = _parse_args(arg_list)

    path = Path(args.target)
    with path.open("rb") as file:
        item = load(file)[args.key]
    url = item["url"]
    old = item["expected"]

    filename = url[url.rindex("/") + 1 :]

    modifier = MODIFIERS[args.key]
    if modifier.startswith("."):
        url += modifier
    else:
        url = url.removesuffix(filename) + modifier
    with urlopen(url) as response:
        content = response.read().decode()
    line = next(i for i in content.splitlines() if filename in i)
    new = line.split()[0]

    text = path.read_text().replace(old, new)
    path.write_text(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
