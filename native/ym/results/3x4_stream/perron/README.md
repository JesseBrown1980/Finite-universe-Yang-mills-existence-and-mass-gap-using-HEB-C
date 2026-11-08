# 3×4 Perron certificate — research status (November 7, 2026)

**Finite high-cluster bound: ACCEPTED from pinned computational evidence.** **First-excitation mass gap and continuum: OPEN.**

The older `PERRON-RESULT.hbp` says `gap_verdict=OPEN` because formal adoption of the Perron route was on administrative HOLD when that record was made. The actual finite lower bound, all-row reconstruction and exact all-pairs self-adjointness numbers had passed. The user authorized a separate acceptance on November 7; the new finite verdict is documented without overwriting the old evidence.

## What the accepted finite calculation actually proves

On the complete periodic (3\times4) (S_3) physical space, with **one-based** eigenvalue indexing (E_1\le E_2\le\cdots):

```text
r=9:     E9_full − E8_full >= 24.039673 J_E
r>=9:    E9_full − E8_full >= [22.070673 + 3(r−9)] J_E
```

This is the gap **above the eight magnetic-flat-state cluster**, not the first excitation inside that cluster.

The input space has 2,177,317,873 gauge orbits; the stored (Sx+Sy+) sector has 45,508,080 symmetry-lumped rows. Independent Go checking, 45,508,080/45,508,080 rows independently reconstructed and 1,632,625,631/1,632,625,631 weighted pairs verified with no mismatches are recorded in the original source. The new acceptance checks the original HBP/proof Git blob seals, exact counts and gap arithmetic; the new acceptance does **not** repeat the entire 45.5-million-row calculation on a second machine. Therefore the verdict depends on the original numerical certificates and pointwise full-space orbit lift.

## Reference files

| Artifact | Role |
|---|---|
| [Finite accepted verdict](FINITE-HIGH-CLUSTER-VERDICT-20261107.md) | Scope, numerical inequalities, original evidence and explicit limits |
| [Finite verdict rule](PERRON-FINITE-HIGH-CLUSTER-RULE-20261107.md) | Formal fail-closed acceptance gates; no production dispatch |
| [Measured hosted verdict receipt](MEASURED-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp) | Seven generated evidence lines, seven sabotage controls rejected |
| [Frozen predictions](PREDICT-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp) | Twelve predictions committed before the new verifier code |
| [Executable verifier](verify_finite_high_cluster_verdict.py) | Integer-only proof-composition and source-hash checks |
| [Original Perron result](PERRON-RESULT.hbp) | **Immutable historical** `gap_verdict=OPEN` and all original measurements |
| [Original Perron derivation](PERRON-BOUND.md) | Positive comparison-vector inequality and symmetry-orbit whole-space lift |
| [Original review log](PERRON-REVIEW.md) | Full independent-review history, faults and repairs |
| [Historical Perron draft](PERRON-RULE-DRAFT.md) | Former procedural HOLD, now superseded only for the finite accepted claim |
| [Existing 60M production rule](../GAP-VERDICT-RULE-3X4.md) | **Unchanged**; production and other thresholds not authorized by this verdict |

**Not claimed:** a numerical/positive (E_2-E_1) bound of the complete interacting 3×4 Hamiltonian, strict (E_1) Wilson-sum overlap, volume-uniform positivity, SU(2) continuum Yang–Mills existence, or solution of the Clay Millennium problem. Those remain separate scientific tasks.
