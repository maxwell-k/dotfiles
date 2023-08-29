# dotfiles

<!-- toc -->

- [Shell](#shell)
- [Files](#files)

<!-- tocstop -->

## Shell

Create a new container with `git`, `fzf` and `zsh` installed:

_Debian 12_

    lxc launch images:debian/12/cloud c1 \
    && lxc exec c1 -- apt-get install --yes curl fzf git zsh

_Fedora 38_

    lxc launch images:fedora/38/cloud c1 \
    && sleep 1 \
    && lxc exec c1 -- dnf install --assumeyes curl fzf git zsh

Set up ZSH and login:

    lxc exec c1 -- curl -Lo ~/.zshrc \
        https://github.com/maxwell-k/dotfiles/raw/main/dotdrop/zshrc \
    && lxc exec c1 -- sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," \
        /etc/passwd \
    && lxc exec c1 -- mkdir --parents "$HOME/.zsh" "$HOME/.local/bin" \
    && lxc exec c1 -- git clone \
        --branch=v4.14.0 \
         --config advice.detachedHead=false \
        https://github.com/spaceship-prompt/spaceship-prompt.git \
        "$HOME/.zsh/spaceship" \
    && printf 'export "PATH=$PATH:/home/$LOGNAME/.local/bin"\n' \
    | lxc exec c1 -- tee "$HOME/.zshrc.local" \
    && lxc exec c1 -- chown --recursive "$LOGNAME:$LOGNAME" "$HOME" \
    && lxc exec c1 -- su --login "$LOGNAME"

## Files

_The steps below apply to Fedora 38._

Configure the default profile:

    printf 'export DOTDROP_PROFILE=default\n' >> ~/.zshrc.local \
    && . ~/.zshrc.local

Clone this repository, install `pipx`, `dotdrop` and a version of `peru` that is
compatible with `pipx`:

    mkdir --parents ~/github.com/maxwell-k \
    && cd ~/github.com/maxwell-k \
    && git clone https://github.com/maxwell-k/dotfiles.git \
    && sudo dnf install --assumeyes pipx \
    && pipx install dotdrop \
    && pipx install git+https://github.com/maxwell-k/peru

Install personal files:

    cd ~/github.com/maxwell-k/dotfiles \
    && peru sync \
    && dotdrop install

<!-- vim: set filetype=markdown.markdown-toc : -->
