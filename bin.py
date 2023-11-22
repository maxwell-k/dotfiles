#!/usr/bin/python
# bin.py
# Copyright 2022 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
"""Download and extract files onto $PATH

Requires https://curl.se/"""
import tarfile
from collections.abc import Generator
from contextlib import contextmanager
from hashlib import file_digest
from pathlib import Path
from shutil import copy
from stat import S_IEXEC
from subprocess import run
from zipfile import ZipFile

DOWNLOADED = Path("downloaded")
COMPLETIONS = Path("~/.local/share/zsh/site-functions/").expanduser()
DEFAULT_DIRECTORY = "~/.local/bin/"


@contextmanager
def _download(
    url: str,
    target: str | None = None,
    expected: str | None = None,
    version: str | None = "--version",
) -> Generator[tuple[Path, Path], None, None]:
    """Context manager to download and install a program

    url -- the URL to download
    expected -- the SHA256 hex-digest of the file at URL
    target -- the destination
    """
    DOWNLOADED.mkdir(exist_ok=True)
    if url.startswith("https://"):
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

        if expected and digest.hexdigest() != expected:
            raise RuntimeError("Unexpected digest for {}".format(source))
    else:
        source = Path(url)

    if target is None:
        target = DEFAULT_DIRECTORY + source.name

    target_path = Path(target).expanduser()
    target_path.unlink(missing_ok=True)

    yield source, target_path

    if not target_path.is_symlink():
        target_path.chmod(target_path.stat().st_mode | S_IEXEC)
    if version is None:
        print(f"# {target}")
    else:
        print(f"$ {target} {version}")
        run([target_path, version], check=True)


def main():
    with _download("/usr/bin/python3.12", "~/.local/bin/python") as (source, target):
        target.symlink_to(source)

    print()

    with _download(
        "https://github.com/maxwell-k/a4/releases/download/0.0.5/a4",
        # https://github.com/maxwell-k/a4/releases/download/0.0.5/SHA256SUMS
        expected="1495508aabcfcb979bfcedc86a0f5941463bd743ac076be4ee8a3f13859c02cf",
    ) as (source, target):
        copy(source, target)

    print()

    with _download(
        (
            "https://github.com/denoland/deno/releases/download/v1.38.2/"
            "deno-x86_64-unknown-linux-gnu.zip"
        ),
        "~/.deno/bin/deno",
        # No checksum available, see
        # https://github.com/denoland/deno/issues/7253, generated manually
        "8739c81badd437f5d704f8d8299f01b171f8dd3c27ab287026e7f3198ca92fe6",
    ) as (source, target):
        with ZipFile(source, "r") as file:
            file.extract(target.name, path=target.parent)

    print()

    # https://pip.pypa.io/en/stable/installation/, not versioned, latest release
    with _download(
        "https://bootstrap.pypa.io/pip/pip.pyz",
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

    print()

    with _download(
        (
            "https://github.com/homeport/dyff/releases/download/"
            "v1.5.6/dyff_1.5.6_linux_amd64.tar.gz"
        ),
        "~/.local/bin/dyff",
        "a733665e7c622ead6b18e9cc7834788bea30ea64b66273bd2062475dcd19968a",
        version="version",
    ) as (source, target):
        with tarfile.open(source, "r") as file:
            file.extract(target.name, path=target.parent)
    with open(COMPLETIONS / "_{target.name}", "w") as file:
        run([target.name, "completion", "zsh"], check=True, stdout=file)

    print()

    head = "https://raw.githubusercontent.com/libapps/libapps-mirror/master/hterm/etc"
    for tail in ["osc52.sh", "hterm-notify.sh", "hterm-show-file.sh"]:
        with _download(head + "/" + tail, version=None) as (source, target):
            copy(source, target)

    print()

    url = "https://raw.githubusercontent.com/git/git/master/contrib/git-jump/git-jump"
    with _download(url, version=None) as (source, target):
        copy(source, target)


if __name__ == "__main__":
    main()
