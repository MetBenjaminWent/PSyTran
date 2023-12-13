# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes

__all__ = ["is_character"]


def is_character(node):
    """
    Determine whether a :class:`Reference` is of type `CHARACTER`.
    """
    assert isinstance(node, nodes.Reference)
    return "CHARACTER" in node.datatype.type_text
