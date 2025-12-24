mkdir --parents "$HOME/.zsh" \
&& git clone --config advice.detachedHead=false \
    --branch=v4.21.0 https://github.com/spaceship-prompt/spaceship-prompt.git \
    "$HOME/.zsh/spaceship"