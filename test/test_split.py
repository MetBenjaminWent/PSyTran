from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyacc.split import follows, split_consecutive
import pytest

API = "nemo"

_loop_with_3_assignments = """
    PROGRAM test
      REAL :: a(10)
      REAL :: b(10)
      INTEGER :: i

      DO i = 1, 10
        a(i) = 0.0
        b(i) = a(i)
        a(i) = 1.0
      END DO
    END PROGRAM test
    """

_double_loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
      END DO
    END PROGRAM test
    """


def test_follows(parser):
    """
    Test that :func:`follows` correctly determines whether one node follows
    another.
    """
    code = parser(FortranStringReader(_loop_with_3_assignments))
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
    code = parser(FortranStringReader(_loop_with_3_assignments))
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
    code = parser(FortranStringReader(_double_loop_with_1_assignment))
    psy = PSyFactory(API, distributed_memory=False).create(code)
    schedule = psy.invokes.invoke_list[0].schedule
    loops = schedule.walk(nodes.Loop)
    expected = "Block contains nodes with different depths."
    with pytest.raises(ValueError, match=expected):
        split_consecutive(loops)
