#!/bin/sh
MATRIX_IMAGE="${MATRIX_IMAGE:-fedora/41/cloud}"
incus launch "images:$MATRIX_IMAGE" c1 \
  < "config-${MATRIX_IMAGE%%/*}.yaml" \
&& sleep 5 \
&& incus admin waitready \
&& incus exec c1 -- cloud-init status --wait --long \
&& .README.md-files/03.sh \
&& incus exec c1 -- su --login "$LOGNAME" -c \
  /home/maxwell-k/github.com/maxwell-k/dotfiles/.README.md-files/04.sh \
&& incus stop c1 \
&& incus delete c1
#
# tests/matrix.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

