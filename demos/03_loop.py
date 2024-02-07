# Demo 3: Applying OpenACC `loop` directives using PSyACC
# ===========================================================
#
# The `previous demo <02_kernels.py.html>`__ showed how to insert OpenACC `kernels`
# directives into Fortran code using PSyACC. Such directives mark out sections of code
# to be run on the GPU. In this demo, we additionally apply OpenACC `loop` directives to
# loops within such regions and configure them with different clauses.
#
# We have already considered a single loop for zeroing every entry of an array. Now
# consider the extension of this to the case of a 2D array, of dimension
# :math:`10\times1000`, as given in `fortran/double_loop.py`:
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
# *TODO*
#
# This demo can also be viewed as a `Python script <03_loop.py>`__.
