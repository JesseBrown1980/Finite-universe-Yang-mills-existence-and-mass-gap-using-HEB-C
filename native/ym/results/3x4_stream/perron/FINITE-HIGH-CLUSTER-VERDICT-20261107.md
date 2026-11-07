# 3×4 (S_3) Perron high-cluster finite bound — final scoped verdict, November 7, 2026

**VERDICT: ACCEPTED FINITE HIGH-CLUSTER COMPUTATIONAL CERTIFICATE, conditional on the pinned original computational evidence and its stated whole-space positive-vector lift.** This verdict is an explicit new acceptance of the finite (E_9-E_8) result. It is **not** the first-excitation gap (E_2-E_1). The historical original source [PERRON-RESULT.hbp](PERRON-RESULT.hbp) retains `gap_verdict=OPEN` and is **not** retroactively edited. Its historical `OPEN` means formal acceptance was held as of the old receipt, not that its printed vector inequality was a numerical failure.

The user's explicit decision on November 7 authorizes the finite-only acceptance after verifying its gates, merging this separate verdict, and updating the project READMEs. The old [60M ShellSchur production verdict rule](../GAP-VERDICT-RULE-3X4.md) is unchanged and this verdict **does not** approve or run its staged production dispatch.

## Accepted theorem from original pinned evidence

On the (3\times4) periodic spatial (S_3) finite gauge Hamiltonian (H(r)=J_E(E+rM)), label eigenvalues **one-based**, (E_1\le E_2\le \ldots). There are **2,177,317,873** gauge-invariant orbits in the full Hilbert space. The archived 45,508,080-row `Sx+Sy+` store is a **symmetry quotient**, not the complete state space.

```text
At r = 9:
 E9_full(r) >= 94.070673 J_E         [positive Perron comparison vector, lifted pointwise]
 E8_full(r) <= 70.031000 J_E         [155,386-state whole-space K=3 ball]
 E9_full(r) - E8_full(r) >= 24.039673 J_E

At every r >= 9:
 E9_full(r) - E8_full(r) >= [22.070673 + 3(r-9)] J_E
```

The proof follows [PERRON-BOUND.md](PERRON-BOUND.md) exactly: the nonflat principal compression (H') of a non-positive-off-diagonal self-adjoint operator is bounded below by the minimum ((H'd)_h/d_h) for any strictly positive integer vector (d). The certified positive vector on the `Sx+Sy+` orbit-lumped store lifts to a positive vector on **all** nonflat gauge orbits with identical row ratios, giving the full-space (E_9) lower bound by interlacing. The eight mutually independent flat states have `72 I_8` compression at all couplings; the stronger (r=9) bound on (E_8) comes from the whole-space ball. For (r\ge9), every nonflat row has (M\ge3), improving the Perron bound by at least (3(r-9)).

## What was independently checked before accepting the finite claim

The old source's exact SHA-256 certificate vector is
`f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1`. Its lower bound `94.070673`, minimizing row 45,507,968 and (M=3) are independently reported by `perroncert`, `check_d_strict.py`, and an [outside Go checker run 41509351749](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/41509351749).

The original full rebuild checked **45,508,080 of 45,508,080 sector rows**, zero key/weight/M/entry mismatches, merkle PASS. The exhaustive exact weighted-adjoint test checked **1,632,625,631** off-diagonal pairs, zero mismatches, with the corrected fail-closed header/count gates PASS. Original passA weights sum to (6^{13}=13,060,694,016), and there are exactly eight full-space flat gauge orbits. The min–max upper bound (70.031) at (r=9) comes from eight counted negative pivots in the K=3 ball, ambiguous zero.

**Caveat:** The very large full rebuild and corrected `allpairs` work were run on the original seat's machine, with evidence read by others; an independent full replay on a second machine remains open. The Go checker is independently authored but does not perform its own exhaustive exact weighted-pair enumeration. An original `allpairs` executable had fail-open conditions, subsequently fixed and rerun; its recorded printed values remained consistent. A new verifier checks the immutable source receipts and logic; it does **not** itself rebuild the entire huge operator or retrieve 27GB of external store.

## Rule and receipt provenance

- [Separate finite Perron acceptance rule](PERRON-FINITE-HIGH-CLUSTER-RULE-20261107.md) — describes exact gates and keeps the original 60M production rule intact.
- [Prediction-first freeze](PREDICT-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp) — 12 predictions committed as `6ef0da44f761e150318cb5f047f40eb04ea23d10` **before** the verifier.
- [Verifier](verify_finite_high_cluster_verdict.py) — pins original HBP/proof/rule by exact Git blob hashes and rechecks the lower bound, original full rebuild, pair counts, lift and arithmetic. Seven deliberately false inputs or conclusions must fail.
- [Hosted verification](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/131/checks) — must pass on the final PR head; [measured verdict receipt](MEASURED-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp) published from hosted logs after success.

No old receipt is rewritten, no frozen prediction altered, no production work authorized, and no claim of a positive (E_2-E_1) gap is being made here.

## Explicitly still OPEN

The **true first vacuum-to-excitation gap (E_2-E_1)** of the interacting 3×4 full Hamiltonian; positive spectral overlap of its first excited state with a specified gauge-invariant winding-sum operator; a separately hosted second-machine full-store rebuild and all-pairs replay; uniformity of a physical-unit gap across volumes and lattice spacings; a nontrivial four-dimensional SU(2) continuum Yang–Mills existence/mass-gap theorem.

**Disposition:** This document closes only the older *administrative hold on acceptance of the already completed finite 3×4 (E_9-E_8) computational certificate*. It does not overwrite previous decisions or close scientific obligations that were never addressed by that certificate.
