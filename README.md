# dotfiles

<!-- toc -->

- [Prerequisites](#prerequisites)
- [Shell](#shell)
- [Files](#files)

<!-- tocstop -->

## Prerequisites

Start with a container including the dependencies for these instructions,
`bin.py` and `dotdrop`:

<!-- embedme .README.md-files/01.sh -->

```
lxc launch images:debian/12/cloud c1 \
&& lxc exec c1 -- apt-get install --yes curl file fzf git php python3.11-venv zsh
```

Login:

    lxc exec c1 -- su --login "$LOGNAME"

## Shell

Download `.zshrc` form the main branch of this repository on GitHub:

    curl --location --output ~/.zshrc \
        https://github.com/maxwell-k/dotfiles/raw/main/dotfiles/zshrc

Switch to ZSH and install spaceship:

<!-- embedme .README.md-files/02.sh -->

```
sudo sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," /etc/passwd \
&& mkdir "$HOME/.zsh" \
&& git clone --branch=v4.15.0 --config advice.detachedHead=false \
    https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship"
```

## Files

Clone this repository from GitHub:

    mkdir --parents github.com/maxwell-k \
    && git -C github.com/maxwell-k \
        clone https://github.com/maxwell-k/dotfiles.git

<!-- for equivalent setup from local checkout see .README.md-files/03.sh -->

Install personal files:

<!-- embedme .README.md-files/04.sh -->

```
cd ~/github.com/maxwell-k/dotfiles \
&& ./bin.py \
&& ~/.local/bin/pipx run dotdrop install --profile=default
```

<!-- cleanup in .README.md-files/cleanup.sh not shown -->

See [tests](/tests/) for more examples of running `bin.py` including on Fedora.

<!-- vim: set filetype=markdown.embedme.markdown-toc.htmlCommentNoSpell.dprint : -->
