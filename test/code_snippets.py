loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10)
      INTEGER :: i

      DO i = 1, 10
        a(i) = 0.0
      END DO
    END PROGRAM test
    """

double_loop_with_1_assignment = """
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

triple_loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
        END DO
      END DO
    END PROGRAM test
    """

quadruple_loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k
      INTEGER :: l

      DO l = 1, 10
        DO k = 1, 10
          DO j = 1, 10
            DO i = 1, 10
              a(i,j,k,l) = 0.0
            END DO
          END DO
        END DO
      END DO
    END PROGRAM test
    """

loop_with_3_assignments = """
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

imperfectly_nested_double_loop = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
        a(1,j) = 1.0
      END DO
    END PROGRAM test
    """

serial_loop = """
    PROGRAM test
      REAL :: a(10)
      INTEGER :: i

      a(1) = 0.0
      DO i = 2, 10
        a(i) = a(i-1)
      END DO
    END PROGRAM test
    """
