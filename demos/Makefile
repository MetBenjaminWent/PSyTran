# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

all: run

run:
	set -eu
	./01_psyclone.sh
	./02_kernels.sh
	./03_loop.sh
	./04_collapse.sh

clean:
	rm -rf __pycache__/
	rm -f *.mod *.o
