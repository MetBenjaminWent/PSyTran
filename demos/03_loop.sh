#!/usr/bin/bash

# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

psyclone -api nemo --script 03_loop.py -opsy outputs/03_loop-double_loop.F90 \
        fortran/double_loop.F90
