#!/usr/bin/bash

psyclone -api nemo --config ../.psyclone/psyclone.cfg fortran/single_loop.F90 \
        --script 02_kernels.py -opsy outputs/02_kernels-single_loop.F90
