# #137 — consolidated independent original finite Wilson proof-chain review

**Date:** 2026-11-20  
**Scope:** original 3×4 periodic finite S₃ gauge-orbit Hilbert space at (r=J_B/J_E=9), original seven-loop summed-winding Wilson observable, full W-weighted physical states, and true (E_1\to E_2) transition.  
**Disposition:** **WHOLE-Q PERRON LIFT — MATHEMATICAL PASS; JOINED FINITE WILSON TRANSFER — EXACT, SOURCE-CONDITIONAL PASS; FINAL ORIGINAL WILSON THEOREM — FORMAL HOLD; FOUR-DIMENSIONAL CONTINUUM — OPEN.**

This is an independently written mathematical dependency review across the source-preserving accepted components. It is neither a third 45.5-million-row production replay nor a claim that pending source-conditional research-draft acceptance obligations have been closed. The original physical Hamiltonian, immutable source archives, hashes, and historical statuses are unchanged.

## One operator, one metric, one observable

1. **Original complete physical operator:** [merged #341](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/341), [hosted #44789976047](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44789976047). Gauge fixed 13 links, residual conjugation, 8 flat gauge orbits, (W_P=\operatorname{diag}(1,3,2,3,3,2,2,2)), 576 flat outgoing electric moves, 264 distinct nonflat boundary orbits, full weighted adjoint (w_xc_{xy}=w_yc_{yx}), (H_{PP}=72I_8), and the complete-Q coupling (B^*B=72I_8). These are the same P/Q and W used below.

2. **Original Wilson operator:** #341 independently reconstructs the seven-loop gauge-invariant diagonal character sum with (O_P=\operatorname{diag}(14,8,5,6,0,2,-7,-7)), (O_9=2O-16I) globally, and (P O Q=Q O P=0). Since the true (E_1\ne E_2) states are W-orthogonal, the (O) transition amplitude equals half the (O_9) transition amplitude. Squared weight consequently receives exactly a factor (1/4), *after normalizing the entire P+Q states*.

3. **Original Perron physical data:** [merged #332](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/332), [composite hosted #44782915318](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44782915318): all 45,508,080 symmetry-sector physical rows independently reconstructed; zero key, weight, magnetic or sparse-entry mismatches; Merkle PASS. All 34 frozen source files authenticated across source jobs, including full sector 374 SHA and exact matched 474,451,863-byte consumed prefix. This remains accurately labeled *composite* source acceptance.

## Exact Perron-to-whole-Q lift: mathematical sign-off

The sector store comprises **45,508,080 total rows with seven flats**. The published (x3-c.bin) witness is zero at these seven flat rows and **strictly positive on 45,508,073 nonflat rows**, with original SHA-256 `f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1`. The complete physical space comprises 2,177,317,873 orbits and eight flats, hence exactly **2,177,317,865 Q states**. The comparison acts on the *nonflat principal compression*, retaining original diagonals while discarding flat columns.

The symmetry group preserves Q and commutes with the full physical Hamiltonian. If (q(x)) is the symmetry orbit of a complete nonflat physical gauge orbit x, (d(x)=d_+(q(x))>0) lifts the **positive nonflat** sector witness. Exact symmetry-equivariant row sums yield ((QHQ,d)(x)=(D_+d_+)(q(x))), pointwise in **every** symmetry sector's underlying states.

For (f_x=d_xu_x), detailed balance and the offdiagonal Z-matrix sign give
[
\langle f,(D-tI)f\rangle_W
=\sum_x w_xd_x[(D-tI)d]_x|u_x|^2+
\frac12\sum_{x\ne y}w_xc_{xy}d_xd_y|u_x-u_y|^2\ge0.
]
This proves (QHQ\succeq tI) on **all** physical nonflat Q states once the independently authenticated original strict comparison rows are accepted. The original exact row minimum is (t=94.070673J_E); the Wilson calculation uses the smaller (γ=94.068200J_E), with exact slack **0.002473 (J_E)**. No reverse interlacing or irreducibility assumption is needed.

The refreshed [PR #345](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/345), [hosted #44822093830](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44822093830) independently checks the weighted ground-state identity and an explicit one-flat/three-nonflat boundary. Its exact example has an invalid *uncompressed* flat-row comparison ((Hd)_{\rm flat}=-10) but a valid *compressed* Q comparison ((D-4I)d=(0,1,1)\ge0). Dedicated proof, optimized Python, integer checks, Rust native gauge and both no-floating-point workflows passed on reviewed head `49842447b7414bb7453d747bbd4e5d720961a69c`.

## Original source-to-Schur and signed matrix theorem

4. **Exact physical source identity:** [merged #343](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/343), [hosted #44792292108](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44792292108): with (b=10^9), trial scale (σ=10^{12}), (X=bQHQ-zI), (R=bBσ+XY), (T=(σI,Y)), (μ_k=R^TW_QX^kR), the **same physical weighted Schur** satisfies (S=U_0-R^TW_QX^{-1}R) for any trial Y, (U_0=T^*_W(bH-zI)T). Original archived Gram scaling is (G_0=6μ_0). This resolves the sixfold source normalization without changing the underlying physical metric.

5. **Original full signed source matrices:** independent K3/Q4/Q5 first-principles source generators [merged #331](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/331) and [merged #335](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/335) matched all **331,818,176** archived two-energy components; [hosted signed μ3 #44581486671](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44581486671) independently reproduced **128/128** third-moment entries across the two original energies. [Draft #317](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/317) independently reconstructs both 16×16 signed localizers and the full 8×8 Gauss/Lobatto Schur arithmetic; [draft #328](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/328) preserves independently executed physical signed third-moment source review. Their drafts remain separately scoped evidence and are **not** silently treated as merged formal source acceptance.

6. **Exact matrix-to-energy logic:** [merged #338](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/338) proves full-matrix Loewner Gauss/Lobatto resolvent bounds from moments (μ_0,ldots,μ_3), exact localizer positivity and (0<gI\preceq X\preceq hI). No commutation of the eight moment matrices is assumed. The accepted original upper support uses (H\preceq468J_E) (electric ≤144 and magnetic ≤324 at r=9); the lower original entire-Q support uses the Perron floor just proved. The Schur inertia and projector inference uses this *same* W-weighted H and eight-flat P.

## True E1/E2 Wilson transition: exact conditional arithmetic

7. **True-energy projectors and same-Q source-correlated Wilson action:** original hosted [#44560968064](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44560968064), archived evidence replay in [draft #319](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/319), physical forward/adjoint source in [draft #315](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/315), and independent exact transfer [merged #337](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/337). The original endpoint inertia jumps are 0→1 and 1→2; original true-projector angle ceilings are **2,034,354,058** and **4,260,581,813 per (10^{12})**.

8. **Independent exact rational cross-check:** the archived source-correlated action provides a conservative positive signal numerator (62,163,774,481), two action error ceilings (25,196,361,952) and (27,389,725,641), and mixed error (292,156,800), all per (10^{12}). Independent integer subtraction yields
[
62,163,774,481-25,196,361,952-27,389,725,641-292,156,800
=9,285,530,088>0.
]
The original full-state normalization bounds are (1+72/(γ-E_i)^2) for each state. Applying both full-state factors and the exact (1/4) Wilson conversion reproduces the **source-conditional strict original squared spectral-weight lower candidate (17,074,763/10^{12}>0)**, rational SHA `7a8255cfb82207653ef3050b1efba0cedda61a309c3084e6a8a50b42deb7abf0`. The derived quantity is for the genuine full-space (E_1\to E_2) transition *if every upstream physical interval/action premise holds*, not merely a Ritz-vector overlap.

## Acceptance gates and remaining work

**Accepted in this review:** original full-space physical W operator and P/Q identity (#341), independent authenticated physical Perron store and composite source integrity (#332), exact mathematical quotient-to-whole-Q Perron lift (#345), original weighted source-to-Schur algebra and (G_0/6) (#343), full-matrix abstract signed Loewner/localizer theorem (#338), and conditional exact normalized Wilson transfer (#337).

**Final original finite Wilson theorem — FORMAL HOLD.** The single joined acceptance still needs a reviewer to treat the pinned **original matched Wilson-action and true E1/E2 source projector receipts** (including the independent source-to-Schur and full signed-moment evidence) as proof of the precise original full Hamiltonian rather than merely as internally consistent archived inputs. The action/interval primary evidence remains held in research drafts #315/#317/#319/#328. This ledger **does not** approve those drafts by implication. A fail-closed joint gate should verify their exact pins, source energy numerator conventions, original (W) and complete-Q couplings, strict endpoint and angular intervals, and the original action/normalization with changed-premise controls.

The 3×4 finite model's distinct high-cluster bound (E_9-E_8) remains accepted under the finite high-cluster rule. The first gap and Wilson spectral weight must retain their separate scopes. The **four-dimensional continuum Yang–Mills existence and mass gap remains OPEN**.

**Review result:** full-Q Perron mathematical implication **PASS**; joined original Wilson mathematics **CONDITIONAL PASS**; complete original Wilson theorem **FORMAL HOLD**, with specific source-action/projector acceptance work identified.
