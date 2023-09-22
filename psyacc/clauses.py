from psyclone.psyir import nodes
from psyacc.directives import (
    has_kernels_directive,
    apply_loop_directive,
    has_loop_directive,
)
from psyacc.family import get_ancestors
from psyacc.loop import _check_loop

__all__ = [
    "has_seq_clause",
    "apply_loop_seq",
    "has_gang_clause",
    "apply_loop_gang",
    "has_vector_clause",
    "apply_loop_vector",
    "has_collapse_clause",
    "apply_loop_collapse",
]


def _prepare_loop_for_clause(loop):
    """
    Prepare to apply a clause to a ``loop`` directive.

    :arg loop: the :class:`Loop` node.
    """
    _check_loop(loop)
    if not has_kernels_directive(loop):
        raise ValueError("Cannot apply a loop clause without a kernels directive.")
    if not has_loop_directive(loop):
        apply_loop_directive(loop)


def has_seq_clause(loop):
    """
    Determine whether a loop has a ``seq`` clause.

    :arg loop: the :class:`Loop` node.
    """
    return has_loop_directive(loop) and loop.parent.parent.sequential


def apply_loop_seq(loop):
    """
    Apply a ``seq`` clause to a loop.

    :arg loop: the :class:`Loop` node.
    """
    _prepare_loop_for_clause(loop)
    if has_gang_clause(loop):
        raise ValueError("Cannot apply seq to a loop with a gang clause.")
    if has_vector_clause(loop):
        raise ValueError("Cannot apply seq to a loop with a vector clause.")
    loop.parent.parent._sequential = True


def has_gang_clause(loop):
    """
    Determine whether a loop has a ``gang`` clause.

    :arg loop: the :class:`Loop` node.
    """
    return has_loop_directive(loop) and loop.parent.parent.gang


def apply_loop_gang(loop):
    """
    Apply a ``gang`` clause to a loop.

    :arg loop: the :class:`Loop` node.
    """
    _prepare_loop_for_clause(loop)
    if has_seq_clause(loop):
        raise ValueError("Cannot apply gang to a loop with a seq clause.")
    loop.parent.parent._gang = True


def has_vector_clause(loop):
    """
    Determine whether a loop has a ``vector`` clause.

    :arg loop: the :class:`Loop` node.
    """
    return has_loop_directive(loop) and loop.parent.parent.vector


def apply_loop_vector(loop):
    """
    Apply a ``vector`` clause to a loop.

    :arg loop: the :class:`Loop` node.
    """
    _prepare_loop_for_clause(loop)
    if has_seq_clause(loop):
        raise ValueError("Cannot apply vector to a loop with a seq clause.")
    loop.parent.parent._vector = True


def has_collapse_clause(loop):
    """
    Determine whether a loop lies within a collapsed loop nest.

    :arg loop: the :class:`Loop` node.
    """
    _check_loop(loop)
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
