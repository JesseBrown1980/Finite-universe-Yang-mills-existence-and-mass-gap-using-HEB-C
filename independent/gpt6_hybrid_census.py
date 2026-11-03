#!/usr/bin/env python3
"""Independent exact S3 low-M census through noncommutative group convolution.

NOT an orbit enumeration and does not import hybridcheck, py_hybrid_recheck
or local_table.py. Derives the gauge-fixed configuration counts from the
torus plaquette-product constraint and two global holonomy commutator.
Everything is integer-only, no floats/NumPy/JSON.
"""
from itertools import permutations
from collections import Counter, defaultdict
import sys

GROUP = tuple(permutations(range(3)))
INDEX = {g: i for i, g in enumerate(GROUP)}
MULT = tuple(tuple(INDEX[tuple(GROUP[i][GROUP[j][k]] for k in range(3))]
                   for j in range(6)) for i in range(6))
INV = tuple(next(j for j in range(6) if MULT[i][j] == MULT[j][i] == 0)
            for i in range(6))

def multiply(*words):
    v = 0
    for w in words:
        v = MULT[v][w]
    return v

COMM = Counter(
    multiply(i, j, INV[i], INV[j])
    for i in range(6) for j in range(6)
)
COST = tuple(
    (0, 0) if sum(p[i] == i for i in range(3)) == 3
    else ((1, 0) if sum(p[i] == i for i in range(3)) == 1 else (0, 1))
    for p in GROUP
)
assert sum(COMM.values()) == 36 and COMM[0] == 18
assert COST.count((0, 0)) == 1 and COST.count((1, 0)) == 3
assert COST.count((0, 1)) == 2

def census(plaquettes, cutoff):
    """Count each (transpositions, 3-cycles) lump by group-algebra DP.

    A genus-one lattice has two global holonomies x,y and P plaquette
    holonomies p_1,...,p_P whose ordered product is [x,y].
    All but the last plaquette value are free; hence this is a bijection to
    gauge-fixed link assignments, before quotient by global conjugation.
    Count sequences in S3 with product g, then weight by #commutator pairs g.
    """
    states = {(0, 0, 0): 1}
    for _ in range(plaquettes):
        next_states = defaultdict(int)
        for (a, b, group_element), count in states.items():
            for h, (da, db) in enumerate(COST):
                aa, bb = a + da, b + db
                if 2*aa + 3*bb <= cutoff:
                    next_states[aa, bb, MULT[group_element][h]] += count
        states = next_states
    result = defaultdict(int)
    for (a, b, product_element), count in states.items():
        result[a, b] += count*COMM[product_element]
    assert result[(0, 0)] == 18
    return dict(result)

TESTS = (
    (3, 3, 13, 3590190, 24948),
    (3, 4, 14, 78547410, 98010),
    (4, 4, 8, 2151648, 0),
    (4, 4, 10, 6919488, 0),
    (4, 4, 12, 119790792, 360360),
    (4, 4, 14, 624556872, 360360),
    (4, 5, 13, 642825270, 959310),
    (5, 5, 11, 563254650, 0),
)

def check(expect_wrong=False):
    for lx, ly, cutoff, expected, count_04 in TESTS:
        result = census(lx*ly, cutoff)
        nonflat = sum(result.values()) - result[0, 0]
        goal = expected
        if expect_wrong and (lx, ly, cutoff) == (4, 4, 12):
            goal += 1
        assert nonflat == goal, (lx, ly, cutoff, nonflat, goal)
        assert result.get((0, 4), 0) == count_04
        print("GPT6_HYBRID_CENSUS|Lx=%d|Ly=%d|cut=%d|nonflat=%d|"
              "flat=18|count_0_4=%d|lumps=%d|result=PASS|json=0" %
              (lx, ly, cutoff, nonflat, count_04, len(result)))
    assert census(16, 12)[0,4] - 315216 == 45144
    print("GPT6_HYBRID_RED|Lx=4|Ly=4|cut=12|lump=0,4|"
          "expected=360360|bad_hybrid=315216|missing=45144|json=0")
    print("GPT6_HYBRID_SCOPE|full_orbit_rep_replay=OPEN|hybrid_vector_inequality=OPEN|json=0")

if __name__ == "__main__":
    if sys.argv[1:] == []:
        check()
    elif sys.argv[1:] == ["--bad-count"]:
        check(expect_wrong=True)  # Must raise and exit nonzero.
    else:
        raise SystemExit("usage: gpt6_hybrid_census.py [--bad-count]")
