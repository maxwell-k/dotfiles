#!/usr/bin/env python3
"""Show information about PDFs stored in git

Requires git and optionally pdfinfo from poppler

Run in a folder of PDFs"""
from collections import Counter
from os.path import getsize
from shutil import which
from subprocess import check_output as run
from subprocess import DEVNULL


def clean(input_):
    input_ = input_.decode("utf8")
    input_ = input_.strip()
    return input_


def pdfinfo(file_):
    """pdfinfo output as a dictionary"""
    output = run(["pdfinfo", file_], stderr=DEVNULL)
    output = clean(output).split("\n")
    return dict([j.strip() for j in i.split(":", maxsplit=1)] for i in output)


def output(files, sizes, pages=None):
    """Print some summary measures"""
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


if __name__ == "__main__":
    files = run(["git", "ls-files"])
    files = clean(files).split("\n")

    sizes = [getsize(i) for i in files]

    if which("pdfinfo"):
        info = [pdfinfo(i) for i in files]
        pages = [int(i["Pages"]) for i in info]
        output(files, sizes, pages)

        authors = [i.get("Author", None) for i in info]
        print(
            "\n".join(
                "{:1d}. {:48s}{:20,d}".format(position, str(value), count)
                for position, (value, count) in enumerate(
                    Counter(authors).most_common(5), 1
                )
            )
        )

        selected = sum(1 for i in info if "A4" in i["Page size"])
        print("{:50s} {:20d}".format("[A4?] files", selected))
    else:
        output(files, sizes)

# pdf-information.py
# Copyright 2018 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
