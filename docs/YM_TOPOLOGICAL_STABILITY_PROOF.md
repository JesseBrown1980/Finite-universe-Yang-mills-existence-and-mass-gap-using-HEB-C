# Volume-uniform gap above the eight-state flat cluster: proof plan via quantum-double stability

Status: **working proof document.** The architecture is Jesse Daniel Brown's.
Lemmas marked **proved** are proved below. Lemmas marked **to instantiate**
carry the theorem-matching described in their section.

## 0. The model and the claim

Spatial periodic Lx × Ly lattice, links carry g ∈ S₃, physical space
𝓗_phys = gauge-invariant functions, and

  H = J_E·E + J_B·M,  r = J_B/J_E,
  E = Σ_ℓ h_{E,ℓ},  h_{E,ℓ} = 3·I − Σ_{t∈T} L_t^ℓ,  T = {(12),(13),(23)},
  M = Σ_p m_p,  m_p = 2 − χ_std(g_p).

**Target theorem.** There exist r₀ and c > 0, independent of Lx and Ly within
an admitted family of growing two-dimensional tori, such that for all r ≥ r₀

  E₉(r, L) − E₈(r, L) ≥ c·J_B = c·r·J_E,

and the width E₈ − E₁ of the eight-state band is at most
J_B·poly(L)·exp(−a·L^{3/8}). Here L is the shorter torus side.

This is the gap above the topologically degenerate eight-state band. The
splittings inside the band are controlled by the width estimate. The admitted
geometry grows both torus sides; the 2×L strips form a separate family (§6, Klich).

## 1. Raw-space extension and local spectra (proved)

Let 𝓗_raw = ⊗_ℓ ℂ[S₃], A_v be the vertex gauge-averaging projector,
Q_v = I − A_v, and B_p the projector onto trivial holonomy, Q_p = I − B_p.

- **m_p.** χ_std takes the value 2 on e, 0 on transpositions and −1 on
  3-cycles. So m_p ∈ {0, 2, 3}, with zero exactly on trivial holonomy. Hence
  ker m_p = ran B_p, and **2·Q_p ⪯ m_p ⪯ 3·Q_p**.
- **h_{E,ℓ}.** Σ_t L_t is the adjacency operator of the Cayley graph of S₃
  with generators T. That graph is K₃,₃ (even ↔ odd permutations), whose
  adjacency spectrum is {3, −3, 0⁴}. So **spec h_{E,ℓ} = {0, 3, 6}** with
  multiplicities 1, 4, 1, and ‖h_{E,ℓ}‖ = 6 exactly. The relevant input is
  this uniform local norm; ‖E‖ itself is extensive.
- **Physical restriction.** Define H₀ = Σ_v Q_v + Σ_p m_p and
  H_λ = H₀ + λE, with λ = 1/r. On 𝓗_phys every Q_v vanishes, so
  H_λ|_phys = M + E/r = H/J_B.

## 2. Commuting, frustration-free, uniformly gapped (proved)

- **Commutation.** The Q_v commute with one another. m_p is a class function
  of the holonomy and is gauge invariant, so [m_p, Q_v] = 0. The m_p are
  diagonal in the configuration basis and commute with one another.
- **Frustration-free.** The common zero space is: gauge invariant and flat at
  every plaquette. That is the ground space of Kitaev's quantum double D(S₃),
  of dimension 8 on a torus (one state per irreducible representation of
  D(S₃)). It equals HEB-C's eight flat states, which `flatcomp` confirms
  exactly on 2×2, 2×3, 2×4, 2×5 and 3×3.
- **Uniform local gap.** Every nonzero simultaneous eigenvalue sum of any
  subset of terms is ≥ 1, since Q_v has nonzero eigenvalue 1 and m_p ≥ 2. So
  both the global gap and every regional (Local-Gap) gap are ≥ 1, independent
  of region size.
- **Same local ground projectors.** On any region, the joint zero projector of
  the H₀ terms supported there equals that of the corresponding
  quantum-double terms, because ker m_p = ran B_p.

## 3. Topological order transferred from Cui et al. (to instantiate)

Cui, Ding, Han, Penington, Ranard, Rayhaun and Shangnan, *Kitaev's quantum
double model as an error correcting code*, Quantum 4, 331 (2020), prove local
indistinguishability for the quantum double of any finite group. On a region
A with a suitable buffer inside B, every normalized state in ran P_B has the
same reduced state ρ_A. Hence, for every O_A,

  P_B O_A P_B = Tr(ρ_A O_A)·P_B,

which is the exact-error form of Michalakis–Zwolak's Local-TQO compression. By
§2 the local ground projectors are the same as for the quantum double, so this
applies to H₀ verbatim.

**Still to write down:**
- the dictionary between Cui's regions (contractibility and buffer),
  BHM's TQO-1/TQO-2 and MZ's Local-TQO, without treating them as identical;
