from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective, ACCLoopTrans
from psyacc.acc_kernels import has_kernels_directive


def has_loop_directive(node):
    """
    Determine whether a node is inside an OpenACC loop directive.
    """
    assert isinstance(node, nodes.Node)
    return node.ancestor(ACCLoopDirective)


def apply_loop_directive(loop, **kwargs):
    """
    Apply OpenACC loop directives around a block of code.

    Any keyword arguments are passed to :meth:`apply`.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not has_kernels_directive(loop):
        raise ValueError("Cannot apply a loop directive without a kernels directive.")
    ACCLoopTrans().apply(loop, **kwargs)
