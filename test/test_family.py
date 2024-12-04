# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyACC's `family` module.
"""

import pytest

from psyclone.psyir import nodes
from utils import get_schedule, simple_loop_code

import code_snippets as cs
from psyacc.family import (
    get_ancestors,
    get_children,
    get_descendents,
    get_parent,
    has_ancestor,
    has_descendent,
)


@pytest.fixture(name="inclusive", params=[True, False])
def fixture_inclusive(request):
    """
    Pytest fixture to control whether the current node is included in
    searches.
    """
    return request.param


@pytest.fixture(name="nest_depth", params=[1, 2, 3, 4])
def fixture_nest_depth(request):
    """Pytest fixture for depth of a loop nest."""
    return request.param


@pytest.fixture(name="relative", params=["ancestor", "descendent"])
def fixture_relative(request):
    """Pytest fixture for the type of relative."""
    return request.param


get_relative = {
    "descendent": get_descendents,
    "ancestor": get_ancestors,
}


def test_get_relatives_typeerror1(fortran_reader, relative):
    """
    Test that a :class:`TypeError` is raised when :func:`get_descendents`
    or :func:`get_ancestors` is called with a non-Boolean ``inclusive`` flag.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a bool, not '<class 'int'>'."
    with pytest.raises(AssertionError, match=expected):
        get_relative[relative](loops[0], inclusive=0)


def test_get_relatives_typeerror2(fortran_reader, relative):
    """
    Test that a :class:`TypeError` is raised when :func:`get_descendents`
    or :func:`get_ancestors` is called with a non-integer ``depth`` keyword
    argument.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected an int, not '<class 'float'>'."
    with pytest.raises(AssertionError, match=expected):
        get_relative[relative](loops[0], depth=2.0)


def test_get_descendents_loop(fortran_reader, nest_depth, inclusive):
    """
    Test that :func:`get_descendents` correctly finds the right number of
    descendents of a loop.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    for i in range(nest_depth):
        loop = loops[i]
        kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
        expected = nest_depth - i if inclusive else nest_depth - 1 - i
        assert len(get_descendents(loop, **kwargs)) == expected
        kwargs["exclude"] = nodes.Loop
        assert len(get_descendents(loop, **kwargs)) == 0


def test_get_ancestors_loop(fortran_reader, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of a loop.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    for i in range(nest_depth):
        loop = loops[nest_depth - 1 - i]
        kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
        expected = nest_depth - i if inclusive else nest_depth - 1 - i
        assert len(get_ancestors(loop, **kwargs)) == expected
        kwargs["exclude"] = nodes.Loop
        assert len(get_ancestors(loop, **kwargs)) == 0


def test_get_descendents_loop_depth(fortran_reader, nest_depth, inclusive):
    """
    Test that :func:`get_descendents` correctly finds the right number of
    descendents of a loop of a specified depth.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    loop = schedule.walk(nodes.Loop)[0]
    depth = loop.depth
    for i in range(nest_depth):
        kwargs = {
            "inclusive": inclusive,
            "node_type": nodes.Loop,
            "depth": depth,
        }
        num_descendents = len(get_descendents(loop, **kwargs))
        assert num_descendents == (0 if not inclusive and i == 0 else 1)
        depth += 2


def test_get_ancestors_loop_depth(fortran_reader, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of a loop of a specified depth.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    loop = schedule.walk(nodes.Loop)[nest_depth - 1]
    depth = loop.depth
    for i in range(nest_depth):
        kwargs = {
            "inclusive": inclusive,
            "node_type": nodes.Loop,
            "depth": depth,
        }
        num_ancestors = len(get_ancestors(loop, **kwargs))
        assert num_ancestors == (0 if not inclusive and i == 0 else 1)
        depth -= 2


def test_get_descendents_assignment(fortran_reader, nest_depth, inclusive):
    """
    Test that :func:`get_descendents` correctly finds the right number of
    descendents of an assignment.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    assignment = schedule.walk(nodes.Assignment)[0]
    kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
    assert len(get_descendents(assignment, **kwargs)) == 0
    kwargs["exclude"] = nodes.Node
    assert len(get_descendents(assignment, **kwargs)) == 0


def test_get_ancestors_assignment(fortran_reader, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of an assignment.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    assignment = schedule.walk(nodes.Assignment)[0]
    kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
    assert len(get_ancestors(assignment, **kwargs)) == nest_depth
    kwargs["exclude"] = nodes.Loop
    assert len(get_ancestors(assignment, **kwargs)) == 0


def test_get_children(fortran_reader):
    """
    Test that :func:`get_children` correctly determines a node's children.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    assignments = schedule.walk(nodes.Assignment)
    assert get_children(loop) == assignments
    assert get_children(loop, node_type=nodes.Loop) == []
    assert get_children(loop, exclude=nodes.Assignment) == []


def test_get_parent(fortran_reader):
    """
    Test that :func:`get_parent` correctly determines a node's parent.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    for assignment in schedule.walk(nodes.Assignment):
        assert get_parent(assignment) == loop


def test_has_ancestor_descendent(fortran_reader):
    """
    Test that :func:`has_ancestor` and :func:`has_descendent` correctly
    determine whether nodes have ancestors or descendents of specified types.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loop = schedule.walk(nodes.Loop)[0]
    assignment = schedule.walk(nodes.Assignment)[0]
    assert has_descendent(loop, nodes.Assignment)
    assert not has_descendent(loop, nodes.Loop)
    assert has_ancestor(assignment, nodes.Loop)
    assert not has_ancestor(assignment, nodes.Assignment)


def test_has_ancestor_name(fortran_reader):
    """
    Test that :func:`has_ancestor` correctly determine whether nodes have
    ancestors whose variables have particular names.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    assignment = schedule.walk(nodes.Assignment)[0]
    assert has_ancestor(assignment, nodes.Loop, name="i")
    assert not has_ancestor(assignment, nodes.Loop, name="j")
