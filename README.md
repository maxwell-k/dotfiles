# dotfiles

<!-- toc -->

- [Shell](#shell)
- [Files](#files)

<!-- tocstop -->

## Shell

Create a new container with `git`, `fzf` and `zsh` installed:

_Debian_

<!-- embedme .README.md-files/00.sh -->

```
lxc launch images:debian/12/cloud c1 \
&& lxc exec c1 -- apt-get install --yes curl fzf git zsh
```

_Fedora_

    lxc launch images:fedora/39/cloud c1 \
    && sleep 1 \
    && lxc exec c1 -- dnf install --assumeyes curl fzf git zsh

Set up ZSH from the main branch of this repository on GitHub:

<!-- embedme .README.md-files/02.sh -->

```
lxc exec c1 -- curl -Lo ~/.zshrc \
    https://github.com/maxwell-k/dotfiles/raw/main/dotfiles/zshrc \
&& lxc exec c1 -- sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," \
    /etc/passwd \
&& lxc exec c1 -- mkdir "$HOME/.zsh" \
&& lxc exec c1 -- git clone \
    --branch=v4.15.0 \
    --config advice.detachedHead=false \
    https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship" \
&& lxc exec c1 -- chown --recursive "$LOGNAME:$LOGNAME" "$HOME"
```

Login:

    lxc exec c1 -- su --login "$LOGNAME"

<!-- cleanup in .README.md-files/cleanup.sh not shown -->

## Files

Create a suitable new container, with dependencies for `bin.py` and
`dotdrop`:

<!-- embedme .README.md-files/files-00.sh -->

```
lxc launch images:debian/12/cloud c1 \
&& lxc exec c1 -- apt-get install --yes file git php python3.11-venv
```

Clone this repository from GitHub:

    mkdir --parents github.com/maxwell-k \
    && git -C github.com/maxwell-k \
        clone https://github.com/maxwell-k/dotfiles.git

<!-- for equivalent setup from local checkout see .README.md-files/files-01.sh -->

Install personal files:

<!-- embedme .README.md-files/files-02.sh -->

```
cd ~/github.com/maxwell-k/dotfiles \
&& ./bin.py \
&& ~/.local/bin/pipx run dotdrop install --profile=default
```

<!-- cleanup in .README.md-files/cleanup.sh not shown -->

See [tests](/tests/) for more examples of running `bin.py`.

<!-- vim: set filetype=markdown.embedme.markdown-toc.htmlCommentNoSpell.dprint : -->
