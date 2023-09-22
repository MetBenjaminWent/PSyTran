from psyclone.psyir import nodes
from utils import *
import pytest


@pytest.fixture(params=[True, False])
def inclusive(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=["descendent", "ancestor"])
def relative(request):
    return request.param


get_relative = {
    "descendent": get_descendents,
    "ancestor": get_ancestors,
}


def test_get_relatives_typeerror1(parser, relative):
    """
    Test that a :class:`TypeError` is raised when :func:`get_descendents`
    or :func:`get_ancestors` is called with a non-Boolean ``inclusive`` flag.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a bool, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        get_relative[relative](loops[0], inclusive=0)


def test_get_relatives_typeerror2(parser, relative):
    """
    Test that a :class:`TypeError` is raised when :func:`get_descendents`
    or :func:`get_ancestors` is called with a non-integer ``depth`` keyword
    argument.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected an int, not '<class 'float'>'."
    with pytest.raises(TypeError, match=expected):
        get_relative[relative](loops[0], depth=2.0)


def test_get_relatives_loop(parser, nest_depth, inclusive, relative):
    """
    Test that :func:`get_descendents` and :func:`get_ancestors` correctly find
    the right number of descendents/ancestors of a loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    for i in range(nest_depth):
        loop = loops[i if relative == "descendent" else nest_depth - 1 - i]
        kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
        num_relatives = len(get_relative[relative](loop, **kwargs))
        expected = nest_depth - i if inclusive else nest_depth - 1 - i
        assert num_relatives == expected


def test_get_relatives_loop_depth(parser, nest_depth, inclusive, relative):
    """
    Test that :func:`get_descendents` and :func:`get_ancestors` correctly find
    the right number of descendents/ancestors of a loop of a specified depth.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loop = schedule.walk(nodes.Loop)[0 if relative == "descendent" else nest_depth - 1]
    depth = loop.depth
    for i in range(nest_depth):
        kwargs = {"inclusive": inclusive, "node_type": nodes.Loop, "depth": depth}
        num_relatives = len(get_relative[relative](loop, **kwargs))
        assert num_relatives == (0 if not inclusive and i == 0 else 1)
        depth += 2 if relative == "descendent" else -2


def test_get_relatives_assignment(parser, nest_depth, inclusive, relative):
    """
    Test that :func:`get_descendents` and :func:`get_ancestors` correctly find
    the right number of descendents/ancestors of an assignment.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    assignment = schedule.walk(nodes.Assignment)[0]
    kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
    num_relatives = len(get_relative[relative](assignment, **kwargs))
    assert num_relatives == 0 if relative == "descendent" else nest_depth


def test_get_children(parser):
    """
    Test that :func:`get_children` correctly determines a node's children.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    assignments = schedule.walk(nodes.Assignment)
    assert get_children(loop) == assignments
    assert get_children(loop, exclude=nodes.Assignment) == []


def test_get_parent(parser):
    """
    Test that :func:`get_parent` correctly determines a node's parent.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    for assignment in schedule.walk(nodes.Assignment):
        assert get_parent(assignment) == loop
        assert get_parent(assignment, exclude=nodes.Loop) == None


def test_get_siblings(parser, inclusive):
    """
    Test that :func:`get_siblings` correctly determines a node's siblings.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    for i in range(3):
        kwargs = {"inclusive": inclusive}
        expected = list(assignments)
        if not inclusive:
            expected.pop(i)
        assert get_siblings(assignments[i], **kwargs) == expected
        kwargs["exclude"] = nodes.Assignment
        assert get_siblings(assignments[i], **kwargs) == []


def test_has_ancestor_descendent(parser):
    """
    Test that :func:`has_ancestor` and :func:`has_descendent` correctly
    determine whether nodes have ancestors or descendents of specified types.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loop = schedule.walk(nodes.Loop)[0]
    assignment = schedule.walk(nodes.Assignment)[0]
    assert has_descendent(loop, nodes.Assignment)
    assert not has_descendent(loop, nodes.Loop)
    assert has_ancestor(assignment, nodes.Loop)
    assert not has_ancestor(assignment, nodes.Assignment)


def test_are_siblings(parser):
    """
    Test that :func:`are_siblings` correctly determines whether nodes are
    siblings.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    assignments = schedule.walk(nodes.Assignment)
    assert are_siblings(assignments[0])
    assert are_siblings(*assignments[1:])
    assert are_siblings(*assignments)
    assert not are_siblings(assignments[0], loop)


def test_is_next_sibling(parser):
    """
    Test that :func:`is_next_sibling` correctly determines whether one node
    follows another.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    assert is_next_sibling(*assignments[:2])
    assert is_next_sibling(*assignments[1:])
    assert not is_next_sibling(*assignments[::2])
