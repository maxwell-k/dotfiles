cd ~/github.com/maxwell-k/dotfiles \
&& bin/dotlocalslashbin.py \
  --input=bin.toml --input=bin/linux-amd64.toml --input=bin/github.toml \
&& PATH="$HOME/.local/bin:$PATH" bin/dotdrop.toml