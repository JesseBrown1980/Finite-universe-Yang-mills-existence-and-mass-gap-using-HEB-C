#!/usr/bin/env python3
"""Counts the bisection steps per level on the eight outward receipt rows, integer only.

Checks the step-count fields of the PRED-TIME row in seat_3x3_ritz_outward_PREDICTION.hbp,
which read 33 at scale 10^6 and 53 at scale 10^12. Uses the solver's own matrix and inertia
functions, and prints each row's step counts beside its outward intervals.

usage seat_3x3_ritz_count_steps.py
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from seat_3x3_vacuum_block_ritz import (  # noqa: E402
    build_system, h_apply, inertia, load_matrix, outward_interval, wdot)

MICRO = 10 ** 6
E12 = 10 ** 12
PREDICTED = {MICRO: 33, E12: 53}
ROWS = (
    ("b33_k1.matrix", 27, 1, MICRO), ("b33_k2.matrix", 27, 2, MICRO), ("b33_k3.matrix", 9, 3, MICRO),
    ("b33_k3.matrix", 27, 3, MICRO), ("b33_k3.matrix", 81, 3, MICRO), ("b33_k3.matrix", 9, 3, E12),
    ("b33_k3.matrix", 27, 3, E12), ("b33_k3.matrix", 81, 3, E12),
)


def counted_bracket(a, b, k, scale):
    size = len(a)

    def count(t):
        return inertia([[scale * b[i][j] - t * a[i][j] for j in range(size)] for i in range(size)])

    lo, hi, steps = 0, 4800 * scale, 0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if count(mid) <= k:
            lo = mid
        else:
            hi = mid
        steps += 1
    return lo, hi, steps


def main():
    seen = {MICRO: [], E12: []}
    for name, jb, order, scale in ROWS:
        n, w, mag, rest, _ = load_matrix(HERE.joinpath("matrices", name))
        col = build_system(n, w, mag, rest, 1, jb)
        basis = [{i: 1} for i in range(n) if mag[i] == 0]
        last = basis
        for _ in range(order):
            last = [h_apply(col, x) for x in last]
            basis.extend(last)
        hcols = [h_apply(col, x) for x in basis]
        a = [[wdot(w, u, v) for v in basis] for u in basis]
        b = [[wdot(w, u, hv) for hv in hcols] for u in basis]
        results = [counted_bracket(a, b, k, scale) for k in range(8)]
        steps = [r[2] for r in results]
        seen[scale].extend(steps)
        levels = "|".join("E%d=[%d,%d]" % ((k,) + outward_interval(results[k][0], results[k][1])) for k in range(8))
        print("RITZ-STEPS|matrix=%s|JB=%d|order=%d|scale=%d|steps=%s|%s|json=0"
              % (name, jb, order, scale, ",".join(str(s) for s in steps), levels))
    for scale in (MICRO, E12):
        low, high = min(seen[scale]), max(seen[scale])
        print("RITZ-STEPS-PREDICTION|scale=%d|levels=%d|predicted_steps=%d|measured_min=%d|measured_max=%d|met=%d|json=0"
              % (scale, len(seen[scale]), PREDICTED[scale], low, high, low == high == PREDICTED[scale]))


if __name__ == "__main__":
    main()
