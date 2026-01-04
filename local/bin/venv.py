#!/usr/bin/env python
"""Check and optionally set up a virutal environment.

Based on inline script metadata. Requires uv. Does not support version
specifiers in package dependencies.
"""

# local/bin/venv.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

import argparse
import logging
import re
import tomllib
from json import loads
from os import access, environ, X_OK
from pathlib import Path
from shlex import quote
from subprocess import CompletedProcess, PIPE, run
from typing import cast

REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
VIRTUAL_ENVIRONMENT = Path(".venv")
PYTHON = VIRTUAL_ENVIRONMENT / "bin/python"

DEBUG = "DEBUG" in environ


logger = logging.getLogger(__name__)


def _main() -> int:
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

    args = _parse_args()
    logger.debug("args %s", args)

    metadata = _read(args.script.read_text())
    if metadata is None:
        logger.error("No metadata found.")
        return 1
    logger.debug("metadata %s", metadata)

    required = metadata.get("requires-python", None)
    logger.debug("requires-python %s", required)
    if args.create:
        cmd = ["uv", "venv", "--clear"]
        if required:
            cmd.append("--python=" + required)
        cmd.append(str(VIRTUAL_ENVIRONMENT))
        _run(cmd)

    if not access(PYTHON, X_OK):
        logger.error("%s is not executable, do you want to --create it?", PYTHON)
        return 1

    if required and not required.startswith(">="):
        logger.warning("Requirement comparison not supported: %s", required)

    if required and required.startswith(">="):
        result = _run((str(PYTHON), "--version"), stdout=True)
        logger.debug("stdout.strip() %s", result.stdout.strip())
        version = result.stdout.removeprefix("Python ")
        actual = tuple(int(i) for i in version.split("."))
        expected = tuple(int(i) for i in required.removeprefix(">=").split("."))
        if not actual >= expected:
            logger.error("Incorrect Python version found: %s", version)
            return 1

    dependencies = cast("set[str]", metadata.get("dependencies", set()))
    logger.debug("dependencies %s", dependencies)
    if args.create:
        cmd = ("uv", "pip", "install", *dependencies)
        _run(cmd)
    cmd = ("uv", "pip", "list", "--format=json")
    result = run(cmd, check=True, capture_output=True, text=True)
    names = {i["name"] for i in loads(result.stdout)}
    logger.debug("names %s", names)
    missing = set(dependencies) - names
    if missing:
        logger.error("Missing dependencies: %s", missing)
        return 1

    return 0


def _run(
    cmd: list[str] | tuple[str, ...],
    *,
    stdout: bool = False,
) -> CompletedProcess:
    logger.debug("Running: %s", " ".join(quote(i) for i in cmd))
    if stdout:
        return run(cmd, check=True, stdout=PIPE, text=True)
    return run(cmd, check=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    help_ = "script with inline metadata"
    parser.add_argument("script", type=Path, help=help_)
    help_ = "create a new virtual environment"
    parser.add_argument("-c", "--create", action="store_true", help=help_)
    return parser.parse_args()


def _read(script: str) -> dict | None:
    name = "script"
    matches = list(
        filter(lambda m: m.group("type") == name, re.finditer(REGEX, script)),
    )
    if len(matches) > 1:
        msg = f"Multiple {name} blocks found"
        raise ValueError(msg)

    if len(matches) == 0:
        return None
    content = "".join(
        line[2:] if line.startswith("# ") else line[1:]
        for line in matches[0].group("content").splitlines(keepends=True)
    )
    return tomllib.loads(content)


if __name__ == "__main__":
    raise SystemExit(_main())
