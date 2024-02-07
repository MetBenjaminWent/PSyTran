# Demo 3: Applying OpenACC ``loop`` directives using PSyACC
# =========================================================
#
# The `previous demo <02_kernels.py.html>`__ showed how to insert OpenACC ``kernels``
# directives into Fortran code using PSyACC. Such directives mark out sections of code
# to be run on the GPU. In this demo, we additionally apply OpenACC `loop` directives to
# loops within such regions and configure them with different clauses.
#
# We have already considered a single loop for zeroing every entry of an array. Now
# consider the extension of this to the case of a 2D array, of dimension
# :math:`10\times1000`, as given in ``fortran/double_loop.py``:
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
# Use the following command for this demo:
#
# .. code-block:: bash
#
#    psyclone -api nemo --config ../.psyclone/psyclone.cfg fortran/double_loop.F90 \
#       --script 03_loop.py -opsy outputs/03_loop-double_loop.F90
#
# Again, begin by importing from the namespace PSyACC, as well as the ``nodes`` module
# of PSyclone. ::

from psyacc import *
from psyclone.psyir import nodes

# We already saw how to extract a loop from the schedule and apply an OpenACC
# ``kernels`` directive to it. In this case, there are two loops. Loops are parsed by
# PSyclone according to depth, so in a simple example such as this we can easily infer
# which loop is the first and which is the second. However, this kind of information
# isn't available in general. We can make use of :py:func:`psyacc.loop.is_outer_loop`
# to query whether a loop is outer-most in its loop nest. Inspecting the API
# documentation, we see that this is a Boolean-valued function, which means we can use
# :py:func:`filter` to extract only the loops for which it returns ``True``. ::


def apply_openacc_kernels(psy):
    schedule = psy.invokes.invoke_list[0].schedule

    # Get the outer-most loop
    loops = schedule.walk(nodes.Loop)
    outer_loops = list(filter(is_outer_loop, loops))
    assert len(outer_loops) == 1
    outer_loop = outer_loops[0]

    # Insert OpenACC syntax
    apply_kernels_directive(outer_loop)
    return psy


#
# *TODO*
#


def trans(psy):
    psy = apply_openacc_kernels(psy)
    return psy


#
# *TODO*
#
#
# This demo can also be viewed as a `Python script <03_loop.py>`__.
