# Exact gauge-orbit pairwise reciprocity theorem for the 3×4 \(S_3\) Hamiltonian

**Status: DERIVED exact finite-group identity; original full-state enumeration
acceptance is a separate numerical gate.**

## The physical configuration quotient and its weights

Take the oriented 3×4 periodic lattice with 12 sites, 24 oriented
links, and a connected tree of 11 edges. Its full link-configuration
set is \(\mathcal U=S_3^{24}\).

The subgroup of local gauge transformations fixing the root site has
order \(6^{11}\). Its action is free: an automorphism fixing the root
and every link is the identity along every tree edge, hence at every
site. Every full configuration therefore has exactly one
root-fixed tree-gauge representative per such gauge orbit, with the
11 tree links equal to the identity.

After this exact gauge fixing, the remaining global conjugations by
\(S_3\) act on the 13 retained links. For a canonical physical state
\(i\), define its orbit weight

\`\`\`text
w_i = | { g u_i g^-1 : g ∈ S_3 } | ∈ {1, 2, 3, 6}.
\`\`\`

The complete full-link gauge orbit represented by state \(i\) has
**exactly \(6^{11}w_i\)** configurations. The original sixfold
physical inner-product metric \(\,W_i=6w_i\) differs by a common
factor from the raw orbit cardinality and therefore has the
same weighted-balance equations.

## Every elementary electric edge is reversible

For each of the 24 oriented links \(e\) and three transpositions
\(t∈S_3\), the electric move

\`\`\`text
T_(e,t): U_e ↦ t U_e
\`\`\`

leaves every other link unchanged. Since \(t^2=1\), the map
\(T_{(e,t)}\) is its own inverse, including for states which become
self-loops after quotienting.

A local gauge transformation with left-site group element \(h\)
converts this edge operation into multiplication by
\(h t h^{-1}\), which is again one of the same three transpositions.
Thus **the multiset of all 72 labeled elementary electric moves is
gauge-equivariant**. Every raw full-configuration directed move
from full orbit \(i\) to full orbit \(j\) is paired bijectively with
the inverse labeled move from full orbit \(j\) to full orbit \(i\).

Let \(c_{ij}\) be the number of the original 72 physical link moves
from any tree-gauge representative of \(i\), after the physical
quotient, that land in canonical class \(j\). The same count holds
for every representative in the orbit, by the above gauge
equivariance. Consequently, the two raw directed transition counts
are

\`\`\`text
E_{i→j} = 6^11 w_i c_ij
E_{j→i} = 6^11 w_j c_ji.
\`\`\`

The involutive inverse pairs these sets exactly. Hence, **for all
physical gauge orbits \(i,j\) on this 3×4 lattice**, including
\(Q5↔Q5\), \(Q4↔Q5\), \(K3↔Q4\), and the supported-to-flat boundary,

\`\`\`text
                     w_i c_ij = w_j c_ji.
                     W_i c_ij = W_j c_ji.
\`\`\`

This is an exact integer identity for the full **72-move** electric
operator, with no spectral approximation, no inferred statistical
symmetry, and no restriction to previously archived pair partitions.
The diagonal self-loop count cancels automatically in the symmetric
Dirichlet squared-difference energy.

## What the theorem certifies and what remains to execute

The theorem proves weighted reversibility **from the defining
group action and link-move rule**. Its application to any particular
archived state store also requires verifying that the store's
canonical addresses, orbit weights, magnetic numbers, and 72
transitions are those of this exact mathematical construction.

- The independent hosted [cross-block pair state audit
  #44579396037](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44579396037)
  checked *every one of the archived* 139,517,148 unordered new
  cross-block pairs and 279,034,296 opposing directed records,
  including 4,096 independently regenerated physical endpoint pairs.
  This is **numerical PASS** for the original cross-block archive.
- The separate [full-state Dirichlet source implementation,
  draft #328](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/328)
  independently rebuilds the physical 72-move row for **each of the
  original 20,738,636 source states**, with exact orbit and
  canonical-key checks, including the complete Q5 principal response
  and the support-to-zero boundary. Its **full hosted production
  acceptance is pending**.
- The \(Q5↔Q5\) pairwise identity is now **DERIVED from the physical
  definition**, but a second exhaustive *stored-pair* audit of all
  Q5-principal directed records on independent hardware is still a
  distinct review option. The finite-group theorem should not be
  mislabeled as a second completed numerical recomputation.

## Consequence for the third-moment proof

For the original signed physical source \(V\), the exact
equivariant pair rule and \(W=6w\) imply

\`\`\`text
Σ_i W_i V_i^T (D_i V_i − b Σ_j c_ij V_j)
  = Σ_i W_i(b·9m_i − z) V_i^T V_i
    + b Σ_(i<j supported) W_i c_ij (V_i−V_j)^T(V_i−V_j)
    + b Σ_(i supported, j outside) W_i c_ij V_i^T V_i.
\`\`\`

This gives the independent [Dirichlet moment identity,
draft #325](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/325)
its exact global symmetry justification. Numeric full-moment
acceptance still requires full source SHA, every state, both energy
samples, every boundary and exact original 128-entry comparison.

**Scientific status:** finite 3×4 \(S_3\) group theorem DERIVED;
hosted cross-block stored-pair audit PASS; independent complete
Q5-principal stored-pair numeric replay OPEN; full-state signed
third-moment production OPEN. Strengthened first-Wilson squared
weight candidate \(17,074,763/10^{12}\) SOURCE-CONDITIONAL /
FORMAL HOLD. Four-dimensional continuum Yang–Mills OPEN.
