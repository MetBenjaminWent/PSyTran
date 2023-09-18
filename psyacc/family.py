from psyclone.psyir import nodes

__all__ = ["get_descendents", "get_ancestors", "is_next_sibling"]


def get_descendents(node, inclusive=False, node_type=nodes.Node, depth=None):
    """
    Get all ancestors of a node with a given type.

    :arg loop: the node to search for descendents of.
    :arg inclusive: if ``True``, the current loop is included.
    :arg node_type: the type of node to search for.
    :kwarg depth: specify a depth for the descendents to have.
    """
    assert isinstance(node, nodes.Node)
    if not isinstance(inclusive, bool):
        raise TypeError(f"Expected a bool, not '{type(inclusive)}'.")
    assert issubclass(node_type, nodes.Node)
    if depth is not None and not isinstance(depth, int):
        raise TypeError(f"Expected an int, not '{type(depth)}'.")
    descendents = list(node.walk(node_type))
    if not inclusive and isinstance(node, node_type):
        descendents.pop(0)
    if depth is not None:
        descendents = [d for d in descendents if d.depth == depth]
    return descendents


def get_ancestors(node, inclusive=False, node_type=nodes.Loop, depth=None):
    """
    Get all ancestors of a node with a given type.

    :arg loop: the node to search for ancestors of.
    :arg inclusive: if ``True``, the current loop is included.
    :arg node_type: the type of node to search for.
    :kwarg depth: specify a depth for the ancestors to have.
    """
    assert isinstance(node, nodes.Node)
    if not isinstance(inclusive, bool):
        raise TypeError(f"Expected a bool, not '{type(inclusive)}'.")
    assert issubclass(node_type, nodes.Node)
    if depth is not None and not isinstance(depth, int):
        raise TypeError(f"Expected an int, not '{type(depth)}'.")
    ancestors = []
    current = node
    if inclusive and isinstance(node, node_type):
        ancestors.append(current)
    while current.ancestor(node_type) is not None:
        current = current.ancestor(node_type)
        ancestors.append(current)
    if depth is not None:
        ancestors = [parent for parent in ancestors if parent.depth == depth]
    return ancestors


def is_next_sibling(node1, node2):
    """
    Determine whether one :class:`Node` immediately follows another.

    :arg node1: the first node.
    :arg node2: the second node.
    """
    assert isinstance(node1, nodes.Node)
    assert isinstance(node2, nodes.Node)
    return (
        node2.sameParent(node1)
        and node2 in node1.following()
        and node1.position + 1 == node2.position
    )
