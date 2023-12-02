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
from tomllib import load
from zipfile import ZipFile

DOWNLOADED = Path("downloaded")
COMPLETIONS = Path("~/.local/share/zsh/site-functions/").expanduser()
DEFAULT_DIRECTORY = "~/.local/bin/"


@contextmanager
def _download(
    *,
    url: str,
    target: str | None = None,
    expected: str | None = None,
    version: str | None = None,
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

    yield source, target_path

    if not target_path.is_symlink():
        target_path.chmod(target_path.stat().st_mode | S_IEXEC)
    if version is None:
        print(f"# {target}")
    else:
        print(f"$ {target} {version}")
        run([target_path, version], check=True)


def main():
    with open("bin.toml", "rb") as file:
        data = load(file)

    with _download(**data["pulumi"]) as (source, target):
        with tarfile.open(source, "r") as file:
            for member in file.getmembers():
                member.path = member.path.removeprefix(f"{target.name}/")
                file.extract(member, path=target.parent)

    print()

    with _download(**data["deno"]) as (source, target):
        with ZipFile(source, "r") as file:
            file.extract(target.name, path=target.parent)

    print()

    with _download(**data["dyff"]) as (source, target):
        with tarfile.open(source, "r") as file:
            file.extract(target.name, path=target.parent)
    with open(COMPLETIONS / "_{target.name}", "w") as file:
        run([target.name, "completion", "zsh"], check=True, stdout=file)

    print()

    with _download(**data["pip"]) as (source, target):
        cmd = (
            "python3.11",
            "-m",
            "zipapp",
            "--python=/usr/bin/python3.11",
            "--output={}".format(target),
            source,
        )
        run(cmd, check=True)

    print()

    with _download(**data["a4"]) as (source, target):
        copy(source, target)

    print()

    for name in ["osc52", "hterm-notify", "hterm-show-file"]:
        with _download(**data[name]) as (source, target):
            copy(source, target)

    print()

    with _download(**data["git-jump"]) as (source, target):
        copy(source, target)

    print()

    with _download(**data["wp"]) as (source, target):
        copy(source, target)

    print()

    with _download(**data["python"]) as (source, target):
        target.symlink_to(source)


if __name__ == "__main__":
    main()
