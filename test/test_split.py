from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyacc.split import follows, split_consecutive
import code_snippets as cs
import pytest

API = "nemo"


def test_follows(parser):
    """
    Test that :func:`follows` correctly determines whether one node follows
    another.
    """
    code = parser(FortranStringReader(cs.loop_with_3_assignments))
    psy = PSyFactory(API, distributed_memory=False).create(code)
    schedule = psy.invokes.invoke_list[0].schedule
    assignments = schedule.walk(nodes.Assignment)
    assert follows(*assignments[:2])
    assert follows(*assignments[1:])
    assert not follows(*assignments[::2])


def test_split_consecutive(parser):
    """
    Test that :func:`split_consecutive` correctly determines consecutive nodes.
    """
    code = parser(FortranStringReader(cs.loop_with_3_assignments))
    psy = PSyFactory(API, distributed_memory=False).create(code)
    schedule = psy.invokes.invoke_list[0].schedule
    assignments = schedule.walk(nodes.Assignment)
    assert len(split_consecutive(assignments)) == 1
    assert len(split_consecutive(assignments[::2])) == 2


def test_split_consecutive_valuerror(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`split_consecutive` is
    called with a block of nodes from different depths.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory(API, distributed_memory=False).create(code)
    schedule = psy.invokes.invoke_list[0].schedule
    loops = schedule.walk(nodes.Loop)
    expected = "Block contains nodes with different depths."
    with pytest.raises(ValueError, match=expected):
        split_consecutive(loops)
