#!/bin/sh
incus launch --no-profiles "images:${SETUP_IMAGE-fedora/40/cloud}" \
  c1 < "${SETUP_CONFIG-tests/config-fedora.yaml}" \
&& sleep 5 \
&& incus admin waitready \
&& incus exec c1 -- cloud-init status --wait \
&& incus file push dotlocalslashbin.py "c1/home/$LOGNAME/" \
&& incus file push bin.toml "c1/home/$LOGNAME/" \
&& incus exec c1 -- su --login "$LOGNAME" -c ./dotlocalslashbin.py \
&& incus stop c1 \
&& incus delete c1
#
# tests/setup.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

