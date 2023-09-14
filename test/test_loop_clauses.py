from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from psyacc.kernels import apply_kernels_directive
import code_snippets as cs
from utils import get_schedule
from psyacc.loop_clauses import _prepare_loop_for_clause
import pytest


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
