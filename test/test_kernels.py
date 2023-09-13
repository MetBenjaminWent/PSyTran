from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyclone.transformations import ACCKernelsDirective
from psyacc.kernels import (
    is_outer_loop,
    has_kernels_directive,
    apply_kernels_directive,
)
import code_snippets as cs
import pytest


def test_is_outer_loop(parser):
    """
    Test that a :func:`is_outer_loop` correctly determines whether a loop is
    outer-most in its nest.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert is_outer_loop(loops[0])
    assert not is_outer_loop(loops[1])


def test_is_outer_loop_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`is_outer_loop` is
    called with something other than a :class:`Loop`.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    assignments = psy.invokes.invoke_list[0].schedule.walk(nodes.Assignment)
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
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert not has_kernels_directive(loops[0])


# TODO: Account for more generic blocks, too
def test_apply_kernels_directive_loop(parser):
    """
    Test that :func:`apply_kernels_directive` correctly applies OpenACC kernels
    directives to a loop.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    assert isinstance(psy.invokes.invoke_list[0].schedule[0], ACCKernelsDirective)


def test_has_kernels_directive(parser):
    """
    Test that :func:`has_kernels_directive` correctly identifies an OpenACC
    kernels directives.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert has_kernels_directive(loops[0])
