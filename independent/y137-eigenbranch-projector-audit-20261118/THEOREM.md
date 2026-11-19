# Issue #137 — independent eigenbranch-to-projector transfer audit

Date: 2026-11-18. Research draft; finite periodic 3×4 S3 at r=9. This file starts the **mathematical** acceptance audit behind PRs #234, #284, #311, #315, and #317. No production Hamiltonian, witness, bound or evidence is changed.

## Accepted inputs and scope

- The previously recorded Perron nonflat floor is 94.070673 J_E; Wilson work conservatively uses gamma = 94.068200 J_E.
- Separate arithmetic reconstruction in #317 produced both 8×8 signed-four-moment Schur endpoint matrices, their 16×16 positive localizers and the E1/E2 inertia counts (1/1 and 2/2).
- The matched witnesses reported W-flat sine caps 0.002362700330 (E1) and 0.005047836049 (E2). The original first-Wilson weight lower floor is a **conditional** 451/10^12.
- This audit derives explicit transfer criteria. The published numerical caps and the positive Wilson result remain HOLD for independent mathematical acceptance until all the corresponding premises are established.

## Theorem A: Schur branch count and identification

Work in a real, orthonormalized version of the weighted orbit Hilbert space. Let
H = [[A, B*,], [B, D]], with A acting on the original eight-dimensional flat subspace P, and D = QHQ >= gamma I (whole Q, all physical symmetry sectors as appropriate). For z < gamma define
R(z) = (D-zI)^(-1) and S(z) = A-zI-B*R(z)B.

Block Gaussian congruence gives inertia(H-zI) = inertia(D-zI) + inertia(S(z)), so inertia_-(H-zI) = inertia_-(S(z)) for z < gamma. This counts all actual eigenvalues below z, including multiplicities. Differentiating gives
S'(z) = -I-B*R(z)^2 B <= -I.
Thus each ordered eigenvalue of S(z) is strictly decreasing as z rises, and the dimensions of negative spaces can only increase.

To assert that a particular matched witness targets the actual E1 or E2 eigenvector, require:
(A1) the exact whole-space physical matrix / symmetry map and W-congruence are fixed and verified;
(A2) two disjoint closed intervals [a1,b1], [a2,b2] below gamma;
(A3) exact certified inertia counts n_-(S(a_i))=i-1 and n_-(S(b_i))=i, plus endpoint nonsingularity, for i=1,2;
(A4) exactly one zero branch within each interval (then the corresponding eigenvalue is simple), verified by these strict counts and monotonicity; and
(A5) the matched flat witness is specified in the *same physical eight-flat coordinate system* as the Schur matrices.

Caution: an inertia (1,1) or (2,2) pair at a *single sampled energy* is not by itself the endpoint-count test in (A3), nor a proof of eigenvector angle. A separate strict whole-space E3 separation is required if used elsewhere in the state-error estimates.

## Theorem B: quantitative flat-projector direction enclosure

Let E be the simple true eigenvalue selected under Theorem A. Let p be its unit **flat component direction**: S(E)p=0. Let u be the unit, phase-aligned candidate in the same flat metric and set Pi=I-u u*. Define the compressed operator C(E) = (Pi S(E) Pi)|_{u-perp}.

If a verified spectral singular-value lower bound sigma_min(C(E)) >= delta > 0 and a verified residual upper bound ||Pi S(E)u|| <= rho hold, write p=a u+y with y perpendicular to u. The projected null equation says C(E)y = -a Pi S(E)u, and so ||y|| <= |a| rho/delta. Therefore

    sin angle(p,u) <= rho / sqrt(delta^2+rho^2).

This handles E2 with an indefinite compression: the required certificate is a *singular-value* lower bound, not positive definiteness or merely an inertia count. The rank-one projector operator norm also obeys ||p p* - u u*||_2 = sin angle(p,u).

For a desired cap s in (0,1), an entirely rational sufficient test is

    rho^2 (1-s^2) <= s^2 delta^2,  delta>0.

## Theorem C: certificate construction from exact Schur envelopes

