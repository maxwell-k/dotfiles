#!/usr/bin/env python3
# bin/install.py
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
"""Install symbolic links to files in this repository.

Maintain compatibility with the system Python on Debian stable. Today that is
Python 3.11.
"""

from os.path import relpath
from pathlib import Path
from subprocess import run

HOME = Path.home()

SPECIFICATIONS: list[tuple[str] | tuple[str, str]] = [
    ("~/.config/ghostty/config",),
    ("~/.config/git/attributes",),
    ("~/.config/git/config",),
    ("~/.config/git/ignore",),
    ("~/.config/lf/lfrc",),
    ("~/.config/litecli/config",),
    ("~/.config/newsboat/config",),
    ("~/.config/newsboat/urls",),
    ("~/.config/pgcli/config",),
    ("~/.config/tig/config",),
    ("~/.config/yamllint/config",),
    ("~/.local/bin/adf",),
    ("~/.local/bin/ansible-lint",),
    ("~/.local/bin/gtree",),
    ("~/.local/bin/lint-all",),
    ("~/.local/bin/mvh1", "local/bin/mvh1.py"),
    ("~/.local/bin/mvslugify",),
    ("~/.local/bin/pdf-information.py",),
    ("~/.local/bin/percollate",),
    ("~/.local/bin/reference.py",),
    ("~/.local/bin/repositories.py",),
    ("~/.local/bin/ygg",),
    ("~/.tmux.conf",),
    ("~/.zshrc",),
]


def _determine(
    specification: tuple[str] | tuple[str, str],
    repository: str | Path | None = None,
) -> tuple[Path, Path]:
    """Determine the link and the target from the specification.

    >>> _determine(('~/.a',), '~/b')
    (PosixPath('~/.a'), PosixPath('b/a'))

    >>> _determine(('~/.a/b', 'a/b.py'), '~/d')
    (PosixPath('~/.a/b'), PosixPath('../d/a/b.py'))
    """
    repository = _repository() if repository is None else Path(repository)
    relative = Path(repository).relative_to(Path("~"))
    link_string = specification[0]
    link = Path(link_string)
    prefix = Path(relpath(Path("~"), link.parent))
    if len(specification) == 1:
        tail = link_string.removeprefix("~/.")
    else:
        tail = specification[1]
    target = prefix / relative / tail
    return (link, target)


def _repository() -> Path:
    """Tilde path to the repository root."""
    result = run(
        ["/usr/bin/git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path("~") / Path(result.stdout.rstrip()).relative_to(Path.home())


def _main() -> int:

    def correct(link: Path, relative_target: Path) -> bool:
        return link.is_symlink() and link.readlink() == relative_target

    paths = list(map(_determine, SPECIFICATIONS))

    problems = 0
    for tilde_link, relative_target in paths:

        link = tilde_link.expanduser()
        if link.exists(follow_symlinks=False) and not correct(link, relative_target):
            print(f"{link} exists and must be removed first")
            problems += 1

        target = link.parent / relative_target
        if not target.resolve().exists():
            # target.exists() can be false here
            print(f"{target} does not exist and must be created first")
            problems += 1

    if problems:
        return 1

    for tilde_link, relative_target in paths:
        link = tilde_link.expanduser()
        created = " "
        if not correct(link, relative_target):
            if not link.parent.is_dir():
                link.parent.mkdir(parents=True)
            link.symlink_to(relative_target)
            created = "+"
        print(f"{created} {tilde_link} -> {relative_target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
