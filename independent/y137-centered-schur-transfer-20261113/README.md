# #137 — true-energy **centered** eight-flat Schur projector test

This independent lane combines two already measured pieces: the fourteen-point exact full-H K3 count proof from PR #182, and the two source-pinned K3 U/G matrices, sample flat vectors and Q-resolvent trial method of accepted PRs #180 and #181. The new source-conditional energy windows are E1 in (69.9085,69.909875505) and E2 in (69.9481,69.949729820), and E3≥69.9686993 in J_E. The historical **sample** energies coincide with the new *upper endpoints* of these windows: they are probe locations and are not silently identified with the true eigenvalues.

All new endpoint inputs, original source hashes, sample vectors and the **centered residual inequality and null-branch acceptance gate** were frozen in PREDICTION.hbp **before the code was written**, based on PR #182's first successful hosted 31-row receipt. Results must not be promoted until the source PR #182 passes final review and is merged.

## Rigorous operator reduction

In W-orthonormal flat and nonflat coordinates, H=(A Bᵀ;B D), with D=QHQ≥γ I, γ=94.0682 J_E from the accepted lift-free floor. For \(z,E<\gamma\),

    S(E) = A-EI-Bᵀ(D-EI)^(-1)B
    S(E)-S(z) = -(E-z)I -(E-z)Bᵀ(D-EI)^(-1)(D-zI)^(-1)B.

The established K3 source yields exact 8×8 U/G and variational Schur envelope \(U/(bT²)-\Lambda\preceq S(z)\preceq U/(bT²)\), with \(\Lambda=W_P^{-1/2}[\mathrm{PS}G/(6\gamma_{\mathrm{num}}bT²)]W_P^{-1/2}\) PSD. For unit trial flat direction x, independently checked from its integer vector v,

    ||[S(z)-U/(bT²)]x|| <= sqrt(tr Λ * <x,Λx>).

The **centered residual**, for \(\mu=\langle x,S(E)x\rangle\), is

    r=(S(E)-mu I)x=(I-xxᵀ)S(E)x.

The scalar direct drift \(-(E-z)I\) vanishes from r **exactly**, so

    ||r|| <= ||(I-xxᵀ)[U/(bT²)]x||
            +sqrt(tr Λ * <x,Λx>)
            +|E-z|*||B||*||R_z Bx||/(gamma-E).

The first term is evaluated with the exact W-normalized **centered** integer expression \(d_i=q(Uv)_i-(v^\top Uv)\,w_i v_i\), \(q=v^\top W_Pv\), so its squared norm is \(\sum_i d_i^2/w_i / (b²T^4 q^3)\). No float or implicit Euclidean weighting is used.

The source-built K3 20-step trial Q vector provides \(\|\hat y\|\) and the **complete source full-Q** residual \(\|r_Q\|\) from the original G and shell-4 edges. Therefore

    ||R_z Bx|| <= min(||Bx||/(gamma-z),
                      ||yhat||+||r_Q||/(gamma-z)).

The exact full P/Q Frobenius coefficient is \(\|B\|_F²=576\), so \(\|B\|\le24\). The code evaluates the new directional bound and the old global bound, selecting the smaller.

## Essential null-branch selection guard

**A centered residual alone does not identify the correct eigenvector.** An unrelated eigenvector would have a zero centered residual too. This runner first independently bounds the Rayleigh quotient:

    |mu| <= |<x,U/(bT²)x>| + <x,Λx>
           + |E-z|[1+||B|| ||R_z Bx||/(gamma-E)]
         = m.

By monotone Schur eigenvalue crossing, the true simple Schur kernel at E1 has other eigenvalues separated by strictly more than E2_lo−E1_hi = **0.038224495 J_E**. At E2, the separation is strictly greater than min(E2_lo−E1_hi, E3_lo−E2_hi) = **0.018969480 J_E**.

Only if \(\boxed{m<\delta}\) does the spectral expansion imply

    sin angle(x, ker S(E)) <= ||r||/(delta-m).

This is the **fail-closed identity-selection gate**. If \(m\ge\delta\), report the centered result as HOLD and retain only the earlier uncentered bound \(\|S(E)x\|/\delta\). In either case, the code selects the minimum of all actually valid outward-rounded upper bounds.

The output records every independently auditable rational component: frozen input hashes, raw/centered variational residual, full Q trial and Q residual norm, directional B, PSD error action and Rayleigh, scalar energy drift, original global Q drift and new direction-specific drift, the strict null gap and \(\mu\) gate, the upper sine angles, and a nonvacuous/HOLD verdict.

## Actual first hosted result: both true Schur null branches identified

The first source-pinned [hosted run 43507229795](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43507229795) **PASSED** with both frozen U/G hashes, complete K3 weighted Q data, integer-only/no-float checks, and independent mandatory Rayleigh null-branch selection. Its four exact rows were filed **after the run** as [RESULT-CENTERED-PROJECTOR.hbp](RESULT-CENTERED-PROJECTOR.hbp). The follow-up CI requires byte-for-byte reproduction. A separate BigInt-only route independently rechecked both Rayleigh bounds, both full/centered residual sums and their two rational sine-angle ceilings.

| Certified source-conditioned quantity | E1 | E2 |
| --- | ---: | ---: |
| Null separation lower, J_E | 0.038224495 | 0.018969480 |
| Rayleigh `abs(mu)` upper | 0.003015255473 | 0.003380208233 |
| Rayleigh selection `mu < gap` | **PASS** | **PASS** |
| W-normalized centered residual upper | 0.003811712270 | 0.003951336576 |
| Uncentered sine-angle upper | 0.135704019583 | 0.294217718884 |
| **Centered sine-angle upper** | **0.108258863901** | **0.253465115951** |

Both true eight-flat null directions now have mathematically nonvacuous **source-conditional** projector estimates; neither of these inequalities would have been valid by simply dropping the scalar energy term without the Rayleigh selection check. Compared with accepted #181's first bounds 0.842057984250 and vacuous 1.465570680225, this gives a substantive numerical improvement with source-complete proof details.

**Remaining HOLD:** these are flat P-space angles, not complete W-normalized state-to-sample errors. The E1/E2 Wilson theorem needs the flat phase discrepancy, true-vs-sample energy-dependent Q-resolvent corrections, full normalization, and an operator-specific signed amplitude enclosure. The simple sufficient combined normalized-state error target of 1/700 is still far smaller than these flat angles; the positive conventional Wilson fixed-sample rational lower bound of merged #180 remains intact and requires no reclassification.

## Scope and next proof obligation

This is a **rigorous finite-model flat-projector error diagnostic** conditional on the accepted source floor and independently confirmed #182 energy windows. It does not assert the actual positive E1→E2 Wilson spectral weight. Merged #180 already certifies a positive *original unshifted conventional Wilson* fixed-Q-resolvent-sample transition. To transfer that sign, full Q-tail and normalized state errors must be bounded as well; a simple sufficient combined W-state error target is **<1/700**, or an operator-specific signed interval proof must close.

Run the new calculation with:

    python3 -I -B independent/y137-centered-schur-transfer-20261113/replay.py

CI must validate frozen source hashes, exact source K3 graph, new energy-window receipt dependence on #182, strict integer-only/no-floating gates, and both Schur null-branch decisions. All actual output must be filed **after** the first hosted run, then byte-replayed at the final head. Any failed guard or vacuous angle is a proper HOLD.
