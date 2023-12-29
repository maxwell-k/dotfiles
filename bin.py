#!/usr/bin/env python3
# bin.py
# Copyright 2022 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
"""Download and extract files from bin.toml onto $PATH"""
import tarfile
from collections.abc import Generator
from contextlib import contextmanager
from hashlib import file_digest
from pathlib import Path
from shlex import split
from shutil import copy
from stat import S_IEXEC
from subprocess import run
from tomllib import load
from urllib.request import urlopen
from zipfile import ZipFile

DOWNLOADED = Path("downloaded")
COMPLETIONS = Path("~/.local/share/zsh/site-functions/").expanduser()
DEFAULT_DIRECTORY = "~/.local/bin/"


@contextmanager
def _download(
    *,
    name: str,
    url: str,
    action: str | None = None,
    target: str | None = None,
    expected: str | None = None,
    version: str | None = None,
    prefix: str | None = None,
    completions: bool = False,
    command: str | None = None,
    ignore: set = set(),
) -> Generator[tuple[Path, Path], None, None]:
    """Context manager to download and install a program

    Arguments:
        url: the URL to download
        action: action to take to install for example copy
        target: the destination
        expected: the SHA256 or SHA512 hex-digest of the file at URL
        version: an argument to display the version for example --version
        prefix: to remove when untarring
        completions: whether to generate ZSH completions
        command: command to run to install after download
    """
    if target is None:
        target = DEFAULT_DIRECTORY + name

    DOWNLOADED.mkdir(exist_ok=True)
    if url.startswith("https://"):
        downloaded = DOWNLOADED / url.rsplit("/", 1)[1]
        if not downloaded.is_file():
            with urlopen(url) as fp, downloaded.open("wb") as dp:
                if "content-length" in fp.headers:
                    size = int(fp.headers["Content-Length"])
                else:
                    size = -1

                print(f"Downloading {name}…")
                written = dp.write(fp.read())

            if size >= 0 and written != size:
                raise RuntimeError("Wrong content length")

        if expected:
            digest = "sha256"
            if len(expected) == 128:
                digest = "sha512"
            with downloaded.open("rb") as f:
                digest = file_digest(f, digest)

            if digest.hexdigest() != expected:
                raise RuntimeError("Unexpected digest for {}".format(downloaded))
    else:
        downloaded = Path(url)

    target_path = Path(target).expanduser()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.unlink(missing_ok=True)

    if action is None:
        if url.endswith(".tar.gz"):
            action = "untar"
        elif url.endswith(".zip"):
            action = "unzip"
        elif url.startswith("/"):
            action = "symlink"
        elif command:
            action = "command"
        else:
            action = "copy"

    if action == "copy":
        copy(downloaded, target_path)
    elif action == "symlink":
        target_path.symlink_to(downloaded)
    elif action == "unzip":
        with ZipFile(downloaded, "r") as file:
            file.extract(target_path.name, path=target_path.parent)
    elif action == "untar":
        with tarfile.open(downloaded, "r") as file:
            for member in file.getmembers():
                if prefix:
                    member.path = member.path.removeprefix(prefix)
                if member.path in ignore:
                    continue
                file.extract(member, path=target_path.parent)
    elif action == "command" and command is not None:
        kwargs = dict(target=target_path, downloaded=downloaded)
        run(split(command.format(**kwargs)), check=True)

    yield downloaded, target_path

    if not target_path.is_symlink():
        target_path.chmod(target_path.stat().st_mode | S_IEXEC)

    if completions:
        COMPLETIONS.mkdir(parents=True, exist_ok=True)
        with open(COMPLETIONS / f"_{target_path.name}", "w") as file:
            run([target_path, "completion", "zsh"], check=True, stdout=file)

    if version is None:
        print(f"# {target}")
    else:
        print(f"$ {target} {version}")
        run([target_path, version], check=True)

    print()


def main() -> int:
    with open("bin.toml", "rb") as file:
        data = load(file)

    for name, kwargs in data.items():
        kwargs["name"] = name
        with _download(**kwargs) as (downloaded, target):
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
