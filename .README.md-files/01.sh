lxc file push dotfiles/zshrc "c1/home/$LOGNAME/.zshrc" \
&& lxc exec c1 -- chown "$LOGNAME:$LOGNAME" "/home/$LOGNAME/.zshrc"
