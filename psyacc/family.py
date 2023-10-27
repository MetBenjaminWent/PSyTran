# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyclone.nemo import NemoKern

__all__ = [
    "get_descendents",
    "get_ancestors",
    "get_children",
    "get_parent",
    "get_siblings",
    "has_descendent",
    "has_ancestor",
    "are_siblings",
    "is_next_sibling",
]


class NoneType:
    """
    Dummy class for type checking.
    """

    pass


def get_descendents(
    node, inclusive=False, node_type=nodes.Node, exclude=NoneType, depth=None
):
    """
    Get all ancestors of a node with a given type.

    :arg node: the node to search for descendents of.
    :arg inclusive: if ``True``, the current node is included.
    :kwarg node_type: the type of node to search for.
    :kwarg exclude: type(s) of node to exclude.
    :kwarg depth: specify a depth for the descendents to have.
    """
    assert isinstance(node, nodes.Node)
    if not isinstance(inclusive, bool):
        raise TypeError(f"Expected a bool, not '{type(inclusive)}'.")
    assert issubclass(node_type, nodes.Node)
    if depth is not None and not isinstance(depth, int):
        raise TypeError(f"Expected an int, not '{type(depth)}'.")
    descendents = [
        descendent
        for descendent in node.walk(node_type)
        if not isinstance(descendent, exclude) and (inclusive or descendent is not node)
    ]
    if depth is not None:
        descendents = [d for d in descendents if d.depth == depth]
    return descendents


def get_ancestors(
    node, inclusive=False, node_type=nodes.Loop, exclude=NoneType, depth=None
):
    """
    Get all ancestors of a node with a given type.

    :arg node: the node to search for ancestors of.
    :arg inclusive: if ``True``, the current node is included.
    :kwarg node_type: the type of node to search for.
    :kwarg exclude: type(s) of node to exclude.
    :kwarg depth: specify a depth for the ancestors to have.
    """
    assert isinstance(node, nodes.Node)
    if not isinstance(inclusive, bool):
        raise TypeError(f"Expected a bool, not '{type(inclusive)}'.")
    assert issubclass(node_type, nodes.Node)
    if depth is not None and not isinstance(depth, int):
        raise TypeError(f"Expected an int, not '{type(depth)}'.")
    ancestors = []
    node = node.ancestor(node_type, excluding=exclude, include_self=inclusive)
    while node is not None:
        ancestors.append(node)
        node = node.ancestor(node_type, excluding=exclude)
    if depth is not None:
        ancestors = [a for a in ancestors if a.depth == depth]
    return ancestors


def get_children(node, node_type=nodes.Node, exclude=NoneType):
    """
    Get all immediate descendents of a node with a given type, i.e., those at
    the next depth level.

    :arg node: the node to search for descendents of.
    :kwarg node_type: the type of node to search for.
    :kwarg exclude: type(s) of node to exclude.
    """
    children = get_descendents(
        node, node_type=node_type, exclude=exclude, depth=node.depth + 2
    )
    if len(children) == 1 and isinstance(children[0], NemoKern):
        assert not isinstance(node, NemoKern)  # Avoid infinite loop
        return get_children(children[0], node_type=node_type, exclude=exclude)
    return children


def get_parent(node, node_type=nodes.Node, exclude=None):
    """
    Get the immediate ancestors of a node with a given type, i.e., the one at
    the previous depth level.

    :arg node: the node to search for ancestors of.
    :arg node_type: the type of node to search for.
    :kwarg exclude: type(s) of node to exclude.
    """
    if node_type == exclude:
        return None
    parents = get_ancestors(
        node, node_type=node_type, exclude=exclude, depth=node.depth - 2
    )
    if len(parents) == 0:
        return None
    assert len(parents) == 1
    parent = parents[0]
    if isinstance(parent, NemoKern):
        assert not isinstance(node, NemoKern)  # Avoid infinite loop
        return get_parent(parent, node_type=node_type, exclude=exclude)
    return parent


def get_siblings(node, inclusive=False, node_type=nodes.Node, exclude=NoneType):
    """
    Get all nodes with a given type at the same depth level.

    :arg node: the node to search for siblings of.
    :arg inclusive: if ``True``, the current node is included.
    :arg node_type: the type of node to search for.
    :kwarg exclude: type(s) of node to exclude.
    """
    return [
        sibling
        for sibling in node.siblings
        if isinstance(sibling, node_type)
        and not isinstance(sibling, exclude)
        and (inclusive or sibling is not node)
    ]


def has_descendent(node, node_type, inclusive=False):
    """
    Check whether a node has a descendent node with a given type.

    :arg node: the node to check for descendents of.
    :arg node_type: the type of node to search for.
    :arg inclusive: if ``True``, the current node is included.
    """
    return bool(get_descendents(node, inclusive=inclusive, node_type=node_type))


def has_ancestor(node, node_type, inclusive=False):
    """
    Check whether a node has an ancestor node with a given type.

    :arg node: the node to check for ancestors of.
    :arg node_type: the type of node to search for.
    :arg inclusive: if ``True``, the current node is included.
    """
    return bool(get_ancestors(node, inclusive=inclusive, node_type=node_type))


def are_siblings(*nodes):
    r"""
    Determine whether a collection of :class:`Node`\s have the same parent.
    """
    assert len(nodes) > 0
    if len(nodes) == 1:
        return True
    for node in nodes[1:]:
        if not nodes[0].sameParent(node):
            return False
    else:
        return True


def is_next_sibling(node1, node2):
    """
    Determine whether one :class:`Node` immediately follows another.

    :arg node1: the first node.
    :arg node2: the second node.
    """
    return (
        are_siblings(node1, node2)
        and node2 in node1.following()
        and node1.position + 1 == node2.position
    )
