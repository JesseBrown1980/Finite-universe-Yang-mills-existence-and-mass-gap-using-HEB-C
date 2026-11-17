# Issue #137 — exact source-centered original Wilson 8x8 physical interval

Research draft. Companion to the separate original centered directional-dual source PR #281 and original unshifted physical full-Q 8×8 interval PR #273.

The actual seven-loop faithful-character Wilson O is integer-valued multiplication in canonical S3 gauge-orbit coordinates. The P=8 flat coordinate and Q all nonflat coordinate projectors obey POQ=QOP=0 exactly. For exact physical true eigenenergies E1,E2, the original effective Wilson operator is

    M_O(E2,E1)=P O P+B†(QHQ-E2)^-1 Q O Q (QHQ-E1)^-1 B.

Gauge-center the physical observable by rational mu=7/2 and form integer O2=2O−7I throughout BOTH P and Q. The exact center effective operator is

    M_center = (1/2) [P O2 P+B†R2 Q O2 Q R1 B].

The source universal character bounds −7≤O≤14 give |O2|≤21 on the WHOLE original physical Hilbert space. This reduces the normalized Q multiplication cap from 14 to 21/2=10.5, a 25% reduction in the source-independent operator norm, without a claim about the total signed transition.

The source script centered_matrix.py copies the original PR #273 exact 64-entry 8×8 source, full 155,378 K3 Q coordinates, exterior shell4 physical residual Gram, two physical true-energy upper endpoint 20-step inverse trials and full original source-conditional energy-drift calculation. It substitutes integer O2 as the multiplication field and uses cap 21 for O2 in each weighted inverse-error and energy-drift radius. Every signed HBP matrix numerator, lower and upper rational endpoint, separate Q and true-energy error radius is then reported over the exact common denominator 2*T*T with T=10^12, i.e. the original rational centered O−7/2, not O2. All 64 signed entries are physically enclosed across the accepted Stage E true E1/E2 energy brackets. Source hashes pin the original Wilson and Q matrix builders, accepted original B†B=72 I, and all shell4 residuals. Negative controls reject omitted QOQ and a wrong scalar-shift identity.

For true distinct eigenstates psi1,psi2, exact Hilbert orthogonality gives

    <psi2,(O−7/2 I)psi1>=<psi2,O psi1>.

For nonorthogonal fixed source trial states u1,u2 the corresponding shift in the trial bilinear is −(7/2)<u2,u1>. This trial overlap must not be silently set to zero; it is recomputed in the independent companion centered source-specific dual PR #281.

## Scope

The 64 rational entry intervals certify the original physical **centered effective operator** at all certified true E1/E2 energy arguments. They do not construct certified true eight-flat eigendirections, nor a normalized positive original first-excitation Wilson weight. The latter needs a signed real physical contraction and source-specific error control as in PR #278. Source-conditional whole finite first energy gap remains accepted, issue #137 first Wilson weight HOLD, continuum theorem OPEN.

To reproduce: python3 -I -B independent/y137-original-centered-wilson-o8-20261117/centered_matrix.py real
