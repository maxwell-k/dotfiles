#!/usr/bin/env python3
"""Validate a TOML file using the Python standard library.

For use with:
https://github.com/dense-analysis/ale
https://codeberg.org/maxwell-k/vimfiles/src/branch/main/ale_linters/toml/tomlv_py.vim

Example input:

    example = [
      "1"
      "2",
    ]

Example output:

    [{"lnum": 3, "col": 3, "text": "Unclosed array"}]
"""
from argparse import ArgumentParser, Namespace
from json import dumps
from pathlib import Path
from re import match
from sys import stdin
from tomllib import loads, TOMLDecodeError

STDIN = "-"

__version__ = "0.0.1"


def error(toml: str) -> tuple[int, int, str] | None:
    r"""Return (line, column, message) for invalid TOML.

    >>> _error("") is None
    True

    >>> _error("example =")
    (1, 9, 'Invalid value')

    >>> _error("x =\n")
    (1, 3, 'Invalid value')

    >>> _error('example = ["1"\n"2"]')
    (2, 1, 'Unclosed array')

    """
    try:
        loads(toml)
    except TOMLDecodeError as err:
        message = err.args[0]
    else:
        return None

    if message.endswith(marker := " (at end of document)"):
        lines = toml.splitlines()
        return (len(lines), len(lines[-1]), message.removesuffix(marker))

    result = match(r"^(.*?) \(at line (\d+), column (\d+)\)$", message)
    if result is None:
        raise _MessageError(message)
    return int(result.group(2)), int(result.group(3)), str(result.group(1))


class _MessageError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message} is not in the expected format")


def _parse_args(argv: list[str] | None) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    help_ = f"TOML file to validate, use '{STDIN}' for stdin (default: '{STDIN}')"
    parser.add_argument("filename", nargs="?", help=help_, default=STDIN)
    return parser.parse_args(argv)


def _main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    text = stdin.read() if args.filename == STDIN else Path(args.filename).read_text()
    return_code, output = 0, []
    if result := error(text):
        line, column, message = result
        return_code, output = 1, [
            {
                "lnum": line,
                "col": column,
                "text": message,
            },
        ]
    print(dumps(output))
    return return_code


if __name__ == "__main__":
    raise SystemExit(_main())

# dotfiles/local/bin/tomlv.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
