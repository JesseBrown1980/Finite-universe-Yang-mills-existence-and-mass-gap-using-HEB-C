# Registered finite 3×4 Perron high-cluster rule (2026-11-07)

**Status:** REGISTERED FOR FINITE COMPUTATIONAL HIGH-CLUSTER VERDICT, subject to a successful hosted run of `verify_finite_high_cluster_verdict.py` and final-head repository CI. This separate rule is accepted only within the scope below. It is **not** the registered [60M production/fan-out rule](../GAP-VERDICT-RULE-3X4.md), and does not authorize running any 60M production jobs or new thresholds.

This rule resolves the old *administrative HOLD on accepting the already calculated 3×4 Perron high-cluster bound* without rewriting older HBP receipts. The previous `PERRON-RESULT.hbp` still says `gap_verdict=OPEN`; that field remains an accurate historical record of its November 2 computation and operator decision. The separate new [verdict file](FINITE-HIGH-CLUSTER-VERDICT-20261107.md) records the subsequent finite-scope decision and explicit dependencies. No historical evidence, approval log or upstream HBP may be edited to make it appear a previous hold never existed.

## Exactly what is accepted

The original 3×4 periodic `S₃` lattice Hamiltonian `H(r)=E+rM` is in `J_E` units, and `E_1 <= E_2 <= ...` is **one-based** full gauge-invariant eigenvalue ordering. For `r=9`:

```text
E9_full(9) >= 94.070673 J_E
E8_full(9) <= 70.031000 J_E
E9_full(9)-E8_full(9) >= 24.039673 J_E
```

For every real coupling `r>=9`, using the same preexisting positive integer comparison vector and `M>=3` off the eight flat states:

```text
E9_full(r)-E8_full(r) >= [22.070673+3(r-9)] J_E.
```

These are **conditional consequences of the recorded, pinned finite computations**, now accepted as computational evidence after cross-checks. This does NOT certify `E2-E1` (the first excitation), a volume-independent positive gap, a four-dimensional SU(2) continuum construction, or a Clay Millennium solution. It must always be labeled the **gap above the eight-flat-state cluster**.

## Required fail-closed inputs

A separate source-audited checker must read and SHA-1 Git-blob-pin these **unmodified** files:

- `PERRON-RESULT.hbp`, blob `cbd428014a4d440732a5c0a541ed57a9041becee`.
- `PERRON-BOUND.md`, blob `53378d4ee68dc88766873713285e3a34465a9d90`.
- Existing 60M rule `../GAP-VERDICT-RULE-3X4.md`, blob `42bfad8820daa8a34c9501d57f35e49447c552de`.

A PASS must verify **all**, not only one, of the following: (1) original `gap_verdict=OPEN` unchanged; (2) the pure (+,+) sector count `45,508,080`, 7 flat states, total gauge-fixed orbit weight `6^13=13,060,694,016`, and 8 full-space flat states; (3) positive Perron vector `f5c5428d...`, exact `t_cert_milli=94070673`, minimum row 45,507,968 with `M=3`; (4) the two original strict checkers and outside independent Go match; (5) full all-rows reconstruction, zero mismatches, merkle PASS; (6) exhaustive `1,632,625,631` weighted self-adjoint pairs, zero mismatches, both corrected header/count gates PASS; (7) whole-space orbit-lift proof (same nonflat row ratios on every symmetry orbit) and min–max/interlacing preconditions; (8) independent 155,386-state K=3 whole-space ball gave eight states below 70.031 and no ambiguity; and (9) exact integer gap subtraction and `M_min=3` slope. Seven explicit false-claim controls must return nonzero status and a named failure.

The original computational runs had known limitations: one machine hosted the full-store rebuild and all-pairs checks, another-machine replay remains open, and the outside Go checker did not itself enumerate every pair. The older `allpairs` executable had fail-open issues that were corrected and rerun, while its recorded values remained unchanged. These limitations must remain visible, not be converted into claims of independent complete reproduction.

## Verification and decision process

Before this verifier was written, twelve prediction rows were frozen in [PREDICT-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp](PREDICT-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp). The new [workflow](../../../../.github/workflows/perron-finite-high-cluster-verdict.yml) must generate its own HBP receipt, compare it byte-for-byte to the committed measured receipt once present, execute seven red controls, and pass the global repository integer-only, no-floating-point and Rust tests.

**Operator authorization (November 7, 2026):** the user expressly authorized establishing the required evidence, merging the accepted finite Perron verdict, closing that specific administrative hold and updating READMEs. This rule is separate from the old production controls and permits **no** automatic production dispatch.

The accepted verdict is scoped to the original finite cluster separation alone. All first-excitation and continuum gates retain `OPEN`.