- edge-orientation and plaquette conventions matched to HEB-C's lattice
  (`torusl`);
- the region shapes (balls versus rectangles) used by each theorem.

## 4. Bounded local perturbation (proved)

E = Σ_ℓ h_{E,ℓ} is a sum of one-link terms with ‖h_{E,ℓ}‖ = 6. Each commutes
with every A_v, because Σ_t L_t is a sum over a full conjugacy class and is
central. So λE is a uniformly bounded, strictly local perturbation of strength
6λ = 6/r per link, and [H_λ, Π_phys] = 0 for every λ, with Π_phys = Π_v A_v.

## 5. The perturbed band stays physical (proved, given an isolated band)

Suppose the ground-originating band of H_λ stays isolated for 0 ≤ λ ≤ λ*.
Let P_λ be its Riesz spectral projector. It is continuous in λ and commutes
with Π_phys, so R_λ = P_λ(I − Π_phys) is a continuous family of orthogonal
projections. Its rank is therefore constant on [0, λ*]. Since R₀ = 0 (the
unperturbed ground space is physical), R_λ = 0 throughout. So
ran P_λ ⊆ 𝓗_phys, and the eight lowest physical levels of H/J_B are that band.

No nondegeneracy, eigenvector continuity or momentum restriction is used. An
energy comparison would not work here: the physical band's energy, about
λ·6·Lx·Ly, exceeds the vertex penalty 1 at large volume, but the blocks never
mix because they are exactly invariant.

## 6. Stability theorem and scaling (to instantiate)

**Primary: Bravyi–Hastings–Michalakis**, *Topological quantum order: stability
under local perturbations*, J. Math. Phys. 51, 093512 (2010), arXiv:1001.0344.
Its local-term formulation admits positive semidefinite commuting terms with a
uniform local gap. So m_p ∈ {0, 2, 3} needs no change of theorem. With
TQO-1/TQO-2 from §3 and the perturbation from §4, for λ ≤ ε₀/6 it gives:
- a band around the ground energy, of width ≤ poly(L)·e^{−aL^{3/8}} (in H/J_B units);
- separation from the rest of the spectrum by a constant independent of L.

Then §5 places that band in 𝓗_phys, and rescaling by J_B gives the target
theorem with r₀ = 6/ε₀.

**Alternative: Michalakis–Zwolak**, *Stability of frustration-free
Hamiltonians*, Commun. Math. Phys. 322, 277 (2013), arXiv:1109.1588. Its added
generality is dropping commutativity, which H₀ does not need. It assumes
Local-TQO and Local-Gap. Local-Gap is §2. Local-TQO is the compression
identity in §3, once the region dictionary is written.

**Geometry.** The admitted family must have both torus sides growing, so that
the code distance grows. Klich, *On the stability of topological phases on a
lattice*, Ann. Phys. 325, 2120 (2010), arXiv:0912.0945, shows instability
mechanisms in thin-torus limits. The 2×L strips are therefore a separate
family of their own.

**Constants.** BHM proves that ε₀ exists; its value is small, so r₀ from the
theorem lies well above 9. The certified finite-r data
show where the regime actually starts on small lattices; the theorem cannot.

## 7. Finite certificates (evidence alongside the proof)

All entries are integer interval-inertia certificates. The scopes are:

| Lattice | Scope | E₉ − E₈ for all r ≥ 9 | Source |
|---|---|---|---|
| 3×3 | zero momentum | ≥ 23.357514 J_E | `native/ym/reference/`, regenerated on fresh machines |
| 2×2, 2×3, 2×4 | zero momentum | ≥ 22.727 / 22.798 / 22.565 J_E | `native/ym/results/2xL/` |
| 2×2, 2×3 | full physical space, all momenta (r = 9 counts) | N(t₁) = N(t_B) = 8 | reflection-only sectors through the backend, equal to the direct full-matrix counts |

The data agree with the theorem's shape: E₉ − E₈ ≈ 3r ∝ J_B. On 3×3 the band
width shrinks rapidly with r. On 2×L the width stays roughly constant in L, as
expected for a fixed short side of 2.

## References

- Bravyi, Hastings, Michalakis, J. Math. Phys. 51, 093512 (2010), arXiv:1001.0344.
- Michalakis, Zwolak, Commun. Math. Phys. 322, 277 (2013), arXiv:1109.1588.
- Cui, Ding, Han, Penington, Ranard, Rayhaun, Shangnan, Quantum 4, 331 (2020).
- Klich, Ann. Phys. 325, 2120 (2010), arXiv:0912.0945.
- Mariani, Pradhan, Ercolessi, arXiv:2301.12224 (finite-group lattice Yang–Mills Hamiltonians and the gauge-invariant Hilbert space).

Bibliographic details are from memory and must be checked against the
publishers before external use.
