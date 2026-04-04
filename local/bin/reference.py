#!/usr/bin/env python3
"""Helper script for reference PDFs.

reference.py find word [word…]
    Print URLs for all PDFs with any of the full words in their name
reference.py match word [word…]
    Print URLs for all PDFs with all of the full words in their name
reference.py
    Show this help

"""

# local/bin/reference.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

from collections.abc import Callable, Generator, Iterable
from itertools import tee
from os import chdir, environ
from pathlib import Path
from subprocess import check_output
from sys import argv

try:
    REFERENCE_REPOSITORY = Path(environ["REFERENCE_REPOSITORY"])
except KeyError as e:
    print("REFERENCE_REPOSITORY environment variable is required and unset")
    raise SystemExit(1) from e


def paths(extra: None | str = None) -> Generator[str]:
    """Yield each path in the repository."""
    cmd = ["git", "ls-files"] + ([extra] if extra else [])
    for i in check_output(cmd).split(b"\n"):
        if i:
            yield i.decode()


def sentences(iterator: None | Iterable[str] = None) -> Generator[list[str]]:
    """Yield the tuples of words for each file."""
    if iterator is None:
        iterator = paths()
    for path in iterator:
        yield path[11:-4].lower().split("-")


def search(
    words: list[str],
    function_: Callable[[Iterable[object]], bool] = any,
) -> Generator[str]:
    """Yield a path for each found PDF."""
    query = [i.lower() for i in words]
    paths1, paths2 = tee(paths())
    for path, sentence in zip(paths1, sentences(paths2), strict=True):
        if function_(i in sentence for i in query):
            yield path


def _argv_ok() -> bool:
    # Exit if no subcommand
    if len(argv) == 1:
        print(__doc__)
        return False

    # Just hygiene, not expected to be broken
    if min(len(i) for i in paths()) == 0:
        print("Zero length path")
        return False

    return True


def _main() -> int:
    chdir(REFERENCE_REPOSITORY)

    if not _argv_ok():
        return 1

    def command(name: str) -> bool:
        return name.startswith(argv[1])

    function = None
    if command("find"):
        function = any
    elif command("match"):
        function = all

    print("\n".join(search(argv[2:], function)) if function else __doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
