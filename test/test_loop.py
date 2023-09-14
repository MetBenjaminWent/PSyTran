from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from psyacc.kernels import apply_kernels_directive
from psyacc.loop import *
import code_snippets as cs
from utils import get_schedule, simple_loop_code
import pytest


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


def test_has_no_loop_directive(parser):
    """
    Test that :func:`has_loop_directive` correctly identifies no OpenACC loop
    directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_loop_directive(loops[0])


def test_apply_loop_directive(parser):
    """
    Test that :func:`apply_loop_directive` correctly applies OpenACC kernels
    directives to a loop.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)


def test_has_loop_directive(parser):
    """
    Test that :func:`has_loop_directive` correctly identifies an OpenACC loop
    directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert has_loop_directive(loops[0])


def test_apply_loop_directive_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
    is called with something other than a :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        apply_loop_directive(assignments[0])


def test_is_perfectly_nested(parser):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested loop.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loops = schedule.walk(nodes.Loop)
    assert is_perfectly_nested(loops[0])


def test_is_perfectly_nested_simple(parser, nest_depth):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    assert is_perfectly_nested(loops[0])


def test_is_not_perfectly_nested(parser):
    """
    Test that :func:`is_perfectly_nested` correctly identifies an imperfectly
    nested loop.
    """
    schedule = get_schedule(parser, cs.imperfectly_nested_double_loop)
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
