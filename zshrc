# shellcheck shell=sh disable=SC1090,SC1091,SC1094
#
#    For portability use POSIX compatible shell script syntax where possible
#
# zshrc
# Copyright 2025 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
#
bindkey -v  # vi mode, see man zshzle
setopt interactive_comments
FPATH="$FPATH:$HOME/.local/share/zsh/site-functions"
# Files for command line completion {{{1
# these files must be generated before the compinit commands
site="$HOME/.local/share/zsh/site-functions"
executable="$HOME/.local/share/uv/tools/nox/bin/register-python-argcomplete"
if [ -x "$executable" ] && [ ! -f "$site/_nox" ] ; then
  mkdir --parents "$site"
  "$executable" nox >> "$site/_nox"  # starts with a compdef line
  rm -f "$HOME/.zcompdump"
fi
executable="$HOME/.local/bin/uv"
if [ -x "$executable" ] && [ ! -f "$site/_uv" ] ; then
  mkdir --parents "$site"
  "$executable" generate-shell-completion zsh >> "$site/_uv"
  rm -f "$HOME/.zcompdump"
fi
unset executable site #}}}1
autoload -U compinit && compinit
autoload -U bashcompinit && bashcompinit  # for nox above
# Aliases {{{1
alias cp="cp -i"  # To avoid accidentally over-writing content
alias mv="mv -i"  # "
alias rm="rm -i"  # To avoid accidentally deleting content
alias ls="ls --color=auto --group-directories-first"
alias lc="tig --reverse remotes/origin/HEAD.."
# Functions for use as commands {{{1
# <80 characters, alphabetically sorted {{{
gcd() { cd "$(git rev-parse --show-toplevel)" || return ; }
lfcd () { cd "$(command lf -print-last-dir "$@")" || return ; }
ywd() { printf '%s' "$PWD" | sed "s,^$HOME,~," | ygg ; printf '\n' ; }
yz() { fc -l -n 0- | fzf --tac | osc52.sh ; }
# }}}
motd() { #{{{
  : > /run/motd && systemctl --user restart uncommitted && cat /run/motd
} #}}}
yy() { # {{{
  if [ ! -t 0 ] ; then
    tail -n 1
  else
    fc -ln -1
  fi | tr -d '\n' | ygg ; >&2 printf '\n'
} # }}}
# }}}
# Editing command lines {{{1
bindkey -M vicmd v edit-command-line
autoload edit-command-line
zle -N edit-command-line
bindkey -M viins '^o' execute-named-cmd #{{{
# using `escape` then `:` causes the result of `execute-named-cmd` to be
# inserted before the last character of the existing line
# }}}
# FZF key bindings {{{
key_bindings=/usr/share/fzf/shell/key-bindings.zsh
if [ ! -f "$key_bindings" ] && [ -d /opt/homebrew/Cellar/fzf ] ; then
  key_bindings="$(find /opt/homebrew/Cellar/fzf -name key-bindings.zsh)"
fi
if [ -f "$key_bindings" ] ; then
  # load binding for ctrl-r ^r
  . "$key_bindings"
  # prefer ctrl-e to alt-c
  bindkey -M vicmd -r '\ec'
  bindkey -M viins -r '\ec'
  bindkey -M vicmd '^e' fzf-cd-widget
  bindkey -M viins '^e' fzf-cd-widget
else
   echo "zshrc: key-bindings.zsh from fzf not found"
