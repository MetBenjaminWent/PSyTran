from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyacc.acc_collapse import get_ancestors
import code_snippets as cs
import pytest


def test_get_ancestors_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`get_ancestors`
    is called with something other than a :class:`Loop`.
    """
    code = parser(FortranStringReader(cs.double_loop_with_1_assignment))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    assignments = psy.invokes.invoke_list[0].schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        get_ancestors(assignments[0])
