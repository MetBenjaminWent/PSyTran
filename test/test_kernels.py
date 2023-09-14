from psyclone.psyir import nodes
from utils import *
import pytest


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


def test_is_outer_loop(parser, nest_depth):
    """
    Test that a :func:`is_outer_loop` correctly determines whether a loop is
    outer-most in its nest.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    assert is_outer_loop(loops[0])
    for i in range(1, nest_depth):
        assert not is_outer_loop(loops[i])


def test_is_outer_loop_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`is_outer_loop` is
    called with something other than a :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        is_outer_loop(assignments[0])
