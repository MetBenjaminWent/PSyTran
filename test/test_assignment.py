# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyACC's `assignment` module.
"""

from psyclone.psyir import nodes
from utils import get_schedule

import code_snippets as cs
from psyacc.assignment import is_literal_assignment


def test_is_literal_assignment(fortran_reader):
    """
    Test that a :func:`is_literal_assignment` correctly determines a node
    corresponding to the assignment of a literal value.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    assert not is_literal_assignment(schedule.walk(nodes.Loop)[0])
    assert is_literal_assignment(schedule.walk(nodes.Assignment)[0])


def test_is_not_literal_assignment(fortran_reader):
    """
    Test that a :func:`is_literal_assignment` correctly determines a node
    not corresponding to the assignment of a literal value.
    """
    schedule = get_schedule(
        fortran_reader, cs.loop_with_1_assignment_and_intrinsic_call
    )
    assert not is_literal_assignment(schedule.walk(nodes.Assignment)[0])
