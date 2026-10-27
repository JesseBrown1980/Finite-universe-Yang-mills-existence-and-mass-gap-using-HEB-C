# The continuum track (separate from the finite certificates)

The finite pipeline certifies exact spectral facts on finite lattices with the gauge group
S₃ in a Hamiltonian formulation: counts, gaps, seals and receipts. The Clay problem asks
for a quantum Yang–Mills theory on ℝ⁴ for a compact simple gauge group G (such as SU(N)),
satisfying the field-theory axioms, with a mass gap Δ > 0. This track lists the
obligations between the two, so that each can be worked and checked on its own.

```
exact finite-lattice theory
→ explicit renormalization transformation (block / phase-cell)
→ localized effective actions
→ uniform stability and error bounds across scales
→ coupling flow consistent with asymptotic freedom
→ continuum and infinite-volume limits
→ Osterwalder–Schrader / Wightman reconstruction
→ separately: the mass gap
```

**The visible route** is Balaban's constructive renormalization-group program for lattice
gauge theory in four dimensions: cluster expansions, localized effective actions, and
recursive coupling-constant equations in the small-field regime, with ultraviolet control
from asymptotic freedom. It is a research route toward uniform estimates. Each step from
our finite S₃ Hamiltonian certificates to a four-dimensional SU(N) continuum theory is its
own obligation: the gauge group, the Euclidean versus Hamiltonian formulation, and the
limits.

**The October 2026 announcement:** existence of 4D Yang–Mills and QCD, building on
Balaban's approach, with a Lean formalization reported. It claims existence, not a mass
gap. The manuscript and Lean files are not yet public; a group led by David Gross is
writing them up. When they appear, their definitions are candidate reference material.
Each one is mapped to our setting, or formally related to it, before anything rests on it.

**What the finite machinery can carry here:**
- exact small-lattice renormalization steps, partitions and effective-action identities,
  checked in integers with receipts;
- per-scale bounds written as explicit recurrences, so that summability is proven
  rather than sampled;
- each claimed lemma, once public, mapped to its assumptions, proof object and place in
  the chain.

Every lattice size, and every scale, earns its own certificate.
