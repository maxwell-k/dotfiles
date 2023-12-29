lxc launch images:debian/12/cloud c1 \
&& lxc exec c1 -- apt-get install --yes curl fzf git zsh
