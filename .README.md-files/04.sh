cd ~/github.com/maxwell-k/dotfiles \
&& ./dotlocalslashbin.py \
  --input=bin.toml --input=linux-amd64.toml --input=github.toml \
&& ~/.local/bin/uv tool run dotdrop install --profile=default