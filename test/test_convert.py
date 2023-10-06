# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from utils import *


def test_convert_array_notation(parser):
    """
    Test that :func:`convert_array_notation` successfully converts an implied array
    range assignment into an explicit one.
    """
    schedule = get_schedule(parser, cs.implied_array_assignment)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
    convert_array_notation(schedule)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == 1
    assert str(schedule) == str(get_schedule(parser, cs.array_assignment))


def test_convert_range_loops(parser):
    """
    Test that :func:`convert_range_loops` successfully converts an array range
    assignment into a loop.
    """
    schedule = get_schedule(parser, cs.array_assignment)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Loop)) == 0
    convert_range_loops(schedule)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Loop)) == 1
