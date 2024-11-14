# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
This module provides functions for converting the array notation used in a
:py:class:`Schedule`.
"""

from psyclone.psyir import nodes
from psyclone.psyir import transformations as trans
from psyclone.psyir.transformations.arrayassignment2loops_trans import (
    ArrayAssignment2LoopsTrans,
)
from psyclone.psyir import symbols
from psyclone.transformations import TransformationError
from psyacc.family import has_ancestor

__all__ = ["convert_array_notation", "convert_range_loops"]


def convert_array_notation(schedule):
    """
    Convert implicit array range assignments into explicit ones.

    Wrapper for the :meth:`apply` method of :class:`Reference2ArrayRangeTrans`.
    If this fails due to a :class:`TransformationError` then the conversion is
    skipped.

    :arg schedule: the Schedule to transform.
    :type schedule: :py:class:`Schedule`
    """
    for reference in schedule.walk(nodes.Reference, stop_type=nodes.Reference):
        if has_ancestor(reference, nodes.Call):
            continue
        if isinstance(reference.symbol, symbols.DataSymbol):
            try:
                trans.Reference2ArrayRangeTrans().apply(reference)
            except TransformationError:  # pragma: no cover
                pass


def convert_range_loops(schedule):
    """
    Convert explicit array range assignments into loops.

    Wrapper for the :meth:`apply` method of
    :class:`ArrayAssignment2LoopsTrans`. If this fails due to a
    :class:`TransformationError` then the conversion is skipped.

    :arg schedule: the Schedule to transform.
    :type schedule: :py:class:`Schedule`
    """
    for assign in schedule.walk(nodes.Assignment):
        try:
            ArrayAssignment2LoopsTrans().apply(assign)
        except TransformationError:  # pragma: no cover
            pass
