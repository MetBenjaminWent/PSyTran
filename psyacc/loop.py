from psyclone.psyir import nodes
from psyclone.psyir.tools import DependencyTools
from psyacc.family import get_children

__all__ = [
    "is_outer_loop",
    "get_loop_nest_num_depths",
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

    Note that we ignore nodes of type :class:`Literal` and :class:`Reference`.

    :arg loop: the outer-most loop of the nest
    """
    _check_loop(loop)
    exclude = (nodes.literal.Literal, nodes.reference.Reference, nodes.Loop)
    current = loop
    while current.depth < get_loop_nest_max_depth(loop):
        loops = get_children(current, node_type=nodes.Loop)
        if len(loops) != 1 or len(get_children(current, exclude=exclude)) > 0:
            return False
        current = loops[0]
    else:
        return True


def is_simple_loop(loop):
    """
    Determine whether a loop nest is simple, i.e., perfectly nested, with only
    literal assignments at the deepest level.

    :arg loop: the outer-most loop of the nest
    """
    if not is_perfectly_nested(loop):
        return False
    innermost_loop = loop.walk(nodes.Loop)[-1]
    for child in get_children(innermost_loop):
        if not (
            isinstance(child, nodes.Assignment)
            and child.depth == innermost_loop.depth + 4
            and child.walk(nodes.Literal)
        ):
            return False
    else:
        return True


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
