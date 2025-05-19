#!/usr/bin/env python3
# helpers/uv.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

"""Update the checksum for uv"""

from deno import main

if __name__ == "__main__":
    raise SystemExit(main("linux-amd64.toml", "uv", ".sha256"))
