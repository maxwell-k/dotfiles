# dotfiles

<!-- toc -->

- [Shell](#shell)
- [Files](#files)

<!-- tocstop -->

## Shell

Create a new container with `git`, `fzf` and `zsh` installed:

_Debian_

    lxc launch images:debian/12/cloud c1 \
    && lxc exec c1 -- apt-get install --yes curl fzf git zsh


    lxc launch images:fedora/39/cloud c1 \
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
    && lxc exec c1 -- chown --recursive "$LOGNAME:$LOGNAME" "$HOME" \
    && lxc exec c1 -- su --login "$LOGNAME"
_Fedora_

## Files

_The steps below apply to Fedora._

Clone this repository, install `pipx` and `dotdrop`:

    mkdir --parents ~/github.com/maxwell-k \
    && cd ~/github.com/maxwell-k \
    && git clone https://github.com/maxwell-k/dotfiles.git \
    && sudo dnf install --assumeyes pipx \
    && pipx install dotdrop \

Install personal files:

    cd ~/github.com/maxwell-k/dotfiles \
    && ./bin.py
    && dotdrop install

<!--

Test `bin.py` in isolation

_Fedora 39_

    lxc launch images:fedora/39/cloud c1 \
    && sleep 1 \
    && lxc exec c1 -- dnf install --assumeyes python3.11 php \
    && lxc file push $PWD/bin.py c1/home/$LOGNAME/ \
    && lxc file push $PWD/bin.toml c1/home/$LOGNAME/ \
    && lxc exec c1 -- su --login "$LOGNAME" -c ./bin.py \
    && lxc stop c1 \
    && lxc delete c1

_Debian 12_

    lxc launch images:debian/12/cloud c1 \
    && sleep 1 \
    && lxc exec c1 -- apt-get install --yes python3 php \
    && lxc file push $PWD/bin.py c1/home/$LOGNAME/ \
    && lxc file push $PWD/bin.toml c1/home/$LOGNAME/ \
    && lxc exec c1 -- su --login "$LOGNAME" -c ./bin.py \
    && lxc stop c1 \
    && lxc delete c1

-->
<!-- vim: set filetype=markdown.markdown-toc.htmlCommentNoSpell : -->
