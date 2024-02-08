#!/usr/bin/bash

psyclone -api nemo --config ../.psyclone/psyclone.cfg fortran/double_loop.F90 \
        --script 04_collapse.py -opsy outputs/04_collapse-double_loop.F90
