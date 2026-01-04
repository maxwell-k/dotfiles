#!/usr/bin/env python3
"""Show information about PDFs stored in git.

Requires git and optionally pdfinfo from poppler

Run in a folder of PDFs
"""

# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from collections import Counter
from pathlib import Path
from shutil import which
from subprocess import check_output as run, DEVNULL

GIT = "/usr/bin/git"
PDFINFO = "/usr/bin/pdfinfo"


def _clean(input_: bytes) -> str:
    return input_.decode("utf8").strip()


def pdfinfo(file_: str) -> dict:
    """Pdfinfo output as a dictionary."""
    output = run([PDFINFO, file_], stderr=DEVNULL)
    output = _clean(output).split("\n")
    return dict([j.strip() for j in i.split(":", maxsplit=1)] for i in output)


def output(files: list[str], sizes: list[int], pages: list[int] | None = None) -> None:
    """Print some summary measures."""
    total = sum(sizes)
    rows = [
        ["Number of files", len(files), "20,d"],
        ["Total number of bytes", total, ">20,d"],
        ["Average number of bytes", total, "23,.2f"],
    ]
    if pages is not None:
        rows += [
            ["Total pages", sum(pages), "20,d"],
            ["Average number of pages", sum(pages) / len(files), "23.2f"],
            ["Average number of bytes per page", total, "23,.2f"],
        ]
    print("\n".join("{0:50s} {1:{2}}".format(*row) for row in rows))


def main() -> int:
    """Report information on all files in git."""
    files = run([GIT, "ls-files"])
    files = _clean(files).split("\n")

    sizes = [Path(i).stat().st_size for i in files]

    if which("pdfinfo"):
        info = [pdfinfo(i) for i in files]
        pages = [int(i["Pages"]) for i in info]
        output(files, sizes, pages)

        authors = [i.get("Author", None) for i in info]
        print(
            "\n".join(
                f"{position:1d}. {value!s:48s}{count:20,d}"
                for position, (value, count) in enumerate(
                    Counter(authors).most_common(5),
                    1,
                )
            ),
        )

        selected = sum(1 for i in info if "A4" in i["Page size"])
        print("{:50s} {:20d}".format("[A4?] files", selected))
    else:
        output(files, sizes)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# local/bin/pdf-information.py
# Copyright 2018 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
