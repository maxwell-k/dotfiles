#!/bin/sh
#
# local/bin/sha1-create.sh
# Copyright 2020 Keith Maxwell
# SPDX-License-Identifier: MPL-2.0
#
# Create a sha1 check sum for each file:
# - that is not stored in git and
# - doesn't already have one.
# Requires a ``git`` and ``openssl`` binary.
#
# These can subsequently be checked with either::
#     sha1sum --strict --check *.sha1 # coreutils
#     sed 's/SHA1(\(.*\))= \(.*\)/\2  \1/' *.sha1 | sha1sum -c # busybox
git ls-files --others | while read -r i
do
    test ! -f "${i}.sha1" &&
    openssl sha1 "${i}" | tee "${i}.sha1"
done
