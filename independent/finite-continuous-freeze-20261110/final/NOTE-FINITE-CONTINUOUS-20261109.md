# Finite against continuous: three prediction sets for the freeze

2026-11-09 · cloud seat, assembly, then the fix seat after review, then the refix seat after verify rounds 2, 3 and 4 · **measurement_status = NOT_RUN, measured_values = 0.**

This note goes with `PREDICTION-FINITE-CONTINUOUS-20261109.hbp` (sha256 `84adf9652ef9c14b403467ec26bebfb1fa1165afa1598b2f9e2007a777435df8`). That file holds 160 prediction rows across three tests:

| test | lane | rows | DERIVED | CONJECTURE | REPORTED | OPEN | MEASURED |
|---|---|---|---|---|---|---|---|
| FC1: universal against non-universal on ten finite S3 tori | T1 | 41 | 37 | 3 | 0 | 1 | 0 |
| FC2: where the break sits for ten finite subgroups of SU(2) | T2 | 60 | 19 | 40 | 1 | 0 | 0 |
| FC3: SU(2)_k past the degree-11 ceiling, and the q-deformed lattice caveat | T3 | 59 | 56 | 2 | 0 | 1 | 0 |
| **total** | | **160** | **112** | **45** | **1** | **2** | **0** |

Blindness of the 160 rows: 34 blind, 49 partly known, 34 controls (value known before the freeze), 40 weak (an approximate tool value existed before the freeze), 3 not blind tests. Section 6 explains the codes. The assembled file counted 96 blind rows. A review then found that the finite repository's own records already held several FC1 values (section 2.5), and that the FC2 tool rows had been evaluated before the freeze (section 3.3). The fix seat recoded those rows, which left 51. A second verify round found 11 more rows with values known before the freeze: seven FC3 rows whose k = 1 and 2 values PF-T3-1 had printed (section 4.3), three FC1 rows covered by further records (section 2.5), and FC2-29 (section 3.2). The refix seat recoded them, which left 40. A third verify round found a further record set, The-matrix-law-essentials [S13], that already gives the exact limits of FC1-16, 17, 18, 20 and 21, and showed that PF-T3-1 also covers k = 1 and 2 of FC3-32 and FC3-58. The refix seat recoded these seven rows in a second round, which left 35. A fourth search round found two more records: the 4D repository's character expansion [FC2-S15], which already proves and checks FC2-12's identity, and Finite-Universe-SU-N-solved [FC1-S14], now cited in FC1-01 and 03. It also showed that [S13] decides the whole of FC1-23's verdict rule. The refix seat's third round made FC2-12 (from blind) and FC1-23 (from partial) controls, which leaves 34 (section 6). No prediction changed. `CHANGES.txt` lists every change and its reason.

The finite repository holds many earlier records, so the blind codes state what was found by the searches listed, not a guarantee. Four search rounds were run: the review, and verify rounds 2, 3 and 4. Section 6.1 lists the repositories and refs they searched and the cutoff, 2026-11-10T11:30Z; the head row repeats them (`search_rounds`, `search_cutoff`). The rule: a previously established result found later reclassifies the affected row as a control (blind = 0) and never changes its prediction (`late_record_rule`).

Nothing here is MEASURED. Only the smallest cases the brief allows were computed: the 2x2 torus, S3 at the level of the group, SU(2)_k for k ≤ 2, plus some arithmetic on closed forms. The one exception is PF-T2-2, which evaluated the FC2 curves with truncated tools for all ten groups. The referee seat decides whether that run went beyond the brief (section 3.3). Each computation is listed in section 8 with its fingerprint. Everything else is a derivation, or a value produced by truncated asymptotic tools. Some FC1 values had already been measured before this file, in the finite repository's own records [S11], in PR #154 [S12] and in The-matrix-law-essentials [S13], and FC2-12's character identity in the 4D repository [FC2-S15]. Those rows are now controls or partly known.

**Source labels.** Each source number names one source across the three tests, except S13 and S14, which exist in both FC1 and FC2. This note writes the FC1 ones as [S13] (The-matrix-law-essentials) and [FC1-S14] (Finite-Universe-SU-N-solved), and every FC2 one from S13 on with its full id: [FC2-S13] (the 4D script), [FC2-S14] (Iconic MEASURE-LADDER.hbp) and [FC2-S15] (the 4D YM4-02c records).

**Tags.** DERIVED: proved in the lane note; the assembly seat checked the steps listed under "checked". REPORTED: read in a source that a seat opened. CONJECTURE: not proved; this includes every number produced by a truncated asymptotic tool. OPEN: not predicted, so the row is not scored.

---

## 1. The owner's frame (not part of the mathematics)

This section states the owner's frame. Sections 2 to 4 do not use it, and no row assumes it.

**The frame, as the owner states it.** The continuous arises from the finite world. A finite structure looks continuous up to some resolution, and then breaks at a point that can be computed. Universal invariants are the fingerprint that all such structures share: the "universal hash".

**How each test was built to be read against the frame.** These are readings, not results.

- **FC1.** The finite structure is S3 lattice gauge theory on a finite torus. The "continuous-looking" feature is the eightfold degenerate flat band (the D(S3) ground space). It is exactly degenerate through order r^-(Lmin-2), it splits at the computable order r^-(Lmin-1), and the coefficient of that splitting is computable too. The candidate fingerprint consists of the eight orbits and their weights, the normalized shape of the splitting, the gap 3r, and, once Lmin ≥ 3, the 1/r coefficient −21. The non-universal content is the order of the splitting, its prefactor, and the thin-torus coefficients. The 2xL family is the contrast case: its splitting order never grows with L.
- **FC2.** The finite structures are the finite subgroups G of SU(2). Each matches SU(2)'s trace moments up to its design strength t and breaks at degree t+1 by ι. The test asks where that break shows up in a smooth 2D observable: an onset β_x set by t, a turnover set by the nearest class, and a large-β envelope that does not depend on G.
- **FC3.** The finite structure is SU(2)_k, a fusion category with k+1 simple objects. It matches SU(2)'s invariant counts through degree 2k+1, which no finite subgroup can do beyond 11, and it breaks there by exactly −1. The caveat is that on a 3D lattice the quantum dimension already shows at β⁶ for every k. This holds for every plaquette weight with b_j/b₀ = O(β²) for all j ≥ 1, a class that contains every Wilson-like weight and the C_k weight. For weights in that class, the moment fingerprint is honest for counting invariants but not for 3D free energies. Outside it (for example b₁/b₀ ~ sβ), the argument does not apply.

**What a verdict will and will not mean.** A MET verdict confirms a mathematical statement. A NOT_MET verdict on a DERIVED row means there is an error in the derivation or in the measurement code; the refuter seat decides which. The owner may read the verdicts through the frame, but no single row tests the frame. FC1's thin tori and FC3's lattice caveat are both cases where the agreement holds in one quantity and fails in another. The rows record those as mathematics only.

---

## 2. FC1: S3 tori (lane T1, checked)

