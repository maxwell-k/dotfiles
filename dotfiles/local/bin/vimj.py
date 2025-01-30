#!/usr/bin/env python3
from os import execlp
from sys import argv


def split(arg: str) -> tuple[str, int | None, int | None]:
    """Parse filename and line number from argument

    >>> split('tests/setup.sh')
    ('tests/setup.sh', None, None)
    >>> split('tests/setup.sh:11')
    ('tests/setup.sh', 11, None)
    >>> split('dotfiles/config/yamllint/config:13:#')
    ('dotfiles/config/yamllint/config', 13, None)
    >>> split('README.md:48:23')
    ('README.md', 48, 23)
    """
    components = arg.split(":", maxsplit=2)
    result: tuple[str, int | None, int | None] = ("", None, None)
    if len(components) >= 1:
        result = (components[0], result[1], result[2])

    if len(components) >= 2 and components[1].isnumeric():
        result = (result[0], int(components[1]), result[2])

    if len(components) >= 3 and components[2].isnumeric():
        result = (result[0], result[1], int(components[2]))

    return result


def main() -> int:
    if len(argv) < 2:
        print("One argument expected")
        return 1

    file, line, column = split(argv[1])

    if line is None:
        execlp("vim", "vim", file)
    elif column is None:
        execlp("vim", "vim", "-c", f":{line}", file)
    else:
        execlp("vim", "vim", "-c", f":{line}", "-c", f"normal {column}|", file)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#
# dotfiles/local/bin/vimj.py
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
# vim: set filetype=python.black.usort :
