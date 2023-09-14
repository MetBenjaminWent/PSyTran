from psyclone.psyir import nodes
from psyclone.transformations import ACCKernelsDirective, ACCKernelsTrans

__all__ = ["is_outer_loop", "has_kernels_directive", "apply_kernels_directive"]


def is_outer_loop(loop):
    """
    Determine whether a loop is outer-most in its nest.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    return loop.ancestor(nodes.Loop) is None


def has_kernels_directive(node):
    """
    Determine whether a node is inside a ``kernels`` directive.
    """
    assert isinstance(node, nodes.Node)
    return node.ancestor(ACCKernelsDirective)


def apply_kernels_directive(block, **kwargs):
    """
    Apply a ``kernels`` directive around a block of code.

    Any keyword arguments are passed to :meth:`apply`.
    """
    ACCKernelsTrans().apply(block, **kwargs)
