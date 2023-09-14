from psyclone.psyir import nodes
from psyacc.kernels import has_kernels_directive
from psyacc.loop import has_loop_directive
from psyacc.loop_clauses import _prepare_loop_for_clause

__all__ = ["get_ancestors", "apply_loop_collapse", "is_collapsed"]


def get_ancestors(node, inclusive=False, node_type=nodes.Loop):
    """
    Get all ancestors of a node.

    :arg loop: the node to search for ancestors of.
    :arg inclusive: if ``True``, the current loop is included.
    :arg node_type: the type of node to search for.
    """
    assert isinstance(node, nodes.Node)
    if not isinstance(inclusive, bool):
        raise TypeError(f"Expected a bool, not '{type(inclusive)}'.")
    assert issubclass(node_type, nodes.Node)
    ancestors = []
    current = node
    if inclusive and isinstance(node, node_type):
        ancestors.append(current)
    while current.ancestor(node_type) is not None:
        current = current.ancestor(node_type)
        ancestors.append(current)
    return ancestors


def apply_loop_collapse(loop, collapse):
    """
    Apply a ``collapse`` clause to a loop.

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
