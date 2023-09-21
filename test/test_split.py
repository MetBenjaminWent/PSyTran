from psyclone.psyir import nodes
from utils import *
import pytest


def test_split_consecutive(parser):
    """
    Test that :func:`split_consecutive` correctly determines consecutive nodes.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    assert len(split_consecutive(assignments)) == 1
    assert len(split_consecutive(assignments[::2])) == 2
