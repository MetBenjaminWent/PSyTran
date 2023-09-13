from psyclone.psyir import nodes
from psyacc.acc_kernels import has_kernels_directive
from psyacc.acc_loop import has_loop_directive


def get_ancestors(loop):
    """
    Get all ancestors of a loop which are also loops.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    ancestors = []
    current = loop
    while current.ancestor(nodes.Loop) is not None:
        current = current.ancestor(nodes.Loop)
        ancestors.append(current)
    return ancestors


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
