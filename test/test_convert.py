# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyACC's `convert` module.
"""

import pytest
import code_snippets as cs
from utils import get_schedule
from psyclone.psyir import nodes
from psyacc.convert import convert_array_notation, convert_range_loops


@pytest.fixture(name="dim", params=[1, 2, 3])
def fixture_dim(request):
    """Pytest fixture for spatial dimension."""
    return request.param


array_assignment = {
    1: cs.array_assignment_1d,
    2: cs.array_assignment_2d,
    3: cs.array_assignment_3d,
}

implied_array_assignment = {
    1: cs.implied_array_assignment_1d,
    2: cs.implied_array_assignment_2d,
    3: cs.implied_array_assignment_3d,
}


def test_convert_array_notation(fortran_reader, dim):
    """
    Test that :func:`convert_array_notation` successfully converts an implied
    array range assignment into an explicit one.
    """
    schedule = get_schedule(fortran_reader, implied_array_assignment[dim])
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
    convert_array_notation(schedule)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == dim
    assert str(schedule) == str(
        get_schedule(fortran_reader, array_assignment[dim])
    )


def test_avoid_array_notation_subroutine(fortran_reader):
    """
    Test that :func:`convert_array_notation` does not use array notation in
    subroutine calls.
    """
    schedule = get_schedule(fortran_reader, cs.subroutine_call)
    assert len(schedule.walk(nodes.Call)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
    convert_array_notation(schedule)
    assert len(schedule.walk(nodes.Call)) == 1
    assert len(schedule.walk(nodes.Range)) == 0


def test_convert_range_loops(fortran_reader, dim):
    """
    Test that :func:`convert_range_loops` successfully converts an array range
    assignment into a loop. If dim > 1 then the loop should itself contain an
    array range assignment.
    """
    schedule = get_schedule(fortran_reader, array_assignment[dim])
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Loop)) == 0
    convert_range_loops(schedule)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Loop)) == dim
