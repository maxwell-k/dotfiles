lxc exec c1 -- curl -Lo ~/.zshrc \
    https://github.com/maxwell-k/dotfiles/raw/main/dotfiles/zshrc \
&& lxc exec c1 -- sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," \
    /etc/passwd \
&& lxc exec c1 -- mkdir "$HOME/.zsh" \
&& lxc exec c1 -- git clone \
    --branch=v4.14.0 \
    --config advice.detachedHead=false \
    https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship" \
&& lxc exec c1 -- chown --recursive "$LOGNAME:$LOGNAME" "$HOME"
