from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyacc.acc_kernels import apply_kernels_directive
from psyacc.acc_loop import apply_loop_directive
from psyacc.acc_collapse import get_ancestors, apply_loop_collapse, is_collapsed
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


def test_apply_loop_collapse_typeerror1(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
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
        apply_loop_collapse(assignments[0], 2)


def test_apply_loop_collapse_typeerror2(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
    is called with a non-integer collapse.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    expected = "Expected an integer, not '<class 'float'>'."
    with pytest.raises(TypeError, match=expected):
        apply_loop_collapse(loops[0], 2.0)


def test_apply_loop_collapse_valueerror(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
    is called with an invalid collapse.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    expected = "Expected an integer greater than one, not 1."
    with pytest.raises(ValueError, match=expected):
        apply_loop_collapse(loops[0], 1)


def test_apply_loop_collapse_no_kernels_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
    is called without a kernels directive.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    expected = "Cannot apply loop collapse without a kernels directive."
    with pytest.raises(ValueError, match=expected):
        apply_loop_collapse(loops[0], 2)


def test_apply_loop_collapse_too_large_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
    is called with too large a collapse.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    expected = "Cannot apply collapse to 3 loops in a sub-nest of 2."
    with pytest.raises(ValueError, match=expected):
        apply_loop_collapse(loops[0], 3)


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
