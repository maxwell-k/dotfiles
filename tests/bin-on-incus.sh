#!/bin/sh
incus file push bin.py "c1/home/$LOGNAME/" \
&& incus file push bin.toml "c1/home/$LOGNAME/" \
&& incus exec c1 -- su --login "$LOGNAME" -c ./bin.py \
&& incus stop c1 \
&& incus delete c1
#
# tests/bin-on-debian.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
