#!/bin/sh
#
# local/bin/create-dot-sha256.sh
# Copyright 2020 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
#
# Create a sha256 check sum for each file:
# - that is not stored in git and
# - doesn't already have one.
# Requires a ``git`` and ``openssl`` binary.
#
# These can subsequently be checked with either::
#     sha256sum --check --strict *.sha256 # coreutils
#     busybox sha256sum -c *.sha256
#
# openssl is used to generate hashes as it is assumed to be faster.
# coreutils format is used as it is supported by tools with -c or --check
git ls-files --others | while read -r i
do
    test ! -f "${i}.sha256" \
    && openssl dgst -sha256 -r "${i}" | tee "${i}.sha256"
done
