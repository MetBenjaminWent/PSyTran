# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for members of PSyACC's `types` module.
"""

from psyclone.psyir import nodes
from utils import get_schedule

import code_snippets as cs
from psyacc.types import is_character, refers_to_character


def test_is_character(fortran_reader):
    """
    Test that :func:`is_character` correctly determines variables of intrinsic
    type `CHARACTER`.
    """
    schedule = get_schedule(fortran_reader, cs.string_assignment)
    assert is_character(schedule.walk(nodes.Reference)[0])
    assert refers_to_character(schedule)
