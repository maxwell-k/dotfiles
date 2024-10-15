sudo sed -i "s,$LOGNAME:/bin/bash$,$LOGNAME:/usr/bin/zsh," /etc/passwd \
&& mkdir --parents "$HOME/.zsh" \
&& git clone --config advice.detachedHead=false \
    --branch=v4.16.2 https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship"