#!/usr/bin/bash

# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

psyclone -api nemo --config ../.psyclone/psyclone.cfg fortran/double_loop.F90 \
        --script 04_collapse.py -opsy outputs/04_collapse-double_loop.F90
