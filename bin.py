#!/usr/bin/python
# bin.py
# Copyright 2022 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
"""Download and extract files onto $PATH

Requires https://curl.se/"""
from contextlib import contextmanager
from hashlib import file_digest
from pathlib import Path
from shutil import copy
from stat import S_IEXEC
from subprocess import run
from zipfile import ZipFile

DOWNLOADED = Path("downloaded")


@contextmanager
def _download(url: str, expected: str | None, target: str):
    """Context manager to download and install a program

    url -- the URL to download
    expected -- the SHA256 hex-digest of the file at URL
    target -- the destination
    """
    DOWNLOADED.mkdir(exist_ok=True)
    source = DOWNLOADED / url.rsplit("/", 1)[1]
    if not source.is_file():
        run(
            [
                "curl",
                "--location",
                "--continue-at",
                "-",
                "--remote-name",
                "--output-dir",
                str(DOWNLOADED),
                url,
            ],
            check=True,
        )

    with source.open("rb") as f:
        digest = file_digest(f, "sha256")

    if expected:
        assert digest.hexdigest() == expected

    target_path = Path(target).expanduser()
    target_path.unlink(missing_ok=True)

    yield source, target_path

    target_path.chmod(target_path.stat().st_mode | S_IEXEC)
    print(f"$ {target} --version")
    run([target_path, "--version"], check=True)


def main():
    with _download(
        "https://github.com/maxwell-k/a4/releases/download/0.0.5/a4",
        # https://github.com/maxwell-k/a4/releases/download/0.0.5/SHA256SUMS
        "1495508aabcfcb979bfcedc86a0f5941463bd743ac076be4ee8a3f13859c02cf",
        "~/.local/bin/a4",
    ) as (source, target):
        copy(source, target)

    print()

    with _download(
        (
            "https://github.com/denoland/deno/releases/download/v1.38.2/"
            "deno-x86_64-unknown-linux-gnu.zip"
        ),
        # No checksum available, see
        # https://github.com/denoland/deno/issues/7253, generated manually
        "8739c81badd437f5d704f8d8299f01b171f8dd3c27ab287026e7f3198ca92fe6",
        "~/.deno/bin/deno",
    ) as (source, target):
        with ZipFile(source, "r") as file:
            file.extract("deno", path=target.parent)

    print()

    # https://pip.pypa.io/en/stable/installation/
    with _download(
        "https://bootstrap.pypa.io/pip/pip.pyz",
        None,  # not versioned, latest release
        "~/.local/bin/pip",
    ) as (source, target):
        run(
            (
                "python3.11",
                "-m",
                "zipapp",
                "--python=/usr/bin/python3.11",
                "--output={}".format(target),
                source,
            ),
            check=True,
        )


if __name__ == "__main__":
    main()
