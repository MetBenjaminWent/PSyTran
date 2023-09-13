from psyclone.psyir import nodes
from psyacc.kernels import has_kernels_directive
from psyacc.loop import has_loop_directive, apply_loop_directive
from psyacc.loop_clauses import _prepare_loop_for_clause


def get_ancestors(loop, inclusive=False):
    """
    Get all ancestors of a loop which are also loops.

    :arg loop: the :class:`Loop` node.
    :arg inclusive: if ``True``, the current loop is included.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not isinstance(inclusive, bool):
        raise TypeError(f"Expected a bool, not '{type(inclusive)}'.")
    ancestors = []
    current = loop
    if inclusive:
        ancestors.append(current)
    while current.ancestor(nodes.Loop) is not None:
        current = current.ancestor(nodes.Loop)
        ancestors.append(current)
    return ancestors


def apply_loop_collapse(loop, collapse):
    """
    Apply a collapse clause to a loop.

    :arg loop: the :class:`Loop` node.
    :arg collapse: the number of loops to collapse
    """
    _prepare_loop_for_clause(loop)
    if not isinstance(collapse, int):
        raise TypeError(f"Expected an integer, not '{type(collapse)}'.")
    if collapse <= 1:
        raise ValueError(f"Expected an integer greater than one, not {collapse}.")
    if len(loop.walk(nodes.Loop)) < collapse:
        raise ValueError(
            f"Cannot apply collapse to {collapse} loops in a sub-nest of"
            f" {len(loop.walk(nodes.Loop))}."
        )
    loop.parent.parent._collapse = collapse


def is_collapsed(loop):
    """
    Determine whether a loop lies within a collapsed loop nest.

    :arg loop: the :class:`Loop` node.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not has_kernels_directive(loop):
        return False
    ancestors = get_ancestors(loop, inclusive=True)
    for i, current in enumerate(ancestors):
        if has_loop_directive(current):
            loop_dir = current.parent.parent
            collapse = loop_dir.collapse
            if collapse is None:
                continue
            else:
                return collapse > i
    return False
