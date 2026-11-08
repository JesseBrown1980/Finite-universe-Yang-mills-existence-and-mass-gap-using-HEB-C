## Second reviewer: PR #136 at `e538bac`

**Verdict: the proof composition holds.** No mathematical defect was found. One labelling fix is requested, below. The result stays conditional on the #131 lift, as the PR says.

### 1. The source bound is the one the Schur step needs

The Feshbach step needs A = QK_zQ ⪰ γW_Q, that is, a lower bound on λ_min of the nonflat principal compression of the whole-space H. E₉ alone would not give that, since λ_min(QHQ) can sit below E₉.

The source proves the compression bound directly. `PERRON-BOUND.md` §1 l.20 is `E_{|F|+1}(H) ≥ λ₁(H′) ≥ min_h (H′d)_h/d_h`, and §2 l.33–40 lifts d to every gauge orbit and concludes "the same minimum bounds λ₁(H′_whole)". The E₉ statement comes after, by interlacing (l.40–43). So λ_min(H′_whole) ≥ 94.070673 J_E is established, conditional on the lift.

**The same Q.** H′_whole removes the whole space's 8 flat orbits (`PERRON-BOUND.md` l.40–41, l.77). #136 removes the same set:
- every commuting pair, 18 in all, giving 8 orbits;
- M = 0 on each, diagonal 72;
- no flat–flat couplings;
- Q is everything else in the 2,177,317,873-orbit space;
- the inner product is the W-weighted orbit one in both.

**The lift's hypotheses** (§2, DERIVED), as I read them:
- the Sx+Sy+ rows are H on G-invariant functions;
- every G-orbit has a row, since the weights sum to 6¹³ (`PERRON-BOUND.md` l.89–90);
- G commutes with H and maps flats to flats;
- d > 0 on every nonflat row, as checked by `perroncert`, `check_d_strict.py` and Go run 41509351749 on `x3-c.bin`.

Under those, (H′_whole d̃)(x) = (H′_sector d)(rep x) holds pointwise, and Collatz–Wielandt applies to the whole-space Z-matrix. The lift is still an argument: it is measured only on 2×2 and 2×3 (`PERRON-BOUND.md` l.205–210). The full-store rebuild and all-pairs check ran on one machine (#131 caveat).

**Requested fix: name the right quantity.** #131's accepted-theorem box states only `E9_full ≥ 94.070673`, and #136's receipt records `accepted_source_assumption=E9_Nonflat_GE_94070673/1000000`. The quantity #136 uses is λ_min(QHQ) ≥ 94.070673 J_E, which is #131's proof step, not its headline. Please name it as such in the HBP field and in the markdown, for example `lambda_min_QHQ_whole_GE_94070673/1000000`, citing `PERRON-BOUND.md` §2 l.40. The math is unchanged; the record should cite the statement actually used.

### 2. The algebra

- **Resolvent identity.** With R = LF − AX for any X, L²S = U − RᵀA⁻¹R, where U = L²C − L(FᵀX + XᵀF) + XᵀAX.
- **Sandwich.** From 0 ≺ A⁻¹ ⪯ γ⁻¹W_Q⁻¹ it follows that U − γ⁻¹RᵀW_Q⁻¹R ⪯ L²S ⪯ U, so n₋(U) ≤ N(z) ≤ n₋(LOWER), with LOWER = 6γ_num·U − 10⁶·G.
- **Strictness.** Every inertia is taken with nonzero leading minors, so each threshold excludes equality:
  - N(69.89) = 0 gives E₁ > 69.89;
  - N(69.92) ≥ 1 gives E₁ < 69.92;
  - N(69.93) ≤ 1 gives E₂ > 69.93;
  - N(69.96) ≥ 2 gives E₂ < 69.96.

  The 6-against-2 mismatch at 69.96 is used one-sidedly, correctly.
- **Completeness of R.** X is supported on the two-move shells and F on shell 1, so R vanishes beyond one further move. The 147,344 exterior rows are complete. Exterior row values follow from detailed balance, which I checked independently, as below.

### 3. Independent reconstruction

`recon.py`, sha256 `f0cce4b865c9c6d7c9d185d389a8c9967740d222def2b26b9ed5833fd764341c`, Python integers only. It shares no code with `finite_s3_3x4_r9_first_gap.py`:
- a different link layout and spanning tree (row 0 plus every column), and its own canonical form;
- exterior rows computed from each exterior state's own 72 moves;
- X from 40 integer Gauss–Seidel sweeps at scale 10¹²;
- U from XᵀAX directly;
- inertia from the exact characteristic polynomial (integer Faddeev–LeVerrier) with Descartes' rule, which is exact for a symmetric matrix's real-rooted polynomial, with a self-test against Sylvester.

It runs in 132 s locally.

```
RECON_CENSUS|flat=8|commuting_pairs=18|flat_weight_sum=18|shell1=264|shell2=7770|exterior_shell3=147344
RECON_BALANCE|edges_checked=all_touching_K2|flat_flat=0
RECON_THRESHOLD|z=6989/100|n_neg_lower=0|n_neg_upper=0
RECON_THRESHOLD|z=6992/100|n_neg_lower=1|n_neg_upper=1
RECON_THRESHOLD|z=6993/100|n_neg_lower=1|n_neg_upper=1
RECON_THRESHOLD|z=6996/100|n_neg_lower=6|n_neg_upper=2
RECON_VERDICT|E1_gt_6989=1|E1_lt_6992=1|E2_gt_6993=1|E2_lt_6996=1|first_gap_in=(1/100,7/100)=1
```

The census and all four counts agree with #136's frozen HBP. The PR's own script also reproduces its HBP byte for byte on this machine.

### 4. Scope, for the record

E₁ and E₂ both lie below E₈ ≤ 70.031 (`PERRON-BOUND.md` l.79–80), so 0.01 < E₂ − E₁ < 0.07 J_E is the splitting inside the cluster of eight flat-sector levels. That is the "vacuum splitting" `PERRON-BOUND.md` l.8–9 anticipates at about 0.04. It is the finite 3×4 Hamiltonian's E₂ − E₁ as claimed, not the gap to the high cluster (E₉ − E₈ ≥ 24.04), and not a continuum statement. The PR's "Not claimed" list already says the latter.

### Disposition

Approve the mathematics, conditional on #131's lift. Request the labelling fix in §1 before merge. The other open items stand as the PR lists them: the second-machine full-store replay, the winding-sum spectral weight, and volume and continuum questions.
