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

## 3. Topological order transferred from Cui et al. (written for even square tori)

Cui, Ding, Han, Penington, Ranard, Rayhaun and Shangnan, *Kitaev's quantum
double model as an error correcting code*, Quantum 4, 331 (2020), prove local
indistinguishability for the quantum double of any finite group. On a region
A with a suitable buffer inside B, every normalized state in ran P_B has the
same reduced state ρ_A. Hence, for every O_A,

  P_B O_A P_B = Tr(ρ_A O_A)·P_B,

which is the exact-error form of Michalakis–Zwolak's Local-TQO compression. By
§2 the local ground projectors are the same as for the quantum double, so this
applies to H₀ verbatim.

**The dictionary, for an L x L torus with L = 2K even.** Written November 3. A second reader is open.

- **Orientation.** `torusl` (`Lat::new`) has links h(x,y) from (x,y) to (x+1,y) and v(x,y) from (x,y) to (x,y+1), each owned by the cell
  (x,y). Cui et al. take any oriented lattice on a closed surface. Flatness and m_p are class functions of the holonomy, so the base point
  and direction of a plaquette loop leave them unchanged.
- **Cui, Theorem 3.1.** For rectangular sublattices A′ ⊂ B′ in contractible subregions with V(A′) ⊂ V(B′)°, every normalized state with
  A_v ψ = B_p ψ = ψ for all v ∈ V(B′)° and p ∈ F(B′) has one reduced state ρ on A′.
- **BHM, §2.** H₀ = Σ_{C∈S(2)} G_C over 2×2 squares of sites, on Z_K × Z_K, "otherwise consider a coarse-grained lattice". With P_B the product of the zero
  projectors of G_C for C ⊆ B: TQO-1 asks P O_A P = c P for A ∈ S(r), r ≤ L*. TQO-2 asks that ρ_A = Tr_{A^c} P and Tr_{A^c} P_B have one kernel, for B ∈ S(r+2)
  the square of A and its nearest neighbours.
- **Unit cells fall one layer short of Cui's hypothesis.** With one site per cell, each 2×2 square holds exactly one star and one plaquette, so the assignment is forced.
  Then P_B lacks a row and a column of the plaquettes of the smallest B′ whose interior holds V(A′), so ran P_B lies outside that ℋ_B′.
  TQO-2 on unit cells may still hold, and Cui's theorem alone leaves it open.
- **2×2 sites close it.** Take each BHM site to be 2×2 cells, 8 links, so K sites per side. Assign the plaquette at (a,b) to the block whose first site column is a/2 − 1 for
  even a and (a−1)/2 for odd a, likewise b. Assign the star at (x,y) to the block whose first site column is x/2 − 1 for even x and (x−1)/2 − 1 for odd x,
  likewise y. G_C is the sum of the terms assigned to C. These commute and are positive semidefinite, with integer spectrum and every nonzero eigenvalue ≥ 1, so G_C² ≥ G_C.
  For A ∈ S(r) at site (X₀,Y₀), let x₀ = 2X₀, y₀ = 2Y₀. A′ has vertices x₀ … x₀+2r by y₀ … y₀+2r, and B′ one original layer more on each side. Then A's links lie in A′,
  V(A′) = V(B′)°, B′ spans less than L for r ≤ K − 2, and every plaquette and interior star of B′ is assigned to a block inside B.
  MEASURED by [`check_bhm_dictionary.py`](check_bhm_dictionary.py), which decides these inclusions with no group and no state: 38,352 regions, every even L from 8 to 40, 0 failures. It also prints the unit-cell
  failure.
- **Consequence.** ran P ⊆ ran P_B ⊆ ℋ_B′, so every normalized state in ran P_B has reduced state ρ_A on A. Hence Tr_{A^c} P_B = rank(P_B) ρ_A and Tr_{A^c} P = rank(P) ρ_A, one kernel, which is TQO-2.
  And P O_A P = Tr(ρ_A O_A) P, which is TQO-1. L* = K − 2 ≥ K/2 for K ≥ 4.

MZ's Local-TQO is the same compression identity on their regions, and it stays the alternative named in §6.

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

## 6. Stability theorem and scaling (matched for even square tori)

**Primary: Bravyi–Hastings–Michalakis**, *Topological quantum order: stability
under local perturbations*, J. Math. Phys. 51, 093512 (2010), arXiv:1001.0344.
Its local-term formulation admits positive semidefinite commuting terms with a
uniform local gap. So m_p ∈ {0, 2, 3} needs no change of theorem. With
TQO-1/TQO-2 from §3 and the perturbation from §4, for λ ≤ ε₀/6 it gives:
- a band around the ground energy, of width ≤ poly(L)·e^{−aL^{3/8}} (in H/J_B units);
- separation from the rest of the spectrum by a constant independent of L.

Then §5 places that band in 𝓗_phys, and rescaling by J_B gives the target
theorem with r₀ = 6/ε₀. That count of one link is corrected beside it, in the matching below.

**The matching, November 3.** BHM §2 states its terms as pairwise commuting and positive semidefinite with G_A² ≥ G_A, as used here, though its introduction speaks of projectors. Its Theorem 1:
for V = Σ_r Σ_{A∈S(r)} V_{r,A} with ‖V_{r,A}‖ ≤ J e^{−μr}, there are J₀, c₁, c₂ > 0 depending only on μ and D such that for J ≤ J₀ the spectrum of H₀ + V lies, up to a shift, in bands
I_k = [k(1 − c₁J) − δ, k(1 + c₁J) + δ], k in the spectrum of H₀, δ = poly(L) exp(−c₂ L^{3/8}), with I_k separated from the others by at least 1/2 when J < J_k = 1/(c₁(4k + 2)).