At an authenticated sample z0, suppose exact symmetric matrices L <= S(z0) <= U are certified in the **same orthonormal flat basis**. Define T=(L+U)/2 and w>=||U-L||_2/2 (a rational Frobenius upper bound, or an exact PSD bracket, is permissible). If E is within |E-z0|<=Delta, and ||B||^2<=72 and E<=b<gamma, then resolvent differentiation gives

    ||S(E)-S(z0)|| <= [1+72/(gamma-b)^2] Delta.

Set eta=w+[1+72/(gamma-b)^2] Delta. Then

    rho = ||Pi T u|| + eta
    delta = sigma_min((Pi T Pi)|u-perp) - eta

are conservative bounds usable in Theorem B whenever delta>0. The squared norms can be certified without floating point. To certify sigma_min(C0)>=d0>0, exhibit an exact PSD/LDL witness for C0^2-d0^2 I on u-perp (or equivalent exact characteristic / inertia argument). An explicitly normalized rational basis for u-perp, with the correct Gram metric, is required.

**Sharper preferred construction:** Instead of the sometimes costly common Lipschitz term eta, use independently source-authenticated Schur enclosures directly at each true-energy interval endpoint and S'(z)<=-I to bracket S(E) for all E in that interval. The E1/E2 intervals in the archive are much wider than the 0.002–0.005 target angle, so a naive sample-to-window derivative error can easily fail. This is a numerical feasibility issue, not a flaw in the transfer theorem.

If exact lower/upper forms are produced in W-bilinear coordinates rather than Euclidean matrices, conjugate *every* operator and witness by the same W^(1/2), or run all residual and compressed calculations in W-inner products; mixing bases invalidates the result.

## Detailed review tasks / fail-closed acceptance

1. Independently authenticate the complete original P-Q 264-link source and P, Q, W, A, B, D definitions; prove the Schur matrices correspond to the full physical Hamiltonian and original sector selection.
2. Establish exact interval endpoint inertias (i-1,i) for E1 and E2 on the *same branch*, with strict nonsingularity. The already reproduced sampled-energy inertia counts are a preliminary input only.
3. Independently verify signed-moment Gauss/Lobatto **Loewner** inequalities L<=S(z)<=U from the finite positive spectral measure for the whole-Q source, with correct orientations and support [gamma,Dmax], not merely reproduce matrix fingerprints. Reproduce the full-Q signed mu3 graph source independently.
4. Build an exact rational u-perp basis (or W-orthogonal projector) for each pinned eight-flat matched witness and certify rho, delta uniformly on its true-energy window. A positive delta and a verified target sine inequality are the decisive new data.
5. Cross-check the existing full-W error route independently; certify that it uses the true branch selected in step 2. Compare this route to the direct Schur projector route without silently identifying different eigenvectors.
6. Transfer the newly accepted angles through the exact two-sided O9 source-correlated action, with the mixed negative-term cosines bounded above by 1, and restore the original O=(O9+16I)/2 with the exact first/second eigenstate orthogonality and physical normalization.
7. Perform independent-machine whole Perron 45,508,080-row rebuild and all-pair weighted-adjoint provenance checks. Preserve the historical allpairs fail-closed review flags.

**Acceptance: FORMAL HOLD** until steps 1–7 are independently discharged. A positive computed matrix-element inequality from archived premises is a source-conditional certificate candidate, not a completed stand-alone theorem.

## Recommended numerical audit output

For each energy produce one fail-closed signed machine-readable row:
- original H and full-Q source SHA, W metric and chosen flat direction SHA
- interval [a,b], strict endpoint inertia counts and exact rational zero-branch isolation
- exact full-Q mu3 SHA, L/U Schur envelope SHA, and independent PSD bracket verification
- exact rho_upper, delta_lower and delta_sign (including outward rounding receipts)
- squared-angle comparison rho^2(1-s^2) <= s^2 delta^2 and the true-eigenbranch ID
- stage-to-stage hash references and independent false-input controls

Until the interval-valid delta/rho values have been generated, label the Stage E transfer **THEOREM FORMULATED / NUMERICAL PREMISES OPEN**, not PASS.

## Directional Loewner refinement and interval drift (second numerical test)