**Model.** Take the periodic Lx x Ly torus with Lx, Ly ≥ 2, V = LxLy vertices and n = 2LxLy links. The Hamiltonian is H/J_E = 6LxLy·I − T + r·M on gauge-invariant states. Here T is the sum over links l and transpositions t of the move g_l → t·g_l, and M = Σ_p (3 − #fix(g_p)), which is 0, 2 or 3 on e, a transposition or a 3-cycle. The brief's constant 72 equals 6LxLy only on 3x4 and 2x6, so every row predicts a difference, or an offset from 6LxLy. Flat classes are labelled by the holonomy pair (a,b): F1 (e,e), F2 (e,T), F3 (e,C), F4 (T,e), F5 (T,T), F6 (C,e), F7 (c,c), F8 (c,c⁻¹). Write Lmin = min(Lx,Ly), Llong = max(Lx,Ly) and κ_m = binom(2m−2, m−1)/4^(m−1).

### 2.1 Part (a): the flat sector (FC1-01 to FC1-05)

- M ≥ 0, and M = 0 exactly on flat configurations. In tree gauge a flat configuration is its commuting holonomy pair, modulo global conjugation.
- S3 has 18 commuting pairs, which form 8 orbits with weights (1,3,2,3,3,2,2,2). These numbers do not depend on Lx or Ly.
- One move turns both plaquettes of its link, which are distinct, into transpositions. So every first-shell state has M = 4, PTP = 0 and PHP = 6LxLy·I_8.
- The plaquette signs multiply to +1, so transposition plaquettes come in pairs. Hence the minimum M over nonflat configurations is 3, attained by a single 3-cycle plaquette.

*Checked by the assembly seat:*
- 18 = |G| × #classes, and the orbit sizes 6/|C(a,b)| are 1, 3, 2, 3, 3, 2, 2, 2.
- The sign argument.
- The first-shell energy.
- #143 [S2] reports the same 8 orbits, the 72 single-move neighbours at M = 4, and no two-move transitions between distinct flat classes on 3x4.

### 2.2 Part (b): where the eightfold degeneracy first breaks (FC1-06 to FC1-26)

**Schur expansion.** Put λ = 6LxLy − ε. On P the Schur equation reads

  ε = Σ(ε) = P T Q (rM_Q − T_Q + ε)⁻¹ Q T P.

This expands into positive walk sums. A walk of j moves contributes at order r^-(j−1), and every ε insertion costs a further O(r^-2). Σ is non-increasing in ε, so its eight branches give exactly the eight lowest levels. The band is isolated once r > 2LxLy.

**Locality theorem (B1 to B4).**
- A flat-to-flat walk of k ≤ Lmin moves keeps the class (B1) unless k = Lmin and the walk moves every link of a *straight line* exactly once. A straight line is a full row of vertical links (Lx links) or a full column of horizontal links (Ly links), on the short side.
- If the incidence graph of the moved links has no non-contractible cycle, the energies along the walk do not depend on the starting flat class (B2, by transport of frames).
- A non-contractible cycle needs at least Lmin links. With exactly Lmin links it is a straight line, and diagonal windings are impossible (B3).

Hence (B4):

  Σ(ε) = σ(ε,r)·I_8 + r^-(Lmin−1)·C + O(r^-Lmin),
  C = κ_Lmin·[Ly·Γ_V·[Lx = Lmin] + Lx·Γ_H·[Ly = Lmin]].

**Straight-line amplitude (B5).** After a subset A of the line has been moved, the intermediate energy is 4·arcs(A). Summed over the m! orderings, the product of 1/arcs is N_m = binom(2m−2, m−1), by a shuffle factorisation and the Catalan recursion. The flat-ending labels are the transpositions that commute with the holonomy around the line.

**Class action (B6).**
- Γ_V: (a,b) → (a, t·b) with t ∈ T ∩ C(a). Count-form entries: F1→F2 3, F2→F1 1, F2→F3 2, F3→F2 3, F4→F5 1, F5→F4 1.
- Γ_H is the same with a and b swapped: F1→F4 3, F4→F1 1, F4→F6 2, F6→F4 3, F2→F5 1, F5→F2 1.
- Both have spectrum (3,1,0,0,0,0,−1,−3).
- Γ_V + Γ_H has characteristic polynomial x⁴(x²−6)(x²−14).

**Per-torus predictions.** E_j − E_i = r^-(Lmin−1)(μ_i − μ_j) + O(r^-Lmin), with μ the spectrum of C sorted from the top.

| torus | FC id | order | C | E2 − E1, leading |
|---|---|---|---|---|
| 2x2 | FC1-13 | r⁻¹ | Γ_V + Γ_H | (√14 − √6)/r ≈ 1.292168/r (control: zgap2 and the 2x2 ladder [S11]) |
| 2x3 | FC1-14 | r⁻¹ | (3/2)Γ_V | 3/r (control: zgap2 and 2xL [S11]) |
| 2x4 | FC1-15 | r⁻¹ | 2Γ_V | 4/r (control: zgap2 and 2xL [S11]) |
| 2x5 | FC1-16 | r⁻¹ | (5/2)Γ_V | 5/r (control: exact limit in [S13]) |
| 2x6 | FC1-17 | r⁻¹ | 3Γ_V | 6/r (control: exact limit in [S13]) |
| 3x3 | FC1-18 | r⁻² | (9/8)(Γ_V + Γ_H) | ≈ 1.453689/r² (control: exact limit in [S13]) |
| 3x4 | FC1-19 | r⁻² | (3/2)Γ_V | 3/r² (control: #143 [S2]) |
| 3x5 | FC1-20 | r⁻² | (15/8)Γ_V | (15/4)/r² (control: exact limit in [S13]) |
| 4x4 | FC1-21 | r⁻³ | (5/4)(Γ_V + Γ_H) | ≈ 1.615210/r³ (control: exact limit in [S13]) |
| 4x5 | FC1-22 | r⁻³ | (25/16)Γ_V | (25/8)/r³ |

**Shape and symmetry.**
- *Rectangles:* the pattern is −(3,1,0,0,0,0,−1,−3)·Llong·κ_Lmin, and (E3−E2)/(E2−E1) → 1/2.
- *Squares:* the pattern is −(√14,√6,0,0,0,0,−√6,−√14)·L·κ_L, and the ratio → (√21+3)/4 ≈ 1.895644.
- *Degeneracy and symmetry:* E3 = E4 = E5 = E6 at this order. C is bipartite under sgn(a)sgn(b), so the pattern is symmetric.
- *Swap sector:* on squares, E2 is odd under the swap x ↔ y.
- *Mean:* the band mean is 6LxLy − (3LxLy/2)/r + O(r⁻²) on every torus.

**Thin tori (FC1-23).** 2xL splits at order 1/r for every L, with E2 − E1 = L/r. Every family with a fixed short side behaves the same way at its own fixed order. The records [S11] already give this on 2x3 and 2x4, and the 2x5 stage-B certificate [S11 2x5B] gives one certified point at r = 9 (E2 − E1 and E8 − E1). The-matrix-law-essentials [S13] gives E2 − E1 = L/r and E8 − E1 = 3L/r exactly on 2x3 to 2x6 (on 2x2 its gap coefficient is √14 − √6, not L = 2), and the 3xL law at L = 4 and 5. FC1-23's verdict rule scores only 2x3 to 2x6, so the row is a control (refix seat, third round). The law for general L is in its scope but is not scored.

*Checked by the assembly seat:*
- The Γ_V and Γ_H entries, by hand from the S3 commutation relations, and their detailed balance with the weights.
- The characteristic polynomials: by hand through the matching and cycle expansion (the 4-cycle F1–F2–F5–F4 contributes −2·3, which turns 90 into 84), and by integer Faddeev–LeVerrier (PF-A-2).
- Bipartiteness, the swap-sector decomposition and the square ratio.
- N_2, N_3 and N_4 = 2, 6, 20 by hand.
- Every per-torus coefficient and every decimal (PF-A-2).
- #143 [S2] reports C1 = CA ⊕ CB ⊕ 0, with CA = ((0,9/2,0),(3/2,0,3),(0,9/2,0)) and CB = ((0,3/2),(3/2,0)). This is (3/2)Γ_V entry for entry, so FC1-19 is a control and not a blind test.
- The 2x2 two-move matrix 6I + Γ_V + Γ_H in the output of PF-T1-3.

*Read and found coherent, but not re-derived:* the frame-transport proof of B2, and the winding argument of B3.

### 2.3 Part (c): the gap above the band (FC1-27 to FC1-37)

**The M = 3 manifold.** M = 3 means a single 3-cycle plaquette p0 with everything else flat. For each p0 there are 3 free conjugation orbits, labelled by (sgnA, sgnB) ∈ {TT, TC, CT}. The manifold has dimension 3LxLy.

- **First order.** Moves on ∂p0 go to M = 4 and all other moves go to M = 7, so P3 T P3 = 0. Hence E9 − E8 = 3r + O(1/r) on every torus. FC1-27 is scored on the exact series coefficient of r. Certified finite-r values count only where certification is feasible (fix seat; the old rule needed r = 1000 on every torus).
- **Lmin ≥ 3 (FC1-28).** The second-order matrix is K = (3LxLy/2 + 9)·I + 3·A_plaq ⊗ I_3:
  - returns: 12 moves with denominator 1, the other moves with denominator 4;
  - hops: 3 per neighbour, with the internal label kept.
  So E9 = E10 = E11 = 3r + 6LxLy − (3LxLy/2 + 21)/r, and **E9 − E8 = 3r − 21/r**, the same on all five tori. The next level is E12 − E9 = 6(1 − cos(2π/Llong))/r (FC1-37). zgap2 [S11] already reports c_L = 21 exactly on 3x3, 3x4 and 4x4, with the reduced operator (x − 84)³. So FC1-28 is blind only on 3x5 and 4x5, and 4x5 has r = 9 bounds on E9 (a Ritz upper bound and a claimed lower bound [S11 rev55]), which do not fix the limit. zgap2's RESULT.hbp also prints E9's own 1/r coefficient (λ_min of H3) on 2x2, 2x3, 2x4, 3x3, 3x4 and 4x4, so FC1-34 is unknown only on 2x5, 2x6, 3x5 and 4x5.
- **2xL, L ≥ 3 (FC1-29 to FC1-32).** The two vertical links of a row bound the same two plaquettes. That adds three kinds of process, each of which flips the internal label between TT and TC:
  - α: weight 4;
  - β: weight 4;
  - row-pair moves in the L−1 other rows: 1/2 each.
  The Perron value of the TT/TC block gives E9 − E8 = 3r − (4L+57)/(2r): −69/2, −73/2, −77/2 and −81/2 for L = 3 to 6. zgap2 [S11] prints 69/2 on 2x3 and 73/2 on 2x4, so FC1-29 and FC1-30 are controls. FC1-32 (2x6) stays blind. FC1-31 (2x5) is partly known: the stage-B certificate [S11 2x5B] gives E9 − E8 at r = 9.
- **2x2 (FC1-33).** At zero momentum the matrix is 27·I + (17/2)·star on (TT, TC, CT), so E9 − E8 = 3r − (21 + 17√2/2 + √14)/r ≈ 3r − 36.762473/r. zgap2 [S11] prints 36.762472… (truncated, irrational) on 2x2. FC1-33 was already a control.

*Checked by the assembly seat:*
- The denominators: a move on ∂p0 turns the 3-cycle into a transposition and makes one more transposition next to it, so M = 4.
- The hop amplitude: exactly 3 ordered pairs of transpositions have a given 3-cycle as their product.
- The arithmetic D0 + 12 = 3LxLy/2 + 21, and (7L+57)/2 − 3L/2 = (4L+57)/2.
- The positive E10 − E9 on 2xL, both at k = 0 and at nonzero momentum.
- The 2x2 12x12 matrix in the output of PF-T1-3: diagonal 60/4 = 15, same-plaquette flip 18/4 = 4 + 1/2, β flip 16/4 = 4, label-keeping hops 24/4 = 6, and zero-momentum entries 108/4 = 27 and 34/4 = 17/2.

*Not checked beyond the lane:* the α and β counts and the row-pair counts for L ≥ 3. The lane flags this itself, because only 2x2 was computed. zgap2 [S11] prints the same coefficients for L = 3 and 4. So the open risk is now L = 5 and 6. Both the diagonal term and the row-pair count are linear in L, so the two controls at L = 3 and 4 fix the law for L = 5 and 6, provided the process structure is as the lane describes. That proviso is the residual risk.

### 2.4 Universal and non-universal content

| | the same on all ten tori | depends on the torus |
|---|---|---|
| flat sector | 8 orbits; weights (1,3,2,3,3,2,2,2); PTP = 0 | the constant 6LxLy |
| splitting | normalized spectrum of C (one shape for rectangles, one for squares); its ratio and symmetry | the order Lmin − 1; the prefactor Llong·κ_Lmin |
| gap | 3r; −21/r once Lmin ≥ 3; threefold E9 | the 1/r coefficients on thin tori; E12 − E9 |

**Conjectures.**
- FC1-38: Γ_V is the closed D(S3) ribbon operator for anyon D. The lane recalled the S-matrix from memory. A measured 6S matrix of D(S3) was already in a record, PR #154 [S12], and with spec(Γ_V) from S2 it fixes the spectral part of the row's verdict rule. So the spectral comparison is a control, and the row is partly known. Only the operator-level identification (the eigenvectors) is unmeasured.
- FC1-39: the E9 triplet splits at order r^-(Lmin−1) into three equally spaced levels.
- FC1-40: the thin-torus break point is L* ≈ (6r² − 57)/4. Its reachability is flagged as low. Its verdict rule has no mechanical tolerance, so only the referee scores it.

**OPEN.** FC1-41: all finite-r values, including r = 9.

### 2.5 Records that already held FC1 values (source FC1-S11, added by the fix seat)

A review after assembly found that the finite repository's own records at commit 6a7fc747 already hold several FC1 values. Lane T1 and the assembly seat did not cite them. The fix seat opened them read-only and re-ran nothing.

- **zgap2** (`native/ym/results/zgap2-2026-10-30-cloud/README.md`, exact integer perturbation theory, 2026-10-30):
  - E9 − E8 = 3r − c_L/r, with c_L = 21 on 3x3, 3x4 and 4x4, 69/2 on 2x3, 73/2 on 2x4 and 36.762472… on 2x2;
  - the reduced operator (x − 84)³, which is the threefold E9;
  - first order adds nothing, and there are 3 orbits per plaquette at M = 3;
  - the flat second-order operator: lowest splitting √14 − √6 on 2x2, exactly 3 on 2x3, exactly 4 on 2x4, and exactly scalar on 3x3.
- **2xL** (`native/ym/results/2xL/README.md`, which S1 points to): certified E2 − E1 and E9 − E8 intervals on 2x2, 2x3, 2x4 and 3x3, at r = 9 to 243. It notes that the first splitting is "close to L/r".
- **3x3 Ritz** (`independent/SEAT_3X3_VACUUM_BLOCK_RITZ_REPORT.md`, and the README row that sums it up). These are trial-space values, and the report states full_gap = NOT_CERTIFIED. They give:
  - the formula (9/8)(√14 − √6)/r², beside Ritz ratios 1.09693, 1.00924 and 1.00098 at r = 9, 27 and 81;
  - the eight Ritz levels at r = 27.
- **2x2 coupling ladder** (README): r(E1 − E0) → √14 − √6.
- **README 2xL summary:** a lower bound E9 − E8 ≥ 21.778 on 2x5 for r ≥ 9. The interval itself is in the stage-B certificate below.

The refix seat (after verify round 2) added three labels to S11 and a new source S12. All S11 files were reopened read-only at 6a7fc747 with `git show`; the quoted lines were confirmed, and the S11 row now records the sha256 of each file.
- **zgap2R** (`native/ym/results/zgap2-2026-10-30-cloud/RESULT.hbp`): ZGAP_C prints λ_min of H3, whose negative is E9's 1/r coefficient, on 2x2 (39.020815…), 2x3 (39), 2x4 (42.5), 3x3 (34.5), 3x4 (39) and 4x4 (45). It prints H0_top = −13.5, −18, −24 with K0_scalar = 1 on 3x3, 3x4 and 4x4, so the vacuum second order is −(3LxLy/2)·I there, and H0_top on 2x2, 2x3 and 2x4. ZGAP_SIZE gives m3_orbits = 3LxLy on six tori.
- **2x5B** (`native/ym/results/2x5_stage_b/HEBC-YM-2X5-STAGE-B.hbp`, added at a853916): certified r = 9 intervals on 2x5 for E1, E2, E8, E9, E2 − E1, E8 − E1 and E9 − E8.
- **rev55** (`native/ym/results/3x4_stream/perron/vector/review-opus55/out/`, added at e0466bd): flat counts on 4x4 and 4x5 (18 pairs, 8 classes, every single move from a flat lands at M = 4); M = 3 as the lowest nonflat M in the r = 9 models; Ritz upper bounds on E9 at r = 9 on 3x4, 4x4 and 4x5; claimed E9 lower bounds at r = 9 on 4x4 and 4x5; a complete-model Ritz value on 3x3 at r = 9; E8 upper bounds at r = 9 on 3x3 to 4x5.
- **S12, PR #154** (branch pr154, commit b8a2daa, 2026-11-09 13:16 −0300, unmerged): `independent/ICONIC-RELATIONSHIP-20261109.hbp`, row MODULAR_S, the measured 6S matrix of D(S3) in the charge-flux basis.

The refix seat's second round (after verify round 3) added source S13:
- **S13, The-matrix-law-essentials** (`data/volume/flat_law.hbp`, `flat_law3.hbp`, `flat_law4.hbp`, `second_order.hbp`, and the README section "Results: exact weak-coupling laws"; commit 28345a6 of 2026-10-25, with the final `flat_law.hbp` and `flat_law3.hbp` at 8a28b50 the same day, unchanged on main e9eb988). The values come from integer characteristic polynomials with Sturm root isolation, so they are exact large-r coefficients, not finite-r estimates. They are in the same convention as the rows (r = J_B/J_E, J_E = 1):
  - the limit of r(E2 − E1): √14 − √6 on 2x2, and exactly 3, 4, 5 and 6 on 2x3 to 2x6;
  - the limit of r²(E2 − E1): (9/8)(√14 − √6) on 3x3, and exactly 3 and 15/4 on 3x4 and 3x5;
  - the limit of r³(E2 − E1): (5/4)(√14 − √6) on 4x4;
  - on 4x5, only that the second order is degenerate;
  - on all ten tori (and 5x5): 8 flat vacua, flat_to_flat = 0, PEP_diag = 6LxLy and intermediate M = 4;
  - the second-order spectra: κ = 27, 21, 18, 15, 9 on 2x6 (and the like on 2x2 to 2x5), scalar 3LxLy/2 on 3x3 to 4x5, and the third- and fourth-order spectra on 3x3, 3x4, 3x5 and 4x4.

Lane T1 and every earlier seat missed this repository. All the quoted lines were found with `git show` on a clone; the S13 row records the sha256 of every file.

Effect on the rows:
- **New controls (blind = 0):** FC1-14 and FC1-15 (the 2x3 and 2x4 splittings), and FC1-29 and FC1-30 (the 2x3 and 2x4 gap coefficients). FC1-13 and FC1-33 were controls already. Their known_before_freeze now names these records.
- **Now partly known:**
  - FC1-18 (3x3): only the formula and uncertified values are in the records, with no exact series coefficient (since the second refix round FC1-18 is a control, because [S13] prints the exact coefficient);
  - FC1-23: blind only on 2x5 and 2x6 (a control since the third refix round, because [S13] decides its verdict rule on 2x3 to 2x6);
  - FC1-28: blind only on 3x5 and 4x5.
- **known_before_freeze filled or extended:** FC1-06, 10, 11, 12, 26, 27, 31, 34, 35, 36 and 41.
- **Refix seat:** FC1-16 and FC1-31 (2x5) are now partly known (FC1-16 became a control in the second round). A certified finite-r record does not fix a limit, but it is an approximate evaluation of it, the same kind of record that made FC1-18 and FC1-27 partial. The head row now states this rule. FC1-38 is partly known (S12). known_before_freeze is filled or extended on FC1-01, 02, 05, 16, 23, 25, 26, 27, 28, 31, 34, 35, 38 and 41.
- **Refix seat, second round (S13):** FC1-16, 17, 18, 20 and 21 are now controls. FC1-22 (4x5) stays blind: S13 has only the second-order degeneracy there. FC1-13, 14, 15 and 19 also cite S13. known_before_freeze is extended on FC1-01, 03, 04, 05, 06, 07, 08, 10, 11, 12, 23, 25 and 26. Their codes stay partial. Most are now blind only on 4x5, or only in a form the records do not print, such as count-form entries or the law for general L. FC1-01, 03 and 04 are covered on all ten tori by S13's counts, so each carries a referee question: recode to 0 if these counts decide the verdict rule.
- **Refix seat, third round (after verify round 4):** FC1-23 is a control, as above; its known_before_freeze now says 2x3 to 2x6, not 2x2 to 2x6. A fourth search round found Finite-Universe-SU-N-solved [FC1-S14] (`docs/FINITE_GROUP_LAWS.md` at main e6d36326, added at 242f8a8 on 2026-10-31; lines 57 and 69–79): N_flat = Σ_[g] k(C(g)), with 8 for S3, described as the flat-vacuum count of every periodic S3 torus (attributed to The-matrix-law-essentials) and enumerated directly. FC1-01 and FC1-03 cite it as further support for their referee question; their codes stay partial.

The reviewer reports that the records agree with the T1 values everywhere it checked. That is the reviewer's statement. Neither the fix seat nor the refix seat changed an FC1 value or measured anything.

---

## 3. FC2: finite subgroups of SU(2) (lane T2, checked)

**Definitions** (row FC2-00). The model is the 2D Wilson model with free boundary, in which the plaquettes are independent.

- c_g = tr(g)/2.
- P_G(β) = Σ_g c_g e^(βc_g) / Σ_g e^(βc_g), and P_SU2 = I₂(β)/I₁(β).
- δ_G = P_G/P_SU2 − 1.
- β_up(θ) and β_down(θ) are the first and last crossings of δ_G = θ, and β_x = β_up(1/100).
- t is the design strength and ι = M_(t+1)^G − M_(t+1)^Haar.

### 3.1 Part (a): design degree and the Transfer coefficients (FC2-01 to FC2-11)

**Lemma A.** M_n^G − M_n^Haar = Σ_(j>0) m(n,j)·dim V_j^G ≥ 0. Hence t + 1 is the smallest positive degree n with d_n > 0, and ι = d_(t+1).

**Lemma B.** The cumulants agree through degree t. So ln z_G − ln z_SU2 = ιβ^(t+1)/(2^(t+1)(t+1)!) + O(β^(t+2)), and P_G − P_SU2 = ιβ^t/(2^(t+1) t!) + ….

| G | t | ι | β^(t+1) coefficient of ln z_G − ln z_SU2 | β^t coefficient of P_G − P_SU2 |
|---|---|---|---|---|
| Z3, Z4, Z6 | 1 | 1 | 1/8 | 1/4 |
| Q8 | 3 | 2 | 1/192 | 1/48 |
| Dic3, Dic4, Dic6 | 3 | 1 | 1/384 | 1/96 |
| 2T | 5 | 1 | 1/46080 | 1/7680 |
| 2O | 7 | 1 | 1/10321920 | 1/1290240 |
| 2I | 11 | 1 | 1/1961990553600 | 1/163499212800 |

*Checked by the assembly seat:*
- Every row of the table, recomputed from Klein's Molien series (1 + t^p)/((1 − t^q)(1 − t^r)) through Lemma A (PF-A-2). This is independent of the lane's group closure.
- The moments by hand: Z3 has traces 2, −1, −1, so M₂ = 2. Q8 has M₄ = 4. Dic3 has M₄ = 3.
- The 2I and Dic values against the ladder table of Transfer 1 [S6].

These rows are **controls**: the lane computed them exactly before the freeze (PF-T2-1), and [S6] reports them.

### 3.2 Exact structure of the curve (FC2-12 to FC2-16, FC2-28, FC2-29)

**Character identity (Proposition 1).** z_G(β) = (2/β) Σ_(n≥0) d_n (n+1) I_(n+1)(β). This follows from a_j = I_(2j) − I_(2j+2) = (2(2j+1)/β) I_(2j+1), which uses DLMF 10.32.3 and 10.29.1, together with E_G[χ_j] = d_(2j).

**An earlier proof and check of the identity (refix seat, third round).** The 4D repository [FC2-S15] (main 830fd3fd) already states, proves and records as MEASURED the expansion behind Proposition 1, class function by class function. `docs/PREDICTION-YM4-02c.hbp` line 8 (YM4_02C_CHARACTER) gives exp(β cos θ) = Σ_n (n+1) l_n(β) χ_n(θ) with l_n = 2 I_(n+1)(β)/β, and line 34 (YM4_02C_RESULT_CHARACTER, MEASURED, met = 1) records 105 identities through β²⁰ at traces 2, 1, 0, −1 and −2, with 0 failures. Lines 9 and 35 hold the ballot moments E[(Tr U)^m χ_n] and their quadrature checks for Q8, 2T, 2O and 2I. `docs/LEMMA-0004-REFLECTION-TRANSFER.md` lines 170–180 prove the expansion (line 319 lists the ballot checks). Averaging over G, with tr g = 2 cos θ and E_G[χ_n] = d_n, is one linear step and gives FC2-12's identity. The traces checked are every trace that occurs in Z3, Z4, Z6, Q8, Dic3 and 2T. The line was added at 0e9bcff and the result at c31a033 (both 2026-11-03), before this file. FC2-12 is therefore a control; its prediction is unchanged.

**Sign theorem (Theorem 3).**
- I_(ν+1)/I_ν increases strictly in β, by Riccati comparison with the equilibrium curve (DLMF 10.29.2). So R = z_G/z_SU2 increases, and P_G > P_SU2 for every β > 0 and every G.
- Since P_G < 1, it follows that δ_G < E(β) = I₁/I₂ − 1.

**Small β (Corollary 4).**
- In general, δ_G = ιβ^(t−1)/(2^(t−1) t!) + ….
- For the t ≥ 3 groups: Q8 β²/12, Dic_n β²/24, 2T β⁴/1920, 2O β⁶/322560, 2I β¹⁰/40874803200.
- The cyclic groups start at δ(0+) = 1: Z3 1 + β/2, Z4 1 − β²/12, Z6 1 − β²/6.

**Large β (Corollary 5).** 1 − P_G ~ N₁Δ₁e^(−βΔ₁), where Δ₁ = 1 − cos(2π/N_max). In FC2-28, Δ₁ for Dic4, 2O and Dic6 is now written (2−√2):2 and (2−√3):2, so that the num:den format cannot be misread; the numbers are unchanged. The Hankel expansion gives P_SU2 = 1 − 3/(2β) + 3/(8β²) + 3/(8β³) + 63/(128β⁴) + 27/(32β⁵) + …, and E = 3/(2β) + 15/(8β²) + 15/(8β³) + 135/(128β⁴) − 45/(32β⁵) + ….

*Checked by the assembly seat:*
- The DLMF steps of Proposition 1, and the Riccati argument.
- The small-β forms of Z3, Z4 and Z6, by explicit cumulants.
- The Hankel rationals of P_SU2 and E, recomputed from DLMF 10.40.1 by exact series division (PF-A-2).
- The (c₁, Δ₁, N₁) table from the element orders: for example, 2O has 6 elements of trace √2, and 2I has 12 elements of trace (1+√5)/2.
- The window choices of FC2-28: at β = 60, 80 and 120 the relative corrections are below 10⁻⁶, so a ±10⁻³ window is safe.

**FC2-29 is partly known.** PF-T2-2 (`ASYM.hbp`, row SU2_LARGE_BETA) and PF-A-2 printed its Hankel rationals exactly before the freeze, and a script in the 4D repository [FC2-S13] builds the same coefficients (its output is not recorded). The row is coded partial. The referee may make it a control if these exact coefficients already decide its verdict rule. The refix seat left this code for the referee.

**An earlier measured series (refix seat, second round).** Iconic's `measurements/su2-ladder/MEASURE-LADDER.hbp` [FC2-S14] (commit 565b9ac on main, 2026-11-09 13:47 −0300) holds ln z_G − ln z_SU2 as exact rationals through β³⁰ for all ten groups. Its β-derivative is the small-β series of P_G − P_SU2. It fixes the small-β region only, which is the content of FC2-15 (already a control); it does not decide FC2-13 or FC2-14 for every β > 0. FC2-12 to 15 now name it in known_before_freeze. FC2-13 and 14 stay blind, each with a referee question: recode to partial if a 30-term series counts as an approximate evaluation. FC2-12 kept the same question until the third refix round; it is now a control because of [FC2-S15] (above), and its question is withdrawn.

### 3.3 Parts (b) and (c): onset, turnover and laws (all CONJECTURE)

The numbers come from three truncated tools, evaluated in integer fixed point (PF-T2-2). None of them is the exact curve.

- **S:** the strong-coupling Wronskian series, used for β ≤ 2.5.
- **D:** the character identity truncated to 4 defects, with Debye or Hankel on the SU(2) side.
- **L:** the two-class gap model. It is rigorous on the group side.

The rule for picking a tool at each crossing was fixed before the rows were written.

| G | β_x (FC2-17 to FC2-23) | β_up(10%) | β_down(10%) | β_down(50%) | peak (value; β) |
|---|---|---|---|---|---|
| Z3 | 0 | 0 | 16.22874 | 4.0531 | 1.24016; 0.886 |
| Z4 | 0 | 0 | 16.22871 | 3.698 | monotone from 1 |
| Z6 | 0 | 0 | 16.17822 | 2.64 | monotone from 1 |
| Q8 | 0.348038 | 1.155757 | 16.22865 | never | 0.3708; 3.73 |
| Dic3 | 0.494155 | 1.719952 | 16.1780 | never | 0.2479; 4.68 |
| Dic4 | 0.494925 | 1.761251 | 15.1925 | never | 0.2100; 4.28 |
| Dic6 | 0.494926 | 1.762092 | 11.20 | never | 0.2060; 4.14 |
| 2T | 2.29211 | 5.56383 | 16.0115 | never | 0.14305; 8.91 |
| 2O | 4.86716 | never | never | never | 0.08445; 14.46 |
| 2I | 12.29801 | never | never | never | 0.04517; 27.50 |

Every group crosses 1 % on the way down at the envelope value 151.2479 (FC2-31). Each row carries its own interval.

**Laws (FC2-25 to FC2-27, FC2-55, FC2-56).**
- The Transfer-leading law 2(0.01·t!/ι)^(1/(t−1)) undershoots by 0.47 %, 0.86 to 1.02 %, 8.67 %, 21.02 % and 40.94 %.
- The heat-kernel law overshoots.
- The true onset grows faster than linearly in t+1: c_t = 0.1235, 0.3820, 0.6084, 1.0248.
- The peak follows a gap law, x* = ln(2N₁x*²/3), which has no root when N₁ = 2.

*Checked by the assembly seat:*
- Every row value traces to `ASYM.hbp`. For example: Dic3 β_x 0.4941554 (S12); 2O 4.8671006 (Debye) and 4.8672240 (Hankel); 2I 12.2980136 and 12.2980029; the D-tool maxima 2T 0.143045 at 8.9114, 2O 0.084447 at 14.4566, 2I 0.045169 at 27.5033.
- The law arithmetic (β_T, the undershoots, c_t, Λ_t, x*, β_peak and δ_peak from the law, the peak products), recomputed in integers (PF-A-2).
- Three of the L-tool descents (2T, Dic4 and Z6 at 10 %), by hand with the leading gap term, which agrees to about 0.01 (PF-A-0).

**These rows check numerical tools. They are not blind predictions (blind = weak).** PF-T2-2 evaluated δ_G(β) for all ten groups before the freeze, with tools that sit close to the exact curve:
- S is the strong-coupling series built from the exact group moments;
- D is truncated at four defects;
- L is rigorous on the group side.

The review found these spreads: S12 − S8 < 10⁻⁶ at the Q8 and Dic onsets (10⁻⁷ for Q8), and D4 − D3 < 10⁻⁹ on 2O. It also found that each crossing interval is about ±0.2 % of the tool value, or three times the tool spread. Peak windows are wider, at about ±2 to 4 %. So these are approximate pre-freeze evaluations of the very quantity to be measured. A MET verdict says that the tool code and its truncation were right. It does not confirm a blind prediction.

All 40 rows for which PF-T2-2 produced a tool value are therefore coded **weak**: FC2-17 to 27, 30 to 57, and 59. The fix seat recoded 38 of them from blind = 1. FC2-32 and FC2-42 (the Z3 descents, whose group side is the exact class sum) were weak already. FC2-55's value now labels its ratios `tool_D_K4:` instead of `measured:`, because they are D-tool values, not measurements. Its MET windows [0.90, 1.00] and [1.03, 1.20] were set around those ratios. PF-T2-2 also printed FC2-29's exact Hankel rationals; that row is partly known, not weak (section 3.2). In FC2, only FC2-12, 13 and 14 remain blind.

**For the referee.** PF-T2-2 evaluated plaquette curves for every group, while the brief barred plaquette curves beyond the smallest cases. Whether that run went past the brief's smallest-case allowance is for the referee seat to decide. The referee records the answer and its reason (field `referee_question` of PF-T2-2).

**Weak spots, recorded in the rows:**
- The Dic6 10 % descent, interval [11.15, 11.30], where D and L both have errors of about 10⁻³.
- "2O never reaches 10 %", where the rising side is covered by D only.
- Peak locations, which have windows of about ±2 to 4 %.

**4D (FC2-60, REPORTED).** Petcher–Weingarten 1980 and Rebbi 1980 report first-order freezing transitions for the binary polyhedral groups in 4D. Bhanot–Rebbi PRD 24 (1981) concerns subgroups of SU(3). No 4D number is predicted. This row is not a blind test (code na). The referee scores it from the sources.

---

## 4. FC3: SU(2)_k (lane T3, checked)

**Conventions.** The simple objects are V_j for j = 0, ½, …, k/2. Fusion follows the triangle rule, the integrality rule and j₁ + j₂ + j₃ ≤ k [S7]. The quantum dimensions are d_j = [2j+1] = sin((2j+1)π/(k+2))/sin(π/(k+2)). Tensoring with V_½ moves one step along the path graph 0 … k (Lemma 1.2).

### 4.1 Part (a): the fingerprint law (FC3-01 to FC3-25)

- **A1.** M_n(k) counts walks from 0 back to 0 on the path graph P_k. It is zero for odd n, and M_(2m)(k) is the number of Dyck paths of height at most k.
- **A2.** M_(2m)(k) = C_m for m ≤ k, and M_(2k+2)(k) = C_(k+1) − 1. Also M_n(k) ≤ M_n(k+1) ≤ C_(n/2).
- **A3, reflection form.** M_n(k) = Σ_t [binom(n, n/2 + tK) − binom(n, n/2 + tK + 1)], with K = k+2.
- **A4, deficits.** For m ≤ 2k+2:

  | m | D_m |
  |---|---|
  | k+1 | 1 |
  | k+2 | 2k+2 |
  | k+3 | 2k² + 7k + 4 |
  | k+4 | 2(k+3)(k+4)(2k+1)/3 |
  | k+5 | N(N−1)(N²−13N+34)/24, with N = 2k+10 |

- **A5, spectral form.** M_n(k) = Σ_l w_l x_l^n, with x_l = 2cos(πl/K) and w_l = (2/K)sin²(πl/K). This is the (k+1)-point Gauss rule of the Haar trace law.
- **A6.** The generating function is P_k/P_(k+1).
- **A7.** The sequence obeys the recurrence with characteristic polynomial U_(k+1)(x/2).
- **A9.** For each spin j, the break comes at n = 2k+2−2j, again by exactly 1.
- **Table.** FC3-13 to FC3-24 give the table for k = 1..12 and n = 0..30. The sha256 of its canonical text is `3c8e7da5…c526c` (FC3-25).

*Checked by the assembly seat:*
- The proofs of A1 to A4, by reading them. The algebra of the D_(k+4) and D_(k+5) polynomials, by hand.
- Spot values of the table: k=4, M₁₈ = 4862 − 1581 = 3281; k=11, M₃₀ = C₁₅ − 3220; k=12, M₂₆ = 742899.
- The internal consistency of the table, in independent code (PF-A-2): odd entries zero, the Catalan prefix, the A3 break values, the A4 polynomials, the A7 recurrence, monotonicity in k, and the file hash.

All of these are checks of predictions against one another. None is a measurement. The k ≥ 3 lines come from the closed form only. Only k ≤ 2 was enumerated (PF-T3-1), so FC3-13 and FC3-14 are controls.

### 4.2 Part (b): design degree (FC3-26 to FC3-31)

- **B1.** t_fp(SU(2)_k) = 2k+1.
- **B2.** t_fp first exceeds the finite-subgroup ceiling of 11 at k = 6, where t_fp = 13 with 7 simple objects.
- **B3, Gauss optimality.** A law with N atoms has t_fp ≤ 2N−1. Equality holds only for ν_(N−1), and its first failing moment is short by exactly 1.
- **B4.** A finite G has t(G) ≤ 2N_G − 2, and t(G) ≤ 2N_G − 3 when −1 ∈ G. The identity is an atom at the endpoint of the trace interval, which costs one degree.
- **B5, the mirror at n = 12.** SU(2)_5 has M₁₂ = 131, Haar has 132 and 2I has 133. The 2D coefficients are ∓1/1961990553600.
- **B6.** The sign of the break is structural: SU(2)_k always falls short, and every finite group overshoots.

*Checked by the assembly seat:*
- The B3 proof.
- The Hankel determinants of the SU(2) trace moments are all 1 for N ≤ 13 (PF-A-2). This makes the falsifier of FC3-28 concrete.
- B4 against all ten FC2 groups and C₂, using the trace counts from `GROUPS.hbp`. For example, 2O has N = 7 and bound 11, against t = 7.

FC3-29 is a control, because the group data were computed before the freeze.

### 4.3 Part (c): the lattice caveat (FC3-32 to FC3-59)

**Construction C_k (FC3-00, a definition).** This is a generalized lattice gauge theory of Oeckl type [S9], on the spherical category SU(2)_k.

- The plaquette weight is W(β) = exp((β/2)[V_½]) = Σ_j a_j[V_j], with a_j = Σ_n (β/2)^n N_n(2j)/n!.
- Each link carries the normalized projector (coev∘ev/d_j for two strands), and each vertex is evaluated as a planar network.
- With Rep SU(2) in place of SU(2)_k, the construction is Wilson LGT.

The details are the lane's own: only Oeckl's abstract was read.

**C1, closed surfaces.** An unbranched closed surface S carrying label j contributes d_j^χ(S)·(a_j/(a₀d_j))^F(S). This is the pivot for every case-(ii) row.

**Case (i): only fusion multiplicities enter (FC3-33 to FC3-46).** This covers the 2D free boundary and the pillow.

- On the 2D free boundary, f_k − f_SU2 = −β^(2k+2)/(4^(k+1)(2k+2)!) + (2k²+5k+4)β^(2k+4)/(4^(k+2)(2k+4)!) + …. For k = 5 this is −1/1961990553600, the negative of the 2I value.
- On the pillow, Z = a₀(2β), so the difference is −β^(2k+2)/(2k+2)!.
- A formula analog exists for finite groups: Iconic's Transfer theorem [S6] gives ι/(2^(t+1)(t+1)!) per plaquette and ι/(t+1)! on the pillow. With t = 2k+1 and ι = −1 these become the two values above. No SU(2)_k value appears there. The su2-ladder values for 2O and 2I match FC3-36 and FC3-38 in magnitude, but they belong to different objects. FC3-33 and FC3-46 now say so in known_before_freeze.

**Case (ii): quantum dimensions enter.**

| complex | FC id | first order | coefficient |
|---|---|---|---|
| 1x2 torus | FC3-47 | β² for every k | tan²(π/(k+2))/16 |
| 2x2 torus | FC3-48 | β⁴ for every k | (sec⁴(π/(k+2)) − 1)/256 for k ≥ 2; 37/768 for k = 1 |
| open cube | FC3-49 | β⁶ for k ≥ 2; β⁴ for k = 1 | (sec⁴ − 1)/1024 for k ≥ 3; 43/15360 for k = 2; −1/64 for k = 1 |
| 3D lattice | FC3-50 | β⁶ for k ≥ 2; β⁴ for k = 1 | c₆ = (sec⁴ − 1)/3072 for k ≥ 3; 11/11520 for k = 2; −1/384 for k = 1 |
| 3D plaquette | FC3-52 | β⁵ (β³ for k = 1) | 6c₆; 11/1920; −1/96 |

**Blindness of case (ii) (refix seat).** PF-T3-1 printed the k = 1 and 2 values of FC3-47, 48, 49 and 50 before the freeze, and also FC3-52 (the β-derivative of FC3-50), FC3-53 (Ψ₆) and FC3-56 (the qKS λ⁴ coefficient). These seven rows are now partly known, blind only on k = 3..12, as FC3-33 and FC3-46 already were. A lint rule now rejects any row that lists PF-T3-1, has some k ≤ 2 in scope and is coded blind.

**A formula analog for the tori (refix seat, third round).** [FC2-S15] also gives the rule on a two-dimensional torus for a finite group, Z = Σ_ρ c_ρ^F d_ρ^(−F) with F = LT plaquettes (LEMMA-0004 line 183; line 321), with MEASURED values (PREDICTION-YM4-02c.hbp line 37): Q8 on 2x2 69425/16, Q8 on 3x2 16917185/64 and 2T on 2x2 1572881/648. FC3-47 and FC3-48 cite it in known_before_freeze. It gives no SU(2)_k value at k = 3..12, so both rows stay partial.

The first refix round kept FC3-32 (Lemma C1) and FC3-58 (the case labels) blind, on the ground that no pre-freeze run evaluated a state sum. That was not accurate. PF-T3-1 checked the pillow sum Z = Σ_j a_j² against a₀(2β) at k = 1 and 2 (`pillow_eq_a0_of_2beta_1`, `_2`), and it printed the first-difference powers at k = 1 and 2 for the 2D free boundary, the pillow, the 1x2 and 2x2 tori, the open cube and the 3D formula. FC3-32's verdict rule includes the pillow, and FC3-58's case labels at k = 1 and 2 can be read off those powers. The second refix round therefore recoded both rows to partial (prefreeze PF-T3-1, blind only on k = 3..12), as FC3-52 was. FC3-33 and FC3-46 now state their PF-T3-1 values first in known_before_freeze. A second lint rule now rejects any FC3 row with some k ≤ 2 in scope that is coded blind, unless PF-T3-1's row exempts it by name. Three rows are exempt, because PF-T3-1 did not evaluate their quantity at any k: FC3-54 (variant transport), FC3-55 (the weak-coupling limit) and FC3-57 (D = 4).

**The rest of part (c).**
- **Size for large k (FC3-51).** c₆ ≈ π²/(1536(k+2)²).
- **Weight-independent ratio (FC3-53).** Ψ₆ = d_½² = 4cos²(π/(k+2)), against 4 for SU(2). This holds for every weight with b_j/b₀ = O(β²) for all j ≥ 1. The row's quantity, verdict rules and falsifier now state this domain, and both weight choices must lie in it.
- **Variant transport (FC3-54).** Keeping SU(2)'s gluing eigenvalues gives a β⁶ coefficient of −sin²(π/(k+2))/3072.
- **Weak coupling (FC3-55).** a_j/a₀ → d_j as β → ∞.
- **Conjectures.** FC3-56: the Hamiltonian qKS model first differs at λ⁴. FC3-57: the D = 4 version.
- **OPEN.** FC3-59: theories outside the Oeckl class. Inside the class, agreement with SU(2) through order 2k+1 is impossible for every weight in the FC3-53 domain (b_j/b₀ = O(β²) for all j ≥ 1), because Ψ₆ ≠ 4 there. If b₁/b₀ ~ sβ, spin-1 surfaces enter at β⁶ and the argument does not apply. The fix seat added this domain to FC3-59's value.

*Checked by the assembly seat:*
- The C2 next-coefficient algebra: (k+2)(2k+3) − (2k+2) = 2k² + 5k + 4.
- The pillow identity Σ_j a_j² = a₀(2β).
- The 1x2 group integral. Each Y_i appears twice in one plaquette, which gives Σ_j a_j²/d_j². This is the case where Transfer 1's hypothesis H1 fails. It is fine here because the claim is about this specific complex.
- The 2x2 torus at k = 1: 15/256 − 4/384 = 37/768.
- The cube at k = 2: 3/1024 − 1/7680 = 43/15360.
- The 3D values at k = 1 and k = 2, including 59/11520.
- The cubes-per-plaquette ratio 1/3.
- The surd forms of c₆ for k = 3, 6, 8 and 10.
- The asymptotic expansion sec⁴x = 1 + 2x² + (7/3)x⁴.
- The C7 variant.
- The arithmetic of the C9 Rayleigh–Schrödinger terms, including the k = 1 value −16/81.
- All 12-digit decimals in FC3-47 to FC3-56, from 2cos(π/(k+2)) found by integer bisection on U_(k+1)(x/2) (PF-A-2).

*One correction (FC3-53).* The lane states Ψ₆ for "any plaquette weight". Its proof needs b_j/b₀ = O(β²) for j ≥ 1. That holds for every Wilson-like weight, because a_j/a₀ = O(β^(2j)). If b₁/b₀ ~ sβ, then spin-1 surfaces add d₁⁻⁴s⁶ and d₁⁻⁶s⁶ at β⁶, and the ratio is no longer d_½². The row now states this domain. The numbers are unchanged.

*Not checked:*
- Whether the Frobenius–Schur signs cancel in C1.
- The vertex-evaluation details of the state sum.
- The hypotheses H-c to H-e of the qKS conjecture.
- The 4D ribbon structure.

The C4 minimal-surface lemma was read and found coherent.

---

## 5. What the assembly seat did

1. **Read** all three NOTE.md and ROWS.hbp files in full (sha256 values are in the head row of the HBP).
2. **Fingerprints.** Every lane script and output fingerprint matches what the lane claimed. Every lane script was then re-run unchanged in `final/repro/`, and every output came out byte-identical (PF-A-1). A token scan of all 11 scripts (8 lane, 3 assembly) finds no float division, no float literal, and no use of math, fractions or decimal (PF-A-4).
3. **Arithmetic.** An integer-only re-derivation of every printed value that follows from a closed formula: 120 checks, 0 failed (PF-A-2, `arith_check.out`). It computes nothing on a torus, a group closure, a fusion iteration or a plaquette curve.
4. **Sources.** The local sources exist at the cited commits:
   - finite repo at 6a7fc747 (both docs) and cbd8b70d (#143);
   - iconic-3-space at pr7 (fb9990e5), file `TRANSFER-THEOREM.md`;
   - `predictions/su2-ladder/` on main.

   The assembly seat re-read #143's C1 blocks and the Transfer ladder table. After review, the fix seat opened the four finite-repo records of [S11] at 6a7fc747 (section 2.5).
5. **Assembly edits.** There are 19 in all, each marked in the row's `asm=` field:
   - 14 touch only a falsifier or a verdict rule: FC1-05, 08, 09, 12, 24, 34, 38, 39 and 41; FC3-28, 29, 54, 58 and 59;
   - 2 edit a value's notation or domain: FC3-12 and FC3-53;
   - 3 add a reachability flag: FC1-40, FC3-56 and FC3-57.

   The PREDICTION_END row gives the same split. In detail:
   - **Falsifiers made explicit:** FC1-05, 08, 09, 12, 24, 34, 38, 39 (lane text "as_not_met"), and FC3-29 and FC3-58.
   - **Self-referential falsifier replaced:** FC3-54.
   - **Verdict rule made concrete:** FC3-28, using the Hankel determinant test.
   - **Domain added:** FC3-53 (see 4.3).
   - **Notation fixed:** FC3-12 (C_(n/2)).
   - **Reachability flags added:** FC1-40, FC3-56 and FC3-57.
   - **OPEN rows set to UNSCORED:** FC1-41 and FC3-59.
   - **Construction row:** T3-C00 became the definition row FC3-00 and is not counted.

   No predicted value was changed.
6. **Lint** (PF-A-3):
   - every line ends in json=0, and every field is KEY=value;
   - ids are unique and sequential;
   - every PREDICT row has an id, src, scope, quantity, value, tag, blind code, prefreeze code, met_if, not_met_if and falsifier;
   - no falsifier is "as_not_met", "same" or "n/a";
   - OPEN rows are UNSCORED;
   - every pre-freeze reference is declared;
   - no MEASURED tag;
   - each value equals the lane text unless an asm field records the edit;
   - no third-person masculine pronoun anywhere in the file.

   The fix seat added these checks:
   - every value equals the lane text unless an asm or fix field records the edit;
   - every blind = 0 or partial row names what was known, in known_before_freeze or prefreeze;
   - every row that PF-T2-2 touches is weak;
   - S11 is cited only by FC1 rows.

   The refix seat added these checks:
   - a row that lists PF-T3-1 and has some k ≤ 2 in scope cannot be blind;
   - a row whose known_before_freeze names a finite-r record cannot be blind;
   - a row that states an exact pre-freeze value must be partial or a control (this is the only exemption from the PF-T2-2 rule);
   - every quantity equals the lane text unless a fix field records the edit.

   A mutation test on a temporary copy confirmed that the first, second and fourth checks fire.

   The refix seat's second round added these checks:
   - a row whose known_before_freeze names a pre-freeze run must list that run in prefreeze;
   - a SOURCE row may list the rows whose values it gives exactly (`gives_exact`), the rows for which it gives some instances (`gives_instances`), and the rows it only names (`names_only`). Every listed row must cite the source in known_before_freeze. A `gives_exact` row must be a control, and a `gives_instances` row cannot be blind, weak or na;
   - an FC3 row with some k ≤ 2 in scope cannot be blind unless PF-T3-1's row exempts it by name.

   A mutation test on a temporary copy (five rows broken on purpose) gave 6 lint errors, one per broken row and one row caught by two rules. Result: 196 lines, 0 errors.

   The refix seat's third round added one check: the head row must carry `search_rounds`, `search_cutoff` and `late_record_rule`. A mutation test on a temporary copy (FC2-12 and FC1-23 left uncoded, the FC1-S14 citation dropped from FC1-03, the rule field renamed) gave 4 lint errors, one per break. Result: 198 lines, 0 errors.
7. **Fix seat (after review).** These changes are recorded in each row's `fix=` field. 61 rows carry one. `CHANGES.txt` gives each change and its reason.
   - Source FC1-S11 added (section 2.5).
   - FC1 recoded: FC1-14, 15, 29 and 30 to controls; FC1-18, 23 and 28 to partial. known_before_freeze filled or extended on FC1-06, 10 to 15, 18, 23, 26 to 31, 33 to 36, and 41 (20 rows).
   - The 38 PF-T2-2 rows with blind = 1 recoded to weak. known_before_freeze filled on all 40 weak rows (section 3.3).
   - FC1-27: verdict rule moved to the exact series coefficient.
   - FC2-55: label `measured:` changed to `tool_D_K4:`.
   - FC3-59: the FC3-53 domain added to its value.
   - PF-T2-2 now carries the referee question. PF-T3-3, PF-A-3, PF-A-4 and PF-A-5 are marked as non-computational. PF-A-5 now keeps the assembly seat's final script and HBP, with their hashes.

   No predicted number was changed.
8. **Refix seat (after verify round 2).** The 18 findings of `FINDINGS-VERIFY-R2.json` were applied in `fc_assemble.py`; each changed row carries an `R3:` note in its fix field (27 rows; list in PREDICTION_END, `refix_round3_rows`). The previous package is kept unchanged in `final/superseded-r3-1/`.
   - Recoded to partial: FC3-47, 48, 49, 50, 52, 53, 56 (PF-T3-1 at k ≤ 2); FC1-16, 31 (2x5B); FC1-38 (S12); FC2-29 (exact pre-freeze rationals).
   - Sources: S11 gains labels zgap2R, 2x5B and rev55, and the sha256 of every file; new S12 (PR #154) and FC2-S13 (4D script).
   - Wording, no number changed: FC1-10 quantity (no double scale); FC1-40 verdict rule (referee only); FC2-28 Δ₁ notation; FC3-53 quantity and verdict rules (domain).
   - The head row defines na as "not a blind test", adds the finite-r and pre-freeze rules, and states that blind codes reflect the searches listed.
9. **Refix seat, second round (after verify round 3).** Nine findings were applied in `fc_assemble.py`; each changed row carries an `R4:` note in its fix field (32 rows; list in PREDICTION_END, `refix_round4_rows`). The previous package is kept unchanged in `final/superseded-r3-2/`.
   - Recoded to control: FC1-16, 17, 18, 20 and 21 (S13).
   - Recoded to partial: FC3-32 and FC3-58 (PF-T3-1 at k ≤ 2).
   - FC1-38 now lists PF-T1-1 in prefreeze, which its known_before_freeze already named.
   - Sources: new S13 (The-matrix-law-essentials) and FC2-S14 (Iconic MEASURE-LADDER.hbp). known_before_freeze extended on 13 partial FC1 rows, on FC1-13, 14, 15, 19 and 22, on FC2-12 to 15, and on FC3-33 and 46.
   - No predicted number, quantity, tag, scope or verdict rule was changed. FC2-29 was left as it was, with its referee question.
10. **Refix seat, third round (after verify round 4).** The seven items of `FINDINGS-VERIFY-R4.json` were applied in `fc_assemble.py`; each changed row carries an `R5:` note in its fix field (6 rows; list in PREDICTION_END, `refix_round5_rows`). The previous package is kept unchanged in `final/superseded-r3-3/`.
   - Recoded to control: FC2-12 ([FC2-S15]) and FC1-23 ([S13] decides its verdict rule on 2x3 to 2x6).
   - FC1-23's known_before_freeze corrected: [S13]'s L/r law holds on 2x3 to 2x6, not on 2x2.
   - Sources: new FC1-S14 (Finite-Universe-SU-N-solved) and FC2-S15 (the 4D YM4-02c records). known_before_freeze extended on FC1-01 and 03 ([FC1-S14]; codes and referee question unchanged) and on FC3-47 and 48 (a formula analog from [FC2-S15]; codes unchanged).
   - The head row records the four search rounds, the refs searched, the cutoff and the late-record rule (section 6.1). The NOTE writes the FC2 sources from S13 on with their full ids.
   - No predicted number, quantity, tag, scope or verdict rule was changed.

**"No value came from a measurement."** This holds in the following sense. Every value is either a derivation, or the output of a truncated asymptotic tool (CONJECTURE), or REPORTED. No row cites the finite repository's records as the source of its value; they appear only in known_before_freeze. Where a pre-freeze computation or an earlier record produced or confirmed a value, the row says so in its `blind`, `prefreeze` and `known_before_freeze` fields:
- the 2x2 torus;
- S3 at the level of the group;
- SU(2)_k for k ≤ 2;
- the exact group moments and trace classes of FC2(a);
- the PF-T2-2 tool values for FC2(b) and (c) (the weak rows), including the Z3 group side;
- earlier measurements in the finite repository's own records [S11], PR #154 [S12], The-matrix-law-essentials [S13] and Finite-Universe-SU-N-solved [FC1-S14], for the FC1 rows of section 2.5;
- the exact small-β series of Iconic's MEASURE-LADDER.hbp [FC2-S14], named in FC2-12 to 15;
- the character expansion proved and checked in the 4D repository [FC2-S15], for FC2-12, and its torus rule for finite groups, named in FC3-47 and 48;
- the exact Hankel rationals of FC2-29 (PF-T2-2, PF-A-2).

Those rows are controls, partly blind, or weak.

---

## 6. Blindness codes

| code | meaning | rows |
|---|---|---|
| 1 | nothing computed or reported before the freeze, among the searches listed, gives the measured value on any instance in scope | 34 |
| partial | some instances are known: the 2x2 torus via PF-T1-3, k ≤ 2 via PF-T3-1, the 3x4 torus via #143 [S2], tori covered by the finite repository's records [S11] or by The-matrix-law-essentials [S13] (one certified or trial-space finite-r record of a limit counts), the D(S3) S-matrix of PR #154 [S12], or an exact pre-freeze value (FC2-29) | 49 |
| 0 | control: the value was computed or reported before the freeze | 34 (FC1-13 to 21, 23, 29, 30, 33; FC2-01 to 12, 15, 16, 28, 58; FC3-13, 14, 29, 34, 35) |
| weak | an approximate pre-freeze evaluation of the measured quantity exists (the PF-T2-2 tools). A MET verdict checks the tool and its truncation | 40 (FC2-17 to 27, 30 to 57, 59) |
| na | not a blind test: the OPEN rows FC1-41 and FC3-59 are UNSCORED; the REPORTED literature row FC2-60 is scored by the referee from its sources | 3 (FC1-41, FC2-60, FC3-59) |

By test:
- FC1: 5 blind (FC1-22, 32, 37, 39, 40), 22 partial, 13 controls, 1 na.
- FC2: 2 blind (FC2-13 and 14), 1 partial (FC2-29), 16 controls, 40 weak, 1 na.
- FC3: 27 blind, 26 partial, 5 controls, 1 na.

Only the 34 blind rows are blind tests in the strict sense. The assembled file counted 96. The fix seat moved 45 rows (96 → 51): 4 FC1 rows became controls, 3 FC1 rows became partial, and 38 FC2 rows became weak. The refix seat moved 11 more (51 → 40), all to partial: FC1-16, 31 and 38; FC2-29; FC3-47, 48, 49, 50, 52, 53 and 56. Its second round moved 5 more out of blind (40 → 35): FC1-17, 20 and 21 to controls, and FC3-32 and 58 to partial. It also moved FC1-16 and 18 from partial to controls. Its third round moved FC2-12 from blind to control (35 → 34) and FC1-23 from partial to control. These codes state what the searches listed in section 6.1 found. The finite repository holds many earlier records, so they are not a guarantee.

Controls are run first. They validate the measuring code before any blind row is opened (section 7.4, step 2).

### 6.1 Searches and their cutoff

Four search rounds looked for earlier records of the row values:
1. **The review after assembly** (2026-11-09): the finite repository's result records at 6a7fc747. It found [S11].
2. **Verify round 2** (`fc-tests/verify-hunter`; refs read with `git ls-remote` at 2026-11-09T21:57Z): the finite repository (main 6a7fc747, 324 refs), Iconic-3-space (main 5886d99, 23 refs) and the 4D repository (main 830fd3fd, 92 refs), with clones of The-matrix-law-essentials and the qnn repository. It found the S11 labels zgap2R, 2x5B and rev55, [S12] and [FC2-S13].
3. **Verify round 3** (`fc-tests/verify-hunter3-1`; refs at 2026-11-10T00:35Z): the same three, The-matrix-law-essentials (main e9eb988, 22 refs) and the qnn repository (main 98ef58a, 48 refs). It found [S13] and [FC2-S14].
4. **Verify round 4** (`fc-tests/verify-hunter3-2`; refs at 2026-11-10T01:04Z, unchanged except one qnn WIP branch): mirror clones of those five, of Finite-Universe-SU-N-solved (main e6d36326, 54 refs) and of continuum-Clay-variation (main 7cba1987, 10 refs), with every object read, unreachable ones included; also the local finite, 4D, qnn, finite-reversible and analysis-of-cubes repositories. It found [FC1-S14] and [FC2-S15].

**Cutoff: 2026-11-10T11:30Z.** The last search read refs as of 2026-11-10T01:04Z. The refix seat compared them with `git ls-remote` at 2026-11-10T14:35Z (`refix-r4/out/lsremote-*.txt`) and did not search what had moved or appeared: the 4D main moved from 830fd3fd to 2616622d (commits of 2026-11-10 13:04Z to 14:05Z; the [FC2-S15] files are unchanged there), the 4D branch of PR #47 (tip 13:50Z), two global-lock branches of the finite repository (PRs #158 and #159, tips 12:23Z and 13:06Z), and the qnn PR #18 head bfd93f4 (02:27Z, before the cutoff). None of these was searched.

**Rule.** A previously established result found later, after the freeze or in a ref the searches did not cover, reclassifies the affected row as a control (blind = 0). It never changes the row's prediction: value, quantity, tag, scope, met_if, not_met_if and falsifier stay as frozen. The head row states the same rule (`late_record_rule`).

---

## 7. Measurement plan (after the freeze)

**Freeze.**
- The parent session records the sha256 of the HBP file and of this note before any measurement script runs.
- Every measurement script prints the sha256 of the frozen HBP and its own sha256 in its first output line.
- Measurement results are written as `MEASURE|id=FCx-yy|value=…|method=…|script_sha256_16=…|json=0`.

**Rules for every engine.**
- Integer only: python3 -I -B, with no float, fractions, decimal or math. Rationals are integer pairs, normalized by gcd. Algebraic numbers live in an integer coefficient ring modulo a minimal polynomial. Real functions are computed in fixed point with an explicit error bound.
- Engines are written independently of the lane scripts and do not import them.
- Each engine runs as a single process, at most 10 minutes per job and at most 2.5 GB of memory per process (the machine has about 3 GB). The 4 cores are shared with five other jobs.

**Verdicts.** `fc_verdict.py` (integer-only) reads the frozen HBP and the MEASURE rows and applies each row's met_if / not_met_if mechanically:
- exact equality for counting rows;
- interval membership for intervals;
- the FC1-00 protocol for limits.

It writes MET, NOT_MET or NOT_RUN. OPEN rows get UNSCORED. The literature row FC2-60, the operator-level part of FC1-38, FC1-40 (no mechanical tolerance) and rows that need judgement go to the referee seat, which records its reasons.

### 7.1 FC1 engine (`fc1_s3_series`): all ten tori

1. **Orbit machinery.** Canonicalize each configuration under gauge transformations: gauge-fix a spanning tree to e, then take the lexicographic minimum over the 6 global conjugations. The orbit size is 6^(V−1)·|G|/|Stab|. The count-form transition matrix between orbits composes along walks, because it does not depend on the representative chosen.
2. **Part (a).** Count flat orbits with a column transfer matrix in exact integers. Check the total of flat configurations, 18·6^(V−1). On 2x2 and 2x3, also count by brute force in tree gauge, as an independent check. Check the first-shell M distribution and the minimum nonflat M with a breadth-first search to depth 1 from all 8 flat orbits.
3. **Part (b), exact Schur series.**
   - Run a breadth-first search over orbits from the 8 flat orbits to depth ⌈Lmin/2⌉. Meet in the middle, using the detailed-balance reverse counts w_a·c(a→b) = w_b·c(b→a).
   - Build every walk sum through order r^-(Lmin−1) as an exact rational, including the ε-insertion terms, and solve the Schur equation order by order.
   - Report the coefficient matrices in count form. Report the scalar parts through r^-(Lmin−2) and the matrix C at r^-(Lmin−1).
   - Compute exact characteristic polynomials by Faddeev–LeVerrier or Bareiss. Algebraic predictions such as √14 − √6 are compared through polynomial identities, not decimals.
   - The heaviest jobs are 4x4 and 4x5: about 120² ≈ 1.4·10⁴ middle orbits per side.
4. **Part (c).**
   - Build the M = 3 orbit manifold with its labels TT, TC and CT.
   - Compute the exact second-order K from walks of 1 move out and 1 move back.
   - Lmin ≥ 3: check that the top eigenvalue 3LxLy/2 + 21 has multiplicity exactly 3, by rank deficiency of K − λI in integer elimination.
   - 2x2: check that 2(x−27)² − 289 divides the characteristic polynomial of the zero-momentum block.
   - Find E12 − E9 from the momentum blocks.
   - FC1-39 needs walks of Lmin moves from the M = 3 manifold; this is the same machinery.
5. **Optional.** Certify finite-r values at r = 10⁴ and 10⁵ on 2x2 only, by Sylvester inertia counts of H − λI with sparse fraction-free LDLᵀ. FC1-40 (2xL with L ≈ 10 to 40) is out of reach for exact methods. It stays NOT_RUN unless a non-perturbative method with certified error is built.
6. **Refuter checks.**
   - A second implementation recomputes C on 3x3 and 3x4, in another language or with another gauge-fixing tree.
   - Every computed matrix satisfies detailed balance, and C is traceless with a symmetric spectrum.
   - Swapping Lx and Ly swaps Γ_V and Γ_H.
   - Before any blind torus is opened, the engine reproduces the FC1 controls (FC1-13 to 21, 23, 29, 30 and 33) and the known part of FC1-28. That means #143's C1 on 3x4, and zgap2's c_L and flat operator [S11]. Section 7.4, step 2, gives the full list.
7. **Planted faults.** The refuter seat plants these in a copy of the engine, without telling the measurer. The verdict engine must flag at least the rows listed. Any further NOT_MET must follow from the fault, and a null fault must change nothing.

   | fault | rows that must turn NOT_MET |
   |---|---|
   | (i) moves by all non-identity elements instead of transpositions | FC1-05 and the gap rows |
   | (ii) one plaquette dropped from M | FC1-01, 03 |
   | (iii) one link mis-oriented in one plaquette | the flat-sector rows |
   | (iv) the verdict engine uses order Lmin instead of Lmin − 1 | FC1-06 on every torus |
   | (v) class labels F2 and F4 swapped in the output | FC1-08 and 09 (count form), while the spectral rows stay MET; this tests that count-form entries are really compared |
   | (vi) null fault: a different spanning tree for the gauge fixing, or the site labels translated by one lattice step | none |

### 7.2 FC2 engine (`fc2_plaquette`): the ten groups (plus C₂ for FC3-29)

1. **Groups.** Rebuild each group from generators as 2x2 matrices over Z[ζ_n], with a representation different from T2's quaternions. Take exact class traces, and moments M_n for n ≤ 42 by direct averaging. Rows FC2-01 to 11, 15, 16, 28 and 58 are controls. The 40 weak rows check the PF-T2-2 tools (section 3.3).
2. **Exact P_G.** Write P_G = Σ c·e^(−β(1−c)) / Σ e^(−β(1−c)). Here c is computed with integer square roots at 10⁻¹⁰⁰, and e^x by halving plus Taylor, in fixed point.
3. **Exact P_SU2.** Write I₂/I₁ as the ratio of the ascending series Σ (β/2)^(2k+ν)/(k!(k+ν)!), scaled by e^(−β), at 10⁻¹²⁰; that is about 300 terms at β = 200. Cross-check with Miller backward recurrence (the continued fraction for I_(ν+1)/I_ν), and require agreement to 10⁻⁴⁰. The engine must not use Debye or Hankel.
4. **Derivatives.** dP_G/dβ is the Gibbs variance of c. dP_SU2/dβ = 1 − 3P_SU2/β − P_SU2², which is exact.
5. **Crossings and peaks.**
   - Crossings by bisection on rational β, to 10⁻⁹.
   - Maxima by bisection on the sign of dδ/dβ.
   - For unimodality, count sign changes on a grid of step 0.05 up to β = 200, then refine every change.
   - The law rows (FC2-25 to 27, 55, 56) are computed from the measured β_x and peaks.
6. **Refuter checks.**
   - The character identity at β ∈ {1, 5, 20}, against the measured z_G, with d_n from the group.
   - The Taylor coefficients at β = 0 equal the moments.
   - P_G > P_SU2 and P_G < 1 at every grid point.
   - Rebuilding each group from different generators gives the same class traces.
7. **Planted faults.**

   | fault | rows that must turn NOT_MET |
   |---|---|
   | (i) action β·tr instead of β·tr/2 | every interval row |
   | (ii) Dic4 and Dic6 swapped | FC2-24, 37, 38, 50, 51 |
   | (iii) deviation defined as (P_G − P_SU2)/P_G | crossing rows |
   | (iv) P_SU2 replaced by a 3-term Hankel truncation | refuter check 6 must fail first |
   | (v) null fault: the group order of summation permuted | none |

### 7.3 FC3 engine (`fc3_su2k`): k = 1..12 (plus 13..20 for the trend in FC3-51)

1. **Part (a).**
   - Implement the full level-k fusion rule from [S7] (triangle, integrality, j₁+j₂+j₃ ≤ k), not the path-graph lemma, and iterate V_½^⊗n for n ≤ 30.
   - As a second method, count height-bounded Dyck paths with a memoized recursion in a separate code path.
   - Write the canonical table text and compare its sha256 with FC3-25. A mismatch is resolved line by line against FC3-13 to FC3-24.
   - Then check every spin j (FC3-11).
2. **Part (b).** Take t_fp from the table. Compute the Hankel determinants of the SU(2) moments for N ≤ 13. Take t(G) and N_G from the FC2 engine.
3. **Part (c), state sums.**
   - Implement SU(2)_k with q-6j symbols from the q-Racah formula, in exact arithmetic over Q(2cos(π/(k+2))). Use isotopy-normalized symbols, so that no square roots are needed.
   - Evaluate the complexes directly, by link projectors and vertex networks, **without using Lemma C1**: the open 3x3 disk, the pillow, the 1x2, 2x2 and 2x3 tori, and the open cube.
   - Because a_j = O(β^(2j)), only label sets with Σ_p 2j_p ≤ 12 contribute through β¹².
   - Ψ₆ (FC3-53) is computed with two weights: the C_k weight, and a random rational weight with b_j/b₀ = O(β^(2j)).
   - Rep SU(2) is the baseline, cross-checked by an independent group-integral character expansion with exact Bessel-series coefficients.
4. **3D series to β⁷.**
   - Enumerate directly, around a root plaquette in a 4x4x4 box, only the plaquette sets of size ≤ 7 that pass the necessary test (every link has 0 or at least 2 nontrivial plaquettes): grow a set only by plaquettes that close an open link. Do not list every connected set first; rooted plaquette animals of size 7 can number 10⁶ to 10⁷, which is too many for pure Python in the job limits.
   - Evaluate the sets that pass.
   - Combine by the polymer expansion. Through β⁷ only single polymers contribute.
5. **qKS, FC3-56.** Build the Zache et al. point-split plaquette operator on two clusters: one plaquette, and two plaquettes sharing an original link. Run exact Rayleigh–Schrödinger perturbation theory to λ⁴, and combine by linked clusters. Test hypotheses H-c to H-e directly. **D = 4 (FC3-57)** is attempted only if a ribbon evaluation exists; otherwise it stays NOT_RUN.
6. **Refuter checks.**
   - As k → 20 the table approaches the Catalan numbers.
   - Rerunning with loop value −[2] (the Kauffman convention) changes no prediction, since χ − F is even.
   - Two different F-symbol gauges give the same evaluations.
   - The baseline reproduces Wilson LGT.
7. **Planted faults.**

   | fault | rows that must turn NOT_MET |
   |---|---|
   | (i) untruncated fusion at k = 5 | FC3-03, 17, 26, 30 |
   | (ii) [2] replaced by 2 in the cube | FC3-49, 50, 52 for k ≥ 2 |
   | (iii) M₁₄(5) = 418 in one table line | FC3-05, 17, 25 (and, through the same entry, the recurrence rows FC3-09 and FC3-10) |
   | (iv) quantum integers computed with π/(k+1) | FC3-47 |
   | (v) null fault: an F-symbol gauge change | none |

### 7.4 Order of work

1. Freeze the files.
2. Run the controls, which are all 34 rows with blind = 0:
   - FC1-13 to 21, 23, 29, 30 and 33;
   - FC2-01 to 12, 15, 16, 28 and 58;
   - FC3-13, 14, 29, 34 and 35.

   For FC1, the engine must reproduce these exactly before any blind torus is opened:
   - #143's C1 on 3x4 (FC1-19);
   - zgap2's c_L [S11]: 36.762472… on 2x2, 69/2 on 2x3 and 73/2 on 2x4 (FC1-33, 29 and 30), and 21 on 3x3, 3x4 and 4x4 (the known part of FC1-28);
   - zgap2's flat second-order operator: lowest splitting √14 − √6 on 2x2, 3 on 2x3 and 4 on 2x4 (FC1-13, 14 and 15), and exactly scalar on 3x3;
   - the exact limits of The-matrix-law-essentials [S13]: 5 and 6 on 2x5 and 2x6 (FC1-16, 17), (9/8)(√14 − √6) on 3x3 (FC1-18), 15/4 on 3x5 (FC1-20) and (5/4)(√14 − √6) on 4x4 (FC1-21);
   - FC1-23: the same 2xL limits, 3, 4, 5 and 6 on 2x3 to 2x6, divided by L.

   It must also agree with the certified 2xL intervals for E2 − E1 and E9 − E8, on 2x2, 2x3, 2x4 and 3x3 at r = 9 to 243. A certified finite-r value from the engine must overlap the recorded interval at the same r. A series value is compared with an interval only together with a bound on its truncation error. zgap2 itself records why: on 2x2, the second-order c_L lies outside the r = 243 interval, because that interval contains the third-order term. Where no rigorous truncation bound and no certified finite-r value from the engine exists (section 7.1 plans certification only on 2x2), the interval comparison is NOT_RUN and does not block this step.
3. Run the planted-fault rounds on the controls.
4. FC3 part (a). It is cheap.
5. FC2. Minutes per group.
6. FC1 parts (a) and (c), then part (b) torus by torus, from 2x2 up to 4x5.
7. FC3 part (c).
8. Run the verdict engine.
9. The refuter seat reviews every NOT_MET, and every row that needed judgement.

---

## 8. Pre-freeze computations (also listed as PREFREEZE rows)

| id | script | sha256-16 | output sha256-16 | scope |
|---|---|---|---|---|
| PF-T1-1 | T1/s3_gamma.py | 575fc383e31edaad | bf45f5047301df10 | S3 at the level of the group; no torus |
| PF-T1-2 | T1/cycle_orderings.py | 7fb2f6306ea736ae | b4a5bc2b2f8fb81f | N_m on the cycle C_m; no torus, no group |
| PF-T1-3 | T1/torus2x2_second_order.py | 52613e3e3f4cee5e | 19fe91c186250ef7 | 2x2 torus only; path sums; nothing diagonalized |
| PF-T2-1 | T2/prefreeze/t2_groups.py | ae3a722e77b7e4b6 | 101da05eeeeda698 | exact closure of the 10 groups, their moments and trace classes |
| PF-T2-2 | T2/prefreeze/t2_asym.py | 0f81d575be9c246a | 3a0533ad62a3358f | truncated tools S, D and L; Z3's group side exact. Every tool row it touches is weak; it also printed FC2-29's exact Hankel rationals (partial). Whether it went past the brief's smallest-case allowance is for the referee to decide |
| PF-T2-3 | superseded runs of t2_asym.py | fe60126fd161300c, 901f3dc3bef21067 | overwritten | same tools |
| PF-T2-0 | none (mental arithmetic while planning) | – | – | no row value comes from it |
| PF-T3-1 | T3/t3_small_checks.py | e7e1fb839db6f61f | 8c7a22012024b94e | the only fusion enumeration: k ≤ 2. Its row names the three FC3 rows with k ≤ 2 in scope that it does not touch (FC3-54, 55, 57) |
| PF-T3-2 | T3/t3_closed_forms.py | efe9a44a9e9dc34b | 08ad75df28761589 | closed form A3 for k = 1..12; writes T3_TABLE.txt (3c8e7da5564a106b) |
| PF-T3-3 | T3/t3_rowlint.py | 835a9375c1dbc94b | stdout only | format lint only; computes no row value; first written one directory up and moved within seconds |
| PF-A-1 | unchanged copies of the 7 lane computation scripts, in final/repro | identical | all byte-identical | reproduction only |
| PF-A-2 | final/fc_arith_check.py | 175ada64e2836416 | 52eeac71afe1ea50 | arithmetic of the derived formulas; 120 checks, 0 failed. Touches FC2-29, whose value is its Hankel rationals; for every other row it re-derives printed values |
| PF-A-3 | final/fc_assemble.py (edited by the fix seat and three times by the refix seat) | b94f58e92f9f8d8b | the HBP, 84adf9652ef9c14b | assembly and lint only; computes no row value |
| PF-A-4 | final/fc_float_scan.py | 22aad868055e922b | a6e19f21911b2734 | token scan of all 11 scripts; 0 hits; lint only, computes no row value. The fix seat re-ran it on the edited assembler, and the refix seat re-ran it after each of its three rounds; every output is byte-identical. Two earlier inline versions of the same scan were run; their text was not kept, so they have no fingerprint, and they computed no row value |
| PF-A-5 | superseded runs of fc_assemble.py: (i) two development runs; (ii) the assembly seat's final version, kept in final/superseded/ | (i) not retained; (ii) ed8d3e0a36531ebc | (i) one crashed before writing, one file was overwritten; (ii) the HBP before the fix seat, 03c8f4c8512318ac, kept in final/superseded/ | assembly and lint only; computes no row value. (iii) Four fix-seat development runs of the edited script, overwritten: scripts 838ffe93f207f4cf, 94b50edcf368c524, d50897a18d5f5794 and de8d7914b29c09af; HBPs 0d6e84f12a69af26, c074579f2b7ce129, 8409391fea0a6f1e and 43db4f3141d120a1. The second and third failed lint, because a dropped space merged two row ids. (iv) The fix seat's final version, script 9e3ce327c711d67e and HBP 7d362f51c4ea1483, kept in final/superseded-r3-1/. (v) Refix-seat runs: two development runs (scripts 3135c7d129327499 and cd2883d376aaa2cb, HBPs b3ef666c0c36e712 and 7da7d6ac48024283, 0 lint errors, overwritten) and one lint mutation test on a temporary copy (deleted, not retained). (vi) The refix seat's first-round final version, script 87f4ef575f2d6567 and HBP 2c0f15dd0f35dbcd, kept in final/superseded-r3-2/. (vii) Second-round runs: one development run in a mirror tree (refix-r3-2/mirror; script d59cf0d757d405f1, HBP d889e3e8f7e4ac08, 0 lint errors, overwritten) and one lint mutation test on a temporary copy (6 errors as expected; deleted). (viii) The refix seat's second-round final version, script 23ada67196ef59da and HBP d36ff8e31e1a81b0, kept in final/superseded-r3-3/. (ix) Third-round runs in a mirror tree (refix-r4/mirror): two development runs (scripts 9f75f76bcafbdf5a and d71f0b9e821d446b, HBPs df09836adfbf439c and 6bb69063be6a0d98, 0 lint errors, overwritten) and one lint mutation test on a temporary copy (4 errors as expected; copy deleted, output refix-r4/out/mut.out 34841b0319b8ac53) |
| PF-A-0 | none (plausibility arithmetic by hand) | – | – | gap-term estimates for three FC2 descents; Γ spectra by hand; no row changed |

All scripts sit under `/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/fc-tests/`. All ran as python3 -I -B with integers only. No repository was written, and nothing was posted to GitHub.

---

## 9. Risks (lanes and assembly, combined)

1. **FC1 tolerance.** The verdict tolerance (5·10⁻³ at r = 10⁵) assumes next-order corrections of at most about 100/r. On 4x5 they may be larger, so exact series coefficients take precedence there.
2. **FC1 thin tori.** The 2xL coefficient −(4L+57)/2 rests on α and β counts and row-pair counts that were computed only on 2x2. zgap2 [S11] prints the same values for L = 3 and 4. Both terms are linear in L, so these two controls fix L = 5 and 6 if the process structure is as the lane describes; that structure is the residual risk.
3. **FC1 conventions and sectors.**
   - If a measurer writes 2xL with the long side first, Γ_V and Γ_H swap in count form. Spectra are unaffected.
   - A computation restricted to a symmetry sector sees a different "E2" (FC1-24).
4. **FC1 uniformity.** The 1/r expansions are not uniform in torus size. On 2xL they become unreliable once L is of order r².
5. **FC2 definitions.** Every FC2 interval depends on the definitions in FC2-00: the action β·tr/2, and δ measured relative to P_SU2.
6. **FC2 tools.** The numbers come from asymptotic tools. Near β ≈ 3–4 the SU(2) side has no rigorous Hankel bound (DLMF 10.40(ii) bounds only K_ν).
7. **FC2 weakest rows.** Dic6 at 10 %, and the "never" for 2O.
8. **FC3 independence.** The FC3 table was produced by the same reflection formula that a lazy measurement would use. The measurement must iterate the fusion rule.
9. **FC3 construction.** Part (c) rests on the lane's own definition of C_k. A measurer who normalizes links, vertices or the weight transport differently will land on FC3-54 or somewhere else. Ψ₆ does not depend on the transport, within its stated domain.
10. **FC3 lattice size.** The 3D rows need L ≥ 7 (a conservative condition) or the series limit.
11. **FC3 conjectures.** The qKS and D = 4 rows are conjectures that rest on unverified hypotheses. The qKS paper was read only through a fetch tool's extraction of the HTML.
12. **Sources recalled, not opened.** Lane T1 recalled the D(S3) S-matrix in FC1-38 from memory. A measured one was already in PR #154 [S12], which the refix seat opened; FC1-38 is now partly known. Klein's Molien degrees are standard, and were used as a check only.
13. **Review.** No second reader has gone through the lane proofs in full. The assembly seat checked the steps listed under "checked" and read the rest. A review after assembly found the blindness problems fixed here (sections 2.5 and 3.3).
14. **Other prior records.** The lanes did not search the finite repository's result records, and the review found four of them [S11]. Other records there may hold further FC1 values. A second verify round found three more (zgap2's RESULT.hbp, the 2x5 stage-B certificate, the review-opus55 outputs) and PR #154 [S12]. A third found The-matrix-law-essentials [S13], a separate repository that none of the earlier searches covered, and Iconic's MEASURE-LADDER.hbp [FC2-S14]. A fourth found Finite-Universe-SU-N-solved [FC1-S14] and the 4D repository's YM4-02c records [FC2-S15]; section 6.1 lists the four rounds, the refs searched and the cutoff, 2026-11-10T11:30Z. The finite repository holds many earlier records, so the blind codes state what these searches found, not a guarantee. Before scoring any FC1 blind row, the referee seat should search `native/ym/results/`, `independent/`, open pull-request branches and the owner's other repositories (The-matrix-law-essentials included) for E2 − E1, E9 − E8, E9, E12 and c_L on the torus concerned. It should recode any row whose value it finds there by the rule of section 6.1: to a control, with the prediction unchanged.
15. **FC2 is mostly a tool check.** 40 of the 60 FC2 rows are weak. Their MET verdicts test the PF-T2-2 tools. Only FC2-13 and 14 are blind tests of the mathematics, and an exact small-β series of the same functions was already recorded [FC2-S14]; FC2-12 is a control ([FC2-S15]), and FC2-29 is partly known.
