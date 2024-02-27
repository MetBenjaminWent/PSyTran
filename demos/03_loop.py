# ..
#    (C) Crown Copyright 2023, Met Office. All rights reserved.
#
#    This file is part of PSyACC and is released under the BSD 3-Clause
#    license. See LICENSE in the root of the repository for full licensing
#    details.
#
#
# Demo 3: Applying OpenACC ``loop`` directives using PSyACC
# =========================================================
#
# The `previous demo <02_kernels.py.html>`__ showed how to insert OpenACC
# ``kernels`` directives into Fortran code using PSyACC. Such directives mark
# out sections of code to be run on the GPU. In this demo, we additionally
# apply OpenACC `loop` directives to loops within such regions and configure
# them with different clauses.
#
# We have already considered a single loop for zeroing every entry of an array.
# Now consider the extension of this to the case of a 2D array, as given in
# ``fortran/double_loop.py``:
#
# .. literalinclude:: fortran/double_loop.F90
#    :language: fortran
#    :lines: 6-
#
# Use the following command for this demo:
#
# .. literalinclude:: 03_loop.sh
#    :language: bash
#    :lines: 8-
#
# Again, begin by importing from the namespace PSyACC, as well as the ``nodes``
# module of PSyclone. ::

from psyacc import *
from psyclone.psyir import nodes

# We already saw how to extract a loop from the schedule and apply an OpenACC
# ``kernels`` directive to it. In this case, there are two loops. Loops are
# parsed by PSyclone according to depth, so in a simple example such as this we
# can easily infer which loop is the first and which is the second. However,
# this kind of information isn't available in general. We can make use of
# :py:func:`psyacc.loop.is_outer_loop` to query whether a loop is outer-most in
# its loop nest. Inspecting the API documentation, we see that this is a
# Boolean-valued function, which means we can use :py:func:`filter` to extract
# only the loops for which it returns ``True``. ::


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
# :py:class:`psyacc.directives.apply_loop_directive`. All this does is mark
# them out; we will add clauses subsequently. ::


def apply_openacc_loops(psy):
    schedule = psy.invokes.invoke_list[0].schedule
    for loop in schedule.walk(nodes.Loop):
        apply_loop_directive(loop)
    return psy


# Now that each loop has a directive, we may iterate over each loop and
# modify the attributes of the corresponding
# :py:class:`psyclone.psyir.nodes.acc_directives.ACCLoopDirective` instance.
# These attributes correspond to whether various clauses are to be used, e.g.,
# ``seq``, ``gang``, ``vector``. Here ``seq`` tells the compiler *not* to
# parallelise the loop, i.e., run it in serial. The ``gang`` and ``vector``
# clauses refer to different ways to parallelise the loop.
#
# A good general approach is to apply both ``gang`` and ``vector`` parallelism
# to outer loops and ``seq`` to all other loops in the nest. We can again use
# :py:func:`psyacc.loop.is_outer_loop` to query whether a loop is outer-most or
# not. If so, we can apply both :py:func:`psyacc.clauses.apply_loop_gang` and
# :py:func:`psyacc.clauses.apply_loop_vector`. If not, we can apply
# :py:func:`psyacc.clauses.apply_loop_seq`.
#
# .. note::
#
#    Whilst the OpenACC syntax is to use ``seq`` to denote a serial clause,
#    PSyclone uses the notation ``sequential`` internally. We don't need to
#    worry about this when using PSyACC, though, as PSyACC follows the OpenACC
#    standard in this case.
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


# Finally, we tie everything together by calling the composition of the above
# functions within the ``trans`` function. ::


def trans(psy):
    return insert_clauses(apply_openacc_loops(apply_openacc_kernels(psy)))


# The output in ``output/03_loop-double_loop.F90`` should be as follows.
#
# .. literalinclude:: outputs/03_loop-double_loop.F90
#    :language: fortran
#
# Hopefully that is as expected.
#
# Again, let's try compiling the PSyclone-generated program. This time, the
# required command is
#
# .. code-block:: bash
#
#    nvfortran -c -acc=gpu -Minfo=accel outputs/03_loop-double_loop.F90
#
# The expected compiler output is
#
# .. code-block::
#
#    double_loop:
#         13, Generating implicit copyout(arr(:m,:n)) [if not already present]
#         15, Loop is parallelizable
#         17, Generating NVIDIA GPU code
#             15, !$acc loop gang, vector(128) ! blockidx%x threadidx%x
#             17, !$acc loop seq
#
# Again, we see implicit use of the ``copyout`` clause. The loop on line 15 is
# determined to be parallelisable, and is parallelised in the way that we
# instructed, with a vector length of 128.
#
# Exercises
# ---------
#
# 1. Check that we get the same result if we drop the ``apply_openacc_loops``
#    step. Convince yourself why this happens by reading the API documentation
#    links referenced above.
#
# 2. Try applying this transformation script to the Fortran source code from
#    the `previous demo <02_kernels.py.html>`__, i.e.,
#    ``fortran/single_loop.py``.
#
# In the `next demo <04_collapse.py.html>`__, we'll revisit the double loop
# example and apply a different clause type: the ``collapse`` clause.
#
# This demo can also be viewed as a `Python script <03_loop.py>`__.
