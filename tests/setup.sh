#!/bin/sh
incus launch --no-profiles "images:${SETUP_IMAGE-fedora/39/cloud}" \
  c1 < "${SETUP_CONFIG-tests/config-fedora.yaml}" \
&& sleep 5 \
&& incus admin waitready \
&& incus exec c1 -- cloud-init status --wait
#
# tests/setup.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

