PROGRAM double_loop
   IMPLICIT NONE
   INTEGER, PARAMETER :: m = 10
   INTEGER, PARAMETER :: n = 1000
   INTEGER :: i, j
   REAL :: arr(m,n)

   DO j = 1, n
     DO i = 1, m
       arr(i,j) = 0.0
     END DO
   END DO
END PROGRAM double_loop
