PROGRAM single_loop
   IMPLICIT NONE
   INTEGER, PARAMETER :: n = 10
   INTEGER :: i
   REAL :: arr(n)

   DO i = 1, n
     arr(i) = 0.0
   END DO
END PROGRAM single_loop
