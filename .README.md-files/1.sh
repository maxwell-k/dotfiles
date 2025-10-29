mkdir --parents "$HOME/.zsh" \
&& git clone --config advice.detachedHead=false \
    --branch=v4.19.1 https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship"