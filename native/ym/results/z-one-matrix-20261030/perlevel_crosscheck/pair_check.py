#!/usr/bin/env python3
"""Independent post-hoc ring-r vs fixed-schedule hierarchical-j enumeration.

The preregistered probe.py uses a different r: r=R+R^2 applied to a selected
ternary address coordinate, not the 1D ring-neighbor operator here. Results
from this independent enumeration are cross-checks and NOT preregistered.
"""
from pathlib import Path

EXPECTED = {
    3: (594, 30, 78),
    4: (6132, 108, 240),
    5: (57732, 348, 726),
}


def digit(a, k):
    return a // (3 ** k) % 3


def j_fixed(a, b, levels):
    """Highest differing digit, with levels visited in increasing k order."""
    return max((k + 1 for k in range(levels) if digit(a, k) != digit(b, k)), default=0)


def r_ring(a, b, size):
    delta = abs(a - b)
    return min(delta, size - delta)


def run():
    rows = ["RJ_PAIR_SCOPE|status=POST_HOC_INDEPENDENT_CROSS_CHECK|r=ring_nearest_neighbor|j=fixed_low_to_high_digit_schedule|json=0"]
    for levels, expected in EXPECTED.items():
        size = 3 ** levels
        j_win = r_win = ties = 0
        for a in range(size):
            for b in range(size):
                if a == b:
                    continue
                jd = j_fixed(a, b, levels)
                rd = r_ring(a, b, size)
                j_win += int(jd < rd)
                r_win += int(rd < jd)
                ties += int(jd == rd)
        assert (j_win, r_win, ties) == expected
        assert j_win + r_win + ties == size * (size - 1)
        rows.append(f"RJ_PAIRS|levels={levels}|sites={size}|ordered_pairs={size * (size - 1)}|j_before_r={j_win}|r_before_j={r_win}|ties={ties}|max_j_ticks={levels}|max_ring_ticks={(size-1)//2}|result=PASS|json=0")
    rows.append("RJ_PAIRS_TOTAL|levels=3|matched=3|overall=PASS|physical_proof=0|json=0")
    return rows

if __name__ == "__main__":
    print("\n".join(run()))
