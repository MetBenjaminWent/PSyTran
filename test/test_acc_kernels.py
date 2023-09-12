from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyacc.acc_kernels import is_outer_loop
import code_snippets as cs
import pytest

API = "nemo"


def test_is_outer_loop(parser):
    """
    Test that a :func:`is_outer_loop` correctly determines whether a loop is
    outer-most in its nest.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory(API, distributed_memory=False).create(code)
    schedule = psy.invokes.invoke_list[0].schedule
    loops = schedule.walk(nodes.Loop)
    assert is_outer_loop(loops[0])
    assert not is_outer_loop(loops[1])


def test_is_outer_loop_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`is_outer_loop` is
    called with something other than a :class:`Loop`.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory(API, distributed_memory=False).create(code)
    schedule = psy.invokes.invoke_list[0].schedule
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        is_outer_loop(assignments[0])
