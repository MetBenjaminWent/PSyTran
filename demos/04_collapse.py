# ..
#    (C) Crown Copyright, Met Office. All rights reserved.
#
#    This file is part of PSyACC and is released under the BSD 3-Clause license.
#    See LICENSE in the root of the repository for full licensing details.
#
#
# Demo 4: Applying OpenACC ``collapse`` clauses using PSyACC
# ==========================================================
#
# The `previous demo <03_loop.py.html>`__ showed how to insert OpenACC ``loop``
# directives with ``gang``, ``vector``, and ``seq`` clauses into Fortran code using
# PSyACC. In this demo, we consider the ``collapse`` clause, which can be used to
# combine loops whose iterations are independent of one another, to increase data
# throughput.
#
# Consider again the same double loop example:
#
# .. code-block:: fortran
#
#    PROGRAM double_loop
#      IMPLICIT NONE
#      INTEGER, PARAMETER :: m = 10
#      INTEGER, PARAMETER :: n = 1000
#      INTEGER :: i, j
#      REAL :: arr(m,n)
#
#      DO j = 1, n
#        DO i = 1, m
#          arr(i,j) = 0.0
#        END DO
#      END DO
#    END PROGRAM double_loop
#
# Convince yourself that combining the ``j`` and ``i`` loops as follows would have the
# same result.
#
# .. code-block:: fortran
#
#      mn = m * n
#      DO k = 1, mn
#        i = MOD(mn,m)
#        j = (k - i) / m
#        arr(i,j) = 0.0
#      END DO
#
# This is effectively what the OpenACC ``collapse`` clause does.
#
# The PSyclone command for this demo is as follows.
#
# .. code-block:: bash
#
#    psyclone -api nemo --config ../.psyclone/psyclone.cfg fortran/double_loop.F90 \
#       --script 04_collapse.py -opsy outputs/04_collapse-double_loop.F90
#
# Again, begin by importing from the namespace PSyACC, as well as the ``nodes`` module
# of PSyclone. ::

from psyacc import *
from psyclone.psyir import nodes

# In the demos so far, we have built up transformation scripts piece by piece. This was
# done for demonstration purposes; in many cases, it is easier to just write it out at
# once. In the following ``trans`` script, you will recognise many of the elements from
# the previous demos. The difference is the call to
# :func:`psyacc.clauses.apply_loop_collapse`, which takes a second argument
# ``collapse``. This is the number of loops within the nest that should be collapsed
# together, starting from the loop that it is being applied to. ::


def trans(psy):
    schedule = psy.invokes.invoke_list[0].schedule

    # Get the outer-most loop
    loops = schedule.walk(nodes.Loop)
    outer_loops = list(filter(is_outer_loop, loops))
    assert len(outer_loops) == 1
    outer_loop = outer_loops[0]

    # Insert OpenACC syntax
    apply_kernels_directive(outer_loop)
    apply_loop_collapse(outer_loop, collapse=2)
    return psy


# Running this example using the PSyclone command above, you should find that the output
# in ``outputs/04_collapse-double_loop.F90`` reads as follows.
#
# .. code-block:: fortran
#
#    program double_loop
#      integer, parameter :: m = 10
#      integer, parameter :: n = 1000
#      integer :: i
#      integer :: j
#      real, dimension(m,n) :: arr
#
#      !$acc kernels
#      !$acc loop independent collapse(2)
#      do j = 1, n, 1
#        do i = 1, m, 1
#          arr(i,j) = 0.0
#        enddo
#      enddo
#      !$acc end kernels
#
#    end program double_loop
#
# This demo can also be viewed as a `Python script <04_collapse.py>`__.
