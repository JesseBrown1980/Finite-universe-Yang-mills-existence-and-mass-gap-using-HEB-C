# Y137 — 429,981,696-dimensional exact matrix-free index and pilot

Research DRAFT (November 16, 2026), stacked on source-certified 20,736-dimensional PR #242. The next proposed **429,981,696** dimension means approximately **430 million**, not 429 billion. A literal 429-billion-dimensional independent basis exceeds the finite 3×4 S3 physical Hilbert space, which has 2,177,317,873 gauge-invariant orbit states.

## Mathematical construction

After spanning-tree gauge fixing, configurations are 13-element words over S3 subject to simultaneous conjugation. The original generator chooses the lexicographically minimum conjugate. A 6-bit finite automaton records which simultaneous conjugations are already lexicographically larger than the candidate prefix. It rejects any link digit with a smaller, still-tied conjugate. Its integer suffix-count recurrence directly ranks or unranks **any** canonical 13-link configuration without materializing the 2.17-billion-state list.

The DP count is cross-checked against exact Burnside:

\[
F(0,0)=(6^{13}+3\cdot 2^{13}+2\cdot 3^{13})/6
=\boxed{2,177,317,873}.
\]

The accepted 20,736-dimensional basis is retained exactly. Its physical support occupies 8,042 canonical K2 orbits and 20,592 selected shell-3 orbits, for **28,634** physical support orbits. Rank and exclude those 28,634 keys. Append the **first 429,960,960 lexicographic canonical orbit indicators outside the old support**. Each newly added direction is physically W-orthogonal to all old directions, and all added coordinate directions are mutually orthogonal with positive S3 conjugacy orbit weights. This gives an exact 429,981,696-dimensional **strictly independent nested basis**, without allocating a dense Gram or Hamiltonian.

## Hosted acceptance scope

The real pilot regenerates the pinned original K2/K3 source and 20,736-dimensional basis, checks every old support rank, and measures **512 or more deterministically spaced new-basis states**. Each measured row is reranked/unranked and checked against the historical canonicalization; its **72 raw electric moves**, magnetic diagonal, orbit weight and projection are computed directly using the historical source. All nonzero couplings to the eight flat, four Krylov, 132 K2 and 20,592 shell-3 original directions are computed by exact physical source action. Weighted reverse-edge identities are independently measured on the early selected rows. The sampled-row SHA-256, source-support SHA, last selected ordinal rank, resource usage and full count are emitted as a reproducible receipt.

This **pilot does not** enumerate all new matrix rows, create the complete bidirectional 429-million-row operator, certify the first two eigenvalues or residuals, or establish a nonzero Wilson spectral weight. Those are separately gated production tasks. The complete new-row scan would require **30,957,189,120** candidate electric transitions at 72 per added orbit, plus the old basis/source joins and graph certification. An uncompressed dense matrix would contain **184,884,258,895,036,416 entries**, approximately **1.48 exabytes** even at only eight bytes per entry.

The pilot is a real source-backed indexing and electric-row run, **not a claim that the requested full 429-million-dimensional spectral calculation has completed**. The positive first-excitation Wilson weight and the 4D continuum Yang–Mills gap remain OPEN/HOLD. Research PR remains DRAFT pending independent acceptance.

## Reproduce

- python3 -I -B independent/y137-h429981696-matrixfree-20261116/orbit_unrank_pilot.py toy
- python3 -I -B independent/y137-h429981696-matrixfree-20261116/orbit_unrank_pilot.py pilot

Hosted workflow: .github/workflows/y137-h429981696-matrixfree-pilot.yml.
