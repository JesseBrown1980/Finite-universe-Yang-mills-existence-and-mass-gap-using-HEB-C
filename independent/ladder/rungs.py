#!/usr/bin/env python3
"""
Fixed-rung gap profile ("the wave"): certified two-sided gap readings at
r = JB/JE in {0,1,2,3,5,6,8,9,27,81,243} plus two even spots inside each
x3 interval {15,21}, {45,63}, {135,189}. Integer-only; certificates come
from ladder.py's four-sector interval Sturm count (same SHA-keyed ledger).

At each rung (JE = 1, JB = r):
  E0 < U  (smallest found x with count >= 1)
  E1 > L  (largest found x with count == 1)
  gap/JE > L - U
"""
import sys

import ladder as LD

RUNGS = [0, 1, 2, 3, 5, 6, 8, 9, 15, 21, 27, 45, 63, 81, 135, 189, 243]


def guesses(r):
    """Integer starting points only: the exact electric spectrum at r=0
    (E0=0, E1=6), the second-order law for larger r. Searches fix the rest."""
    if r == 0:
        return 3000, 1000
    if r < 4:
        return 3000 + 5500 * r, 1500
    return LD.pred_e1(r, 1), 400


def main():
    rungs = [int(a) for a in sys.argv[1:]] or RUNGS
    for r in rungs:
        if r == 0:
            # Electric-only spectrum is exact (E0 = 0, E1 = 6); a threshold placed
            # exactly on an eigenvalue makes a pivot interval contain zero and the
            # verifier fails closed. Certify just off the eigenvalues instead.
            c_lo, c_hi = LD.count(0, 1, 1), LD.count(0, 1, 5999)
            if c_lo < 1 or c_hi != 1:
                raise SystemExit("LADDER|error=rung0_unexpected|counts=%d,%d|json=0" % (c_lo, c_hi))
            LD.record("LADDER|kind=rung|r=0|E0_upper=1/1000|E1_lower=5999/1000|gap_per_JE_gt=5998/1000|certs=2")
            print("rung r=0     E0 < 1/1000   E1 > 5999/1000   gap/JE > 5998/1000   (2 certs)", flush=True)
            continue
        g1, step = guesses(r)
        L, n1 = LD.tight_e1_lower(r, 1, g1, step)
        start = L
        while LD.count(r, 1, start) < 1:      # need a certified E0 upper bound to tighten from
            start += step
        U, n0 = LD.tight_e0_upper(r, 1, start, max(64, step))
        LD.record("LADDER|kind=rung|r=%d|E0_upper=%d/1000|E1_lower=%d/1000|gap_per_JE_gt=%d/1000|certs=%d"
                  % (r, U, L, L - U, n0 + n1))
        print("rung r=%-4d  E0 < %d/1000   E1 > %d/1000   gap/JE > %d/1000   (%d certs)"
              % (r, U, L, L - U, n0 + n1), flush=True)


if __name__ == "__main__":
    main()
