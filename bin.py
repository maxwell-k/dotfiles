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
from shlex import split
from shutil import copy
from stat import S_IEXEC
from subprocess import run
from tomllib import load
from zipfile import ZipFile

DOWNLOADED = Path("downloaded")
COMPLETIONS = Path("~/.local/share/zsh/site-functions/").expanduser()
DEFAULT_DIRECTORY = "~/.local/bin/"


@contextmanager
def _download(
    *,
    url: str,
    action: str | None = None,
    target: str | None = None,
    expected: str | None = None,
    version: str | None = None,
    prefix: str | None = None,
    completions: bool = False,
    command: str | None = None,
) -> Generator[tuple[Path, Path], None, None]:
    """Context manager to download and install a program

    Arguments:
        url: the URL to download
        action: action to take to install for example copy
        target: the destination
        expected: the SHA256 hex-digest of the file at URL
        version: an argument to display the version for example --version
        prefix: to remove when untarring
        completions: whether to generate ZSH completions
        command: command to run to install after download
    """
    DOWNLOADED.mkdir(exist_ok=True)
    if url.startswith("https://"):
        source = DOWNLOADED / url.rsplit("/", 1)[1]
        if not source.is_file():
            cmd = (
                "curl",
                "--location",
                "--continue-at",
                "-",
                "--remote-name",
                "--output-dir",
                str(DOWNLOADED),
                url,
            )
            run(cmd, check=True)

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
        copy(source, target_path)
    elif action == "symlink":
        target_path.symlink_to(source)
    elif action == "unzip":
        with ZipFile(source, "r") as file:
            file.extract(target_path.name, path=target_path.parent)
    elif action == "untar":
        with tarfile.open(source, "r") as file:
            for member in file.getmembers():
                if prefix:
                    member.path = member.path.removeprefix(prefix)
                file.extract(member, path=target_path.parent)
    elif action == "command" and command is not None:
        run(split(command.format(target=target_path, source=source)), check=True)

    yield source, target_path

    if not target_path.is_symlink():
        target_path.chmod(target_path.stat().st_mode | S_IEXEC)

    if completions:
        with open(COMPLETIONS / "_{target.name}", "w") as file:
            run([target_path.name, "completion", "zsh"], check=True, stdout=file)

    if version is None:
        print(f"# {target}")
    else:
        print(f"$ {target} {version}")
        run([target_path, version], check=True)

    print()


def main():
    with open("bin.toml", "rb") as file:
        data = load(file)

    for name in data:
        with _download(**data[name]) as (source, target):
            pass


if __name__ == "__main__":
    main()
