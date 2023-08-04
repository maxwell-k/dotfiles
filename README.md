# dotfiles

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
        https://github.com/maxwell-k/dotfiles/raw/main/zsh/dot-zshrc \
    && lxc file push ~/.zshrc c1/home/maxwell-k/.zshrc \
    && lxc exec c1 -- sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," \
        /etc/passwd \
    && lxc exec c1 -- mkdir --parents "$HOME/.zsh" "$HOME/.local/bin" \
    && lxc exec c1 -- git clone \
        --branch=v4.14.0 \
        https://github.com/spaceship-prompt/spaceship-prompt.git \
        "$HOME/.zsh/spaceship" \
    && printf 'export "PATH=$PATH:/home/$LOGNAME/.local/bin"\n' \
    | lxc exec c1 -- tee "$HOME/.zshrc.local" \
    && lxc exec c1 -- su --login $LOGNAME
