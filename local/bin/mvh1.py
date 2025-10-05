#!/usr/bin/env -S uv run --script
"""Read each filename, find the top level heading, slugify and move the file.

**The .py extension is necessary so that doctests function.**

Command to setup a development environment:

    ./noxfile.py --session dev

Command to run tests:

    .venv/bin/python -m doctest --verbose local/bin/mvh1.py

Command to install a coverage tool:

    uv pip install coverage

Command to produce an coverage report in HTML:

    .venv/bin/python -m coverage run -m doctest --verbose local/bin/mvh1.py \
    && .venv/bin/python -m coverage html
"""

# local/bin/mvh1.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

# /// script
# dependencies = ["python-slugify", "markdown-it-py"]
# requires-python = ">=3.13"
# ///

from argparse import ArgumentParser, Namespace
from pathlib import Path

from markdown_it import MarkdownIt
from slugify import slugify


def _parse_args(args: list[str] | None = None) -> Namespace:
    """Parse command line arguments.

    >>> _parse_args(['one.md']).path, len(_parse_args(['one.md', 'two.md']).path)
    ([PosixPath('one.md')], 2)

    >>> _parse_args(['one.md']).dry_run, _parse_args(['--dry-run', 'one.md']).dry_run
    (False, True)

    """
    parser = ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Do not move any files")
    parser.add_argument("path", nargs="+", type=Path)
    return parser.parse_args(args)


def _h1(text: str) -> str | None:
    r"""Return b.

    >>> _h1('# Simple')
    'Simple'

    >>> _h1('# `code` <https://example.org>')
    '`code` <https://example.org>'

    >>> (_h1(''), _h1('Underlined\n=========='))
    (None, None)

    """
    tokens = MarkdownIt().parse(text)
    try:
        h1 = next(i for i in tokens if i.tag == "h1")
    except StopIteration:
        return None
    if h1.markup != "#" or h1.map is None:
        return None
    text = "".join(text.splitlines()[slice(*h1.map)])
    return text.removeprefix(h1.markup).lstrip()


def _main() -> int:
    """Read each filename, find the top level heading, slugify and move the file."""
    parsed = _parse_args()
    for path in parsed.path:
        if not path.is_file():
            print(f"'{path}' does not exist")
            continue
        h1 = _h1(path.read_text())
        if h1 is None:
            print(f"No h1 found in '{path}'")
            continue
        after = path.parent.joinpath(slugify(h1, lowercase=False) + ".md")
        if after == path:
            continue
        print(f"'{path}' → '{after}'")
        if not parsed.dry_run:
            path.rename(after)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
