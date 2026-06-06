#!/usr/bin/env -S uv run --script
"""Get the latest transcript from OpenWhispr.

- Read the port and bearer token from ~/.openwhispr/cli-bridge.json.
- Query the list API to get the last transcription ID.
- Return 1 if the last transcription has not completed.
- Fetch the last transcription from the API using the ID.
- Print the text.
"""

# local/bin/openwhispr.py
# Copyright 2026 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "urllib3",
# ]
# ///

import logging
from json import load
from pathlib import Path

import urllib3

logging.basicConfig()


def _main() -> int:
    logger = logging.getLogger(__name__)

    # Read http bridge data from a configuration file
    # https://github.com/OpenWhispr/openwhispr-cli/blob/main/src/lib/config.ts#L8
    path = Path("~/.openwhispr/cli-bridge.json").expanduser()
    if not path.is_file():
        logger.error("Path does not exist: %s, is OpenWhispr running?", path)
        return 1
    with path.open("rb") as file:
        data = load(file)

    headers = urllib3.HTTPHeaderDict()
    headers.add("Authorization", "Bearer " + data["token"])
    transcriptions = "http://127.0.0.1:" + str(data["port"]) + "/v1/transcriptions"

    resp = urllib3.request("GET", transcriptions + "/list?limit=1", headers=headers)

    data = resp.json()["data"]
    if len(data) != 1:
        logger.error("Unexpected error.")
        return 1
    transcription = data[0]
    if transcription["status"] != "completed":
        logger.error(
            "Unexpected transcription status found: %s, please try again.",
            transcription["status"],
        )
        return 1

    url = transcriptions + "/" + str(transcription["id"])
    resp = urllib3.request("GET", url, headers=headers)
    print(resp.json()["data"]["text"])

    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