The frozen-sample source run #44444792307 passed execution and returned sampled angle HOLD for both E1 and E2 using a conservative *global* operator-envelope penalty. Its actual midpoint projected residuals were tiny (3.62e-10 and 4.20e-9 in that run's common-midpoint normalization); the normalized global half-width bounds were about 0.0005166 and 0.0007783. These numbers are diagnostics, not physical angle certificates.

Here is a sharper valid estimate. In the physical W-flat Hilbert space let L <= S(z) <= U and let A=U-L >=0, T=(L+U)/2. Let u be a unit matched flat witness. The symmetric operator E=S(z)-T satisfies -A/2 <= E <= A/2; hence there is a self-adjoint contraction J on the range of A with E=A^(1/2) J A^(1/2)/2. Consequently

    ||E u|| <= (1/2) sqrt( ||A|| * <u,A u> ).

This bound is *directional* and can be much smaller than ||A||/2. Both ||A|| and <u,A u> admit exact-rational upper bounds using the original W-bilinear matrix and source witness. A weighted Frobenius upper ||A||_F supplies a safe bound on ||A||.

With z the frozen source energy and true E in [a,b], let bmax=max(z,b)<gamma and h=max(|z-a|,|z-b|). The whole-Q resolvent derivative obeys

    S'(t) = -I - B* (D-t)^(-2) B.

The projected residual of the identity term vanishes because Pi u=0. Thus with ||B||^2 <= 72:

    ||Pi S(E)u|| <= ||Pi T u||
      + (1/2) sqrt(||A|| * <u,A u>)
      + 72*h/(gamma-bmax)^2.

The compressed singular separation is bounded more conservatively:

    sigma_min(C(E)) >= sigma_min(C(T))
      - ||A||/2
      - (1+72/(gamma-bmax)^2)*h.

The source's integer Schur bilinear matrices must first be divided by the original normalization D_original = DEN*UNIT^2 as defined in `recentred_angle.angle` to obtain physical J_E units; energy numerators must be divided by DEN. The new `source_window.py` enforces these conversions and tests the exact squared-sine criterion for both original matched E1/E2 witnesses. Its success still depends on formal source provenance, exact spectral endpoint branch identification and independent mathematical review, even when the interval arithmetic tests PASS.

A failed sufficient inequality is a numerical HOLD, not evidence that the true Wilson transition vanishes.

## Source-matched Q-resolvent and exact width eigenvalue refinement

For t<=z, D>=gamma and R(t)=(D-t)^(-1), functional calculus gives ||R(t) B u|| <= ||R(z) B u|| for the same fixed normalized u. Suppose a source-authenticated q_upper(z,u) bounds the RHS. Then

    ||Pi B*R(t)^2 B u|| <= ||B|| q_upper(z,u)/(gamma-z).

This improves the projected-residual energy drift to

    ||Pi S(E)u|| <= ||Pi T u||
      + 1/2 sqrt(w_A * <u,A u>)
      + ||B|| q_upper(z,u) * |E-z|/(gamma-z),

where A=U-L>=0 and w_A is any exact upper on its W-generalized maximum eigenvalue. The previously used ||B||^2/(gamma-z)^2 bound remains for the *full compressed operator* perturbation unless separately strengthened.

The original #187 full-state source supplies a norm enclosure for the historical flat direction v0. For a moved matched witness u, the triangle inequality and the accepted ||R(z) B|| <= ||B||/(gamma-z) transport that q norm by

    q_upper(z,u) = q_upper(z,v0)
                   + ||B||*||u-v0||/(gamma-z)

with W-unit directions and outward-rounded roots. The numerical checker uses the historical exact integer q upper, original four-moment witness movement, original B_NORM_UP, and the pinned physical energy scale.

The spectral upper w_A is obtained with exact 8x8 strict positive definiteness of w_A*W-A and rational bisection; a Frobenius upper is used only as a verified starting ceiling. This improves both the directional residual term and the compressed singular-value allowance, while every true-branch/source acceptance obligation stays separate.

These are **additional sufficient conditional bounds**. A successful interval inequality would not independently authenticate the large full-Q source, whole Perron reconstruction, or original Wilson dual-action receipts.
