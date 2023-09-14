from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from utils import *
import pytest


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=["sequential", "gang", "vector"])
def clause(request):
    return request.param


def test_has_no_loop_directive(parser):
    """
    Test that :func:`has_loop_directive` correctly identifies no ``loop``
    directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_loop_directive(loops[0])


def test_apply_loop_directive(parser):
    """
    Test that :func:`apply_loop_directive` correctly applies a ``loop``
    directive.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)


def test_has_loop_directive(parser):
    """
    Test that :func:`has_loop_directive` correctly identifies a ``loop``
    directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert has_loop_directive(loops[0])


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


def test_is_perfectly_nested_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`is_perfectly_nested`
    is called with something other than a :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        is_perfectly_nested(assignments[0])


def test_is_perfectly_nested_valueerror(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`is_perfectly_nested`
    is called on a loop other than the outer-most.
    """
    schedule = get_schedule(parser, cs.quadruple_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "is_perfectly_nested should be applied to outer-most loop."
    for i in range(1, 4):
        with pytest.raises(ValueError, match=expected):
            is_perfectly_nested(loops[i])


def test_is_perfectly_nested(parser):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested loop.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loops = schedule.walk(nodes.Loop)
    assert is_perfectly_nested(loops[0])


def test_is_simple_loop(parser, nest_depth):
    """
    Test that :func:`is_simple_loop` correctly identifies a simple loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    assert is_simple_loop(loops[0])


def test_is_not_perfectly_nested(parser):
    """
    Test that :func:`is_perfectly_nested` correctly identifies an imperfectly
    nested loop.
    """
    schedule = get_schedule(parser, cs.imperfectly_nested_double_loop)
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])


def test_is_not_simple_loop(parser):
    """
    Test that :func:`is_simple_loop` correctly identifies a non-simple loop.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loops = schedule.walk(nodes.Loop)
    assert not is_simple_loop(loops[0])


def test_get_loop_variable_name(parser):
    """
    Test that :func:`get_loop_variable_name` correctly determines loop variable
    names.
    """
    schedule = get_schedule(parser, cs.quadruple_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    for i, expected in enumerate(["l", "k", "j", "i"]):
        assert get_loop_variable_name(loops[i]) == expected
