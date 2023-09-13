from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from psyacc.kernels import apply_kernels_directive
from psyacc.loop import has_loop_directive, apply_loop_directive
import code_snippets as cs
import pytest


def test_has_no_loop_directive(parser):
    """
    Test that :func:`has_loop_directive` correctly identifies no OpenACC loop
    directives.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert not has_loop_directive(loops[0])


def test_apply_loop_directive(parser):
    """
    Test that :func:`apply_loop_directive` correctly applies OpenACC kernels
    directives to a loop.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)


def test_has_loop_directive(parser):
    """
    Test that :func:`has_loop_directive` correctly identifies an OpenACC loop
    directives.
    """
    code = parser(FortranStringReader(cs.loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    assert has_loop_directive(loops[0])


def test_apply_loop_directive_typeerror(parser):
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
        apply_loop_directive(assignments[0])
