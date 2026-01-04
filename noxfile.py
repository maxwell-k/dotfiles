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
def check(session: Session) -> None:
    """Check each path is in the file contents."""
    session.run("bin/check_each_path_is_in_file_contents.py")


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
    """Run bin/vendor.toml and check for changes."""
    for cmd in ["bin/vendor.toml", "git diff --exit-code"]:
        session.run(*cmd.split(" "))


@nox.session(python=False)
def doctest(session: Session) -> None:
    """Run all doctests in this repository."""
    for i in [
        "bin/update.py",
        "bin/install.py",
        "local/bin/mvh1.py",
    ]:
        python = "python"
        if "/// script" in Path(i).read_text():
            session.run("local/bin/venv.py", "--create", "--quiet", i)
            python = ".venv/bin/python"
        session.run(python, "-m", "doctest", "-v", i)


if __name__ == "__main__":
    nox.main()
