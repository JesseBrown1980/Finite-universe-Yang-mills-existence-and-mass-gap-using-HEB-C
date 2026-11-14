# Degree-11 production: exact shell-5 spill and paired-moment plan

## Goal

The **production** target is degree **11**, consuming the real
accepted-K3 complete-Q moments mu0,...,mu21 (22 exact 8×8 matrices
per frozen source sample). The accepted mu0 and mu1 are already
source-conditional PASS. The first new moment **mu2** requires
the full first-step vector V1=X R, including *every* shell-5 target.
A partial shell-5 calculation cannot be called mu2.

## Techniques actually justified from Matrix Laws Essentials

| Existing method | Precise application | Verification required |
|---|---|---|
| Frozen-source SHA / HBI→HBP→SHA→HASH | Pin accepted-K3 Y, the complete Q4/inner residual and receipt; changes refuse | Original U/G source blobs, complete source census and independent transition replay |
| Fixed-trial parameter replay | Share the expensive gauge orbit geometry and magnetic costs across the two z samples | Each frozen R_z differs: shift only X on the same *sample-specific* R_z, do not equate moments of different initial vectors |
| Exact packed integer lanes | Eight nonnegative residual columns packed in fixed-width integer digits | Bound each target's incoming weighted move count by 72 and prevent cross-digit carries; independent unpack/repack |
| Source/target sparse push and spill | Emit canonical target code, source index, reverse multiplicity, target weight in fixed 14-byte binary records | Every *raw* source move accounted; no shell-5 exits dropped |
| Out-of-core hash/address partition | Partition by target code, not by originating Q4 source shard, then merge | All eight disjoint source shards must be combined **before squaring** each shared target contribution |
| Paired W-Gram moments | mu_(2j)=V_j*W V_j, mu_(2j+1)=V_j*W V_(j+1) | 11 full-Q applications give 22 moments, not 21 separate powers; W is the exact orbit metric |
| Exact vector/moment reuse | For the same R_z, retain V_j and V_(j+1) for two moments at a time | Q projection after each full Hamiltonian action; independent moment equality and block-Hankel/localizer tests |
| Exact polynomial Chebyshev compression | Once 22 moments exist, evaluate degree-11 corrected U as one fixed integer-linear combination and reuse spectral polynomial | Accepted integer-source prefactor 1/K11², **never b/K11²**; new bracket nested inside old; E1/E2 inertia 1 and 2 |
| Independent receipt/negative controls | Detect bad edges, wrong W, source omission, duplicate source, and original billion-fold normalization fault | Byte-for-byte host outputs are integrity evidence, **not** replacement for completeness |

**Not applicable without a separate theorem:** the power-of-three NTT
jump exploits a Fourier-diagonalizable fixed circulant operator.
This gauge-orbit QHQ is not proven to have that structure. No
\`3^k\` jump, affine source reduction or fast nonlinear conjugacy may
replace the eleven full-Q operator passes without exact proof of
equivalence.

## Exact shell5 vector rule

For the accepted source R_z in source integer units, the exterior
shell4 entries have a frozen sign \`R_z(f)=-P_z(f)\`, with
\`P_z(f)\` nonnegative. The canonical 3×4 S3 electric adjacency
satisfies full-row sum \`Σ_y T_fy=72\` and
\`W_f T_fg = W_g T_gf\`. The actual Q operator is

    X = b(QHQ-z) = b(72 I - T +9M)-z_num I, b=10^9.

At a shell5 target \`g\`, the original source is zero, so

    (X R_z)(g) = -b Σ_(f in shell4) T_gf R_z(f)
               =  b Σ_(f in shell4) [W_f T_fg/W_g] P_z(f).

Every omitted Q4→Q5 edge affects V1, and every cross-source-shard
shared target has a **cross term** when forming its W-weighted Gram.
The mathematically correct complete moment is

    mu2 = R*W X² R = (X R)*W (X R),

where the right side must include all active K3/Q4/Q5 components,
with exact Q-sector projection. The shell-5 contribution is

    mu2_shell5 = sum_(g in all shell5)
                   W_g V1(g)* V1(g).

The outer contribution is positive semidefinite **after all shard
contributions to each target g have been merged**. Separately
squaring each source shard omits valid cross terms and must be
rejected.

The source positions \`f\` are only references to the already
frozen 1,985,218-element accepted Q4 residual P vectors.
A binary record \`<QIBB\` stores:
- 64-bit canonical shell5 target key;
- 32-bit Q4 source position;
- unsigned exact weighted reverse multiplicity \`T_gf\`;
- one-byte exact W_g.

A 14-byte event avoids duplicating the potentially huge eight
source coefficients. The source vector is held once, or separately
addressed from frozen source data. This compresses the OUTGOING
edge stream rather than the mathematical state itself.

## Bounded first real pilot

The initial run enumerates **1024 genuine Q4 sources** from the real
accepted-K3 trial, generates exactly 72 raw electric moves each,
classifies every destination (K3, Q4, Q5, flat), emits all Q5 events,
and replays the actual binary spill by an **independently written
sort-and-accumulate loop**. It checks a sample of genuine reversed
raw electric rows. Both original E1/E2 residuals are read without
changing their frozen source hashes; their signed eight-column
spills are packed at a provably carry-free integer width.

**This is a partial operator-source pilot.** Its Q5 target vectors
and 8×8 partial Gram are exact only for those 1024 Q4 source
positions. They are not the real full-Q mu2, nor a Loewner lower
bound in every signed flat-space direction. The code prints
\`actual_mu2=NOT_COMPUTED\` and \`HOLD\` explicitly.

The separate toy uses two nontrivially weighted source rows with
different reverse multiplicities feeding one shell5 target. It
proves that squaring partial shards before target aggregation
gives an incorrect Gram; altered or missing edges are negative
controls.

## Production promotion gates

1. Full accepted K3 Q4 source census 1,985,218; no missing raw moves
   from any of the 8 source shards, and each Q5 event is indexed.
2. All emitted binary records have immutable SHA, source/canonical
   pins and are aggregated by target across **all** originating
   shards, before any weighted Gram.
3. Exact V1 on K3 and Q4 is combined with complete shell5 V1 and
   separately replayed to produce **mu2**. The original mu0 and mu1
   must reappear *exactly*.
4. Reconstruct next frontier shell6 from full V1, then repeat
   complete-Q streaming paired moments until mu21. Stop with
   RESOURCE_HOLD rather than silently trimming the reached set.
5. Evaluate corrected U11 with the tested \`1/K11²\` factor and
   old/new Schur nesting plus E1=1 and E2=2 inertia gates.
6. Verify actual normalized Wilson E1→E2 sign/overlap with the
   **independent** energy-direction bound, not only the source
   residual norm contraction.

**No completed 11-pass source or Wilson-positive conclusion is
implied by this bounded pilot.** The branch remains DRAFT and
issue #137 stays OPEN.
