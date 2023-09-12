def follows(node1, node2):
    """
    Determine whether two nodes immediately follow one another.
    """
    if node1 is None or node2 is None:
        return False
    return (
        node2.sameParent(node1)
        and node2 in node1.following()
        and node1.position + 1 == node2.position
    )
