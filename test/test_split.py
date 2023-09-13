from psyclone.psyir import nodes
from psyacc.split import follows, split_consecutive
import code_snippets as cs
from utils import get_schedule
import pytest


def test_follows(parser):
    """
    Test that :func:`follows` correctly determines whether one node follows
    another.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    assert follows(*assignments[:2])
    assert follows(*assignments[1:])
    assert not follows(*assignments[::2])


def test_split_consecutive(parser):
    """
    Test that :func:`split_consecutive` correctly determines consecutive nodes.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    assert len(split_consecutive(assignments)) == 1
    assert len(split_consecutive(assignments[::2])) == 2


def test_split_consecutive_valuerror(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`split_consecutive` is
    called with a block of nodes from different depths.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Block contains nodes with different depths."
    with pytest.raises(ValueError, match=expected):
        split_consecutive(loops)
