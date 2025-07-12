#!/usr/bin/env -S uv run
# noxfile.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
# /// script
# dependencies = ["nox"]
# requires-python = ">=3.13"
# ///
"""Run checks.

Dependencies:

- [npm](https://github.com/npm/cli)
- [uv](https://github.com/astral-sh/uv)

"""
from pathlib import Path

import nox
from nox.sessions import Session

nox.options.default_venv_backend = "uv"

VENV = Path(".venv").absolute()


@nox.session(python=False)
def dev(session: Session) -> None:
    """Set up a development environment (virtual environment)."""
    metadata = nox.project.load_toml("noxfile.py")
    session.run("uv", "venv", "--python", metadata["requires-python"], VENV)
    env = {"VIRTUAL_ENV": str(VENV)}
    session.run("uv", "pip", "install", *metadata["dependencies"], env=env)


@nox.session(python=False)
def ruff(session: Session) -> None:
    """Lint all Python files."""
    cmd = "uv tool run ruff check"
    session.run(*cmd.split(" "))


@nox.session(python=False)
def reuse(session: Session) -> None:
    """Check copyright information in all files."""
    cmd = "uv tool run reuse lint"
    session.run(*cmd.split(" "))


@nox.session(python=False)
def dprint(session: Session) -> None:
    """Format files configured in .dprint.json."""
    cmd = "npm exec --yes dprint -- check"
    session.run(*cmd.split(" "))


@nox.session(python=False)
def embedme(session: Session) -> None:
    """Check the content embedded into README.md."""
    cmd = "npm exec --yes embedme -- --verify README.md"
    session.run(*cmd.split(" "))


@nox.session(python=False)
def usort(session: Session) -> None:
    """Check imports are sorted in all Python files."""
    files = session.run("git", "ls-files", "*.py", silent=True)
    if files is None:
        session.error("No files found.")
    cmd = "uv tool run usort check"
    session.run(*cmd.split(" "), *files.rstrip("\n").split("\n"))


@nox.session(python=False)
def black(session: Session) -> None:
    """Format all of the Python files."""
    cmd = "uv tool run black --check ."
    session.run(*cmd.split(" "))


@nox.session(python=False)
def vendor(session: Session) -> None:
    """Run vendor.toml and check for changes."""
    for cmd in ["./vendor.toml", "git diff --exit-code"]:
        session.run(*cmd.split(" "))


if __name__ == "__main__":
    nox.main()
