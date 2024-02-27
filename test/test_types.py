# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from utils import *


def test_is_character(parser):
    """
    Test that :func:`is_character` correctly determines variables of intrinsic
    type `CHARACTER`.
    """
    schedule = get_schedule(parser, cs.string_assignment)
    references = schedule.walk(nodes.Reference)
    assert is_character(references[0])
    assert refers_to_character(schedule)
