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


# Next, we apply ``loop`` directives to every loop using
# :py:class:`psyacc.directives.apply_loop_directive`. All this does is mark them out; we
# will add clauses subsequently. ::


def apply_openacc_loops(psy):
    schedule = psy.invokes.invoke_list[0].schedule
    for loop in schedule.walk(nodes.Loop):
        apply_loop_directive(loop)
    return psy


# Now that each loop has a directive, we may iterate over each loop and modify the
# attributes of the corresponding
# :py:class:`psyclone.psyir.nodes.acc_directives.ACCLoopDirective` instance. These
# attributes correspond to whether various clauses are to be used, e.g., ``seq``,
# ``gang``, ``vector``. Here ``seq`` tells the compiler *not* to parallelise the loop,
# i.e., run it in serial. The ``gang`` and ``vector`` clauses refer to different ways to
# parallelise the loop.
#
# A good general approach is to apply both ``gang`` and ``vector`` parallelism to outer
# loops and ``seq`` to all other loops in the nest. We can again use
# :py:func:`psyacc.loop.is_outer_loop` to query whether a loop is outer-most or not. If
# so, we can apply both :py:func:`psyacc.clauses.apply_loop_gang` and
# :py:func:`psyacc.clauses.apply_loop_vector`. If not, we can apply
# :py:func:`psyacc.clauses.apply_loop_seq`.
#
# .. note::
#
#    Whilst the OpenACC syntax is to use ``seq`` to denote a serial clause, PSyclone
#    uses the notation ``sequential`` internally. We don't need to worry about this
#    when using PSyACC, though, as PSyACC follows the OpenACC standard in this case.
#
# ::


def insert_clauses(psy):
    schedule = psy.invokes.invoke_list[0].schedule
    for loop in schedule.walk(nodes.Loop):
        if is_outer_loop(loop):
            apply_loop_gang(loop)
            apply_loop_vector(loop)
        else:
            apply_loop_seq(loop)
    return psy


# Finally, we tie everything together by calling the composition of the above functions
# within the ``trans`` function. ::


def trans(psy):
    return insert_clauses(apply_openacc_loops(apply_openacc_kernels(psy)))


# The output in ``output/03_loop-double_loop.F90`` should be as follows.
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
#      !$acc loop gang vector independent
#      do j = 1, n, 1
#        !$acc loop seq
#        do i = 1, m, 1
#          arr(i,j) = 0.0
#        enddo
#      enddo
#      !$acc end kernels
#
#    end program double_loop
#
# Hopefully that is as expected.
#
# Exercises
# ---------
#
# 1. Check that we get the same result if we drop the ``apply_openacc_loops`` step.
#    Convince yourself why this happens by reading the API documentation links
#    referenced above.
#
# 2. Try applying this transformation script to the Fortran source code from the
#    `previous demo <02_kernels.py.html>`__, i.e., ``fortran/single_loop.py``.
#
# In the `next demo <04_collapse.py.html>`__, we'll revisit the double loop example and
# apply a different clause type: the ``collapse`` clause.
#
# This demo can also be viewed as a `Python script <03_loop.py>`__.
