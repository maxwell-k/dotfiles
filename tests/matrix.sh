#!/bin/sh
MATRIX_IMAGE="${MATRIX_IMAGE:-fedora/43/cloud}"
incus launch "images:$MATRIX_IMAGE" c1 \
  < "config-${MATRIX_IMAGE%%/*}.yaml" \
&& sleep 5 \
&& incus admin waitready
incus exec c1 -- cloud-init status --wait --long || true
incus file pull c1/var/log/cloud-init-output.log .
incus file pull c1/var/log/cloud-init.log .
#
# tests/matrix.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

