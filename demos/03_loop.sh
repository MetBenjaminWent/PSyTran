#!/usr/bin/bash

psyclone -api nemo --config ../.psyclone/psyclone.cfg fortran/double_loop.F90 \
        --script 03_loop.py -opsy outputs/03_loop-double_loop.F90
