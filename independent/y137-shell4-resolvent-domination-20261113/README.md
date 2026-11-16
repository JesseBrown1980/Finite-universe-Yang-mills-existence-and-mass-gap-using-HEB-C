# First actual shell-4 boundary-resolvent source measurement for #137

**Source status:** prediction and code are supplied for a new hosted measurement. Until the hosted
result, its second independent replay, and the full-space strict sign-transfer audit finish,
the first-excitation Wilson spectral-weight claim remains **HOLD**.

This is an independently checkable **full-Q enclosure from actual shell4 source
data**, not the final E1/E2 amplitude theorem. It avoids exhaustive shell5 enumeration
by using the complete globally valid weighted electric norm bound, rather than
pretending the shell4-truncated residual is the full Q residual.

## New exact operator inequality

In the correctly weighted orbit Hilbert space, let A=QHQ-z and
A >= gamma-z >0 from the merged lift-free certificate. The nonnegative
electric transition adjacency T is weighted self-adjoint and has EXACT
row sum 72, as checked by the original 24-link S3 operator builder.
Weighted similarity makes T symmetric with eigenvalues between -72
and 72 (or use its stochastic contraction), hence every principal
compression, including the shell4 block, has ||T44||<=72.

Let Y be the accepted source K3 Q trial columns, with full-Q residual
R=AY-B in the **positive Y convention**, supported on inner K3 plus
the complete shell4 exterior. Write R4 for the shell4 projection, and
G4 for its exact W-weighted Gram. Let m4max be the EXACT maximum
plaquette magnetic cost across all original 1,985,218 shell4 orbits,
reconstructed from their keys. Since the magnetic energy is 9m and
the electric diagonal is 72 before self moves,

    A44 <= (144 + 9*m4max - z) I = h I.

Set V=R4/h in its complete Q support (zero off shell4), and Y'=Y-V.
The full-Q variational Schur form is

    U(Y') = U(Y) - 2<R,V> + <V,AV>
          <= U(Y) - <R4,R4>/h.

No shell5 matrix elements have been silently dropped: the quadratic
form <V,AV> uses the exact principal compression A44; all couplings
out to shell5 enter the global spectral bound on T and the underlying
exact whole-Q Schur variational identity. This is a **conservative
boundary-resolvent supersolution**, valid even though R' extends to
shell5.

The old accepted Schur lower bound also remains valid. In the source
scaled integer representation, with b=10^9, source Y scale=10^12,
the 8x8 symmetric U/G matrices and full-Q source floor numerator
gamma_num = b*94068200 - z_num*10^6 obey

    U - (10^6 G)/(6 gamma_num)
         <= S(z) <= U - G4/(6 h_num),

where h_num=b*(144+9*m4max)-z_num, and where these are the
Schur matrices in the source's common b*scale^2 normalization.

Thus new Schur width

    Lambda_new = (10^6 G)/(6 gamma_num) - G4/(6h_num)

is PSD and smaller than the accepted old full-Q uncertainty
Lambda_old=(10^6 G)/(6 gamma_num). This is a genuine stronger upper
source bound, not an assumption that unknown exterior resolvents
are diagonal or vanish.

## What the hosted code checks

- Exact historical K3 source hashes, exact input sample energies and
  flat vectors, source floor, graph state/edge counts, and 8-state weights
- Exhaustive shell4 magnetic-number census from **all** target keys
- Original full 8x8 G minus independently reconstructed complete
  K3-inner 8x8 Gram equals exact shell4 G4
- Full weighted exterior edge traversal independently reproduces
  v^T G4 v for each of the two frozen sample vectors
- All 255 principal minors of Ginner, G4, and the new width matrix
  are nonnegative; deleted exterior edge control changes the result
- The new U upper-bound is strictly stronger in the two tested trial
  directions, while preserving exact energy brackets and the E2
  sector separation

## Remaining obligation

The measured improved source Schur interval must be independently
replayed at the **same final head**, including its complete 8x8
matrices and the weighted 72-move contraction proof. Only then should
the new interval be used to re-evaluate the 7D orthogonal Schur
projector, exact inertia microbrackets, full normalized W states,
and the original unshifted seven-loop Wilson transition.

A positive directional U-upper reduction alone does **not** prove
the actual E1->E2 spectral weight. Keep issue #137 open.
