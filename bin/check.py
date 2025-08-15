#!/usr/bin/env python
"""Check that each file contains its filename."""
from pathlib import Path
from subprocess import check_output

TARGET = Path("dotfiles")

IGNORED = [
    ".README.md-files/01.sh",
    ".README.md-files/02.sh",
    ".README.md-files/03.sh",
    ".README.md-files/04.sh",
    ".dprint.json",
    ".en.utf-8.add",
    ".gitignore",
    ".renovaterc.json",
    ".renovaterc.json.license",
    "LICENSES/CC0-1.0.txt",
    "LICENSES/MPL-2.0.txt",
    "config/git/attributes",
    "config/git/ignore",
    "local/bin/jsonlint",
    "local/bin/prettier",
    "local/bin/pyright-langserver",
]


def _main() -> int:
    count = 0
    files = check_output(("git", "ls-files"), text=True).splitlines()
    for file in files:
        text = Path(file).read_text()
        if file not in text and file not in IGNORED:
            print(file)
            count += 1

    return min(1, count)


if __name__ == "__main__":
    raise SystemExit(_main())

# bin/check.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
