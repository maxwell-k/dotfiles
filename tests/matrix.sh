#!/bin/sh
MATRIX_IMAGE="${MATRIX_IMAGE:-fedora/43/cloud}"
incus create "images:$MATRIX_IMAGE" c1 \
  < "config-${MATRIX_IMAGE%%/*}.yaml" \
&& incus file push 99-preserve-hostname.cfg c1/etc/cloud/cloud.cfg.d/ \
&& incus start c1 \
&& sleep 5 \
&& incus admin waitready
incus exec c1 -- cloud-init status --wait --long || true
incus file pull c1/var/log/cloud-init-output.log .
incus file pull c1/var/log/cloud-init.log .
#
# tests/matrix.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