fi
unset key_bindings #}}}
# Ctrl-f to present an fzf menu of fzf menus {{{
zshrc_fzf_fzf() {
  cmd=$( fzf<<EOF
git status --short | fzf --multi | cut -c4-
find | fzf --multi
git diff --name-only HEAD^..HEAD | fzf --multi
git ls-files | fzf --multi
git ls-files --others --exclude-standard | fzf --multi
EOF
  )
  # shellcheck disable=SC2016
  cmd="$cmd"' | while read item; do echo -n "${(q)item} "; done'  # applies quoting
  LBUFFER="$LBUFFER$(eval "$cmd")"
  unset cmd
  # local is better than POSIX alternatives
  # shellcheck disable=SC3043
  local ret=$?
  zle reset-prompt
  return $ret
}
zle -N zshrc_fzf_fzf
bindkey _M viins '^f' zshrc_fzf_fzf
bindkey _M vicmd '^f' zshrc_fzf_fzf
# }}}
# Ctrl-p to select a git commit hash with tig {{{
zshrc_tig() {
  # relies on the following in config_home/tig/config
  # bind refs <Ctrl-g> <sh -c "echo %(refname) >/tmp/tig-output"
  # bind generic <Ctrl-g> <sh -c "echo %(commit) >/tmp/tig-output"
  #
  # reset to known good state
  /bin/rm -f /tmp/tig-output

  tig </dev/tty
  # local is better than POSIX alternatives
  # shellcheck disable=SC3043
  local ret=$?
  if [ -f /tmp/tig-output ] ; then
    read -r tig_output </tmp/tig-output
    LBUFFER="$LBUFFER $tig_output"
    unset tig_output
    zle reset-prompt
  fi

  /bin/rm -f /tmp/tig-output
  return $ret
}
zle -N zshrc_tig
bindkey _M viins '^p' zshrc_tig
bindkey _M vicmd '^p' zshrc_tig
#}}}
zmodload zsh/complist
zshrc_menu_select() { zle expand-or-complete; zle menu-select ; }
zle -N zshrc_menu_select
bindkey -M viins '^[j' zshrc_menu_select
bindkey -M menuselect j down-history
bindkey -M menuselect k up-history
bindkey -M menuselect l vi-forward-char
bindkey -M menuselect h vi-backward-char
bindkey -M menuselect '^[' undo
bindkey -M menuselect '^I' accept-and-hold  # ^I = Tab
# }}}1
# Environment variables {{{1
# Interactive command line {{{2
# Set the PATH {{{3
#
# On MacOS /usr/libexec/path_helper changes the order of the entries in PATH.
# Following the advice in the gist below I do not use a separate zshenv file to
# avoid that issue.
# https://gist.github.com/Linerre/f11ad4a6a934dcf01ee8415c9457e7b2
#
for i in \
  "$HOME/.deno/bin" \
  "$HOME/.local/bin" \
  ;
do
    if ! test -d "$i" ; then continue ; fi
    case "$PATH" in
      *"$i"*) true ;;
      *) export PATH="$i:$PATH" ;;
    esac
done
unset i # }}}3
if [ -x /usr/bin/vim ]; then
  export EDITOR=vim
else
  export EDITOR=vi
fi
export FCEDIT=$EDITOR
export READNULLCMD=cat  # more is the default
if fzf --version >/dev/null 2>&1 ; then export FZF_DEFAULT_OPTS='--height=10 --bind=ctrl-a:select-all' ; fi
if command -v pager >/dev/null ; then export PAGER=pager ; fi
# https://chromium.googlesource.com/apps/libapps/+/master/nassh/doc/FAQ.md#Why-do-curses-apps-display-x_q_etc_instead-of-and-and-other-graphics
export NCURSES_NO_UTF8_ACS=1
# Wider {{{2
export ANSIBLE_COLLECTIONS_PATH="$HOME/.ansible/collections:/usr/lib/python3.12/site-packages/ansible_collections/"
export DOTDROP_PROFILE=default
# }}}1
# Prompt — PS1 {{{1
# https://spaceship-prompt.sh
if [ -f "$HOME/.zsh/spaceship/spaceship.zsh" ] && [ -z "$SPACESHIP_DISABLE" ] ; then
  spaceship_tmux() {  # show a computer inside tmux
    tmux_status=""
    [ -n "$TMUX" ] && tmux_status="💻 "
    spaceship::section::v4 --color white "$tmux_status"
    unset tmux_status
  }
  # the SPACESHIP_* variables are used inside spaceship
  # shellcheck disable=SC2034
  {
    # SPACESHIP_PROMPT_ORDER needs to be an array
    # shellcheck disable=SC3030
    SPACESHIP_PROMPT_ORDER=(
      dir           # Current directory section
      tmux          # See spaceship_tmux above
      venv          # virtualenv section
      git           # Git section (git_branch + git_status)
      host          # Host name so it is clear if using toolbox
      exec_time     # Execution time
      line_sep      # Line break
      jobs          # Background jobs indicator
      exit_code     # Exit code section
      char          # Prompt character
    )
    SPACESHIP_HOST_SHOW=always
    SPACESHIP_PROMPT_PREFIXES_SHOW=false
    SPACESHIP_EXIT_CODE_SHOW=true
    SPACESHIP_GIT_BRANCH_PREFIX="🪵 "
    SPACESHIP_CHAR_SYMBOL="%% "
    SPACESHIP_EXIT_CODE_SYMBOL=""
    SPACESHIP_VENV_SYMBOL="🧫 "
    SPACESHIP_DIR_LOCK_SYMBOL="🔒"
    SPACESHIP_VENV_COLOR=207
  }
  . "$HOME/.zsh/spaceship/spaceship.zsh"
elif [ -n "$TMUX" ] ; then
  PS1="%? ⁅%23<<%d⁆%# "
else
  PS1="%? [%23<<%d]%# "
fi
# }}}
if [ -s /run/motd ]; then cat /run/motd ; fi
if [ -f ~/.zshrc.local ]; then . ~/.zshrc.local ; fi # late so that PS1 & spaceship can be overridden
# vim: set foldmethod=marker foldlevel=0 filetype=sh :
