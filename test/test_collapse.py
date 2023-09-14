from psyclone.psyir import nodes
from utils import *
import pytest


def test_is_collapsed_no_kernels(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop which doesn't
    have a kernels directive.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not is_collapsed(loops[0])


def test_is_collapsed_kernels_no_loop(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop with a kernels
    directive but no loop directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    assert not is_collapsed(loops[0])


def test_is_collapsed_loop_no_collapse(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop with a loop
    directive but no collapse clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert not is_collapsed(loops[0])
