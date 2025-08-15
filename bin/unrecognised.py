#!/usr/bin/env python3
"""Check for unrecognised files in ~/.local/bin/."""
from pathlib import Path
from tomllib import load

TARGET = Path("~/.local/bin/").expanduser()
TOML_INPUTS = [
    "bin.toml",
    "bin/github.toml",
    "bin/linux-amd64.toml",
]


def main() -> None:
    """Check for unrecognised files in ~/.local/bin/."""
    toml = set()
    for toml_input in TOML_INPUTS:
        with Path(toml_input).open("rb") as file:
            toml |= set(load(file).keys())
    unrecognised = set(TARGET.iterdir())
    # if pulumi is in toml, then recognise pulumi-language-python and others
    unrecognised -= {i for i in unrecognised if any(i.name.startswith(j) for j in toml)}
    links = {i for i in unrecognised if i.is_symlink()}
    unrecognised -= {i for i in links if "uv" in i.readlink().parts}
    unrecognised -= {i for i in links if "dotfiles" in i.readlink().parts}
    for i in unrecognised:
        if i.name == "__pycache__":
            continue
        if not i.is_file():
            msg = f"{i} is not a file."
            raise ValueError(msg)
        try:
            text = i.read_text()
        except UnicodeDecodeError:
            text = "\n\n"
        if text.splitlines()[1].startswith("exec npm exec"):
            # wrappers around npm exec installed in vimfiles
            continue
        print(i)


if __name__ == "__main__":
    raise SystemExit(main())

# bin/unrecognised.py
# SPDX-License-Identifier: MPL-2.0
# Copyright Keith Maxwell 2025
