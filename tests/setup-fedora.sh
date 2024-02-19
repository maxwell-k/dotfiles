#!/bin/sh
incus launch --no-profiles images:fedora/39/cloud c1 <tests/incus-config.yaml \
&& sleep 5 \
&& incus admin waitready \
&& incus exec c1 -- dnf install --assumeyes python3.11 php \
#
# tests/setup-fedora.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

