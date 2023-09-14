from psyclone.psyir import nodes
from psyclone.transformations import ACCKernelsDirective, ACCKernelsTrans, ACCLoopDirective, ACCLoopTrans

__all__ = ["apply_kernels_directive", "has_kernels_directive", "apply_loop_directive", "has_loop_directive"]


def apply_kernels_directive(block, options={}):
    """
    Apply a ``kernels`` directive around a block of code.

    :arg block: the block of code in consideration.
    :kwarg options: a dictionary of clause options.
    """
    if not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    ACCKernelsTrans().apply(block, options=options)


def has_kernels_directive(node):
    """
    Determine whether a node is inside a ``kernels`` directive.
    """
    assert isinstance(node, nodes.Node)
    return node.ancestor(ACCKernelsDirective)


def apply_loop_directive(loop, options={}):
    """
    Apply a ``loop`` directive.

    :arg loop: the :class:`Loop` node.
    :kwarg options: a dictionary of clause options.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    if not has_kernels_directive(loop):
        raise ValueError("Cannot apply a loop directive without a kernels directive.")
    ACCLoopTrans().apply(loop, options=options)


def has_loop_directive(node):
    """
    Determine whether a node has an OpenACC ``loop`` directive.
    """
    assert isinstance(node, nodes.Node)
    return isinstance(node.parent.parent, ACCLoopDirective)
