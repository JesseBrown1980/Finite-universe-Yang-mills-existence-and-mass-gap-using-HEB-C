# Shadow stack, layer 2: SAT and exact #SAT

`orbit_cnf.py` is a count-preserving CNF for the 2×2 gauge-orbit count. The object counted
is the 5 free links of the maximal-tree gauge in S₃⁵, up to simultaneous conjugation. The
CNF has exactly one satisfying assignment per orbit, its lexicographically smallest
member. Links are one-hot, and every auxiliary variable is defined by a full equivalence,
so the total count equals the count projected onto the links. The run checks that equality.

| gate | check |
|---|---|
| E1 | pycosat enumerates every model over all variables |
| E2 | pysat (Minisat 2.2) enumerates models projected on the link variables |
| E3 | every model decodes to the lexicographic minimum of its own orbit, checked directly without the CNF |
| E4 | direct orbit enumeration without the CNF, and Burnside (6⁵ + 3·2⁵ + 2·3⁵)/6 |

**Result** (`ORBIT-2X2.hbp`, CNF SHA-256 `89991393…`): E1 = E2 = E3 = E4 = Burnside = **1,393**,
the recorded `gauge_orbits`. Verdict: CERTIFIED.

| control | fault planted | outcome |
|---|---|---|
| `drop_g` | every lex constraint for one conjugation removed | 2,155, NOT_CERTIFIED |
| `loose_aux` | one auxiliary variable left undetermined | total 3,062 ≠ projected 2,155, NOT_CERTIFIED |

Any timeout, disagreement or malformed output is NOT_CERTIFIED.
