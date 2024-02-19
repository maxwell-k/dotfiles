#!/bin/sh
sudo snap remove lxd --purge
sudo snap remove core20 --purge || true
sudo apt-get autopurge --yes docker-ce docker-ce-cli uidmap
sudo ip link delete docker0
sudo nft flush ruleset
#
# .github/reset-network.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
