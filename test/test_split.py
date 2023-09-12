from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyclone.psyir import nodes
from psyacc.split import follows

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
