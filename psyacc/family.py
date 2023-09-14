from psyclone.psyir import nodes

__all__ = ["get_ancestors"]


def get_ancestors(node, inclusive=False, node_type=nodes.Loop):
    """
    Get all ancestors of a node.

    :arg loop: the node to search for ancestors of.
    :arg inclusive: if ``True``, the current loop is included.
    :arg node_type: the type of node to search for.
    """
    assert isinstance(node, nodes.Node)
    if not isinstance(inclusive, bool):
        raise TypeError(f"Expected a bool, not '{type(inclusive)}'.")
    assert issubclass(node_type, nodes.Node)
    ancestors = []
    current = node
    if inclusive and isinstance(node, node_type):
        ancestors.append(current)
    while current.ancestor(node_type) is not None:
        current = current.ancestor(node_type)
        ancestors.append(current)
    return ancestors
