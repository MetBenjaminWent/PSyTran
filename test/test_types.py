# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for members of PSyACC's `types` module.
"""

import pytest

from psyclone.psyir import nodes
from utils import get_schedule

import code_snippets as cs
from psyacc.types import is_character, refers_to_character


def test_is_character_error_string(fortran_reader):
    """
    Test that :func:`is_character` and :func:`refers_to_character` raise
    exceptions as expected when applied to a *string* assignment with the
    `unknown_as` parameter unset.
    """
    schedule = get_schedule(fortran_reader, cs.string_assignment)
    expected = (
        "is_character could not resolve whether the expression 'c' operates on"
        " characters."
    )
    with pytest.raises(ValueError, match=expected):
        is_character(schedule.walk(nodes.Reference)[0])
    with pytest.raises(ValueError, match=expected):
        refers_to_character(schedule)


def test_is_character_char(fortran_reader):
    """
    Test that :func:`is_character` and :func:`refers_to_character` correctly
    determine variables of intrinsic type `CHARACTER`.
    """
    schedule = get_schedule(fortran_reader, cs.char_assignment)
    assert is_character(schedule.walk(nodes.Reference)[0])
    assert refers_to_character(schedule)
