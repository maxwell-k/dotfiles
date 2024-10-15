incus launch images:debian/12/cloud c1 \
&& incus exec c1 -- apt-get install --yes curl file fzf git python3.11-venv zsh