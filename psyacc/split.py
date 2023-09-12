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


def split_consecutive(block):
    """
    Given a block of nodes at some depth, separate out those which follow one another.
    """
    blocks = []
    current = []
    depth = block[0].depth
    for node in block:
        if node.depth != depth:
            raise ValueError("Block contains nodes with different depths.")
        if len(current) == 0 or follows(current[-1], node):
            current.append(node)
        else:
            blocks.append(current)
            current = [node]
    if len(current) > 0:
        blocks.append(current)
    return blocks
