#!/usr/bin/env python3
# update.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

"""Upate the checksums in a TOML file."""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from tomllib import load
from urllib.request import HTTPError, urlopen


def parse_args(arg_list: list[str] | None) -> Namespace:
    """Parse command line arguments.

    >>> parse_args([])
    Namespace(key=None, target=PosixPath('linux-amd64.toml'))
    """
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


def apply_modifier(url: str, modifier: str) -> str:
    """Apply a modifier to the file URL to get the checksum URL.

    >>> apply_modifier("https://example.org/file-1.1.1.zip", "SHA256SUMS")
    'https://example.org/SHA256SUMS'

    >>> apply_modifier("https://example.org/file-1.1.1.zip", "checksums-bsd")
    'https://example.org/checksums-bsd'

    >>> apply_modifier("https://example.org/file-1.1.1.zip", ".sha256")
    'https://example.org/file-1.1.1.zip.sha256'

    >>> url = "https://example.org/file_1.2.3_linux_amd64.tar.gz"
    >>> apply_modifier(url, "_checksums.txt")
    'https://example.org/file_1.2.3_checksums.txt'

    >>> url = "https://example.org/file_1.2.3_linux_amd64.zip"
    >>> apply_modifier(url, "_checksums.txt")
    'https://example.org/file_1.2.3_checksums.txt'
    """
    filename = url[url.rindex("/") + 1 :]
    for suffix in ["_linux_amd64.tar.gz", "_linux_amd64.zip"]:
        url = url.removesuffix(suffix)
    if modifier[0] != ".":
        url = url.removesuffix(filename)
    url += modifier
    return url


def extract(text: str, filename: str) -> str:
    r"""Extract the hash for filename from text.

    Handles output from `sha256sum`:

    >>> text = "a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447  file"
    >>> extract(text, "file")
    'a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447'

    Handles output from `sha256sum --tag`:

    >>> text = "SHA256 (file) = "
    >>> text += "a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447\n"
    >>> extract(text, "file")
    'a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447'

    Handles output from `rhash -r -a --bsd` see https://github.com/rhash/RHash:

    >>> text = "SHA256 (file.zip) = "
    >>> text += "0000000000000000000000000000000000000000000000000000000000000000\n"
    >>> text += "CRC32 (file) = af083b2d\n"
    >>> text += "SHA256 (file) = "
    >>> text += "a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447\n"
    >>> extract(text, "file")
    'a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447'
    """
    lines = text.splitlines()
    if "=" in lines[0]:
        marker = f"({filename})"
        line = next(i for i in lines if marker in i and i.startswith("SHA256"))
        result = line.split()[3]
    else:
        line = next(i for i in lines if filename in i)
        result = line.split()[0]
    return result


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
    url = apply_modifier(url, modifier)
    try:
        with urlopen(url) as response:
            text = response.read().decode()
    except HTTPError as error:
        print(f"{url} responded with status code {error.status}")
        return
    new = extract(text, filename)

    text = target.read_text().replace(old, new)
    target.write_text(text)


def main(arg_list: list[str] | None = None) -> int:
    """Update each expected field using a modifier field and a GET request."""
    args = parse_args(arg_list)
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
