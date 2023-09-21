from psyclone.psyir import nodes

__all__ = [
    "get_descendents",
    "get_ancestors",
    "get_children",
    "get_siblings",
    "get_parents",
    "is_next_sibling",
]


def get_descendents(node, inclusive=False, node_type=nodes.Node, depth=None):
    """
    Get all ancestors of a node with a given type.

    :arg node: the node to search for descendents of.
    :arg inclusive: if ``True``, the current node is included.
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

    :arg node: the node to search for ancestors of.
    :arg inclusive: if ``True``, the current node is included.
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


def get_children(node, node_type=nodes.Node):
    """
    Get all immediate descendents of a node with a given type, i.e., those at the
    next depth level.

    :arg node: the node to search for descendents of.
    :arg node_type: the type of node to search for.
    """
    return get_descendents(node, node_type=node_type, depth=node.depth + 2)


def get_parents(node, node_type=nodes.Node):
    """
    Get all immediate ancestors of a node with a given type, i.e., those at the
    previous depth level.

    :arg node: the node to search for ancestors of.
    :arg node_type: the type of node to search for.
    """
    return get_ancestors(node, node_type=node_type, depth=node.depth - 2)


def get_siblings(node, inclusive=False, node_type=nodes.Node):
    """
    Get all nodes with a given type at the same depth level.

    :arg node: the node to search for siblings of.
    :arg inclusive: if ``True``, the current node is included.
    :arg node_type: the type of node to search for.
    """
    parents = get_parents(node, node_type=node_type)
    assert len(parents) == 1
    siblings = get_children(parents[0], node_type=node_type)
    for i, sibling in enumerate(siblings):
        assert sibling.depth == node.depth
        if not inclusive and sibling == node:
            siblings.pop(i)
            break
    return siblings


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
