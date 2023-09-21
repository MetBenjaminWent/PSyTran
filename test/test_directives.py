from psyclone.psyir import nodes
from psyclone.transformations import ACCKernelsDirective, ACCLoopDirective
from utils import *
import pytest


@pytest.fixture(params=["sequential", "gang", "vector"])
def clause(request):
    return request.param


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


def test_apply_kernels_directive_schedule(parser):
    """
    Test that :func:`apply_kernels_directive` correctly applies a ``kernels``
    directive to a schedule.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    apply_kernels_directive(schedule)
    assert isinstance(schedule[0], ACCKernelsDirective)


def test_apply_kernels_directive_loop(parser):
    """
    Test that :func:`apply_kernels_directive` correctly applies a ``kernels``
    directives to a loop.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    assert isinstance(loops[0].parent.parent, ACCKernelsDirective)
    assert has_kernels_directive(loops[0])


def test_has_no_kernels_directive(parser):
    """
    Test that :func:`has_kernels_directive` correctly identifies no OpenACC
    kernels directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_kernels_directive(loops[0])


def test_force_apply_loop_directive(parser):
    """
    Test that :func:`apply_loop_directive` correctly force-applies a ``loop``
    directive.
    """
    schedule = get_schedule(parser, cs.serial_loop)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0], options={"force": True})
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)


def test_force_apply_loop_directive_with_seq_clause(parser):
    """
    Test that :func:`apply_loop_directive` correctly force-applies a ``loop``
    directive with a ``seq`` clause.
    """
    schedule = get_schedule(parser, cs.serial_loop)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0], options={"force": True, "sequential": True})
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)
    assert has_seq_clause(loops[0])


def test_apply_loop_directive_with_clause(parser, clause):
    """
    Test that :func:`apply_loop_directive` correctly applies a ``loop``
    directive with a clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0], options={clause: True})
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)
    assert has_clause[clause](loops[0])


def test_apply_loop_directive_with_gang_vector(parser, clause):
    """
    Test that :func:`apply_loop_directive` correctly applies a ``loop``
    directive with ``gang`` and ``vector`` clauses.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0], options={"gang": True, "vector": True})
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)
    assert has_gang_clause(loops[0])
    assert has_vector_clause(loops[0])


def test_apply_loop_directive_typeerror1(parser):
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


def test_apply_loop_directive_typeerror2(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
    is called with options that aren't a :class:`dict`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a dict, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        apply_loop_directive(loops[0], options=0)


def test_apply_loop_directive_valueerror(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
    is called to a loop with no ``kernels`` directive.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Cannot apply a loop directive without a kernels directive."
    with pytest.raises(ValueError, match=expected):
        apply_loop_directive(loops[0])


def test_has_no_loop_directive(parser):
    """
    Test that :func:`has_loop_directive` correctly identifies no ``loop``
    directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_loop_directive(loops[0])
