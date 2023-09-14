from psyclone.psyir import nodes
from psyacc.family import get_ancestors
from psyacc.directives import has_kernels_directive, has_loop_directive

__all__ = ["is_collapsed"]


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
