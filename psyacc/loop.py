from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective, ACCLoopTrans
from psyacc.kernels import has_kernels_directive, is_outer_loop

__all__ = ["has_loop_directive", "apply_loop_directive", "is_perfectly_nested"]


def has_loop_directive(node):
    """
    Determine whether a node has an OpenACC ``loop`` directive.
    """
    assert isinstance(node, nodes.Node)
    return isinstance(node.parent.parent, ACCLoopDirective)


def apply_loop_directive(loop, **kwargs):
    """
    Apply ``loop`` directives around a block of code.

    Any keyword arguments are passed to :meth:`apply`.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not has_kernels_directive(loop):
        raise ValueError("Cannot apply a loop directive without a kernels directive.")
    ACCLoopTrans().apply(loop, **kwargs)


def is_perfectly_nested(loop):
    """
    Determine whether a loop nest is perfectly nested, i.e., each level except
    the deepest contains only the next loop.

    :arg loop: the outer-most loop of the nest
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not is_outer_loop(loop):
        raise ValueError("is_perfectly_nested should be applied to outer-most loop")
    loops = loop.walk(nodes.Loop)
    depth = loop.depth
    for i in range(1, len(loops)):
        depth += 2
        child_nodes = loops[i].walk(nodes.Node)
        nodes_at_depth = [node for node in child_nodes if node.depth == depth]
        if len(nodes_at_depth) != 1:
            return False
        assert isinstance(nodes_at_depth[0], nodes.Loop)
    else:
        return True
