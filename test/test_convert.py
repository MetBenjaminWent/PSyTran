from psyclone.psyir import nodes
from utils import *
import pytest


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
