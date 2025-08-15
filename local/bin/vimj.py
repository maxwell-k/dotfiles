#!/usr/bin/env python3
"""Open vim at the specified file, line and column.

Command to run tests:

    python -m doctest --verbose local/bin/vimj.py

vimj.py not vimj so that the command above passes.
"""
from argparse import ArgumentParser, Namespace
from os import execlp

FILE = 1
FILE_AND_LINE = 2
FILE_AND_LINE_AND_COLUMN = 3


def split(arg: str) -> tuple[str, int | None, int | None]:
    """Parse filename, line and column numbers  from argument.

    >>> split('tests/setup.sh')
    ('tests/setup.sh', None, None)
    >>> split('tests/setup.sh:11')
    ('tests/setup.sh', 11, None)
    >>> split('config/yamllint/config:13:#')
    ('config/yamllint/config', 13, None)
    >>> split('README.md:48:23')
    ('README.md', 48, 23)
    """
    components = arg.split(":", maxsplit=2)
    result: tuple[str, int | None, int | None] = ("", None, None)
    if len(components) >= FILE:
        result = (components[0], result[1], result[2])

    if len(components) >= FILE_AND_LINE and components[1].isnumeric():
        result = (result[0], int(components[1]), result[2])

    if len(components) >= FILE_AND_LINE_AND_COLUMN and components[2].isnumeric():
        result = (result[0], result[1], int(components[2]))

    return result


def _parse_args(args: list[str] | None = None) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("reference")
    return parser.parse_args(args)


def main() -> int:
    """Open vim at specified file, line and column."""
    args = _parse_args()
    file, line, column = split(args.reference)

    if line is None:
        args = (file,)
    elif column is None:
        args = ("-c", f":{line}", file)
    else:
        args = ("-c", f":{line}", "-c", f"normal {column}|", file)

    execlp("vim", "vim", *args)  # noqa: S606, S607
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# local/bin/vimj.py
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
