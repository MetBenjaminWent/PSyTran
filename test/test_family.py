from psyclone.psyir import nodes
from utils import *
import pytest


@pytest.fixture(params=[True, False])
def inclusive(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


def test_get_ancestors_loop(parser, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of a loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    expected = nest_depth if inclusive else nest_depth - 1
    assert len(get_ancestors(loops[-1], inclusive=inclusive)) == expected


def test_get_ancestors_assignment(parser, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of an assignment.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    assignment = schedule.walk(nodes.Assignment)[0]
    num_ancestors = len(get_ancestors(assignment, inclusive=inclusive))
    assert num_ancestors == nest_depth


def test_get_ancestors_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`get_ancestors`
    is called with a non-Boolean ``inclusive`` flag.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a bool, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        get_ancestors(loops[0], inclusive=0)
