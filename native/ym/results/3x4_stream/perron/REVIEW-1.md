# Review 1, verbatim

Relayed by the operator on November 2, 2026. The reviewer read the PR at head `155acdd`. This is the summary that reached this seat. The original also offered its full text as a Markdown download.

---

Independent review — Yang–Mills PR #79
Not approved for scientific merge yet
I checked the actual PR #79, its source code, mathematical derivation, and committed receipts.

The core Perron-bound argument is mathematically sound, conditional on the stored matrix correctly representing the Hamiltonian. This is a worthwhile alternative to the much more expensive 3×4 Schur-column computation.

Two parts of the proof check out:
\[
E_9(H)\ \geq\ \lambda_{\min}(H')
\ \geq\ \min_i\frac{(H'd)_i}{d_i},
\qquad d_i>0.
\]

The first inequality follows from eigenvalue interlacing after removing the eight flat-state basis vectors. The second is valid for a real, symmetrizable matrix with nonpositive off-diagonal entries, using a positive vector \(d\).

I also checked the proposed lift from the \((+,+)\) sector to the full gauge-invariant Hilbert space. The lifting argument is valid in principle: when the sector is the orbit-constant subspace of a symmetry group that preserves the Hamiltonian and flat states, the same positive test vector extends to all non-flat configurations. Its row ratios are preserved.

That is a significant result: it can potentially establish a finite-lattice bound across all momenta and symmetry sectors from one sector's computation.

The distinction is that the mathematical theorem and the actual 3×4 numerical certificate need separate verification.
Findings that must be resolved before certifying 3×4
Review item    Finding    Status
Perron inequality and interlacing    Mathematically valid under stated assumptions    PASS
Whole-space lifting argument    Valid if the sector is the exact symmetry reduction    Conditional PASS
Rust checker arithmetic    Exact integer calculation and appropriate sign checks    PASS on reviewed logic
3×4 value \(t_{\mathrm{cert}}=93.061051\)    Reported in your transcript; not publicly replayed here    Pending
Independent 3×4 Hamiltonian-row reconstruction    Not yet demonstrated    Pending
Certified 3×4 gap verdict    Rule not yet registered for the Perron method    Not established

Two concrete changes will strengthen the independent verification. The Python checker should fail immediately if bad_d or positive_offdiag is nonzero, rather than merely reporting those values. It should also use explicit errors rather than assert for critical validation, because optimized Python execution can disable assertions.

The more consequential remaining check is reconstructing selected 3×4 Hamiltonian rows independently from passA.bin, including orbit weights, magnetic terms and transitions. A correct checksum proves the stored bytes are unchanged; it does not alone prove those bytes encode the intended operator.
What your reported result would establish
If the published certificate vector and independent checks reproduce \(t_{\mathrm{cert}}=93.061051\,J_E\), the derivation supports these finite-lattice bounds:
\[
\begin{aligned}
E_9(r)-E_8(r)&\ge21.061051\,J_E &&(r\ge9),\\
E_9(9)-E_8(9)&\ge23.030051\,J_E.
\end{aligned}
\]

The second bound also depends on the independently validated whole-space upper bound \(E_8(9)\le70.031\,J_E\).

These would be substantial finite-lattice results, but do not establish the arbitrary-volume mass-gap theorem.
Download the full review
Independent Review — PR #79

Mathematical proof review, source assessment, independent test, blocking issues and merge conditions.

Download review (Markdown)


My merge recommendation: PR #79 can be merged as experimental tools and draft mathematical methodology, provided that scope is explicit. I would not approve merging it as a certified 3×4 numerical result until the 364 MB certificate vector, separate checker output and independent row validation are published and checked.

The mathematical approach has passed my independent conceptual review. The remaining requirement is evidence verification, not a new theory.
