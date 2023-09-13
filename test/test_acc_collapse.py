from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyacc.acc_kernels import apply_kernels_directive
from psyacc.acc_loop import apply_loop_directive
from psyacc.acc_collapse import get_ancestors, is_collapsed
import code_snippets as cs
import pytest


def test_get_ancestors_single_loop(parser):
    """
    Test that :func:`get_ancestors` correctly finds no ancestors.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert len(get_ancestors(loops[-1])) == 0


def test_get_ancestors_double_loop(parser):
    """
    Test that :func:`get_ancestors` correctly finds one ancestor.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert len(get_ancestors(loops[-1])) == 1


def test_get_ancestors_triple_loop(parser):
    """
    Test that :func:`get_ancestors` correctly finds two ancestors.
    """
    code = parser(FortranStringReader(cs.triple_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert len(get_ancestors(loops[-1])) == 2


def test_get_ancestors_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`get_ancestors`
    is called with something other than a :class:`Loop`.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    assignments = psy.invokes.invoke_list[0].schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        get_ancestors(assignments[0])


def test_is_collapsed_no_kernels(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop which doesn't
    have a kernels directive.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert not is_collapsed(loops[0])


def test_is_collapsed_kernels_no_loop(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop with a kernels
    directive but no loop directives.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert not is_collapsed(loops[0])


def test_is_collapsed_loop_no_collapse(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop with a loop
    directive but no collapse clause.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert not is_collapsed(loops[0])
