#!/usr/bin/env python3
# update.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

"""Upate the checksums in a TOML file."""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from tomllib import load
from urllib.request import HTTPError, urlopen


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


def _apply_modifier(url: str, modifier: str) -> str:
    """Apply a modifier to the file URL to get the checksum URL.

    >>> _apply_modifier("https://example.org/file-1.1.1.zip", "SHA256SUMS")
    'https://example.org/SHA256SUMS'

    >>> _apply_modifier("https://example.org/file-1.1.1.zip", ".sha256")
    'https://example.org/file-1.1.1.zip.sha256'

    >>> url = "https://example.org/file_1.2.3_linux_amd64.tar.gz"
    >>> _apply_modifier(url, "_checksums.txt")
    'https://example.org/file_1.2.3_checksums.txt'

    >>> url = "https://example.org/file_1.2.3_linux_amd64.zip"
    >>> _apply_modifier(url, "_checksums.txt")
    'https://example.org/file_1.2.3_checksums.txt'
    """
    filename = url[url.rindex("/") + 1 :]
    for suffix in ["_linux_amd64.tar.gz", "_linux_amd64.zip"]:
        url = url.removesuffix(suffix)
    if modifier.startswith("SHA256SUMS"):
        url = url.removesuffix(filename)
    url += modifier
    return url


def _update(target: Path, key: str) -> None:
    with target.open("rb") as file:
        item = load(file)[key]
    url = item["url"]
    old = item["expected"]

    try:
        modifier = item["modifier"]
    except KeyError:
        print(f"{key} does not have `modifier` specified")
        return
    filename = url[url.rindex("/") + 1 :]
    url = _apply_modifier(url, modifier)
    try:
        with urlopen(url) as response:
            content = response.read().decode()
    except HTTPError as error:
        print(f"{url} responded with status code {error.status}")
        return
    line = next(i for i in content.splitlines() if filename in i)
    new = line.split()[0]

    text = target.read_text().replace(old, new)
    target.write_text(text)


def main(arg_list: list[str] | None = None) -> int:
    """Update each expected field using a modifier field and a GET request."""
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