On the 2×2 sites of §3, V = λE has only r = 1 terms, each of norm 48λ: 8 links at ‖h_{E,ℓ}‖ = 6. So J = 48 λ e^{μ}, for any μ > 0, and with H/J_B = H_λ on 𝓗_phys:

  (E₉ − E₈)/J_B ≥ 1 − c₁J − 2δ(K), from the ends of I₀ and I₁, for J ≤ J₀.

The first version of this section read "E₉ − E₈ ≥ J_B/2 for every r ≥ r₀ = 48 e^{μ} / min(J₀(μ,2), 1/(2c₁(μ,2))), on L × L tori with L even and K = L/2 ≥ 4". That skipped δ. The second reader
(GPT-6, on [#88](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/88)) found it and gave the repair below. BHM's prose states the separation of 1/2 in its large-L setting.

- **Large volume.** Take J ≤ min(J₀, 1/(4c₁)), and K₀ with δ(K) ≤ 1/8 for every K ≥ K₀. Then E₉ − E₈ ≥ J_B/2 for every even L = 2K with K ≥ K₀.
- **The finitely many smaller sides, by min–max.** On 𝓗_phys, H/J_B = M + E/r with E ≥ 0. M has the eight flat states as its zero space, and M ≥ 2 off it, since m_p ≥ 2 on a non-flat plaquette, so E₉/J_B ≥ 2.
  Each L_t moves a link and so changes the holonomy of its plaquettes, which gives P L_t P = 0 on the flat space P, and P E P = 3·(2L²)·P = 6L²·P. With the flat states as the trial space, E₈/J_B ≤ 6L²/r. So

  E₉ − E₈ ≥ J_B (2 − 6L²/r), which is at least J_B/2 for r ≥ 4L².

  The second reader's form uses only ‖E‖ ≤ 12L² and the raw-space gap: E₉ − E₈ ≥ J_B (1 − 12L²/r), at least J_B/2 for r ≥ 24L². Either closes the step.
- **Together, for every even L:**

  E₉ − E₈ ≥ J_B/2 for every r ≥ r₀ = max(48 e^{μ}/J₀, 192 c₁ e^{μ}, 4 (2K₀)²),

  with J₀, c₁ and K₀ taken at D = 2 and a chosen μ > 0. So c = 1/2 on this family. This is an existence formula, since K₀, J₀ and c₁ await extraction from BHM's proof.

Open:
- **r₀ as a number.** J₀, c₁, c₂ and the polynomial in δ come from BHM's proof, and they have not been traced through it. The certified finite-r data in §7 stand beside this as evidence.
- **Odd sides and rectangles.** BHM states Z_L × Z_L, and the dictionary here is checked for even L. Sites of mixed size for odd L, and Lx ≠ Ly, each need their own check.
- **The rest of BHM.** This matching rests on its §2 and Theorem 1. Whether its proof uses anything beyond those hypotheses for non-projector G_A has yet to be read through.
- **Other finite groups.** Cui's theorem covers any finite group, so this route extends to Q8, 2T, 2O and 2I once each group's m_p, its local gap and its link norm replace S₃'s.
- **Second reader.** GPT-6 read §3 and this section at `ea96c16`, with its own implementation of the geometry: 38,352 regions, 0 failures, geometry PASS, the matching supported, with the finite-size step above to correct. Its reports are on [#88](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/88). It works at the operator's direction and is a different model from this seat's. A reader outside the project is open.

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

**Constants.** BHM proves that ε₀ exists, and the theorem's explicit constants
fix r₀ once the instantiation is complete. Until then r₀ is not determined. In
particular, r₀ = 9 is not established. The certified finite-r data show, lattice
by lattice, the coupling from which the gap is measured.

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

**Added November 3, 2026: whole-space bounds at r = 9, on larger lattices.** These come from Perron vectors, by Barta and interlacing, rather than from interval inertia:

| Lattice | E₉ − E₈ ≥ | Source |
|---|---:|---|
| 3×3 | 23.914694 J_E | [`perroncert`, every row of the store](../native/ym/results/3x4_stream/perron/PERRON-BOUND.md) |
| 3×4 | 24.039673 J_E | The same |
| 4×4 | 23.947629 J_E | [No store: the hybrid vector and a tighter E₈](../native/ym/results/3x4_stream/perron/vector/VECTOR-BOUND.md) |
| 4×5 | 23.618291 J_E | The same |
| 5×5 | 21.792208 J_E | The same |

Their lower bounds sit within about 5 J_E of 3r = 27 on each torus up to 5×5, which fits the theorem's shape. Each is a statement about one finite torus, and uniformity in volume stays with this plan. **Next here:** the finite-size constant r₀ as a number, odd and rectangular tori, and the rest of the matching in section 6.

## References

- Bravyi, Hastings, Michalakis, J. Math. Phys. 51, 093512 (2010), arXiv:1001.0344.
- Michalakis, Zwolak, Commun. Math. Phys. 322, 277 (2013), arXiv:1109.1588.
- Cui, Ding, Han, Penington, Ranard, Rayhaun, Shangnan, Quantum 4, 331 (2020).
- Klich, Ann. Phys. 325, 2120 (2010), arXiv:0912.0945.
- Mariani, Pradhan, Ercolessi, arXiv:2301.12224 (finite-group lattice Yang–Mills Hamiltonians and the gauge-invariant Hilbert space).

Checked November 3 against arXiv and the journal pages: Cui et al. is arXiv:1908.02829. arXiv lists the second author of 1109.1588 as Justyna Pytel, and the journal as Zwolak. Mariani et al. carries the DOI 10.1103/PhysRevD.107.114513.
A shorter proof of the same stability result: Bravyi, Hastings, arXiv:1001.4363.
