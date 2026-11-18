# Independent proof-dependency audit — original first Wilson spectral weight

2026-11-18, original finite periodic `3×4` `S₃` at `r=9`. This is a separate code path from original Wilson source-replay PR #315. Its purpose is to evaluate the conditional theorem premises, identify exactly which parts have been reproduced, and supply a transparent referee-ready acceptance record.

## Target statement

Let `H` be the authentic orbit-weighted finite 3×4 S3 Hamiltonian and `O` the original seven-loop Wilson observable. For its distinct first and second **actual** normalized energy eigenstates, the source/projector calculation in PR #315 yields the proposed conditional inequality

```
abs(<psi2,O psi1>_W)^2 > 451 / 10^12
```

provided the whole-nonflat spectral bound, the signed-fourth-moment eigenprojector cone enclosures and the complete Q dual/action calculations are mathematically accepted. The inequality is a **finite, source-conditional certificate candidate**; no continuum SU(2)/SU(3) result is inferred.

## Independently checked logical steps

1. **Whole nonflat Q floor.** The existing Perron archive (immutable Git blob `cbd428014a4d440732a5c0a541ed57a9041becee`) records `QHQ≥94.070673` in units `J_E`. The Wilson proof uses `γ=94.068200`, leaving a numerical safety difference of **0.002473**. The recorded store has 45,508,080 sector rows reconstructed from source, all 1,632,625,631 weighted pairs checked, the external Go checker output, and an all-orbit symmetry-lift proof. The verifier authenticates the archive and rechecks all recorded values; **it does not redo 45 million graph rows**, so this stays conditional on accepted source provenance. The historical second-seat allpairs fail-closed review flags are retained as separate work.
2. **Stage E E1/E2 eigendirection cones.** The original signed μ3 and fourth-moment Schur source are regenerated using the original fixed source-pinned code for E1 and E2. The new verifier imports **no code** from either source generator; it verifies the exact archived chosen eight-flat directions, hosted E1/E2 direct distance receipts, original window upper endpoints, and independently checks the mathematical sufficiency of the W-flat sine conversion by exact integer cross multiplication:
   ```
   s_i^2 (γ-Ei_hi)^2 >= d_i^2 ((γ-Ei_hi)^2 + 72)
   ```
   where s_i and d_i use the same 10^12 scalar units and γ/energies use physical `J_E`. This checks the conversion independently but **does not reprove** the full signed eight-by-eight Schur moment enclosure or exact spectral branch identification.
3. **Original Wilson operator identity.** For distinct true eigenstates, `O9=2O−16I` has `<psi2,O9 psi1>=2<psi2,O psi1>`. The `8×8` same-Q Feshbach expression is `M9=P O9 P+C-sharp R2 O9_Q R1 C`. The audit includes a two-level exact integer toy with true distinct orthogonal eigenstates and a nontrivial G21 cancellation.
4. **Source-action and projector proof.** The referee checker downloads the **original frozen hosted artifact** from #315 run `44411639918`, not manually reproduced numbers. It checks the original W-flat metric, matched E1/E2 source vectors, 264 original weighted graph link receipt, complete-Q source scope, and separately recalculates the two-sided projector-angle inequality with upper cosines ONE for the negative terms:
   ```
   amplitude_lower >= c1_lo*c2_lo*source_lower
     - s1*adjoint_action_upper
     - s2*forward_action_upper
     - s1*s2*operator_upper.
   ```
   The independent integer result must be strictly positive `+47,724,563/10^12`. It independently reconstructs the exact physical norm and O9-to-O factor, and confirms the strictly positive rational squared-weight bound has integer floor **451 parts per trillion**, although its parts-per-billion floor is zero.
5. **Adversarial acceptance.** Eight mutations of source-Perron, original finite gap, physical link count, cosine direction, angular bound, physical weight, and selected E1/E2 angular source are all rejected.

## Scientific disposition and further review

**Perron source provenance: PASS as pinned receipt replay; fresh entire-sector/all-orbit independent-machine reconstruction: OPEN.**

**Signed Stage E mathematical source: source-generated receipt replay and independent projected-flat angle conversion: PASS; independent construction and proof of the signed Schur enclosures and eigenbranch identification: OPEN.**

**Full-Q original Wilson source/graph: hosted PASS in PR #315, independent mathematical acceptance of the complete source and true transfer: REVIEW REQUIRED.**

**Original physical finite first-excitation Wilson spectral weight: CONDITIONAL POSITIVE CANDIDATE / FORMAL HOLD.**

**4D Yang–Mills continuum theorem: OPEN.**

This separation is intentional. A successful test of the new independent audit strengthens reproducibility and checks the critical inequalities but cannot substitute for unperformed full independent matrix/source proofs. The actionable next step is an external reviewer independently reconstructing the pinned signed fourth-moment Schur enclosure and the exact whole-Q all-orbit Perron lift from the historical source definitions.

## Reproduction

```sh
gh run download 44411639918 \
  --name y137-original-S3-matched-Wilson-directional-action \
  --dir /tmp/wilson-action \
  --repo JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C

python3 -I -B independent/y137-e1-matched-projector-20261118/matched_e1.py real > /tmp/E1.hbp
python3 -I -B independent/y137-e2-matched-witness-20261117/matched.py real > /tmp/E2.hbp

python3 -I -B independent/y137-independent-premise-audit-20261118/audit.py \
  native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp \
  native/ym/results/3x4_stream/perron/MEASURED-FINITE-HIGH-CLUSTER-VERDICT-20261107.hbp \
  /tmp/wilson-action/ALL.hbp /tmp/E1.hbp /tmp/E2.hbp
```
