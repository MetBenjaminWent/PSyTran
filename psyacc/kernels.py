from psyclone.psyir import nodes

__all__ = ["is_outer_loop"]


def is_outer_loop(loop):
    """
    Determine whether a loop is outer-most in its nest.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    return loop.ancestor(nodes.Loop) is None
