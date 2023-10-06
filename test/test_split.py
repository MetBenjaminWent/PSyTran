# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from utils import *


def test_split_consecutive(parser):
    """
    Test that :func:`split_consecutive` correctly determines consecutive nodes.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    assert len(split_consecutive(assignments)) == 1
    assert len(split_consecutive(assignments[::2])) == 2
