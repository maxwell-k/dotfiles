lxc launch images:fedora/39/cloud c1 \
&& sleep 1 \
&& lxc exec c1 -- dnf install --assumeyes python3.11 php \
&& lxc file push bin.py "c1/home/$LOGNAME/" \
&& lxc file push bin.toml "c1/home/$LOGNAME/" \
&& lxc exec c1 -- su --login "$LOGNAME" -c ./bin.py \
&& lxc stop c1 \
&& lxc delete c1
#
# tests/bin-on-fedora.sh
# Copyright 2023 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
