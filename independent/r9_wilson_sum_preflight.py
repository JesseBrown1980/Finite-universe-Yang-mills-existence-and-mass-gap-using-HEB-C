#!/usr/bin/env python3
"""Exact small-group preflight for issue 137; NOT a 2.17B-orbit overlap solve.

The forecast in PREDICT-S3-3X4-R9-WILSON-SUM-FIRST-WEIGHT-20261108.hbp
was committed first at b2185df9. No float, JSON, NumPy or stored Perron vector.
"""
from hashlib import sha256
from itertools import permutations
from sys import argv

FAULTS = {
    "F1_character": "character_census",
    "F2_missing_winding": "translation_cyclic_invariance",
    "F3_wrong_dimension": "Burnside_complete_space",
    "F4_unit_flat_weights": "flat_orbit_weights",
    "F6_dual_operator": "operator_identity",
}
fault = argv[1][9:] if len(argv) == 2 and argv[1].startswith("sabotage=") else ""
if len(argv) > 2 or (len(argv) == 2 and fault not in FAULTS):
    raise SystemExit("usage: r9_wilson_sum_preflight.py [sabotage=F1_character|F2_missing_winding|F3_wrong_dimension|F4_unit_flat_weights|F6_dual_operator]")


def check(test, name):
    if not test:
        print("R9_PREFLIGHT_FAIL|reason=" + name + "|json=0", flush=True)
        raise SystemExit(1)


G = tuple(permutations(range(3)))
LOOK = {g: i for i, g in enumerate(G)}
IDENTITY = LOOK[(0, 1, 2)]
MUL = tuple(tuple(LOOK[tuple(G[a][G[b][i]] for i in range(3))]
                  for b in range(6)) for a in range(6))
INV = tuple(next(b for b in range(6) if MUL[a][b] == IDENTITY
                 and MUL[b][a] == IDENTITY) for a in range(6))
TRANS = tuple(a for a in range(6) if a != IDENTITY and MUL[a][a] == IDENTITY)
CHECK_CENT = [sum(int(MUL[g][h] == MUL[h][g]) for h in range(6))
              for g in range(6)]
check(sorted(CHECK_CENT) == [2, 2, 2, 3, 3, 6], "S3_centralizers")
orbit_count = (6**13 + 3 * 2**13 + 2 * 3**13) // 6
if fault == "F3_wrong_dimension":
    orbit_count = 45508080
check(orbit_count == 2177317873, "Burnside_complete_space")

# Character of the standard 2D permutation-minus-trivial representation.
CHI = {i: sum(int(G[i][k] == k) for k in range(3)) - 1
       for i in range(6)}
if fault == "F1_character":
    CHI[TRANS[0]] = 1
check(CHI[IDENTITY] == 2 and all(CHI[t] == 0 for t in TRANS)
      and all(CHI[k] == -1 for k in range(6)
              if k not in TRANS and k != IDENTITY), "character_census")


def conjugate(a, by):
    return MUL[MUL[by][a]][INV[by]]


# 24 oriented positive links on periodic 3x4 spatial torus, d=0 x and d=1 y.
EDGES = tuple((x, y, d) for x in range(3) for y in range(4) for d in range(2))


def target(x, y, d):
    return ((x + (d == 0)) % 3, (y + (d == 1)) % 4)


def holonomy(U, x, y, d):
    out = IDENTITY
    steps = 3 if d == 0 else 4
    for _ in range(steps):
        out = MUL[out][U[(x, y, d)]]
        x, y = target(x, y, d)
    return out


def observable(U):
    x_terms = sum(CHI[holonomy(U, 0, y, 0)]
                  for y in range(4) if not
                  (fault == "F2_missing_winding" and y == 0))
    y_terms = sum(CHI[holonomy(U, x, 0, 1)] for x in range(3))
    return x_terms + y_terms


