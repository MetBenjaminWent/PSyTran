#!/usr/bin/bash

psyclone -api nemo --config ../.psyclone/psyclone.cfg \
        fortran/empty.F90 --script ./01_psyclone.py -opsy outputs/01_psyclone.F90
