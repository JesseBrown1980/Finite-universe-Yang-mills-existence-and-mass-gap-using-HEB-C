# #137 Worker 1 — Stage C signed source and complete μ₃ production acceptance plan

**Status:** Started 2026-11-16 on draft PR #216, from unified B6/B8 tree PR #215. The frozen Stage B predictions, two energy numerators, accepted eight Q5 source fingerprints and B5/B6 exact matrices remain unchanged. Original B6/B8 real-hosted controls rerun on unified PR #215 successfully (B6 43860569101, B8 43860568581, original source recheck 43860568354).

## Pinned source and formulas

Parameters: `b=1000000000`, `z_1=69909875505`, `z_2=69949729820`. For each canonical state i of the gauge-fixed 3×4 S3 torus, `D_i=b*(72+9*m_i)-z` and `X_ij=D_i delta_ij-b*c_ij` (including actual self loops in c). The physical inner product applies `W_i=6*w_i` **exactly once**.

The historical accepted source builder `independent/y137-real-Q-moment-20261114/mu1_shard.py` reconstructs its K3 trial `Y` and verifies the two original source U/G hashes through `source_cache.py` and `source.py`. Its `build_inputs()` returns `ball,ex,inner,flat,width,mask,items`, where `items[k]=(frozen_row, original_result, R_K3, packed_positive_Q4)` for both energies.

Signed residual before applying X:
- K3 residual on exactly 155,378 inner states: `R_K3=inner_residuals(Y)` (signed integer eight-vectors).
- Q4 residual on 1,985,218 outer shell-4 states: `R_Q4=-unpack(packed_positive_Q4)`.
- Q5 residual is zero. The accepted Stage B `V1_Q5=b*unpack(V1_over_b)` is therefore a *positive* source obtained by the original Q4→Q5 electric action.

After one X:
- `V1_K3 = D*R_K3 - b*sum_K3(c_ij*R_K3_j) + b*sum_Q4(c_if*pf_f)`.
- `V1_Q4 = -[D*pf_i - b*sum_Q4(c_ij*pf_j) + b*sum_K3(c_ij*R_K3_j)]`. This is **negative of** the previously stored *positive response* in the historical μ₁ builder; flipping this sign is a μ₃ error even when μ₂ Grams match.
- `V1_Q5 = +b*sum_Q4(c_ij*pf_j)` (the accepted frozen Q5 packed spools).

Complete actual third moment:
`mu3_six(z) = 6 * sum_{i in K3,Q4,Q5} w_i * V1_i^T * (X V1)_i`.
The diagonal retains all 72 raw moves. The offdiagonal includes K3↔K3, K3↔Q4, Q4↔Q4, Q4↔Q5 and Q5↔Q5 as present in the actual graph, plus any other observed supported transitions; outside-support neighbors have zero V1 and must remain separately counted rather than mislabeled.

## Acceptance and independent checks

1. **Source preflight.** Verify original frozen K3 U/G source hashes, canonical 72-degree rows, K3↔Q4 reverse-edge counts, magnetic values, per-state orbit weight. Verify the direct application of X to the signed residual agrees with the *negative* original Q4 response at both energies. Current `c_signed_q4_preflight.py` tests 27 real states per each of 8 K3/Q4 shards, plus source-free sign/cross-term faults. It is an exploratory **sample**, not the whole-source certificate.
2. **Full signed source materialization.** Produce 155,378 K3 and 1,985,218 Q4 signed 8-vectors at both energies. Partition by canonical address modulo 64, with exact input U/G/source SHA, ordered addresses, orbit weights, magnetic numbers and explicit signed lane encoding. A source-free signed encoding decoder, independent full-source index and source manifest must precede matrix accumulation.
3. **Independent signed source proof.** Recompute at least one full signed source path by a distinct row/edge contraction, including all K3/Q4 electric joins and Q4/Q5 boundary. Reject planted sign flips, omitted K3 terms, omitted Q4 terms, swapped samples and incorrect physical b scaling; a shared-sign row/pair agreement alone is insufficient.
4. **Complete graph join.** Reuse the exact original 18,598,040 Q5 Q5 principal source, and independently reenumerate all 72 raw electric moves for every nonzero-V1 state. Require weighted reciprocal edges for every supported block and all cross-block pairs. Preserve off-support census and actual self loops, if any.
5. **Full 8×8 matrices, both samples.** Compute the exact ordered-row and independently weighted-unordered-pair `mu3_six` (all 128 entries equal), with terms partitioned by block and cross-block. The accepted B5 Q5 principal contribution must appear as an exact separately hashed submatrix; B6 sixteen original Q5 μ₂ Grams remain identical.
6. **Bounded arithmetic.** Independently establish physical K3/Q4 amplitude and signed contracted-product bounds. Refuse signed 320-bit overflow, enforce a proved absolute partial-sum cap and term counts at *runtime*. Stage B7's Q5-only proof does not automatically cover K3/Q4.
7. **Prior-moment regression.** Reproduce accepted complete Q μ₀/μ₁/μ₂ exact fingerprints before accepting real μ₃. Preserve sources, executable SHA, build toolchain, source manifest hashes and both encoded row/pair matrices in repository, not just expiring CI artifacts.
8. **Stage D.** Only with an authenticated whole-space signed μ₃ run exact rational Loewner and Gauss/Lobatto acceptance, true Wilson normalization and strict spectral weight uncertainty `<1/700`. Existing best full-state error ≈0.014153976076 is still HOLD.

## Status contract

`K3_Q4_signed_preflight=IN_PROGRESS`
`K3_Q4_all_rows=NOT_COMPUTED`
`whole_Q_mu3=NOT_COMPUTED`
`first_Wilson_spectral_weight=HOLD`
`issue_137=OPEN`

**Branching:** No merge of #198/#208–#216. Cloud GPT-6 should review exact PR #215 unified runs and PR #216 preflight source code and published receipts before full-scale Stage C deployment.
