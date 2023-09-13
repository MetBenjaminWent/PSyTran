from psyclone.psyir import nodes
from psyacc.kernels import has_kernels_directive
from psyacc.loop import has_loop_directive, apply_loop_directive


def _apply_loop_clause(loop):
    """
    Apply a loop clause to a loop.

    :arg loop: the :class:`Loop` node.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not has_kernels_directive(loop):
        raise ValueError("Cannot apply a loop clause without a kernels directive.")
    if not has_loop_directive(loop):
        apply_loop_directive(loop)


def apply_loop_seq(loop):
    """
    Apply a seq clause to a loop.

    :arg loop: the :class:`Loop` node.
    """
    _apply_loop_clause(loop)
    loop.parent.parent._sequential = True


def apply_loop_gang(loop):
    """
    Apply a gang clause to a loop.

    :arg loop: the :class:`Loop` node.
    """
    _apply_loop_clause(loop)
    loop.parent.parent._gang = True


def apply_loop_vector(loop):
    """
    Apply a vector clause to a loop.

    :arg loop: the :class:`Loop` node.
    """
    _apply_loop_clause(loop)
    loop.parent.parent._vector = True
