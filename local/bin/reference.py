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
from os import chdir, environ
from pathlib import Path
from subprocess import check_output
from sys import argv

try:
    REFERENCE_REPOSITORY = Path(environ["REFERENCE_REPOSITORY"])
except KeyError as e:
    print("REFERENCE_REPOSITORY environment variable is required and unset")
    raise SystemExit(1) from e


def search(
    words: list[str],
    function_: Callable[[Iterable[object]], bool] = any,
) -> Generator[str]:
    """Yield a path for each found PDF."""
    query = [i.lower() for i in words]
    cmd = ["git", "ls-files"]
    for i in check_output(cmd).split(b"\n"):
        if not i:
            continue
        path = i.decode()
        sentence = path[11:-4].lower().split("-")
        if function_(i in sentence for i in query):
            yield path


def _main() -> int:
    chdir(REFERENCE_REPOSITORY)

    def command(name: str) -> bool:
        return len(argv) > 1 and name.startswith(argv[1])

    function = None
    if command("find"):
        function = any
    elif command("match"):
        function = all

    print("\n".join(search(argv[2:], function)) if function else __doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
