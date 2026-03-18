#!/usr/bin/env -S uv run --script
"""Create a mailbag from the backup.

First copies the Got Your Back backup from a nested structure to a flat structure.
Then calls mailbagit to derive PDFs and split out attachments.

The nested structure is implemented in backup_message:
https://github.com/GAM-team/got-your-back/blob/v1.95/gyb.py#L1839
"""

# /// script
# dependencies = ["mailbagit",]
# requires-python = ">=3.13"
# ///


from collections import Counter
from datetime import datetime, UTC
from pathlib import Path
from shutil import copy

from mailbagit import mailbag_parser, main  # pyright: ignore[reportMissingImports]

GLOB = "GYB-GMail-Backup-*@gmail.com"
FLAT = Path("flat")
_TODAY = datetime.now(tz=UTC).strftime("%Y-%m-%d")
MAILBAG = Path(f"archive-{_TODAY}-0").absolute()


def _main() -> int:
    matches = list(Path().glob(GLOB))
    if len(matches) != 1:
        print(f"Requires one directory to match the input glob '{GLOB}': {matches}")
        return 1
    source = matches[0]

    emails = list(source.rglob("*.eml"))
    counter = Counter(i.name for i in emails)
    duplicates = [name for name, count in counter.items() if count > 1]
    if duplicates:
        print("Duplicates found in {}: {}".format(source, " ".join(duplicates)))
        return 1

    if FLAT.exists() and not FLAT.is_dir():
        print(f"{FLAT} already exists and is not a directory")
        return 1

    if FLAT.exists() and FLAT.is_dir() and any(FLAT.iterdir()):
        print(f"{FLAT} already exists and is not an empty directory")
        return 1

    if not FLAT.is_dir():
        FLAT.mkdir()

    for file in emails:
        year = int(file.parts[1])
        month = int(file.parts[2])
        day = int(file.parts[3])
        id_ = file.parts[4]
        destination = FLAT / f"{year:04d}-{month:02d}-{day:02d}-{id_}"
        print(f"Copying to {destination} from {file}")
        copy(file, destination)

    args = [
        "flat",
        "--input=eml",
        "--derivatives=pdf-chrome",
        f"--mailbag={MAILBAG}",
    ]

    if MAILBAG.exists():
        print(f"{MAILBAG} already exists")
        return 1

    main(mailbag_parser.parse_args(args))
    FLAT.rmdir()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())

# local/bin/bag.py
# SPDX-License-Identifier: MPL-2.0
# Copyright 2026 Keith Maxwell
