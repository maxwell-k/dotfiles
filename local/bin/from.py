#!/usr/bin/env -S uv run --script
"""Count how often an email address/domain appears in From: in .eml files.

Steps:

(1) Recursively find each file with a `.eml` extension.
(2) Parse the email address out of the "From" header.
(3) (Optionally) Extract the single domain before the public suffix in that address.
(4) Increment a count for that value
(5) Print all counts above --threshold and a total.

"""

# /// script
# dependencies = ["tldextract",]
# requires-python = ">=3.13"
# ///


import email
from argparse import ArgumentParser, Namespace
from collections import Counter
from collections.abc import Generator
from doctest import ELLIPSIS, testmod
from email.utils import parseaddr
from logging import basicConfig, DEBUG, getLogger, INFO
from pathlib import Path

from tldextract import extract  # pyright: ignore[reportMissingImports]

FILES = "*.eml"

logger = getLogger(__name__)


def _main(arg_list: list[str] | None = None) -> int:
    args = _parse_args(arg_list)

    level = DEBUG if args.debug else INFO
    format_ = "%(levelname)s:%(name)s:%(asctime)s:" if args.debug else ""
    format_ += "%(message)s"
    basicConfig(level=level, format=format_)
    logger.debug("parsed command line arguments: %s", args)

    if args.test:
        results = testmod(optionflags=ELLIPSIS)
        logger.info("test results: %s", results)
        return max(0, min(results.failed, 1))

    elements = list(_from(FILES))
    if not args.include_username:
        elements = [i.split("@", 1)[1] for i in elements]
        elements = [extract(i).top_domain_under_public_suffix for i in elements]
    counter = Counter(elements)
    emails = sum(1 for _ in Path().rglob(FILES))
    if counter.total() != emails:
        print("Totals do not match")
        return 1
    fmt = "{:8,} {}"
    for domain, count in counter.most_common():
        if count < args.threshold:
            break
        print(fmt.format(count, domain))

    if args.threshold > 0:
        print("         …")
    print(fmt.format(emails, "Total"))
    return 0


def _parse_args(arg_list: list[str] | None) -> Namespace:
    """Parse command line arguments.

    >>> _parse_args([])
    Namespace(debug=False, threshold=5, include_username=False, test=False)

    >>> _parse_args(["--debug", "--threshold=0", "--include-username", "--test"])
    Namespace(debug=True, threshold=0, include_username=True, test=True)
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--debug", action="store_true", help="Show debug logging.")
    help_ = "Hide if count is below this threshold."
    parser.add_argument("--threshold", default=5, type=int, help=help_)
    help_ = "Include the local part of the email address before the @."
    parser.add_argument("--include-username", action="store_true", help=help_)
    help_ = "Run doctest against this file."
    parser.add_argument("--test", action="store_true", help=help_)
    return parser.parse_args(arg_list)


def _from(glob: str) -> Generator[str]:
    for i in Path().rglob(glob):
        msg = email.message_from_bytes(i.read_bytes())
        from_ = msg["From"]  # Forename Surname <forename.surname@example.com>
        if from_ is not None:
            yield parseaddr(from_)[1]  # forename.surname@example.com


if __name__ == "__main__":
    raise SystemExit(_main())

# local/bin/from.py
# SPDX-License-Identifier: MPL-2.0
# Copyright 2026 Keith Maxwell
