#!/usr/bin/env python3
"""Independent exact integer arithmetic on the *reported* hybrid inequalities.

Checks outward-rounded 16-flat-trial E8 upper and arithmetic gap difference.
Does not check the underlying trial-space construction or the hybrid E9 lower
certificate; those are separate open mathematical proof obligations.
"""
from math import isqrt

ROWS = (
    (4, 4, 9, 117453728, 93506099, 23947629),
    (4, 4, 6, 103521056, 92508067, 11012989),
    (4, 5, 9, 140546984, 116928693, 23618291),
    (5, 5, 9, 168020667, 146228459, 21792208),
)

def upper_e8_micro(lx, ly, ratio):
    links = 2*lx*ly
    argument = 4*ratio*ratio + 3*links
    # E8 <= 3*links+2*r - sqrt(argument); to obtain a rigorous
    # **upper** integer micro-unit endpoint subtract FLOOR sqrt.
    sqrt_floor = isqrt(argument * 10**12)
    bound = (3*links + 2*ratio)*10**6 - sqrt_floor
    assert sqrt_floor**2 <= argument*10**12
    assert (sqrt_floor+1)**2 > argument*10**12
    return bound

def check():
    for lx, ly, r, lower_e9, upper_e8, gap in ROWS:
        calc = upper_e8_micro(lx, ly, r)
        assert calc == upper_e8
        assert lower_e9 - calc == gap
        print("GPT6_HYBRID_ARITH|Lx=%d|Ly=%d|r=%d|E9_lower_micro=%d|"
              "E8_upper_micro=%d|gap_from_inputs_micro=%d|"
              "E9_certificate_independently_proved=0|json=0" %
              (lx, ly, r, lower_e9, calc, gap))
    print("GPT6_HYBRID_ARITH_SCOPE|dressed_flat_trial_proof=NOT_REEXECUTED|"
          "large_vector_all_rows=OPEN|json=0")

if __name__ == "__main__":
    check()
