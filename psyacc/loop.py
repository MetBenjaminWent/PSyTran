# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyclone.psyir.tools import DependencyTools
from psyacc.family import get_children

__all__ = [
    "is_outer_loop",
    "is_perfectly_nested",
    "is_simple_loop",
    "get_loop_variable_name",
    "get_loop_nest_variable_names",
    "is_parallelisable",
]


def _check_loop(loop):
    """
    Check that we do indeed have a :class:`Loop` node.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")


def is_outer_loop(loop):
    """
    Determine whether a loop is outer-most in its nest.
    """
    _check_loop(loop)
    return loop.ancestor(nodes.Loop) is None


def _perfect_nest_iter(loops, non_loops):
    """
    Determine whether a nest iteration is perfect.
    """
    return (len(loops) == 1 and not non_loops) or (
        not loops and not (any([node.walk(nodes.Loop) for node in non_loops]))
    )


def is_perfectly_nested(loop):
    """
    Determine whether a loop nest is perfectly nested, i.e., each level except
    the deepest contains only the next loop.

    Note that we ignore nodes of type :class:`Literal` and :class:`Reference`.

    :arg loop: the outer-most loop of the nest
    """
    _check_loop(loop)
    exclude = (nodes.literal.Literal, nodes.reference.Reference, nodes.Loop)
    loops, non_loops = [loop], []
    while len(loops) > 0:
        non_loops = get_children(loops[0], exclude=exclude)
        loops = get_children(loops[0], node_type=nodes.Loop)
        if not _perfect_nest_iter(loops, non_loops):
            return False
    else:
        return True


def is_simple_loop(loop):
    """
    Determine whether a loop nest is simple, i.e., perfectly nested, with only
    literal assignments at the deepest level.

    :arg loop: the outer-most loop of the nest
    """
    return is_perfectly_nested(loop) and all(
        [
            isinstance(child, nodes.Assignment) and child.walk(nodes.Literal)
            for child in get_children(loop.walk(nodes.Loop)[-1])
        ]
    )


def get_loop_variable_name(loop):
    """
    Given a :class:`Loop` node, return its variable name.
    """
    assert isinstance(loop, nodes.Loop)
    return loop.variable.name


def get_loop_nest_variable_names(loop):
    """
    Given a :class:`Loop` node, return the variable names of each loop it
    contains.
    """
    assert isinstance(loop, nodes.Loop)
    return [get_loop_variable_name(loop) for loop in loop.walk(nodes.Loop)]


def is_parallelisable(loop):
    """
    Determine whether a :class:`Loop` can be parallelised.

    Note: wraps the :meth:`can_loop_be_parallelised` method of :class:`DependencyTools`.
    """
    return DependencyTools().can_loop_be_parallelised(loop)
