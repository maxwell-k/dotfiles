#!/usr/bin/env -S uv run --script
"""Google Keep automation."""

# local/bin/keep.py
# Copyright 2026 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "gkeepapi",
#   "keyring",
#   "gpsoauth",
# ]
# ///

import argparse
import getpass
import json
import logging
import webbrowser
from collections.abc import Callable
from os import getenv
from pathlib import Path
from typing import Literal
from uuid import getnode

from gkeepapi import Keep
from gpsoauth import exchange_token
from keyring import get_password, set_password

logger = logging.getLogger(__name__)

DUMP = Path("state.json")
EXPECTED = getenv("KEEP_PY_EXPECTED")
SERVICE_NAME = "keep.py"


Secret = Literal["master_token", "email"]


def _main() -> int:
    args = _parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    format_ = "%(levelname)s:%(name)s:%(asctime)s:" if args.debug else ""
    format_ += "%(message)s"
    logging.basicConfig(level=level, format=format_)

    return args.func(args)


def _parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=check)
    help_ = "show debug logging."
    parser.add_argument("--debug", action="store_true", help=help_)
    help_ = f"read data from {DUMP}."
    parser.add_argument("--offline", action="store_true", help=help_)
    help_ = f"write data to {DUMP}."
    parser.add_argument("--dump", action="store_true", help=help_)

    def doc(function: Callable) -> str:
        return (function.__doc__ or "").removesuffix(".").lower()

    subparsers = parser.add_subparsers()
    subparsers.add_parser("email", help=doc(email)).set_defaults(func=email)
    subparsers.add_parser("exchange", help=doc(exchange)).set_defaults(func=exchange)
    subparsers.add_parser("count", help=doc(count)).set_defaults(func=count)
    help_ = doc(check) + " (default)"
    subparsers.add_parser("check", help=help_).set_defaults(func=check)
    return parser.parse_args(args)


def exchange(_: argparse.Namespace) -> int:
    """Exchange oauth_token cookie for a master token and store securely."""
    url = "https://accounts.google.com/EmbeddedSetup"
    webbrowser.open(url)
    print(
        f"Visit <{url}>, login and agree. "
        "After agreeing the progress will continue indefinitely. "
        "Copy the value of the cookie 'oauth_token'. It will start 'oauth2_4/'. "
        "For detailed instructions visit: "
        "https://github.com/rukins/gpsoauth-java/blob/master/README.md#receiving-an-authentication-token",
    )

    email = secret("email")
    if email is None:
        logger.error("Email not available.")
        return 1
    token = getpass.getpass(prompt="ouath_token: ")
    if not token.startswith("oauth2_4/"):
        logger.error("Token should start oauth2_4/.")
        return 1

    android_id = "0123456789abcdef"
    android_id = f"{getnode():x}"

    response = exchange_token(email, token, android_id)
    master_token = response["Token"]
    if not master_token.startswith("aas_et/"):
        logger.error("Issue obtaining master token, it does not start aas_et/.")
        return 1

    secret("master_token", master_token)

    return 0


def count(args: argparse.Namespace) -> int:
    """Count the number of notes."""
    if (keep := data(args)) is None:
        return 1

    archived = sum(1 for _ in keep.find(archived=True))
    if archived:
        logger.warning("%d archived notes found.", archived)
    total = sum(1 for _ in keep.find())
    msg = f"{total} notes found."
    print(msg)
    logger.debug("Call to _count complete: '%s'", msg)
    return 0


def check(args: argparse.Namespace) -> int:
    """Check for unexpected note titles."""
    expected = set(EXPECTED.split(",") if EXPECTED else [])

    if (keep := data(args)) is None:
        return 1

    issues = 0
    for i in keep.find():
        if "," in i.title:
            logger.error("Comma found in title: '%s'.", i.title)
            issues += 1
        if i.title in expected:
            continue
        if i.title == "":
            logger.error("Note found with no title.")
        else:
            logger.error("Unexpected title: '%s'.", i.title)
        issues += 1
    if issues > 0:
        logger.error("%d issue%s found.", issues, "" if issues == 1 else "s")
    return min(issues, 1)


def data(args: argparse.Namespace) -> Keep | None:
    """Load data."""
    keep = Keep()
    if args.offline:
        if not DUMP.is_file():
            logger.error("--offline requires '%s' to be a file.", DUMP)
            return None
        if args.dump:
            logger.error("--dump and --offline are incompatible.")
            return None
        with DUMP.open("r", encoding="utf-8") as file:
            state = json.load(file)
        keep.restore(state)
        logger.info("Read '%s'", DUMP)
        return keep

    email = secret("email")
    master_token = secret("master_token")
    if not email or not master_token:
        logger.error("Email or token not available.")
        return None
    keep.authenticate(email, master_token)
    logger.info("Authenticated successfully.")

    if args.dump:
        with DUMP.open("w") as file:
            json.dump(keep.dump(), file, indent=2)
        logger.info("Wrote '%s'", DUMP)

    return keep


def email(_: argparse.Namespace) -> int:
    """Prompt for email address and store securely."""
    secret("email", input("Email: "))
    return 0


def secret(secret: Secret, value: str | None = None) -> str | None:
    """Get or set a secret securely."""
    if value is None:
        return get_password(service_name=SERVICE_NAME, username=secret)
    return set_password(service_name=SERVICE_NAME, username=secret, password=value)


if __name__ == "__main__":
    raise SystemExit(_main())
