from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopTrans
from psyacc.kernels import has_kernels_directive

__all__ = ["apply_loop_directive"]


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
