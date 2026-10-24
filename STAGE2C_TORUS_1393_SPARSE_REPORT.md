# Stage 2C — Exact periodic 2×2 S₃ torus: 1,393-state sparse interacting Hamiltonian

**Date:** October 24, 2026  
**Native source:** [native/src/torus2.rs](native/src/torus2.rs)  
**Execution:** Rust 1.81, integer arithmetic only, no native JSON/Node/JavaScript/V8 or screen, and Clippy zero warnings.

## The physical gauge geometry

The periodic 2×2 lattice has **4 vertices, 8 directed, independently variable gauge links, and 4 plaquettes**. The oriented link set is:

- x0: 0→2, x1: 1→3, x2: 2→0, x3: 3→1
- y0: 0→1, y1: 1→0, y2: 2→3, y3: 3→2

The opposite directed links on this very small periodic lattice are distinct *parallel fundamental edges*. They are not forced to be group inverses.

The full unconstrained group-link space has **6⁸ = 1,679,616** assignments. Fixing a spanning tree of three edges leaves **6⁵ = 7,776** configurations. A single residual S₃ rotation simultaneously conjugates all five remaining loop coordinates. Exact canonicalization leaves **1,393 distinct Gauss-invariant orbit-value basis states**. A separate BFS using just the generating transpositions independently verifies all 1,393 orbit sizes and their multiplicities; multiplying by the tree-fixing factor 216 recovers the 1,679,616 raw configurations.

Each of the four periodic plaquette holonomies and local vertex gauge moves is independently checked for gauge invariance.

## Explicit interacting electric and magnetic operators

The 1,393×1,393 electric matrix is not assumed or pre-filled. It is reconstructed row by row by applying **24 actual link moves** (eight edges × all three S₃ transpositions), then tree-gauge-fixing and classifying the result in the physical Gauss sector.

The magnetic term multiplies each orbit by the sum over the **four periodic faces** of (2 − χ_standard(plaquette holonomy)). The common Hamiltonian is H = J_E H_E + J_B H_B. It has **32,385 stored nonzero electric entries**, as measured by the running implementation.

Because the physical basis stores *orbit values*, its inner product is weighted by the orbit cardinalities. The correct self-adjointness check is w_i H_ij = w_j H_ji. This is verified for every stored sparse entry. The code separately checks the zero electric row sum, nonpositive off-diagonal entries, connectivity, exact gauge invariance and nonnegative quadratic forms.

## Spectral results: quantified versus unquantified

| Couplings | Rigorous finite-S₃ conclusion | Numeric bound |
|---|---|---|
| J_E=0, J_B=0 | Entire Hamiltonian is zero, 1,393 degenerate states | Exact gap 0 |
| J_E=1, J_B=0 | Ground state constant, first excitation on a noncontractible length-two loop | **Exact gap 6** |
| J_E>0, J_B=0 | Same electric operator rescaled | **Exact gap 6×J_E** |
| J_E=0, J_B>0 | Eight gauge-inequivalent flat-connection ground states | **Exact gap 0** |
| J_E>0, J_B>0 | Sparse electric graph connected; stoquastic weighted-self-adjoint Hamiltonian has a unique ground state by Perron–Frobenius | **Positive, but numerical interval not yet certified** |

The exact electric-only gap uses the raw per-link S₃ Cayley eigenvalues 0, 3, 6. An electric eigenvalue 3 would require precisely one excited link, which cannot produce a nonconstant locally gauge-invariant state. A length-two noncontractible Wilson character is orthogonal to the constant ground state and is independently verified across **all 1,393 rows** to be an eigenfunction of energy 6.

In the magnetic-only model, all four plaquette holonomies can be trivial while the torus retains noncontractible commuting X/Y Wilson holonomies. The code verifies exactly **eight** distinct simultaneous-conjugation classes of commuting flat Wilson pairs. Thus the first excitation gap defined as E₁−E₀ is zero in that limit. The count of eight flat *potential minima* remains a property of the operator even when the electric term is turned on; with both couplings positive, the Hamiltonian's ground state is no longer simply one of those eight basis vectors.

The mixed-coupling qualitative positive-gap result follows from Perron–Frobenius irreducibility and **does not** constitute a rigorous numerical lower bound for E₁−E₀. An independently verified sparse integer/rational eigensolver remains the next research hurdle.

## HBI / HBP / SHA / SH / HASH replay

The torus command saves four native plain-text artifacts: run.hbp, index.hbi, run.anchor and run.measure. A source SHA-256 commits the full gauge orbit keys, orbit weights, five-link representatives, magnetic diagonal and all sparse electric rows. The SH short source locator is the first 16 hexadecimal characters of the full source digest.

The HBI and HBP records include deterministic byte lengths, row digests and chained HASH. The verifier does not merely accept the recorded root: it rebuilds the **full 1,393-dimensional torus operator**, regenerates its digests, and checks for byte-for-byte identity. Deliberately corrupted HBP receipts and HBI indices must be rejected. The anchor is a hash commitment, not an independently authenticated digital signature.

## Reproduction

From the repository's **native/** directory, with Rust 1.81 installed:

1. Run: cargo +1.81.0 test --all-targets --locked --offline
2. Run: cargo +1.81.0 clippy --all-targets --locked --offline -- -D warnings
3. Run: cargo +1.81.0 build --release --locked --offline
4. Run: target/release/hebc torus2-spectrum 1 0 torus2-electric
5. Run: target/release/hebc torus2-verify torus2-electric
6. Run: target/release/hebc torus2-spectrum 0 1 torus2-magnetic
7. Run: target/release/hebc torus2-spectrum 1 1 torus2-interacting
8. Run: target/release/hebc torus2-verify torus2-interacting

The optional localhost adapter exposes GET /torus2/JE/JB over conventional HTTP/1.1; *HTTP-0* is the internal virtual-kernel addressing name, not a claimed HTTP transport standard.

**Research boundary:** this is a finite discrete S₃ gauge theory. Neither the nonzero electric gap nor the unique interacting finite-volume ground state solves the Clay four-dimensional continuum Yang–Mills existence/mass-gap conjecture.

## Next exact milestone

Compute tight, **independently certified rational intervals** for the two lowest eigenvalues of the full 1,393-dimensional **mixed-coupling** operator at (J_E,J_B)=(1,1) and (3,5), respecting the correct weighted inner product. The present qualitative Perron–Frobenius check should not be presented as a numerical spectral-gap certificate. This work remains open on [Issue #2](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/2).
