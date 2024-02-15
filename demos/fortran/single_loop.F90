! (C) Crown Copyright, Met Office. All rights reserved.
!
! This file is part of PSyACC and is released under the BSD 3-Clause license.
! See LICENSE in the root of the repository for full licensing details.

PROGRAM single_loop
  IMPLICIT NONE
  INTEGER, PARAMETER :: n = 10
  INTEGER :: i
  REAL :: arr(n)

  DO i = 1, n
    arr(i) = 0.0
  END DO
END PROGRAM single_loop
