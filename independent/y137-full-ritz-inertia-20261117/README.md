# #137 Stage K — full 20,738-dimensional exact inertia via certified 10×10 Schur enclosures

Research draft, November 17, 2026. This code extends the accepted source
chains #242 (old H20736), #249 (rank-two residual Gram), #251 (physical Htt),
and #254/#255 (complete original C and whole-block norm). It leaves those
sources and the main branch unchanged. It does not substitute a four-vector
Ritz gap for a full finite-Hamiltonian gap or a Wilson spectral-weight proof.

## Full projected generalized pencil

In the old basis, let P be the eight physical flat vectors; let Q0 be the
remaining **20,728 old nonflat directions**; retain the two integer-scaled
residual vectors V. The accepted full 20,738-dimensional Hamiltonian is
`K_ext=[[K_old,C],[C^T,Htt]]` with positive metric
`G_ext=diag(G_old,d E)`. The Gram blocks P–Q0, P–V and Q0–V are zero.

At an exact rational energy z/D, with D=10^9, partition the *integer*
pencil `D K_ext - z G_ext` as

    [ T(z)    B(z)^T ]
    [ B(z)      A(z) ]

where `T(z)` is 10×10 on P+V, `A(z)=D K_Q0Q0-z G_Q0Q0`
on 20,728-dimensional Q0, and `B(z)` is 20,728×10.
The accepted whole-nonflat source floor is at least 94.070673, so the
**weaker frozen premise** `QHQ >= (94.0682) Q` implies
`A(z) >= (94068200000-z)G_Q0` for each listed z below that floor.
The original physical Hamiltonian bound `H <= 468` supplies
`A(z) <= (468D-z)G_Q0`. Thus the eliminated A(z) is strictly positive
and full negative inertia equals the negative inertia of its exact 10×10
Schur complement `S=T-B^T A^-1 B`.

## Exact inverse enclosure, no floats or large dense factorization

The non-coordinate 4×4 Krylov overlap plus diagonal coordinate metric
allows **integer** application of `N G_Q0^-1`, where N=6 times the
positive 285-bit 4×4 Schur Gram determinant. The source code independently
checks this inverse against the original sparse metric and all four positive
Schur leading minors.

Let `L=N G_Q0^-1 A` with known integer spectral interval `[amin,amax]`,
where `amin=N*(94068200000-z)`, `amax=N*(468D-z)`. For each of the ten
columns `b=N G_Q0^-1 B`, use integer Chebyshev recurrences for numerator
vectors `p_m,q_m` and positive integer denominator `t_m`:

    C=amin+amax, F=amax-amin, Vop=C*I-2*L
    p_0=0, p_1=2*b, q_0=b, q_1=Vop*b
    t_0=1, t_1=C
    p_(m+1)=2*Vop*p_m-F^2*p_(m-1)+4*t_m*b
    q_(m+1)=2*Vop*q_m-F^2*q_(m-1)
    t_(m+1)=2*C*t_m-F^2*t_(m-1)

These satisfy **exactly** `t_m*b-L*p_m=q_m`, reverified using a fresh
matrix-free multiplication at the end of each hosted run. With `X=p/t`,
the dual residual is `R=B-A X=G_Q0*q/(N*t)`.

For any such X, self-adjoint positivity gives the matrix inequality

    2 B^T X-X^T A X
       <= B^T A^-1 B
       <= 2 B^T X-X^T A X + (R^T G_Q0^-1 R)/(94068200000-z).

The code forms both exact 10×10 integer-scaled Schur endpoint matrices and
counts their **negative inertias** using signed leading principal minors
of exact fraction-free Bareiss determinants. A reversed-coordinate
congruence provides a second order-sensitive check. The trial source
pencils, Chebyshev integer recurrence and Schur-error Gram must be exactly
symmetric. If the two Loewner endpoint inertias agree, full-20,738 inertia
is certified; otherwise the code reports `NOT_CERTIFIED` and the hosted
strict acceptance refuses the endpoint.

## Locally reproduced full-20,738 results

Original production artifacts (not repository checker output) were
retrieved by GitHub Actions artifact IDs: old sparse matrix 14276245914,
complete cross 14289244160, rank-two Gram 14286313578, Htt 14288034476.
Their decompressed files are checked by hard-coded original SHA-256 values.

| z/D | Chebyshev degree | Lower Schur negative inertia | Upper Schur negative inertia | Whole-space Ritz count |
|---|---:|---:|---:|---|
| 69.890000000 | 6 | 0 | 0 | 0 certified |
| 69.913037770 | 6 | 1 | 1 | 1 certified |
| 69.930000000 | 6 | 1 | 1 | 1 certified |
| 69.960000000 | 6 | 2 | 2 | 2 certified |

These infer full **20,738-dimensional Ritz** brackets
`69.89<lambda_1^(20738)<69.913037770` and
`69.93<lambda_2^(20738)<69.96`.
The already accepted four-vector variational Ritz bound sharpens the
second *upper* bound to `lambda_2^(20738)<69.952639135`, hence

    lambda_2^(20738)-lambda_1^(20738) > 0.016962230.

This is a **full projected/Galerkin** first-two separation, conditional
on the inherited whole-Q floor and authenticated source entries. It is
not a lower bound on the complete 2,177,317,873-dimensional physical
first gap and does not certify a normalized Wilson first-excitation weight.

A local degree-six exact run at the first upper endpoint measured
approximately 32.82 s wall and 581,144 KiB maximum resident set size in
the execution container, including source loading and independent
recurrence verification. The degree-eight experiment at the tighter
second Ritz endpoint exceeded a 120-second local execution cap, so that
endpoint remains separate. Hosted workflow durations and limits are
engineering budgets, not an assurance of completion time.

## Reproduce / acceptance

    python3 -I -B independent/y137-full-ritz-inertia-20261117/exact_20738_inertia_pilot.py toy
    python3 -I -B independent/y137-full-ritz-inertia-20261117/exact_20738_inertia_pilot.py pilot OLD CROSS RESIDUAL HTT 69890000000 6 0

`OLD`, `CROSS`, `RESIDUAL`, and `HTT` may be the original GitHub ZIP
artifacts or their unzipped directories. The new workflow downloads
all four original immutable artifacts from their recorded GitHub Actions
runs, performs exact source/tamper checks, evaluates the four thresholds
in separate bounded jobs, and requires a four-of-four final acceptance.
The input source SHA and the signed output receipt are retained in Actions.

Issue #137 Wilson spectral-weight result: **OPEN/HOLD**. Full original
finite physical spectral gap and 4D continuum mass gap: separate work.