incus launch images:debian/12/cloud c1 \
&& incus exec c1 -- apt-get install --yes curl file fzf git php python3.11-venv zsh
