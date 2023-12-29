# dotfiles

<!-- toc -->

- [Shell](#shell)
- [Files](#files)

<!-- tocstop -->

## Shell

Create a new container with `git`, `fzf` and `zsh` installed:

_Debian_

<!-- embedme .README.md-files/debian.sh -->

```
lxc launch images:debian/12/cloud c1 \
&& lxc exec c1 -- apt-get install --yes curl fzf git zsh
```

_Fedora_

    lxc launch images:fedora/39/cloud c1 \
    && sleep 1 \
    && lxc exec c1 -- dnf install --assumeyes curl fzf git zsh

Set up ZSH:

<!-- embedme .README.md-files/zsh.sh -->

```
lxc exec c1 -- curl -Lo ~/.zshrc \
    https://github.com/maxwell-k/dotfiles/raw/main/dotfiles/zshrc \
&& lxc exec c1 -- sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," \
    /etc/passwd \
&& lxc exec c1 -- mkdir --parents "$HOME/.zsh" "$HOME/.local/bin" \
&& lxc exec c1 -- git clone \
    --branch=v4.14.0 \
     --config advice.detachedHead=false \
    https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship" \
&& lxc exec c1 -- chown --recursive "$LOGNAME:$LOGNAME" "$HOME"
```

Login:

    lxc exec c1 -- su --login "$LOGNAME"

## Files

Clone this repository:

    mkdir --parents github.com/maxwell-k \
    && git -C github.com/maxwell-k \
        clone https://github.com/maxwell-k/dotfiles.git

Install personal files:

    cd ~/github.com/maxwell-k/dotfiles \
    && ./bin.py \
    && pipx run dotdrop install

See [tests](/tests/) for more examples of running `bin.py`.

<!-- vim: set filetype=markdown.embedme.markdown-toc.htmlCommentNoSpell.dprint : -->
