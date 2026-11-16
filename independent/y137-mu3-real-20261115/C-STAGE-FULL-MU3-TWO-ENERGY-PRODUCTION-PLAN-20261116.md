# #137 Stage C — authentic full signed μ3 production acceptance (2026-11-16)

**Frozen scope:** The full source and electric graph are authenticated; the complete third-moment matrices have **not** been computed. This contract is for cloud review before production.

## Original physical sources and operator

- Two exact integer samples: z1=69909875505; z2=69949729820; b=1000000000.
- 20,738,636 distinct canonical source states: K3=155378, Q4=1985218, Q5=18598040. Original source-support join run 43869667616. Physical signed V1=XR on K3/Q4 is authenticated by run 43867088509; the Q4 source is the **negative** historical positive response. Q5 has the positive physical source V1=b*(original V1/b).
- Physical orbit factor is 6*w_i; apply it **once**. Raw electric operator has D_i=b*(72+9*m_i)-z, with all 72 moves retained in the diagonal, including destinations outside supported source.
- Original accepted Q5 principal 8x8 μ3 matrices are pinned in RESULT-WORKER1-B5-REAL-20261116.hbp, run 43850680079. All sixteen original B6 Q5 μ2 Gram fingerprints remain unchanged.
- Complete source graph: run 43873674889, 1,493,181,792 moves, 139,517,148 **new non-Q5/Q5 unordered pairs**, exactly two opposite weighted-direction records per pair across 256 SHA-pinned partitions. Original B4 Q5/Q5 62,477,796 pairs remain separately accepted.

## Independent row and paired-edge evaluation

**Ordered-row calculation:** Initialize at the exact archived B5 Q5 principal matrix. For each K3/Q4 source row, add the full contribution

    6*w_i*v_ia * (D_i*v_ib - b*sum_{j in source} c_ij*v_jb).

For Q5 rows, add ONLY directed offdiagonal Q5-to-K3/Q4 contributions

    -6*b*w_i*sum_{j in K3 or Q4} c_ij*v_ia*v_jb.

Q5 diagonal and Q5-to-Q5 terms are already included in the original B5 principal result. Preserve true off-support counts as zero-vj transitions while retaining 72 in D.

**Unordered-pair calculation:** Initialize independently from the same exact B5 principal matrix. Add the diagonal contributions 6*w_i*D_i*v_ia*v_ib over K3/Q4. For each accepted new unordered pair i<j, use exactly one positive physical weighted flux f=w_i*c_ij=w_j*c_ji, and add

    -6*b*f*(v_ia*v_jb + v_ja*v_ib).

All true supported self-loop counts are zero in the exact accepted graph. The Q5/Q5 principal block must not be added again.

**Matrix gate:** Every one of the 128 integer entries (8x8 at two energies) must agree exactly across row/pair methods and be exactly symmetric. Verify the full magnetic diagonal, signed Q4 source, boundary interactions, 20.74M source membership and actual original B5 block. Reproduce historical full Q μ0/μ1/μ2 before claiming full μ3 acceptance.

## Checked arithmetic, negative controls, and receipts

The exact accepted full-residual envelope implies max physical signed source |V1|<2^112, and N<2^25, physical W<2^6, and max (|D|+72b)<2^39 imply a total absolute row and paired-edge contribution below **2^294**. Every signed 320-bit accumulator update must check overflow and strict partial-sum bound <2^294, including intermediate products. The physical signed source lanes fit in i128; *products and moments must never be accumulated in i128*.

Reject planted wrong-Q4-sign, energy swap, doubled factor six, missing cross contribution, omitted exterior diagonal, B5 double counting, forged SHA provenance, missing or duplicated reverse record, and signed overflows.

Persist both complete decimal 8x8 matrix strings, executable/Cargo.lock/source SHA256, the 256 pair partition SHA256 receipts and individual block counts to GitHub. The original binary pair artifact is GitHub Actions artifact 14228504695, while the 256-partition SHA manifest has SHA256 dda57b417ecb0bd0dd51842013981ef483ede7ddc509066786ce861ef277c027.

**Scientific disposition:** full signed source PASS; 1.493B-move graph and 201,994,944 total supported unordered reciprocal pairs PASS; two-energy whole-Q μ3 NOT_COMPUTED; Wilson spectral weight HOLD pending exact uncertainty strictly below 1/700. Issue #137 OPEN, research PRs DRAFT.
