from psyclone.psyir import nodes
from utils import *
import pytest


@pytest.fixture(params=[True, False])
def inclusive(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=["child", "ancestor"])
def relative(request):
    return request.param


get_relative = {
    "child": get_children,
    "ancestor": get_ancestors,
}


def test_get_relatives_typeerror(parser, relative):
    """
    Test that a :class:`TypeError` is raised when :func:`get_children`
    or :func:`get_ancestors` is called with a non-Boolean ``inclusive`` flag.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a bool, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        get_relative[relative](loops[0], inclusive=0)


def test_get_relatives_loop(parser, nest_depth, inclusive, relative):
    """
    Test that :func:`get_children` and :func:`get_ancestors` correctly find
    the right number of children/ancestors of a loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loop = schedule.walk(nodes.Loop)[0 if relative == "child" else -1]
    num_relatives = len(get_relative[relative](loop, inclusive=inclusive))
    expected = nest_depth if inclusive else nest_depth - 1
    assert num_relatives == expected


def test_get_relatives_assignment(parser, nest_depth, inclusive, relative):
    """
    Test that :func:`get_children` and :func:`get_ancestors` correctly find
    the right number of children/ancestors of an assignment.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    assignment = schedule.walk(nodes.Assignment)[0]
    num_relatives = len(get_relative[relative](assignment, inclusive=inclusive))
    expected = 0 if relative == "child" else nest_depth
    assert len(get_children(assignment, inclusive=inclusive)) == 0


def test_is_next_sibling(parser):
    """
    Test that :func:`is_next_sibling` correctly determines whether one node
    follows another.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    assert is_next_sibling(*assignments[:2])
    assert is_next_sibling(*assignments[1:])
    assert not is_next_sibling(*assignments[::2])
