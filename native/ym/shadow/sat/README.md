# Shadow stack, layer 2: SAT, exact #SAT and checked UNSAT proofs

All evidence is two-sided:

| case | required outcome |
|---|---|
| clean encoding `E` | `E ∧ ¬P` is UNSAT, with an independently checked proof bound to the exact CNF hash; for counts, the exact count agrees across independent engines plus a direct count that uses no CNF |
| planted semantic fault `E′` | `E′ ∧ ¬P` is SAT, with an explicit countermodel re-checked against the original property, or the count moves off the certified value |
| tampered proof, CNF, hash or checker record, a timeout, or any disagreement | NOT_CERTIFIED |

## Gauge-orbit counts: `orbit_cnf.py`, `orbit_ganak.py`, `direct_orbits.rs`

The object counted is the free links of the maximal-tree gauge, in S₃ᵏ up to
simultaneous conjugation. There are 5 free links on 2×2 and 10 on 3×3. The CNF has
exactly one satisfying assignment per orbit, its lexicographically smallest member. Links
are one-hot and the auxiliaries are Tseitin-defined, so the total count equals the count
projected onto the links, and each run checks that equality.

**2×2** (`ORBIT-2X2.hbp`):
- **Count:** pycosat over all variables = pysat (Minisat 2.2) projected = Ganak total =
  Ganak projected = direct = Burnside = **1,393**, the recorded value.
- **Bijection:** the decoded model set equals the directly computed lex-min set. Both
  hashes are `b9c22fbc…`, and the list is kept in `ORBIT-2X2-MODELS.txt`.

**3×3** (`ORBIT-3X3.hbp`): Ganak total = Ganak projected = `direct_orbits` (60,466,176
configurations, no CNF) = Burnside = **10,097,891**, stage A's recorded `gauge_orbits`.

| control | fault planted | outcome |
|---|---|---|
| `drop_g` | every lex constraint for one conjugation removed | 2×2: 2,155; 3×3: 16,143,997. NOT_CERTIFIED |
| `loose_aux` | one auxiliary left undetermined | total ≠ projected (2×2: 3,062 vs 2,155; 3×3: 22,869,534 vs 16,143,997). NOT_CERTIFIED |

## Column partitions of sealed merges: `partition_sat.py`

**Claim:** a countmerge's cells cover every column of `[0, core)` exactly once. The CNF
asserts the negation. The claim holds iff it is UNSAT, with the Glucose 4 DRUP proof
verified by drat-trim (`marijnheule/drat-trim@2e3b2dc`) against the formula whose hash is
recorded. Lean's `countmerge_conserves` then gives: merged count = whole count.

| run | clean | `shift` (one-column gap) | `weaken_cnf` | `hash_tamper` |
|---|---|---|---|---|
| 3×3 sealed part 2, 7 merges (`PARTITION-3X3-PART2.hbp`) | UNSAT, VERIFIED, EXACT | SAT, column 60 covered by 0, confirmed by arithmetic | NOT_VERIFIED | NOT_CERTIFIED |
| 2×2 miniature certification, 2 merges (`PARTITION-2X2-MINIATURE.hbp`) | UNSAT, VERIFIED, EXACT | SAT, countermodel confirmed | NOT_VERIFIED | NOT_CERTIFIED |

This runs alongside the frozen certify step and decides nothing in it: the deterministic
receipts and gates decide certification.
