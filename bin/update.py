#!/usr/bin/env python3
"""Upate the checksums in a TOML file."""

# bin/update.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///


import json
import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import run
from tomllib import load, loads
from urllib.request import HTTPError, Request, urlopen

logger = logging.getLogger(__name__)


def main(arg_list: list[str] | None = None) -> int:
    """Update each expected field using a modifier field and a GET request."""
    args = parse_args(arg_list)

    level = logging.DEBUG if args.debug else logging.INFO
    format_ = "%(levelname)s:%(name)s:%(asctime)s:" if args.debug else ""
    format_ += "%(message)s"
    logging.basicConfig(level=level, format=format_)

    keys: list[str] = []

    if args.all:
        toml = load(args.target.read_bytes())
        for key, value in toml.items():
            if "modifier" in value:
                keys.append(key)

    if args.git:
        keys.extend(_git(args.target))

    if args.key:
        keys.append(args.key)

    logger.debug("looping through keys: %s", keys)
    for key in keys:
        _update(args.target, key)

    return 0


def parse_args(arg_list: list[str] | None) -> Namespace:
    """Parse command line arguments.

    >>> parse_args([])
    Namespace(target=PosixPath('bin/linux-amd64.toml'), git=True, all=False, key=None)

    >>> parse_args(['--git'])
    Namespace(target=PosixPath('bin/linux-amd64.toml'), git=True, all=False, key=None)

    >>> parse_args(['--all'])
    Namespace(target=PosixPath('bin/linux-amd64.toml'), git=False, all=True, key=None)

    >>> parse_args(['--key=one'])
    Namespace(target=PosixPath('bin/linux-amd64.toml'), git=False, all=False, key='one')

    >>> parse_args(['--all', '--git'])
    --all is not compatible with --git, ignoring.
    Namespace(target=PosixPath('bin/linux-amd64.toml'), git=True, all=False, key=None)

    >>> parse_args(['--all', '--key', 'one'])
    --all is not compatible with --key, ignoring.
    Namespace(target=PosixPath('bin/linux-amd64.toml'), git=False, all=False, key='one')
    """
    parser = ArgumentParser()
    help_ = "file to update, default: '%(default)s'"
    default = Path("bin/linux-amd64.toml")
    parser.add_argument("target", nargs="?", type=Path, help=help_, default=default)
    help_ = "update items that changed in the last commit (default)"
    parser.add_argument("--git", help=help_, action="store_true")
    help_ = "update all items that have a modifier"
    parser.add_argument("--all", help=help_, action="store_true")
    parser.add_argument("--key", nargs="?", type=str, help="item to update")
    parser.add_argument("--debug", action="store_true", help="show debug logging.")
    args = parser.parse_args(arg_list)
    if args.key is None and args.all is False:
        args.git = True
    if args.git and args.all:
        logger.error("--all is not compatible with --git, ignoring.")
        args.all = False
    if args.all and args.key:
        logger.error("--all is not compatible with --key, ignoring.")
        args.all = False

    return args


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

    >>> url = "https://example.org/file_1.2.3_linux_amd64"
    >>> apply_modifier(url, "_checksums.txt")
    'https://example.org/file_1.2.3_checksums.txt'
    """
    filename = url[url.rindex("/") + 1 :]
    for suffix in ["_linux_amd64.tar.gz", "_linux_amd64.zip", "_linux_amd64"]:
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

    new = None
    if "modifier" in item:
        url = apply_modifier(url, item["modifier"])
        try:
            with urlopen(url) as response:
                text = response.read().decode()
        except HTTPError as error:
            logger.exception("%s responded with status code %s", url, error.status)
            return
        filename = url[url.rindex("/") + 1 :]
        new = extract(text, filename)
    elif url.startswith("https://github.com/") and "/releases/download/" in url:
        new = api(url)

    if new is None:
        logger.error("No checksum available for %s", key)
    else:
        text = target.read_text().replace(item["expected"], new)
        target.write_text(text)


def api(url: str) -> str | None:
    """Fetch the sha2556 from the GitHub releases API."""
    logger.debug("querying GitHub for sha256 for %s", url)
    filename = url[url.rindex("/") + 1 :]
    project, tag = (
        url.removeprefix("https://github.com/")
        .removesuffix("/" + filename)
        .split("/releases/download/")
    )
    api = f"https://api.github.com/repos/{project}/releases/tags/{tag}"
    logger.debug("GET %s", api)
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    with urlopen(Request(api, headers=headers, method="GET")) as response:
        text = response.read().decode()
        assets = json.loads(text).get("assets", [])

    result = None
    for asset in assets:
        if asset["name"] == filename and "digest" in asset:
            result = asset["digest"].removeprefix("sha256:")
            break

    return result


def _git(target: Path) -> list[str]:
    cmd = ("git", "show", f"HEAD^:{target}")
    result = run(cmd, capture_output=True, check=True, text=True)

    before = loads(result.stdout)
    after = loads(target.read_text())

    return [key for key in after.keys() & before.keys() if after[key] != before[key]]


if __name__ == "__main__":
    raise SystemExit(main())
