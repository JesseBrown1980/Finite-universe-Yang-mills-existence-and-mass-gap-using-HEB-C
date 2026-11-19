# Y137 — independently reconstructed original Q5 physical V1 boundary

This source-level certificate challenges the **original frozen Q5 source** by reconstructing
the physical signed V1 response directly from the accepted frozen Q4 residual and an
independently implemented 72-move periodic 3×4 S3 gauge-fixed electric rule.

## Immutable sources

- Original eight Q5 packed V1/b groups: [run #43615270310](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43615270310), 18,598,040 canonical Q5 states, 3,140,900,108 bytes, all eight exact SHA256 fingerprints frozen in `q5_boundary.py`.
- Frozen original K3 trial `Y`, Q4 positive packed residual `P`, support lookup and immutable original energies from `independent/y137-real-Q-moment-20261114/mu1_shard.py`.
- Independent gauge-fix, orbit, magnetic and all 72 electric moves from `independent/y137-d11-shell5-spill-20261114/independent_move_rule.py`.

For each of 27 SHA-selected actual Q5 states from each original Q5 group, use

```text
R_K3 = original signed K3 residual
R_Q4 = -P_Q4
R_Q5 = 0
D_i = b(72+9*m_i) - z
V1_Q5 = [(D-bC)R]_Q5 = b * sum_(neighbor j in Q4) c_Q5,j P_Q4,j.
```

Thus the archived original `Q5 V1/b` must **exactly equal** the independently
reconstructed nonnegative eight-lane sum for **both** original source energies.
The checker derives all (Q5\to Q4) links and their weighted reverse
identities with a separately written S3 permutation/gauge rule. It also
reconstructs all 72 Q5 raw moves, canonical orbit weights and magnetic numbers.

## Acceptance scope

One successful eight-shard hosted fan-in would establish:

- all eight original Q5 source group SHA256 hashes, complete original 18,598,040-row archive format, counts, byte lengths and ordered buckets authenticated;
- **216 disjoint original Q5 physical source states** checked on both energies, or **3,456 exact Q5 source components**;
- **15,552 raw electric moves** independently generated and supported Q5-to-Q4 reverse edge identities;
- all **11 modified/fake receipt controls rejected**.

A full positive run would strengthen original-source confidence in the original Stage C
20,738,636-state calculation, together with the previously completed 864-state
K3/Q4 source challenge in [draft #322](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/322).

**This is still a sampled source audit.** The accepted original Q4 positive residual
and K3 Y remain premises. Full original Q5/Q4/K3 source regeneration at every
physical state, independent full third-moment 8×8 matrix and Perron full-store
reconstruction remain separate gates. Improved original seven-loop Wilson squared
weight `17074763 / 10^12` remains **source-conditional / FORMAL HOLD**;
4D continuum Yang–Mills OPEN.

The workflow is `.github/workflows/y137-independent-q5-boundary.yml`; inspect
its hosted run and sealed fan-in artifact before claiming any actual Q5-source PASS.
No original Hamiltonian, data archive, source receipt or repository policy gate changes.
