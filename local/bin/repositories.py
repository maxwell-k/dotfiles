#!/usr/bin/env python3
"""Find everything called .git in $HOME.

- SKIP certain directories.
- Do not print submodules or repositories inside repositories.

"""

# local/bin/repositories.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

from pathlib import Path

HOME = Path.home()

SKIP = (
    ".cache",
    ".local/share/Trash",
    ".local/share/containers",
)


def _find(start_path: Path | None = None) -> int:
    if start_path is None:
        start_path = HOME
    elif start_path.joinpath(".git").exists():
        print(f"~/{start_path.relative_to(HOME)}")
        return 0

    for child in start_path.iterdir():
        if any(child == HOME / skipped for skipped in SKIP):
            continue
        if child.is_dir():
            _find(child)

    return 0


if __name__ == "__main__":
    raise SystemExit(_find())
