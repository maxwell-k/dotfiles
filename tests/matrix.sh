#!/bin/sh
MATRIX_IMAGE="${MATRIX_IMAGE:-fedora/41/cloud}"
incus launch "images:$MATRIX_IMAGE" c1 \
  < "tests/config-${MATRIX_IMAGE%%/*}.yaml" \
&& sleep 5 \
&& incus admin waitready \
&& incus exec c1 -- cloud-init status --wait --long \
&& incus file push bin/dotlocalslashbin.py "c1/home/$LOGNAME/" \
&& incus file push bin/python.toml bin/linux-amd64.toml "c1/home/$LOGNAME/" \
&& incus exec c1 -- su --login "$LOGNAME" -c \
  "./dotlocalslashbin.py --input python.toml --input linux-amd64.toml" \
&& incus stop c1 \
&& incus delete c1
#
# tests/matrix.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

