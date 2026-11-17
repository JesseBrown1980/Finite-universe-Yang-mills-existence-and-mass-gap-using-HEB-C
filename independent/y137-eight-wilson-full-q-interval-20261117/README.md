# Issue #137 — original seven-loop 8×8 effective Wilson matrix interval

Research draft, November 17, 2026. Source-frozen real physical S3 calculation with **64 exact signed integer matrix-entry enclosures** valid across the source-conditional E1/E2 **whole finite physical energy brackets**. This is a matrix enclosure, not a certificate that the true two-energy eigendirection contraction has positive Wilson spectral weight.

## Exact original-source operator structure

Let P be the original eight-flat coordinate projector in the weighted physical S3 gauge-orbit basis, Q=I−P, B=QHP, and O the full seven-loop faithful-character summed Wilson multiplication observable. As an exact operator on the full 2,177,317,873-orbit finite space,

    POQ=QOP=0.

The true effective observable between flat components at true physical eigenenergies E1,E2 is the 8×8 bilinear matrix

    M(E2,E1)=POP + B^† (QHQ-E2)^(-1) QOQ (QHQ-E1)^(-1) B.

It is in general NOT a symmetric real matrix for E2≠E1; do not symmetrize or substitute a single-energy inverse. In raw flat coordinate units, the weighted matrix entry is

    M_ij = wf_i O_i delta_ij + sum_Q wq Oq (R2 B)_qi (R1 B)_qj.

The original source check.py and replay.py are pinned by immutable Git blob SHA. The independent accepted #185 source also gives B^† B=72 I in the Wflat-orthonormal basis, with wflat=(1,3,2,3,3,2,2,2). The tool independently reconstructs the complete 8×8 weighted B^†B Gram from all 264 original nonzero flat-to-Q edges and demands agreement.

## Two-energy original Q approximation and full inverse residual bound

The accepted Stage E source-conditional physical energy intervals, written in integer units b=10^9, are

    E1 numerator in (69909429421,69909586556)
    E2 numerator in (69949264147,69949433884).

Source lower nonflat floor gamma=94.0682, integer scale PS=10^6, upper physical H ceiling 468. Reconstruct the actual original 8-column Q Jacobi inverse trial matrices Y1,Y2 at the **upper certified energy endpoints**, using b=10^9 and T=10^12 scale, with the pinned original 20-step full K3 source. The source output residual Gram G_i includes all physical exterior shell4 targets; the source identity is

    G_i = 6 S_i^† W_Q S_i
    S_i = (b QHQ-a_i)Y_i - b*T*C,

where C is the signed original flat-to-Q electric coupling in the original source convention. The factor six is verified in the inherited original #180 source. For each raw flat coordinate j, the full-Q exact true inverse-action error in integer T-scaled units satisfies

    ||Y_true_j - Y_trial_j||_W <= sqrt(G_jj/6) / g_j,
    g_j = b*(gamma-E_j_upper) > 0.

The code uses integer outward sqrt and ceildiv for the strictly valid integer error ceiling e_j. It also uses an integer ceiling q_j for each weighted ||Y_trial_j||_W.

With ||QOQ||<=14, a source-accepted bound for the QOQ matrix-entry error at the upper endpoints, in numerator units T², is

    radius_Q_ij =
      14*(e2_i*q1_j + e1_j*q2_i + e2_i*e1_j).

This includes the double-error term and all Q outside K3 through the original residual Gram and gamma floor. It does not treat the K3 truncated trial as an exact Q resolvent.

## Enclosure for **all** certified E1/E2 windows

The matrix depends on true E1 and E2. Resolvent identities provide a separate uniform energy-drift bound without sampling unknown true energies:

    ||R(z2) O_Q R(z1) - R(z2_hi) O_Q R(z1_hi)||
       <= 14 * [ (Delta_z2)/(gap2²*gap1)
                 +(Delta_z1)/(gap2*gap1²) ],

where gap_i=gamma-Ei_upper, and Delta_zi=Ei_upper-Ei_lower. Multiplication by B^† and B contributes exact norm factor ||B||²=72. A raw weighted flat ij matrix element contributes at most sqrt(wflat_i*wflat_j), rounded upward to an integer.

Using b=10^9 energy numerator units and gap_i_num=b*(gamma-Ei_upper), the outward numerator-T² radius for each term is calculated as

    ceil[ceil_sqrt(wflat_i*wflat_j)*72*14*b²*T²
         * Delta_zi_num / (products of 3 gap_num factors)].

Thus every entry has a valid signed interval over **both full physical energy windows**:

    (Mhat_ij-radius_Q_ij-radius_energy_ij)/T²
      <= M(E2,E1)_ij <=
    (Mhat_ij+radius_Q_ij+radius_energy_ij)/T².

All numerators, denominators, radii, original U/G hashes, and the complete 64 entries are preserved in the hosted RESULT.hbp. Since all claims are strict source-conditional, the endpoint evaluation is a bounding device; it is not a substituted historical sample energy and does not assert that a true energy lies at the upper endpoint.

## Acceptance / theorem boundary

The calculation checks the actual original 24-link seven-loop operator, source-pinned Q graph, both endpoint inverse source Gram matrices with **full shell4**, original B isometry and reflection symmetry. The toy tests two nonzero P/Q blocks, rejects dropping QOQ, and checks integer outward rounding. Source SHA changes and CI no-float violations fail closed.

**Next proof gate:** Apply source-authenticated interval 8×8 Schur projectors for the true simple E1/E2 energies to this entire effective Wilson matrix, then normalize the whole physical states and require a strict signed first-excitation Wilson overlap interval excluding zero. The existing E1/E2 energy intervals and full Q floor alone cannot supply these eigendirections. The earlier historical #180 fixed-sample original-Wilson weight >0.000416300 remains a separate sample-level theorem.

The accepted finite full physical E2−E1 gap is source-conditionally (0.039677591,0.040004463) J_E. First-excitation Wilson spectral weight **HOLD**, Issue #137 **OPEN**, 4D continuum Yang–Mills theorem **OPEN**.

To reproduce:

    python3 -I -B independent/y137-eight-wilson-full-q-interval-20261117/physical_wilson_matrix.py toy
    python3 -I -B independent/y137-eight-wilson-full-q-interval-20261117/physical_wilson_matrix.py real