def gauge(U, hx, hy, h):
    modified = dict(U)
    for (x, y, d), g in U.items():
        tx, ty = target(x, y, d)
        gs = h if (x, y) == (hx, hy) else IDENTITY
        gt = h if (tx, ty) == (hx, hy) else IDENTITY
        modified[(x, y, d)] = MUL[MUL[gs][g]][INV[gt]]
    return modified


def translate(U, dx, dy):
    return {((x + dx) % 3, (y + dy) % 4, d): g
            for (x, y, d), g in U.items()}


configs = [{e: IDENTITY for e in EDGES}]
for e in EDGES:
    for g in range(6):
        if g == IDENTITY:
            continue
        state = {edge: IDENTITY for edge in EDGES}
        state[e] = g
        configs.append(state)
for k in range(27):
    configs.append({e: (k + 3 * i + (i * i) // 7) % 6
                    for i, e in enumerate(EDGES)})
gauge_checked = 0
trans_checked = 0
for U in configs:
    val = observable(U)
    check(-7 <= val <= 14, "Wilson_sum_character_range")
    for x in range(3):
        for y in range(4):
            for g in range(1, 6):
                gauge_checked += 1
                check(observable(gauge(U, x, y, g)) == val,
                      "full_gauge_covariance")
    for dx, dy in ((1, 0), (0, 1)):
        trans_checked += 1
        check(observable(translate(U, dx, dy)) == val,
              "translation_cyclic_invariance")

# All commuting pairs of S3 holonomies modulo simultaneous conjugation.
reps = []
flat_to_class = {}
weights = []
for a in range(6):
    for b in range(6):
        if MUL[a][b] != MUL[b][a] or (a, b) in flat_to_class:
            continue
        orbit = {(conjugate(a, g), conjugate(b, g)) for g in range(6)}
        index = len(reps)
        reps.append((a, b))
        weights.append(len(orbit))
        for pair in orbit:
            flat_to_class[pair] = index
if fault == "F4_unit_flat_weights":
    weights = [1] * len(weights)
check(len(reps) == 8 and len(flat_to_class) == 18
      and tuple(weights) == (1, 3, 2, 3, 3, 2, 2, 2),
      "flat_orbit_weights")

# On flat fields the full 7-loop observable is multiplication by 4chi(a)+3chi(b).
O = [4 * CHI[a] + 3 * CHI[b] for a, b in reps]
g0 = (1, 1, 1, 0, 0, 0, 0, 0)
g1 = (0, 0, 0, 1, 1, 0, 0, 0)
norm0 = sum(w * a * a for w, a in zip(weights, g0))
norm1 = sum(w * a * a for w, a in zip(weights, g1))
cross = sum(weights[k] * g0[k] * O[k] * g1[k] for k in range(8))
check(norm0 == 6 and norm1 == 6 and cross == 0,
      "leading_flat_Wilson_matrix_element_zero")
# Dual holonomy shift has off-diagonal transitions, unlike the Wilson sum.
if fault == "F6_dual_operator":
    O[0] = "non_diagonal_dual_shift"
check(all(type(x) is int for x in O), "operator_identity")
print("R9_PREFLIGHT_GROUP|S3=6|characters=2,0,-1|Burnside=2177317873|flat_classes=8|commuting_pairs=18|json=0")
print("R9_PREFLIGHT_OPERATOR|loops=7|horizontal=4|vertical=3|pointwise_range=-7:14|diagonal=YES|json=0")
print("R9_PREFLIGHT_SYMMETRY|configurations=" + str(len(configs)) +
      "|gauge_transform_tests=" + str(gauge_checked) +
      "|translation_tests=" + str(trans_checked) + "|json=0")
print("R9_PREFLIGHT_C1|weighted_ground_norm2=6|weighted_first_norm2=6|leading_Wilson_transition=0|r9_full_weight=OPEN|json=0")
print("R9_PREFLIGHT_DONE|status=PASS_DEFINITIONS_ONLY|full_spectrum=NOT_COMPUTED|json=0")
