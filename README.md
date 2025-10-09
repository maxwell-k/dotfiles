# dotfiles

<!-- toc -->

- [Prerequisites](#prerequisites)
- [1. Spaceship](#1-spaceship)
- [2. Clone](#2-clone)
- [3. Configuration files and executables](#3-configuration-files-and-executables)
- [Test strategy](#test-strategy)

<!-- tocstop -->

## Prerequisites

Command to start a container and install the dependencies for these
instructions:

    incus launch images:debian/13/cloud c1 < config-debian.yaml

Command to login:

    incus exec c1 -- su --login "$LOGNAME"

(Optional) Command to download `.zshrc` from the main branch of this repository on GitHub:

    curl --location --output ~/.zshrc \
        https://github.com/maxwell-k/dotfiles/raw/main/zshrc

## 1. Spaceship

Commands to install spaceship:

<!-- embedme .README.md-files/1.sh -->

```
mkdir --parents "$HOME/.zsh" \
&& git clone --config advice.detachedHead=false \
    --branch=v4.19.0 https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship"
```

## 2. Clone

Commands to clone this repository from GitHub:

    mkdir --parents github.com/maxwell-k \
    && git -C github.com/maxwell-k \
        clone https://github.com/maxwell-k/dotfiles.git

<!-- for equivalent setup from a local checkout see .README.md-files/2.sh -->

## 3. Configuration files and executables

Commands to install configuration files and executables:

<!-- embedme .README.md-files/3.sh -->

```
cd ~/github.com/maxwell-k/dotfiles \
&& bin/dotlocalslashbin.py \
  --input=bin/python.toml --input=bin/linux-amd64.toml --input=bin/github.toml \
&& bin/install.py
```

## Test strategy

This repository is tested against the latest stable release of Debian and Fedora
Linux, see [`.github/workflows/main.yaml`](.github/workflows/main.yaml) and
[`tests/matrix.sh`](tests/matrix.sh).

<!--
README.md
SPDX-License-Identifier: CC0-1.0
Copyright Keith Maxwell
-->
<!-- vim: set filetype=markdown.embedme.markdown-toc.htmlCommentNoSpell.dprint : -->
