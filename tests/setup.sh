#!/bin/sh
incus launch --no-profiles "images:${SETUP_IMAGE:-fedora/41/cloud}" \
  c1 < "${SETUP_CONFIG:-tests/config-fedora.yaml}" \
&& sleep 5 \
&& incus admin waitready \
&& incus exec c1 -- cloud-init status --wait \
&& incus file push bin/dotlocalslashbin.py "c1/home/$LOGNAME/" \
&& incus file push bin.toml linux-amd64.toml "c1/home/$LOGNAME/" \
&& incus exec c1 -- su --login "$LOGNAME" -c \
  "./dotlocalslashbin.py --input bin.toml --input linux-amd64.toml" \
&& incus stop c1 \
&& incus delete c1
#
# tests/setup.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

