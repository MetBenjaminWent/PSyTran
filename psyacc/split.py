from psyacc.family import is_next_sibling

__all__ = ["split_consecutive"]


def split_consecutive(block):
    """
    Given a block of nodes at some depth, separate out those which follow one
    another.
    """
    blocks = []
    current = []
    depth = block[0].depth
    for node in block:
        if node.depth != depth:
            raise ValueError("Block contains nodes with different depths.")
        if len(current) == 0 or is_next_sibling(current[-1], node):
            current.append(node)
        else:
            blocks.append(current)
            current = [node]
    if len(current) > 0:
        blocks.append(current)
    return blocks
