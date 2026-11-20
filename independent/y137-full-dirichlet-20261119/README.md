# #137 — independently recomputed whole 20,738,636-state signed third moment

This draft adds a third complete physical-moment computation method. It is a
new Rust 1.81 3×4 S3 gauge/move implementation and a separate exact 320-bit
signed matrix accumulator, with an independent Python integer-only 16-shard
matrix acceptance program. It imports **no original B5 Q5-principal matrix**,
Q5 pair graph archive, or original Stage C row/pair producer code.

## Original immutable source premises

The numerical starting point is the **authenticated original source
vectors**, not a newly regenerated ground-up K3 trial-Y construction:
the signed original K3/Q4 physical V1 and packed original Q5 V1/b for
both frozen energies. All 17 original source files must pass SHA256
checks against [SOURCE-SHA256.txt](SOURCE-SHA256.txt), including the
complete 18,598,040-state Q5 support, before any numerical calculation.
These are original immutable physical-source data premises.

The alternative S3 gauge generator independently constructs each
periodic 3×4, 24-link, 11-tree/13-kept-link, six-permutation canonical
physical state and its **72 electric moves**, raw orbit weight and
magnetic plaquette number. Original Q5 physical V1 amplitudes are
reconstituted from packed nonnegative lanes using exact b=10^9.

## Exact third moment

At each frozen energy \(z\) in

\`\`\`text
{69,909,875,505 ; 69,949,729,820},
\`\`\`

the physical operator \(X(z) = D(z)-bC\), \(D_i(z)=b(72+9m_i)-z\),
metric \(W_i=6w_i\), and complete signed original vector \(V_i\) yield

\`\`\`text
μ3_six(z) = Σ_i W_i V_i^T (D_i V_i - b Σ_j c_ij V_j).
\`\`\`

This is computed using a **symmetric Dirichlet rearrangement**:

\`\`\`text
μ3_six(z) =
    Σ_i 6w_i [b(72+9m_i)-z] V_i V_i^T
  − Σ_i 3bw_i [ V_i S_i^T + S_i V_i^T ],
S_i := Σ_(j in original source support) c_ij V_j.
\`\`\`

Weighted reciprocity \(w_i c_{ij}=w_j c_{ji}\) makes this identity
exact. This is algebraically the independently verified
[weighted Dirichlet edge-difference identity from draft #325](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/325),
including *every* source-to-zero boundary and every Q5→Q5 principal
edge. The computation DOES NOT import historical B5.

The implementation computes all 36 upper triangular entries using
checked 320-bit five-limb signed integer arithmetic, and then
symmetrizes the complete 8×8 physical matrix. It asserts each
intermediate signed partial magnitude below \(2^{294}\), the original
exact arithmetic requirement. The frozen original energies and
physics are maintained exactly.

## Full-state acceptance protocol

1. Eight disjoint source workers each load all 20,738,636 immutable
   physical state source vectors, verify all 17 SHA fingerprints,
   then independently reenumerate all 72 electric moves for states
   with \`address mod 8 = shard\`. Every one of the original physical
   states is therefore visited exactly once per energy across eight
   workers, without decomposing any states into approximate shadows.
   Each worker evaluates both frozen energies **sequentially** to
   bound RAM; 16 exact source/energy matrix contributions result.
2. Verify full 3×4 physical support count and exact K3/Q4/Q5
   source-shell transition counts. The complete physical graph census
   includes original K3↔Q4, Q4↔Q5, **Q5↔Q5 principal**
   \`125,005,512\` original raw moves, and **all Q5 exterior**
   \`1,088,585,976\` original raw moves. There can be no imported B5.
3. Challenge independent weighted reciprocal electric edges while
   rebuilding every full row. The exhaustive separate 256-partition
   cross-block pairwise audit is [draft #327](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/327).
   The full-Q5 principal reverse-pair proof remains a distinct graph
   integrity gate even after a numerical full-state 8×8 matrix passes.
4. Recombine the 16 exact wide integer matrix contributions and
   assert the whole physical 20,738,636-state census at each energy,
   all \`1,493,181,792\` original raw electric moves at each energy,
   12 exact original shell-to-shell/exterior graph transition counts,
   original magnetic and orbit checks, and exact 64/64 symmetry for
   each recomputed full 8×8 matrix.
5. Compare **all 128 exact 8×8 entries** independently to frozen
   original [Stage C two-energy production receipt](../y137-mu3-real-20261115/RESULT-WORKER1-C-FULL-SIGNED-MU3-TWO-ENERGY-20261116.hbp),
   recheck original matrix fingerprints, reject twelve forged partial
   matrix receipts, and seal the new source commit and SHA256 result.

The workflow [y137-fullstate-dirichlet.yml](../../.github/workflows/y137-fullstate-dirichlet.yml)
first tests standalone exact integer and fake-source controls, then
runs all eight production workers before strict independent fan-in.
No claim of a production PASS can be made until the **final hosted
full-state matrix acceptance** job succeeds.

## Separate proof review obligations

This production method independently regenerates the physical
**electric rows, Q5 principal and complete matrix accumulator**
from immutable original source vectors. Complete K3 trial-Y / Q4
positive-residual generation independently from first principles,
independent-machine Perron-store full-row replication, and final
original source-correlated Wilson operator theorem acceptance remain
distinct review gates. The strong original Wilson squared weight
lower candidate \`17,074,763/10^12\` remains SOURCE-CONDITIONAL /
**FORMAL HOLD** pending those prerequisites; the four-dimensional
continuum Yang–Mills problem remains OPEN.

No original Hamiltonian, original physical source spool, original
third-moment receipt, production code or main README is changed.
