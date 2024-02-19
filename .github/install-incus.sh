#!/bin/sh
sudo cp .github/zabbly.asc /etc/apt/keyrings/ \
&& sudo cp .github/zabbly-incus-stable.sources /etc/apt/sources.list.d/ \
&& sudo apt-get update \
&& sudo apt-get install --yes incus \
&& sudo sed -i s/incus-admin/adm/ /opt/incus/lib/systemd/system/incus.service \
&& sudo sed -i s/incus-admin/adm/ /opt/incus/lib/systemd/system/incus.socket \
&& sudo systemctl daemon-reload \
&& sudo systemctl restart incus.socket \
&& incus admin init --auto \
&& incus --version
#
# .github/install-incus.sh
# Copyright 2024 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
