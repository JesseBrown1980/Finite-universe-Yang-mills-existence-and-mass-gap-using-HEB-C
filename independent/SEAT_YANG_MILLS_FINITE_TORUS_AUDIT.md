# Other-seat independent finite S₃ Yang–Mills torus audit

**Parent source:** `stage2g-certified-torus-gap` at `fe0daee0aa13e7d78a86a0374b2340d503dd8943`.

**Scope:** An independently written reconstruction of the existing 2×2 periodic, 8-link, 4-face **finite S₃** gauge model, followed by an exact-arithmetic recheck of Stage 2G's Collatz–Poincaré energy bounds. This is not a new physics operator, a continuum model, or an independently authenticated physical measurement. **Do not merge with or supersede PR #4, #5 or #6.**

## What the checker reconstructs

The complete implementation is `independent/seat_yang_mills_audit.py`, which uses Python's standard library and **does not call** the Rust implementation, Rust eigenvalue certifier, or existing HBP verifier. All published results are stored in `independent/seat_yang_mills_audit.measure` with `json=0`.

1. Generate all six permutations of three symbols as a group and calculate composition/inverses, instead of importing the Rust `PERM` multiplication table.
2. Derive **1,393** orbit count separately from Burnside's lemma:
   
   `(6^5 + 3×2^5 + 2×3^5)/6 = (7776 + 96 + 486)/6 = 1393`.
   
   Enumerate the entire simultaneous-conjugation orbit partition of the 7,776 tree-gauge-fixed configurations independently, and verify the orbit weights sum to 7,776.
3. Build each 8-link representative on the actual periodic 2×2 graph; calculate tree gauge frames by graph traversal, rather than hard-coding the Rust `gauge_fix` equations. Test **33,432** local gauge transformations (1,393 representatives × four sites × six group elements) for unchanged orbit and magnetic action.
4. Reconstruct the S₃ character-based four-plaquette magnetic term, and the electric Laplacian by applying the three transpositions to each of eight oriented links. Require **32,385** nonzero stored coefficients, zero electric row sums, `W`-weighted Hermiticity, connectivity, and exactly eight flat configurations.
5. Build a noncontractible Wilson character mode and check the **exact electric eigenvalue 6** and weighted orthogonality to the constant mode. The lower-bound assertion that 6 is the *smallest* nonzero physical electric eigenvalue additionally relies on the standard one-link/gauge-invariance representation argument; an eigenvector alone does not prove minimality.
6. Serialize the independently reconstructed operator using the **published canonical byte-order contract** and require its SHA-256 to equal the Rust certificate's operator fingerprint:
   
   `b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3`.

The match gives reproducible agreement on the exact finite matrix under the same geometry, S₃ character, and serialization convention. It is stronger than merely running the same Rust test on a second machine, but it is not an independent derivation of the chosen physical Hamiltonian from continuum axioms.

## Ground-state and conservative gap check

The independently constructed weighted electric/magnetic matrix was used in Python's arbitrary-precision integer arithmetic. For each coupling, a fresh 256-step positive shifted-power witness produced outward `1/1,000,000` Collatz–Wielandt enclosures. The Poincaré comparison uses the established **finite pure-electric gap 6**, leading to the following positive gap lower bounds.

| `JE,JB` | Ground energy `E0` enclosure | Conservative `E1-E0` lower bound |
|---|---|---|
| `1,1` | `[7634198,7634199]/1000000` | `671034/1000000` |
| `3,5` | `[36699227,36699228]/1000000` | `344589/1000000` |

The original PR #4 reports the **stronger** rank-one inertia results:

| `JE,JB` | PR #4 reported `E1-E0` interval |
|---|---|
| `1,1` | `[5605801,5608535]/1000000` |
| `3,5` | `[14140772,14142823]/1000000` |

**Important distinction:** this audit independently reconstructs the matrix, then **replays the same Collatz–Poincaré mathematical approach** as Stage 2G. It does **not** independently reprove the Stage 2H rank-one Cholesky inequality or those stronger `E1` intervals. No exact eigenvalue solving or full spectrum is claimed. A separate algebraic audit of the inertia certificate remains an open review requirement.

## Reproducibility

```bash
python3 independent/seat_yang_mills_audit.py > /tmp/seat-yang-mills-audit.measure
cmp /tmp/seat-yang-mills-audit.measure independent/seat_yang_mills_audit.measure
```

The dedicated GitHub Actions workflow re-runs the unmodified checker, compares its entire pipe-delimited output to the pinned measure, and requires eight `json=0` lines. All calculations above were run locally before publishing and passed.

**Scientific limitations:** finite 2D spatial lattice; finite non-Abelian **S₃** gauge group, not the compact-simple Lie-group continuum gauge theory of the Clay question; no thermodynamic-limit sequence of periodic lattices, no rigorously established confinement/string tension, no 4D continuum Yang–Mills existence or mass gap. The two finite couplings and their local gap witnesses do not establish a uniform gap as lattice spacing tends to zero.

**Review stance:** another seat's separately written mathematical model implementation, not a claim of institutional independence or independent physical-host attestation. The operator's definition, group, lattice graph, and digest layout are deliberately shared with the reviewed repository and form the comparison contract.
