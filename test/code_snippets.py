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

triple_loop_with_conditional_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            IF (i > 0) THEN
              a(i,j,k) = 0.0
            END IF
          END DO
        END DO
      END DO
    END PROGRAM test
    """

double_loop_with_2_loops = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
        DO i = 1, 10
          a(i,j) = 0.0
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

loop_with_2_literal_assignments = """
    PROGRAM test
      REAL :: a(10)
      REAL :: b(10)
      INTEGER :: i

      DO i = 1, 10
        a(i) = 0.0
        b(i) = 1.0
      END DO
    END PROGRAM test
    """

double_loop_with_3_assignments = """
    PROGRAM test
      REAL :: a(10,10)
      REAL :: b(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
          b(i,j) = a(i,j)
          a(i,j) = 1.0
        END DO
      END DO
    END PROGRAM test
    """

double_loop_with_conditional_3_assignments = """
    PROGRAM test
      REAL :: a(10,10)
      REAL :: b(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          IF (i > 0) THEN
            a(i,j) = 0.0
            b(i,j) = a(i,j)
            a(i,j) = 1.0
          END IF
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_double_loop_with_if = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        IF (j > 0) THEN
          DO i = 1, 10
            a(i,j) = 0.0
          END DO
        END IF
      END DO
    END PROGRAM test
    """

imperfectly_nested_double_loop_before = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        a(1,j) = 1.0
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_double_loop_after = """
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

imperfectly_nested_triple_loop_with_if = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        IF (k > 0) THEN
          DO j = 1, 10
            DO i = 1, 10
              a(i,j,k) = 0.0
            END DO
          END DO
        END IF
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop_before = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        a(1,1,k) = 1.0
        DO j = 1, 10
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop_after = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
        END DO
        a(1,1,k) = 1.0
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop_before_with_if = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        a(1,1,k) = 1.0
        DO j = 1, 10
          DO i = 1, 10
            IF (i > 0) THEN
              a(i,j,k) = 0.0
            END IF
          END DO
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop_after_with_if = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            IF (i > 0) THEN
              a(i,j,k) = 0.0
            END IF
          END DO
        END DO
        a(1,1,k) = 1.0
      END DO
    END PROGRAM test
    """

conditional_imperfectly_nested_triple_loop = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        IF (k > 0) THEN
          DO j = 1, 10
            DO i = 1, 10
              a(i,j,k) = 0.0
            END DO
          END DO
        END IF
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
