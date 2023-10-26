# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyacc.family import is_next_sibling

__all__ = ["split_consecutive"]


def split_consecutive(block):
    """
    Given a block of nodes, separate out those which directly follow one
    another.

    The nodes may have different depths.
    """
    blocks = {}
    current = {}
    for node in block:
        depth = node.depth
        if depth not in blocks:
            blocks[depth] = []
        if depth not in current:
            current[depth] = [node]
            continue
        if is_next_sibling(current[depth][-1], node):
            current[depth].append(node)
        else:
            blocks[depth].append(current[depth])
            current[depth] = [node]

    ret = []
    for depth, values in current.items():
        if len(values) > 0:
            blocks[depth].append(values)
        ret += blocks[depth]
    assert isinstance(ret, list)
    return ret
