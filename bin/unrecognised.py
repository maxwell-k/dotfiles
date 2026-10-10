#!/usr/bin/python3
"""Check for unrecognised files in ~/.local/bin/."""

# bin/unrecognised.py
# SPDX-License-Identifier: MPL-2.0
# Copyright 2025 Keith Maxwell

# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from pathlib import Path
from tomllib import load

TARGET = Path("~/.local/bin/").expanduser()
_REPOSITORY_ROOT = Path(__file__).parent.parent
TOML_INPUTS = [
    _REPOSITORY_ROOT / "bin/python.toml",
    _REPOSITORY_ROOT / "bin/github.toml",
    _REPOSITORY_ROOT / "bin/linux-amd64.toml",
]
LISTED = _REPOSITORY_ROOT / "recognised.toml"


def main() -> None:
    """Check for unrecognised files in ~/.local/bin/."""
    toml = set()
    for toml_input in TOML_INPUTS:
        with toml_input.open("rb") as file:
            toml |= set(load(file).keys())
    unrecognised = set(TARGET.iterdir())
    # if pulumi is in toml, then recognise pulumi-language-python and others
    unrecognised -= {i for i in unrecognised if any(i.name.startswith(j) for j in toml)}
    links = {i for i in unrecognised if i.is_symlink()}
    unrecognised -= {i for i in links if "uv" in i.readlink().parts}
    unrecognised -= {i for i in links if "dotfiles" in i.readlink().parts}
    unrecognised -= {i for i in links if ".vim" in i.readlink().parts}
    listed = set()
    if LISTED.is_file():
        with LISTED.open("rb") as file:
            for i in load(file).get("items", []):
                listed.add(i)
    for i in unrecognised:
        if i.name in listed:
            continue
        if not i.is_file():
            msg = f"{i} is not a file."
            raise ValueError(msg)
        try:
            text = i.read_text()
        except UnicodeDecodeError:
            text = "\n\n"
        if text.startswith("#!") and text.splitlines()[1].startswith("exec npm exec"):
            # wrappers around npm exec installed in vimfiles
            continue
        print(i)


if __name__ == "__main__":
    raise SystemExit(main())
