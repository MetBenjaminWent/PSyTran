# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
This module provides functions for checking whether ``CHARACTER`` assignments
are associated with a :py:class:`Node` or its descendents.
"""

from psyclone.psyir.nodes import Reference
from psyacc.family import get_descendents

__all__ = ["is_character", "refers_to_character"]


def is_character(ref, unknown_as=None):
    """
    Determine whether a Reference Node is of type ``CHARACTER``.

    :arg ref: the Node to check.
    :type ref: :py:class:`Reference`
    :kwarg unknown_as: Determines behaviour in the case where it cannot be
        determined whether the DataNode is a character. Defaults to None,
        in which case an exception is raised.
    :type unknown_as: Optional[bool]

    :returns: ``True`` if the Reference is to a ``CHARACTER``, else ``False``.
    :rtype: :py:class:`bool`
    """
    assert isinstance(ref, Reference)
    return ref.is_character(unknown_as=unknown_as)


def refers_to_character(node, unknown_as=None):
    r"""
    Determine whether a Node contains References to ``CHARACTER``\s.

    :arg node: the Node to check.
    :type node: :py:class:`Node`
    :kwarg unknown_as: Determines behaviour in the case where it cannot be
        determined whether the DataNode is a character. Defaults to None,
        in which case an exception is raised.
    :type unknown_as: Optional[bool]

    :returns: ``True`` if there are References to ``CHARACTER``\s, else
        ``False``.
    :rtype: :py:class:`bool`
    """
    return any(
        is_character(ref, unknown_as=unknown_as)
        for ref in get_descendents(node, Reference)
    )
