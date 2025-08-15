cd ~/github.com/maxwell-k/dotfiles \
&& ./dotlocalslashbin.py \
  --input=bin.toml --input=linux-amd64.toml --input=github.toml \
&& PATH="$HOME/.local/bin:$PATH" ./dotdrop.toml