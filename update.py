#!/usr/bin/env python3
# update.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

"""Upate the checksums in a TOML file."""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from tomllib import load
from urllib.request import urlopen


def _parse_args(arg_list: list[str] | None) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "key",
        nargs="?",
        type=str,
        help="item to update, all items if unspecified",
    )
    parser.add_argument(
        "target",
        nargs="?",
        type=Path,
        help="file to update, default: '%(default)s'",
        default=Path("linux-amd64.toml"),
    )
    return parser.parse_args(arg_list)


def _update(target: Path, key: str) -> None:
    with target.open("rb") as file:
        item = load(file)[key]
    url = item["url"]
    old = item["expected"]

    filename = url[url.rindex("/") + 1 :]

    try:
        modifier = item["modifier"]
    except KeyError:
        print(f"{key} does not have `modifier` specified")
        return
    if modifier.startswith("."):
        url += modifier
    else:
        url = url.removesuffix(filename) + modifier
    with urlopen(url) as response:
        content = response.read().decode()
    line = next(i for i in content.splitlines() if filename in i)
    new = line.split()[0]

    text = target.read_text().replace(old, new)
    target.write_text(text)


def main(arg_list: list[str] | None = None) -> int:
    """Update the expected hash in target using the URL plus a suffix."""
    args = _parse_args(arg_list)
    if args.key:
        _update(args.target, args.key)
        return 0

    with args.target.open("rb") as file:
        keys = [key for key, value in load(file).items() if "modifier" in value]
    for key in keys:
        _update(args.target, key)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
