from psyclone.psyir import nodes
from psyclone.transformations import ACCKernelsDirective
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


def test_has_no_kernels_directive(parser):
    """
    Test that :func:`has_kernels_directive` correctly identifies no OpenACC
    kernels directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_kernels_directive(loops[0])


def test_apply_kernels_directive_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_kernels_directive`
    is called with options that aren't a :class:`dict`.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a dict, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        apply_kernels_directive(loops[0], options=0)


# TODO: Account for more generic blocks, too
def test_apply_kernels_directive_loop(parser):
    """
    Test that :func:`apply_kernels_directive` correctly applies OpenACC kernels
    directives to a loop.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    assert isinstance(schedule[0], ACCKernelsDirective)


def test_has_kernels_directive(parser):
    """
    Test that :func:`has_kernels_directive` correctly identifies an OpenACC
    kernels directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    assert has_kernels_directive(loops[0])
