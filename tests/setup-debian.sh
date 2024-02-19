#!/bin/sh
incus launch --no-profiles images:debian/12/cloud c1 <tests/incus-config.yaml \
&& incus admin waitready \
&& incus exec c1 -- apt-get install --yes python3 php
#
# tests/setup-debian.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0

