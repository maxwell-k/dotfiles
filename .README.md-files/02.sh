sudo sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," /etc/passwd \
&& mkdir --parents "$HOME/.zsh" \
&& git clone --branch=v4.15.0 --config advice.detachedHead=false \
    https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship"
