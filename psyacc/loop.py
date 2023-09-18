from psyclone.psyir import nodes
from psyclone.nemo import NemoKern
from psyacc.family import get_descendents, get_children

__all__ = [
    "is_outer_loop",
    "get_loop_nest_num_depths",
    "is_perfectly_nested",
    "is_simple_loop",
    "get_loop_variable_name",
    "get_loop_nest_variable_names",
]


def is_outer_loop(loop):
    """
    Determine whether a loop is outer-most in its nest.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    return loop.ancestor(nodes.Loop) is None


def get_loop_nest_num_depths(loop):
    """
    Determine the number of depth levels in a loop (sub-)nest.

    :arg loop: the outer-most loop of the nest
    """
    return len({l.depth for l in loop.walk(nodes.Loop)})


def get_loop_nest_max_depth(loop):
    """
    Determine the maximum depth of a loop (sub-)nest.

    :arg loop: the outer-most loop of the nest
    """
    return max({l.depth for l in loop.walk(nodes.Loop)})


def is_perfectly_nested(loop):
    """
    Determine whether a loop nest is perfectly nested, i.e., each level except
    the deepest contains only the next loop.

    :arg loop: the outer-most loop of the nest
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    nest_depth = get_loop_nest_num_depths(loop)
    for depth in range(loop.depth, loop.depth + 2 * nest_depth, 2):
        nodes_at_depth = get_descendents(loop, inclusive=True, depth=depth)
        if len(nodes_at_depth) != 1 or not isinstance(nodes_at_depth[0], nodes.Loop):
            return False
    else:
        return True


def is_simple_loop(loop):
    """
    Determine whether a loop nest is simple, i.e., perfectly nested, with a
    single assignment at the deepest level.

    :arg loop: the outer-most loop of the nest
    """
    if not is_perfectly_nested(loop):
        return False
    innermost_loop = loop.walk(nodes.Loop)[-1]
    children = get_children(innermost_loop)
    if len(children) != 1 or not isinstance(children[0], NemoKern):
        return False
    grandchildren = get_children(children[0])
    return len(grandchildren) == 1 and isinstance(grandchildren[0], nodes.Assignment)


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
