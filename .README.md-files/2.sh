git bundle create HEAD.bundle HEAD \
&& incus file push HEAD.bundle c1/tmp/ \
&& rm HEAD.bundle \
&& incus exec c1 -- mkdir --parents "/home/$LOGNAME/github.com/maxwell-k/dotfiles" \
&& incus exec c1 -- git \
  -c advice.detachedHead=false \
  -C "/home/$LOGNAME/github.com/maxwell-k/dotfiles" \
  clone /tmp/HEAD.bundle . \
&& incus exec c1 -- chown --recursive "$LOGNAME:$LOGNAME" "/home/$LOGNAME/"
