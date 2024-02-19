#!/usr/bin/bash

# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

PSYCLONE_DIR=$(python3 -c "import psyclone; print(psyclone.__path__[0])")/../..
mkdir ${VIRTUAL_ENV}/share/psyclone
cp ${PSYCLONE_DIR}/config/psyclone.cfg ${VIRTUAL_ENV}/share/psyclone
