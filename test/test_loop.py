from psyclone.psyir import nodes
from utils import *
import pytest


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=["before", "after"])
def imperfection(request):
    return request.param


imperfectly_nested_double_loop = {
    "before": cs.imperfectly_nested_double_loop_before,
    "after": cs.imperfectly_nested_double_loop_after,
}

imperfectly_nested_triple_loop = {
    "before": cs.imperfectly_nested_triple_loop_before,
    "after": cs.imperfectly_nested_triple_loop_after,
}


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


def test_is_perfectly_nested_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`is_perfectly_nested`
    is called with something other than a :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        is_perfectly_nested(assignments[0])


def test_is_perfectly_nested(parser):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested loop.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loops = schedule.walk(nodes.Loop)
    assert is_perfectly_nested(loops[0])


def test_is_not_perfectly_nested(parser, imperfection):
    """
    Test that :func:`is_perfectly_nested` correctly identifies an imperfectly
    nested loop.
    """
    schedule = get_schedule(parser, imperfectly_nested_double_loop[imperfection])
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])


def test_is_perfectly_nested_subnest(parser, imperfection):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    sub-nest.
    """
    schedule = get_schedule(parser, imperfectly_nested_triple_loop[imperfection])
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
    assert is_perfectly_nested(loops[1])


def test_is_simple_loop(parser, nest_depth):
    """
    Test that :func:`is_simple_loop` correctly identifies a simple loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    assert is_simple_loop(loops[0])


def test_is_not_simple_loop(parser):
    """
    Test that :func:`is_simple_loop` correctly identifies a non-simple loop.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loops = schedule.walk(nodes.Loop)
    assert not is_simple_loop(loops[0])


def test_get_loop_variable_name(parser):
    """
    Test that :func:`get_loop_variable_name` correctly determines loop variable
    names.
    """
    schedule = get_schedule(parser, cs.quadruple_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    for i, expected in enumerate(["l", "k", "j", "i"]):
        assert get_loop_variable_name(loops[i]) == expected


def test_get_loop_nest_variable_names(parser):
    """
    Test that :func:`get_loop_nest_variable_names` correctly determines all loop
    variable names in a nest.
    """
    schedule = get_schedule(parser, cs.quadruple_loop_with_1_assignment)
    indices = ["l", "k", "j", "i"]
    for i, loop in enumerate(schedule.walk(nodes.Loop)):
        assert get_loop_nest_variable_names(loop) == indices[i:]
