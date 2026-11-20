# #137 — exact original weighted source residual to physical Schur identity

**Scope:** Algebraic source-to-Schur identity in the **same** weighted physical P/Q Hilbert space whose original 3×4 S₃ group action, eight flats, exact W metric, B*B=72I and original Wilson multiplication were independently accepted in [PR #341](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/341). The original numerical signed moment source equality is separately accepted by PRs #331/#335 and hosted full-Q signed third-moment run #44581486671. This proof does not re-read/recompute 20 million states.

## Exact physical source geometry and scaling

Let H be the original self-adjoint weighted orbit operator, P its eight magnetic-flat W-orthogonal directions, and Q its complete complement. Put A=PHP, B=QHP, D=QHQ, with B* the **W-weighted physical adjoint** established in #341.

For each real energy E below the whole-Q spectral floor and original integer source scale b=10⁹, let z=b E (or the equivalent exact integer sampled-energy numerator). Define X=bD-zI on Q and a trial Q operator Y:P→Q, with original input P columns scaled by σ=10¹². The full trial map is T=(σI,Y). The original **signed Q source residual** is

\[
R=Q(bH-zI)T=b\,B\,\sigma+XY.
\]

This residual can have both signs on the K3 portion and is also supported in the exterior Q4 shell, precisely as reconstructed independently in the accepted K3/Q4 source audit. There is **no positivity shortcut** for signed R.

The original trial bilinear matrix is

\[
U_0=T^\ast_W(bH-zI)T
 = \sigma^2 W_P(bA-zI)
 +Y^\top W_Q R
 +\sigma b B^\top W_Q Y ,
\]

with the source convention that matrices written in the unnormalized flat orbit basis are **W-weighted bilinear matrices**, hence W_P appears explicitly. The source moment matrices are

\[
\mu_k=R^\top W_Q X^k R,\qquad k=0,1,2,3.
\]

In the archived exact integer G0 source, the Gram accumulator uses **six times the orbit weight**, so its exact normalization is

\[
\boxed{G_0=6\mu_0,\quad\mu_0=G_0/6.}
\]

This is directly visible in the independently accepted original K3 source implementation and matches the independently checked four-moment input reconstruction. The factor six is a source-format integer convention, not a different physical inner product. Treating the uncorrected G0 as μ0 would create a sixfold error.

## Exact Feshbach identity for **any** trial Y

Define the true physical weighted Schur operator bilinear on P,

\[
S(z)=\sigma^2 W_P(bA-zI)
-\sigma^2 b^2 B^\top W_Q X^{-1} B.
\]

Since R=bBσ+XY and X is positive, direct expansion and cancellation of all Y terms gives

\[
\boxed{ S(z)=U_0-R^\top W_Q X^{-1}R.}
\]

It is an identity for **any** Y (including the original 20-sweep integer Jacobi approximation), not an approximation caused by the trial. Since X is self-adjoint positive in W_Q, the moments μk are simultaneous exact W_Q Gram forms. All Loewner inequalities in [merged PR #338](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/338) apply to precisely these matrices, subject to the separately authenticated original whole-Q spectral support and source moments.

The complete original K3/Q4/Q5 first-principles physical source reconstruction passed 331,818,176 original V1 components (merged PRs #331/#335); the original complete 20,738,636-state signed μ3 values independently passed 128/128 source-operator matrix entries (run #44581486671). Those physical source-data facts, the merged #341 W/PQ identity, and this algebraic theorem supply a direct mathematical chain from original finite Hamiltonian to exact Schur-moment arithmetic.

## Source-independent integer control and interpretation

The [standalone verifier](verify_identity.py) uses the original integer scales b=10⁹, σ=10¹² in a synthetic weighted P=2, Q=3 Hermitian example with W_P=(1,3), W_Q=(2,6,3), explicit weighted-adjoint PQ couplings, Q diagonal energies (75,76,77), sample E=70 and an **arbitrary nonzero trial Y**. It independently constructs exact signed R, U0, μ0..μ3, G0, true physical Schur and common-denominator residual correction. The exact source bilinear is U0/(bσ²)=[[70,12],[12,187]], μ0/(b²σ²)=[[378,54],[54,1256]], archived G0/(b²σ²)=[[2268,324],[324,7536]], and true Schur numerator/(b²σ²)=[[336,0],[0,960]] under inverse denominator 210b. Every equality is checked by **integer cross multiplication**. Seven altered source/normalization/resolvent/Gram inputs must be rejected, with checks invariant under optimized Python.

**Acceptance boundary:** This establishes the exact source-to-Schur algebra and the original G0/6 conversion independently of the previously accepted physical matrix computations. **Final combined original E₁/E₂ first-Wilson theorem remains SOURCE-CONDITIONAL / FORMAL HOLD** pending joint review of source-moment provenance and the complete whole-Q Perron top-vector symmetry lift at original couplings. The four-dimensional continuum Yang–Mills problem remains OPEN.
