from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from psyacc.kernels import apply_kernels_directive
import code_snippets as cs
from utils import get_schedule, simple_loop_code
from psyacc.loop_clauses import *
from psyacc.loop_clauses import _prepare_loop_for_clause
import pytest


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


def test_prepare_loop_for_clause_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when
    :func:`_prepare_loop_for_clause` is called with something other than a
    :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        _prepare_loop_for_clause(assignments[0])


def test_prepare_loop_for_collapse_no_kernels_error(parser):
    """
    Test that a :class:`ValueError` is raised when
    :func:`_prepare_loop_for_clause` is called without a kernels directive.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Cannot apply a loop clause without a kernels directive."
    with pytest.raises(ValueError, match=expected):
        _prepare_loop_for_clause(loops[0])


def test_prepare_loop_for_clause_no_loop_dir(parser):
    """
    Test that :func:`_prepare_loop_for_clause` is correctly applied when there
    is no loop directive.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    _prepare_loop_for_clause(loops[0])
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)


def test_apply_loop_seq(parser, nest_depth):
    """
    Test that :func:`apply_loop_seq` is correctly applied.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    for i in range(nest_depth):
        apply_loop_seq(loops[i])
        assert loops[i].parent.parent.sequential
        assert has_seq_clause(loops[i])


def test_apply_loop_gang(parser, nest_depth):
    """
    Test that :func:`apply_loop_gang` is correctly applied.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    for i in range(nest_depth):
        apply_loop_gang(loops[i])
        assert loops[i].parent.parent.gang
        assert has_gang_clause(loops[i])


def test_apply_loop_vector(parser, nest_depth):
    """
    Test that :func:`apply_loop_vector` is correctly applied.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    for i in range(nest_depth):
        apply_loop_vector(loops[i])
        assert loops[i].parent.parent.vector
        assert has_vector_clause(loops[i])


def test_apply_loop_seq_gang_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_seq` is
    applied to a loop with a ``gang`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_gang(loops[0])
    expected = "Cannot apply seq to a loop with a gang clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_seq(loops[0])


def test_apply_loop_seq_vector_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_seq` is
    applied to a loop with a ``vector`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_vector(loops[0])
    expected = "Cannot apply seq to a loop with a vector clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_seq(loops[0])


def test_apply_loop_gang_seq_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_gang` is
    applied to a loop with a ``seq`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_seq(loops[0])
    expected = "Cannot apply gang to a loop with a seq clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_gang(loops[0])


def test_apply_loop_vector_seq_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_vector` is
    applied to a loop with a ``seq`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_seq(loops[0])
    expected = "Cannot apply vector to a loop with a seq clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_vector(loops[0])
