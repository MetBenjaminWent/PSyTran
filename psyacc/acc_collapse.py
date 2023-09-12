from psyclone.psyir import nodes


def get_ancestors(loop):
    """
    Get all ancestors of a loop which are also loops.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    ancestors = []
    current = loop
    while current.ancestor(nodes.Loop) is not None:
        current = current.ancestor(nodes.Loop)
        ancestors.append(current)
    return ancestors
