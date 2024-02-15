#!/usr/bin/bash

# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

psyclone -api nemo --config ../.psyclone/psyclone.cfg \
        fortran/empty.F90 --script ./01_psyclone.py -opsy outputs/01_psyclone.F90
