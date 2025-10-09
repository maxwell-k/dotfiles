# dotfiles

<!-- toc -->

- [Prerequisites](#prerequisites)
- [Shell](#shell)
- [Files](#files)

<!-- tocstop -->

## Prerequisites

Command to start a container and install the dependencies for these
instructions:

<!-- embedme .README.md-files/01.sh -->

```
incus launch images:debian/13/cloud c1 \
&& incus exec c1 -- apt-get install --yes curl file fzf git python3 zsh
```

Command to login:

    incus exec c1 -- su --login "$LOGNAME"

## Shell

Command to download `.zshrc` from the main branch of this repository on GitHub:

    curl --location --output ~/.zshrc \
        https://github.com/maxwell-k/dotfiles/raw/main/zshrc

Commands to switch to ZSH and install spaceship:

<!-- embedme .README.md-files/02.sh -->

```
sudo sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," /etc/passwd \
&& mkdir --parents "$HOME/.zsh" \
&& git clone --config advice.detachedHead=false \
    --branch=v4.19.0 https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship"
```

## Files

Commands to clone this repository from GitHub:

    mkdir --parents github.com/maxwell-k \
    && git -C github.com/maxwell-k \
        clone https://github.com/maxwell-k/dotfiles.git

<!-- for equivalent setup from local checkout see .README.md-files/03.sh -->

Commands to install personal files:

<!-- embedme .README.md-files/04.sh -->

```
cd ~/github.com/maxwell-k/dotfiles \
&& bin/dotlocalslashbin.py \
  --input=bin/python.toml --input=bin/linux-amd64.toml --input=bin/github.toml \
&& PATH="$HOME/.local/bin:$PATH" bin/dotdrop.toml
```

<!-- cleanup in .README.md-files/cleanup.sh not shown -->

Another example using Fedora Linux is included as in [tests](/tests/).

<!--
README.md
SPDX-License-Identifier: CC0-1.0
Copyright Keith Maxwell
-->
<!-- vim: set filetype=markdown.embedme.markdown-toc.htmlCommentNoSpell.dprint : -->
