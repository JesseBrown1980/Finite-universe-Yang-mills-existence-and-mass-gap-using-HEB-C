#!/usr/bin/env python3
"""AFTER THE RUN (exploratory, not predicted): the frozen run found the brute-force electric levels to be
integers (0, 12, 18, 21, 24, 30, 36) where the printed thesis block [[18,0,e],[0,24,-e],[e,-e,21]],
e = 3*sqrt(2)/2, has levels 21 and 21 +- 3*sqrt(2). The link electric terms commute and each has levels
0, 3, 6, so every electric level is an integer. This script tests the printed matrices with the
off-diagonal electric entries removed, for each placement of 18, 21, 24 on the last three basis states.
Integers only."""
import os
import sys
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import two_plaquette as t  # noqa: E402

data = t.orbit_data()
P2, _ = t.scaled_P(True)
brute = {r: t.charpoly([[4 * x for x in row] for row in t.orbit_matrix(r, 1, data)]) for r in (9, 12)}
for perm in permutations((18, 24, 21)):
    HE = [row[:] for row in t.HE2]
    for a, b in ((8, 10), (9, 10), (10, 8), (10, 9)):
        HE[a][b] = 0
    for k, v in zip((8, 9, 10), perm):
        HE[k][k] = 2 * v
    ok = [t.charpoly([[2 * HE[i][j] - r * P2[i][j] + (16 * r if i == j else 0) for j in range(11)]
                      for i in range(11)]) == brute[r] for r in (9, 12)]
    t.emit("BENCH2_EXPLORE", electric_block_diagonal=",".join(map(str, perm)), offdiagonal_electric_entries=0,
           HB_entry_8_5=2, full_charpoly_equal_r9=int(ok[0]), full_charpoly_equal_r12=int(ok[1]))
