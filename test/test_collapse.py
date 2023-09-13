from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from psyacc.kernels import apply_kernels_directive
from psyacc.loop import apply_loop_directive
from psyacc.collapse import get_ancestors, apply_loop_collapse, is_collapsed
import code_snippets as cs
from parameterized import parameterized
import pytest


@pytest.fixture(params=[True, False])
def inclusive(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=[2, 3])
def collapse(request):
    return request.param


def simple_loop_code(depth):
    if depth == 1:
        return cs.loop_with_1_assignment
    elif depth == 2:
        return cs.double_loop_with_1_assignment
    elif depth == 3:
        return cs.triple_loop_with_1_assignment
    elif depth == 4:
        return cs.quadruple_loop_with_1_assignment
    else:
        raise NotImplementedError


def test_get_ancestors(parser, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors.
    """
    code = parser(FortranStringReader(simple_loop_code(nest_depth)))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    expected = nest_depth if inclusive else nest_depth - 1
    assert len(get_ancestors(loops[-1], inclusive=inclusive)) == expected


def test_get_ancestors_typeerror1(parser):
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


def test_get_ancestors_typeerror2(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`get_ancestors`
    is called with a non-Boolean ``inclusive`` flag.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    expected = "Expected a bool, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        get_ancestors(loops[0], inclusive=0)


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


def test_apply_loop_collapse_typeerror1(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
    is called with something other than a :class:`Loop`.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    schedule = psy.invokes.invoke_list[0].schedule
    assignments = schedule.walk(nodes.Assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
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
    apply_kernels_directive(loops[0])
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
    apply_kernels_directive(loops[0])
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
    expected = "Cannot apply a loop clause without a kernels directive."
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
    expected = "Cannot apply collapse to 3 loops in a sub-nest of 2."
    with pytest.raises(ValueError, match=expected):
        apply_loop_collapse(loops[0], 3)


def test_apply_loop_collapse_no_loop_dir(parser, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied when there is no
    loop directive.
    """
    code = parser(FortranStringReader(simple_loop_code(collapse)))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_collapse(loops[0], collapse)
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert is_collapsed(loop)


def test_apply_loop_collapse(parser, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied when there is a
    loop directive.
    """
    code = parser(FortranStringReader(simple_loop_code(collapse)))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    apply_loop_collapse(loops[0], collapse)
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert is_collapsed(loop)


def test_apply_loop_collapse_subnest(parser, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a sub-nest.
    """
    code = parser(FortranStringReader(simple_loop_code(collapse + 1)))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    loops = psy.invokes.invoke_list[0].schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    apply_loop_directive(loops[-1])
    apply_loop_collapse(loops[0], collapse)
    assert loops[0].parent.parent.collapse == collapse
    for i in range(collapse):
        assert is_collapsed(loops[i])
    assert loops[-1].parent.parent.collapse is None
    assert not is_collapsed(loops[-1])
