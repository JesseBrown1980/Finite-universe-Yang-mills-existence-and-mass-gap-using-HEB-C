#!/usr/bin/env python3
"""Exact integer/rational counterexamples for 3x3 Ritz reporting claims.

Do NOT run eigensolvers; compare diagonal Hamiltonians and their exact
orthogonal two-dimensional Ritz subspace. All numbers are integers. The
examples establish scope limitations, not a refutation of the raw Ritz data.
"""

def two_dimensional_ritz(diagonal):
    # Trial space is span{(1,0,1), (0,1,0)}, orthogonal under ordinary L2.
    assert len(diagonal) == 3
    # First trial vector has norm squared 2; second norm squared 1.
    # Energies are (diag[0]+diag[2])/2 and diag[1].
    sum_end = diagonal[0] + diagonal[2]
    middle_twice = 2*diagonal[1]
    return tuple(sorted((sum_end, middle_twice)))  # Energies in halves.

def assert_not_full_gap():
    small = (0, 10, 12)
    upper0, upper1 = two_dimensional_ritz(small)
    assert (upper0, upper1) == (12, 20)
    assert upper0 >= 2*small[0] and upper1 >= 2*small[1]
    assert upper1 - upper0 == 8 < 2*(small[1]-small[0])

    large = (0, 1, 20)
    upper0, upper1 = two_dimensional_ritz(large)
    assert (upper0, upper1) == (2, 20)
    assert upper0 >= 2*large[0] and upper1 >= 2*large[1]
    assert upper1 - upper0 == 18 > 2*(large[1]-large[0])

def assert_outward_micro_brackets():
    # Suppose a rigorous bisection gives t_raw in (7,8) for t_raw=24*E
    # (with 10^6 suppressed): exact E=5/16, so t_raw=15/2.
    lo, hi = 7, 8
    exact_energy_numerator, exact_energy_denominator = 5, 16
    assert lo*exact_energy_denominator < 24*exact_energy_numerator
    assert 24*exact_energy_numerator < hi*exact_energy_denominator
    old_lower, old_upper = lo//24, hi//24
    assert old_lower == old_upper == 0
    assert not (old_lower*exact_energy_denominator <=
                exact_energy_numerator <=
                old_upper*exact_energy_denominator)
    corrected_lower, corrected_upper = lo//24, (hi+23)//24
    assert corrected_lower == 0 and corrected_upper == 1
    assert corrected_lower*exact_energy_denominator <= exact_energy_numerator
    assert exact_energy_numerator <= corrected_upper*exact_energy_denominator

if __name__ == "__main__":
    assert_not_full_gap()
    assert_outward_micro_brackets()
    print("GPT6_RITZ_LOGIC|variational_single_eigenvalue_upper=VALID|"
          "difference_is_full_gap=FALSE|counterexamples=2|json=0")
    print("GPT6_RITZ_ROUNDING|old_code=FLOOR_BOTH_ENDPOINTS|"
          "old_bracket_may_exclude_true_value=1|"
          "correct_upper=CEIL|control=PASS|json=0")
    print("GPT6_SCOPE|3x3_original_Ritz_numbers=UNMODIFIED|"
          "full_gap_certification=OPEN|continuum_mass_gap=OPEN|json=0")
