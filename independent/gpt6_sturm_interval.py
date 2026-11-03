#!/usr/bin/env python3
"""Independent integer-only interval LDL Schur inertia with all 8 quotient corners.
Never imports the other seat's Sturm algorithm, no floats, NumPy, JSON or Node.
All pivots are strict signs or the check FAILS without a certificate.
"""
from pathlib import Path
from hashlib import sha256
import sys

PINS = {
    "pp": "fb6dbb3acbd411f61779f98881e6545d21ab7a39816c351d755fafe2c3f2c652",
    "pm": "9dc22f4bb6f410ebfcdc0bfb3854bf6d2827901ee379ed685772649d28315d48",
    "mp": "88eb8250eaf85815f155f09656f8a4dd19733148dd9e4505af978bed5974a75b",
    "mm": "d7dce164177f2b5498a367c9df78ff8d64c8d173a262daa65815b321ff21b653",
}
SIZES = {"pp": 385, "pm": 336, "mp": 336, "mm": 336}

def ceil_div(n, d):
    assert d != 0
    return -((-n) // d)

def quotient(x, y, pivot):
    """Enclose every x*y/pivot for x,y,pivot in intervals, exact integer floors."""
    if pivot[0] <= 0 <= pivot[1]:
        raise ArithmeticError("pivot is not sign definite")
    lower = []
    upper = []
    for a in x:
        for b in y:
            for c in pivot:
                lower.append(a*b // c)
                upper.append(ceil_div(a*b, c))
    return min(lower), max(upper)

def load_sector(directory, name, je, jb, t, precision=40):
    raw = (directory / (name + ".matrix")).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("source matrix SHA mismatch: " + name)
    values = tuple(map(int, raw.split()))
    n = values[0]
    assert n == SIZES[name]
    w = values[1:1+n]
    mag = values[1+n:1+2*n]
    entries = values[1+2*n:]
    assert len(entries) % 3 == 0 and all(v > 0 for v in w)
    factor = 10**precision
    matrix = [{} for _ in range(n)]
    included = set()
    for i, j, entry in zip(entries[0::3], entries[1::3], entries[2::3]):
        if not 0 <= i <= j < n or (i, j) in included:
            raise ValueError("duplicate or invalid matrix coordinate")
        included.add((i, j))
        if entry:
            element = factor * 1000 * je * w[i] * entry
            matrix[i][j] = (element, element)
            matrix[j][i] = (element, element)
    for i in range(n):
        diag = matrix[i].get(i, (0, 0))
        shift = factor * w[i] * (1000*jb*mag[i]-t)
        matrix[i][i] = (diag[0] + shift, diag[1] + shift)
    assert all(matrix[i][j] == matrix[j][i]
               for i in range(n) for j in matrix[i])
    return matrix

def inertia(matrix):
    remaining = set(range(len(matrix)))
    negatives = 0
    max_fill = 0
    while remaining:
        good = [i for i in remaining if
                matrix[i][i][0] > 0 or matrix[i][i][1] < 0]
        if not good:
            raise ArithmeticError("no sign-definite pivot: UNCERTIFIED")
        # Fixed minimum-degree ordering, and largest pivot magnitude for ties.
        k = min(good, key=lambda i: (
            len(matrix[i]),
            -(abs(matrix[i][i][0]) + abs(matrix[i][i][1])), i
        ))
        pivot = matrix[k][k]
        if pivot[1] < 0:
            negatives += 1
        neighbors = sorted((j, matrix[k][j])
                           for j in matrix[k] if j != k)
        max_fill = max(max_fill, len(neighbors))
        for u, (i, x) in enumerate(neighbors):
            for j, y in neighbors[u:]:
                qlow, qhigh = quotient(x, y, pivot)
                old = matrix[i].get(j, (0, 0))
                updated = (old[0] - qhigh, old[1] - qlow)
                if updated == (0, 0):
                    matrix[i].pop(j, None)
                    matrix[j].pop(i, None)
                else:
                    matrix[i][j] = updated
                    matrix[j][i] = updated
        for j, _ in neighbors:
            matrix[j].pop(k)
        matrix[k].clear()
        remaining.remove(k)
    return negatives, max_fill

def prove_quotient_corners():
    # Exhaustive unit interval arithmetic controls, including negative divisor.
    for a in range(-2, 3):
        for b in range(-2, 3):
            for d in (-3, -2, -1, 1, 2, 3):
                lo, hi = quotient((a, a), (b, b), (d, d))
                assert lo == (a*b)//d
                assert hi == ceil_div(a*b, d)

def run(directory, je, jb, t, expected=None, digits=40):
    if not (je > 0 and jb >= 0 and t >= 0 and digits >= 30):
        raise ValueError("invalid integer coupling, threshold or guard precision")
    prove_quotient_corners()
    counts = []
    for name in ("pp", "pm", "mp", "mm"):
        negative, max_fill = inertia(load_sector(directory, name, je, jb, t, digits))
        counts.append(negative)
        print("GPT6_SECTOR|sector=%s|negative=%d|pivots=%d|max_fill=%d|result=PASS|json=0"
              % (name, negative, SIZES[name], max_fill), file=sys.stderr)
    count = sum(counts)
    if expected is not None and count != expected:
        raise ValueError("wrong independently measured inertia: expected %d but saw %d" %
                         (expected, count))
    print("GPT6_STURM|JE=%d|JB=%d|threshold=%d/1000|digits=%d|pivots=1393|"
          "negative=%d|counts=%s|ambiguous=0|json=0" %
          (je, jb, t, digits, count, ",".join(map(str, counts))))

if __name__ == "__main__":
    if len(sys.argv) not in (5, 6):
        raise SystemExit("usage: gpt6_sturm_interval.py DIR JE JB T [EXPECTED]")
    directory = Path(sys.argv[1])
    je, jb, t = map(int, sys.argv[2:5])
    expected = int(sys.argv[5]) if len(sys.argv) == 6 else None
    run(directory, je, jb, t, expected)
