from psyclone.psyir import nodes
from psyclone.transformations import ACCKernelsDirective


def is_outer_loop(loop):
    """
    Determine whether a loop is outer-most in its nest.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    return loop.ancestor(nodes.Loop) is None


def has_kernels_directive(node):
    """
    Determine whether a node is inside an OpenACC kernels directive.
    """
    assert isinstance(node, nodes.Node)
    return node.ancestor(ACCKernelsDirective)
