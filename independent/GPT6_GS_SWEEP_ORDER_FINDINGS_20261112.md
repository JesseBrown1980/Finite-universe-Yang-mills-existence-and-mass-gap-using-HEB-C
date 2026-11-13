# Independent r12 Gauss–Seidel order intervention — November 12, 2026

**Claim boundary:** Exact computational controls for the **finite r=12 Schur-comparison certificate writer**. This is not a physical continuum Yang–Mills construction, a full-spectrum mass-gap theorem, or evidence that the separate room simulation exhibits quantum entanglement. The r=9 HOLD remains unchanged.

## Before observing the new results

The original frozen [prediction](GPT6_GS_SWEEP_PREDICTION_R12_20261112.hbp) specified an integer identity for the last Gauss–Seidel sweep and a possible cutoff-7 exception. It incorrectly predicted a positive forward-coupling correlation for **all three cutoff-7 words**. The [full reversal prediction](GPT6_REVERSE_WRITER_PREDICTION_20261112.hbp) was committed before the writer's inner loop was reversed.

The final test uses one and only one source edit to the external Rust 1.81 writer's inner sweep traversal, replacing ascending `0..n` with descending `(0..n).rev()`. The physical finite graph, coupling r=12, cutoff, word, and exact independent certificate verifier remain unchanged. The solver chooses a fresh floor parameter, so the Schur comparison matrix evaluated at that floor can change slightly.

## Phase 1: independently reconstructed fixed inverse solve

[Hosted run 43259833533](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43259833533) **PASS**: all 9 authentic merged y140 certificates and canonical rows authenticated, the last-sweep integer remainder identity checked after 8 and 24 sweeps for forward and reversed index orders (36 identities, 0 mismatches). All 18 forward/reverse comparisons showed less absolute equation residual at 24 than at 8 sweeps.

The exact identity is

```
((F − sigma) x_new − E v)_a
  = − floor_division_remainder_a
    − sum[j updated later than a] w[a,j] * (x_new[j] − x_old[j]).
```

The future neighbors are `j>a` in forward GS and `j<a` in reverse GS. This identity applies to a **single fixed inner inverse solve**; the subsequent full-writer reversal is the stronger intervention.

At cutoff 7, original frozen leaf Spearman rank correlations with the forward coupling U are **−0.168** for word `1`, **+0.962** for `6,5,4,3`, and **+0.957** for `8,7,6,5,4`. The predicted positive sign for cutoff-7 word `1` is **FALSIFIED** and is retained. The single-weight certificate is also cap-limited.

The existing pinned cutoff-7 word `1` artifact used floor t=80.4068, whereas the main y140 certificate with the published residual leaves uses t=80.4069 and a different v. We did **not** mix these vectors. Every result associated with the published leaf pattern uses its matching main y140 certificate, checked against the immutable canonical row hash.

## Phase 2: full compiled Rust writer, actual reversed inner sweep

[Hosted run 43260992122](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43260992122) **PASS**: new actual certificates generated with the modified (temporary hosted) Rust engine, independently authenticated by its distinct `cert_gate.py` verifier, then paired with all original certificates for exact integer-ratio ranks. The original writer, published certificates, and repo main were not modified.

| m0 | Weight word | Original corr(leaf,U), ×1000 | Reverse corr(leaf,B), ×1000 | Reversal favors B? |
| --- | --- | ---: | ---: | :---: |
| 7 | `1` | −168 | −317 | **No** |
| 7 | `6,5,4,3` | +962 | +939 | Yes |
| 7 | `8,7,6,5,4` | +957 | +944 | Yes |
| 8 | `1` | +983 | +985 | Yes |
| 8 | `6,5,4,3` | +971 | +983 | Yes |
| 8 | `8,7,6,5,4` | +973 | +982 | Yes |
| 9 | `1` | +980 | +982 | Yes |
| 9 | `6,5,4,3` | +951 | +955 | Yes |
| 9 | `8,7,6,5,4` | +954 | +954 | Yes |

**Eight of nine** reversed-writer cases favor coupling toward the *previously* earlier rows. All six cutoff-8/9 cases pass the directional prediction, with strong rank correlations. For m0=8 and m0=9, word `1` retains **exactly the same t** under both solver orders; the reversal there cannot be dismissed as an altered floor threshold.

The m0=7 cap-limited word `1` remains a genuine exception that may reflect the Schur-cap or different convergence dynamics.

**Interpretation:** Strong causal evidence that the dominant shared *rank pattern* in the long-weight finite certificates is an algorithmic sweep-order signature. It does **not** prove every higher-order pattern is explained by the algorithm, nor does it invalidate certificate inequalities independently verified with an exact gate. The next research problem is to formalize when and how the cap-limited m0=7 exception violates the last-change approximation, and determine whether alternative ordering and tighter outer convergence remove that difference.

## Separate room density V19C reproducibility

The original strict own-digit-shuffle (27 controls/cell) output in PR #166 has 6/6 Fano values inside controls, and its dataset was already committed to main. An initial independent hosted replay used alphabetical source order, changing the function population even though the room block SHA matched. Two **explicitly nonblind** provenance probes resolved the original input order as:

1. `S_cert_m9_r12_1_f6-5-4-3.leaf.hbp`;
2. `S_cert_m9_r12_1_f8-7-6-5-4.leaf.hbp`;
3. `S_cert_m9_r12_1_f1.leaf.hbp`.

The 729-function and 6561-function **real** Fano, FAR, and centre-share values each match exactly with that order across frozen and global-hash. The complete six-cell 27-control replay is [hosted here](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43261572315); its final verdict should be taken from that actual hosted run rather than inferred from these two source-order probes. Windows CRLF text-record endings require normalization before exact row comparison.

**No r=9 computation was run or approved.**
