#!/usr/bin/env python3
# helpers/deno.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

"""Upate the checksum for deno"""

from pathlib import Path
from tomllib import load
from urllib.request import urlopen


def main(target: str, key: str, suffix: str) -> int:
    """Update the expected hash in target using the URL plus a suffix"""
    path = Path(target)
    with path.open("rb") as file:
        item = load(file)[key]

    url = item["url"] + suffix
    with urlopen(url) as response:
        content = response.read()
    new = content.decode().split()[0]

    old = item["expected"]
    text = path.read_text().replace(old, new)
    path.write_text(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main("linux-amd64.toml", "deno", ".sha256sum"))
