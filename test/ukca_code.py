asad_prls_kernel6 = """
  PROGRAM test
    INTEGER :: j, j2, jl, js, i1, i2, knspec, kl
    INTEGER :: nprdx2(2,knspec)
    INTEGER :: kspec(knspec)
    INTEGER :: ngrp(knspec,2)
    REAL :: pd(kl,knspec)
    REAL :: prk(kl,knspec)
    LOGICAL :: l_convergence_mask(kl)

    DO j = 1, knspec
      js = kspec(j)
      DO j2 = 1, ngrp(js,2)
        DO jl = 1, kl
          IF (l_convergence_mask(jl)) THEN
            i1 = nprdx2(1,js)
            i2 = nprdx2(2,js)
            pd(jl,js) = pd(jl,js) + prk(jl,i1) + prk(jl,i2)
          END IF
        END DO
      END DO
    END DO
  END PROGRAM test
  """
