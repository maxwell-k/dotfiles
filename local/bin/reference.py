#!/usr/bin/env python3
"""Helper script for reference PDFs.

reference.py
    Show this help
reference.py check
    Exit with status 1 if any errors are found
reference.py find word [word‥]
    Print URLs for all PDFs with any of the full words in their name
reference.py match word [word‥]
    Print URLs for all PDFs with all of the full words in their name
reference.py status
    Show information including details of any errors
reference.py untracked [paths]
    Print URLs or paths for all PDFs that are not tracked in git

"""

# local/bin/reference.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0


from collections.abc import Callable, Generator, Iterable
from datetime import datetime, UTC
from itertools import tee
from os import chdir, environ
from pathlib import Path
from subprocess import check_output
from sys import argv

try:
    from enchant import DictWithPWL
except ImportError as e:
    # This script depends upon https://pyenchant.github.io/pyenchant/
    print("PyEnchant required and not installed; try python3-enchant")
    raise SystemExit(1) from e


try:
    REFERENCE_WORD_LIST = environ["REFERENCE_WORD_LIST"]
except KeyError as e:
    print("REFERENCE_WORD_LIST environment variable is required and unset")
    raise SystemExit(1) from e

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


def dates(iterator: None | Generator[str] = None) -> Generator[tuple[int, int, int]]:
    """Yield the date of each path in the repository."""
    if iterator is None:
        iterator = paths()
    for path in iterator:
        year, month, day = int(path[:4]), int(path[5:7]), int(path[8:10])
        yield (year, month, day)


def invalid_dates() -> Generator[tuple[int, int, int]]:
    """Yield any invalid dates."""
    for date in dates():
        try:
            datetime(*date, tzinfo=UTC)
        except ValueError:
            yield date


def words(iterator: None | Generator[str] = None) -> Generator[str]:
    """Yield the tuples of words for each file."""
    if iterator is None:
        iterator = paths()
    for path in iterator:
        yield from path[11:-4].split("-")


def sentences(iterator: None | Iterable[str] = None) -> Generator[list[str]]:
    """Yield the tuples of words for each file."""
    if iterator is None:
        iterator = paths()
    for path in iterator:
        yield path[11:-4].lower().split("-")


def spelling_errors() -> Generator[str]:
    """Yield each word not in the dictionary."""
    dictionary = DictWithPWL("en_GB", REFERENCE_WORD_LIST)

    for i in set(words()):
        if i.isdigit() or dictionary.check(i):
            continue
        else:
            yield i


def file_url(input_: str) -> str:
    """Return a file:/// url for an PDF."""
    return f"file://{REFERENCE_REPOSITORY / input_}"


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


def _check() -> int:
    if any(invalid_dates()) or any(spelling_errors()):
        print("Errors found, run 'reference.py status' for details")
        return 1
    return 0


def _status() -> int:
    pdfs = sum(1 for i in paths())
    print(f"{pdfs:8,d} pdf files")
    print(f"{len(set(words())):8,d} distinct words")

    # Information about date errors
    errors = 0
    for date in invalid_dates():
        errors += 1
        print("{:04d}/{:02d}/{:02d} is not a valid date".format(*date))
    print(f"{errors:8,d} invalid dates")

    # Information about spelling errors
    errors = list(spelling_errors())
    if errors:
        print("\n".join(sorted(errors)))
    print(f"{len(errors):8,d} words not in the dictionary")
    if errors:
        print(f'         see "{REFERENCE_WORD_LIST}"')
    return 0


def _find() -> int:
    for i in search(argv[2:], any):
        print(file_url(i))
    return 0


def _untracked() -> int:
    for i in paths("--others"):
        argv.pop(0)
        if len(argv) and "paths".startswith(argv[1]):
            print(REFERENCE_REPOSITORY / i)
        else:
            print(file_url(i))
    return 0


def _argv_ok() -> bool:
    # Exit if no subcommand
    if len(argv) == 1:
        print(__doc__)
        return False

    # Just hygiene, not expected to be broken
    if min(len(i) for i in paths()) == 0:
        print("Zero length path")
        return False

    if not all(i.endswith(".pdf") for i in paths()):
        print("Path without '.pdf'")
        return False

    if any(" " in i for i in paths()):
        print("Space in path")
        return False

    return True


def _main() -> int:
    chdir(REFERENCE_REPOSITORY)

    if not _argv_ok():
        return 1

    # Main functionality
    if "check".startswith(argv[1]):
        return _check()

    if "status".startswith(argv[1]):
        return _status()

    if "find".startswith(argv[1]):
        return _find()

    if "match".startswith(argv[1]):
        for i in search(argv[2:], all):
            print(file_url(i))
    elif "untracked".startswith(argv[1]):
        return _untracked()
    else:
        print(__doc__)

    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
