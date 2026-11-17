# #137 finite Big Bang → cooling → MTP shells → conditional Big Loop

**Date:** 2026-11-17. **Scope:** exact-integer *hypothetical rule-engine demonstration*. A finite matrix seeded with 96 content-addressed pixels, six opposite pyramid sectors of a cube, active address growth, temperature-directed outward transport and lower-temperature clustering, global freeze/edit/evaluate/play snapshots, three MTP-style checker levels, and a separately seeded ultradense Big Loop acceptance control.

## Provenance and relation to existing research

- [`JesseBrown1980/Metatagging-data-for-a-Quantum-universe`](https://github.com/JesseBrown1980/Metatagging-data-for-a-Quantum-universe): particle metatags, `bh_inject_between` address expansion, catalog is persistent while slices advance.
- [`JesseBrown1980/Asolaria` prime-cylinder expansion](https://github.com/JesseBrown1980/Asolaria/blob/main/prime_cylinder_expansion.py): relation between higher address levels and available space.
- [`JesseBrown1980/asolaria-behcs-256` MAP](https://github.com/JesseBrown1980/asolaria-behcs-256/blob/main/MAP.md): exact 3,200-byte ⇄ 2,560-symbol (base 1024) transcode preserving bit count, *not* quantum Hilbert expansion or archive compression.
- Finite S3 original project PRs #288 (bounded gauge-invariant shell potential), #289 (frozen-U quantum negative control), #290 (table-recomputed nonlocal toy): independently verified source controls. **No modification to the original physical 3×4 S3 Hamiltonian, its eight flat sectors, its Perron bound, or its Wilson observable.**

## What the program computes

### Geometry and initial conditions

- 96 persistent identity records, 16 in each of six polar sectors ±x, ±y, ±z. The three opposite sector pairs have *proposed* opposite baryon-tag signs and distinct color paths. These are identity labels, not demonstrated quarks, antiquarks, QCD baryon number, or cosmological sectors.
- Each pixel begins at (0,0,0), thermal counter 18. Initial bounded cube radius 2 encloses 5³=125 addressable locations; maximum permitted radius is 48. Global state and metadata are fully finite at every simulated slice.
- Sector assignment for nonzero addresses uses the axis with greatest |coordinate|, with deterministic tie-breaking. Exactly six disjoint pyramidal regions partition a cube, aside from shared boundaries assigned by convention.

### Slice and physical movement rules

- Each tick reads **one source snapshot**, computes all proposals, asks two larger MTP-style reviewers to correct planted bad proposals, resolves occupancy/cold-core brakes, then commits the full next snapshot with a SHA256 receipt.
- Hot temperature ≥11: each pixel must move exactly **one Manhattan-neighbor cell per tick** (c=1, one cell / one slice). A corrected hot error falls back to the legal outward step. Hot pixels do not acquire binding tags; they move away from the center with a deterministic ternary primary/sideways schedule.
- Warm 5–10: outward motion on every second tick, allowing cooling. Cold ≤4: global identity-catalog centroid attraction is active; cold-core occupancy brakes block proposed over-capacity destination moves. This **explicitly installs** a global attractive rule; it does not derive an empirical force law.
- Cooling per tick is `min(temp, 1 + floor(Manhattan radius/6))`; lost thermal energy is credited **exactly** to a vacuum energy reservoir. `sum(pixel thermal)+vacuum=96×18=1728` is asserted after *every* slice. Temperature thresholds are chosen hypotheses, not measured QCD phase-transition temperatures.
- The active addressed cube grows *only when required* by a permitted pixel move. Old addresses and pixel identities persist. Address capacity expansion is separate from quantum Hilbert expansion. A **small exact isometric Hilbert-space embedding** (amplitudes 3/5,4/5, append vacuum ternary digit) verifies the illustrative embedding rule; a physical many-body quantum model with all new degrees of freedom is **not implemented**.

### Hierarchical MTP error experiment

- MTP1 proposes motion; MTP3 and MTP27 independently validate deliberately corrupted local predictions using deterministic fail-closed rules. All decisions derive from one frozen source. A higher shell can hold a cooler pixel; at hot temperature it falls back to an outward legal step. Some planted errors are allowed to pass by design, producing distinct final local clock counts and residual error tallies.
- These are **deterministic finite checking functions inspired by 1/3/27 MTP shells**, not model weights or the full Asolaria agent stack; an MTP disagreement is a controlled algorithm test, not an observed physical spacetime distortion.

### Big Loop and no-teleport control

- Main expansion/cooling run: 48 ticks, with ultradense `CORE_TRIGGER=72` cold pixels inside radius 2. The observed final cold core count is **61**, so the main arm **does not** reach the trigger and **does not** demonstrate spontaneous global recollapse.
- Separately preset a fully cold dense 96-pixel core with the corresponding vacuum energy already stored. The Big Loop gate accepts this input and reheats the pixels from the conserved energy reservoir, changing metadata rather than teleporting positions. Their first new outbound tick again obeys c=1. This is a **conditional trigger demonstration**, not a derivation of a new Big Bang from real black holes.

### Hash and computational complexity controls

- `source_sha256` and `result_sha256` are hashes of the exact full snapshot key, not a substitute for the snapshot itself. The program verifies the next state from the full table, then computes its digest. A digest alone cannot generally recover the full state; 257-bit possible states outnumber 256-bit SHA digests.
- One finite global state and forward-replayable transition law do **not** prove P=NP. P versus NP is asymptotic over families of input lengths; the finite example does not supply a uniform polynomial-time algorithm for NP-complete problems.

## Exact hosted pilot outcomes (standalone local execution)

| Readout | Result |
|---|---:|
| Initial physical pixel records | 96 |
| Initial / final active address counts | 125 / 2,197 |
| Additional addressable vacuum cells | 2,072 |
| Global source-snapshot commits | 48 |
| Plant/correct/escape deterministic MTP errors | 84 / 77 / 7 |
| Cold-core maximum within Manhattan radius 2 | 61 |
| Spontaneous CORE_TRIGGER=72 during main run | **NO** |
| Local clocks after 48 global ticks | sector-dependent, 47–48 |
| Total modeled thermal + vacuum energy | 1,728 at all ticks |
| Max physical movement | 1 cell / tick |
| Preset ultradense core Big Loop reheat | **PASS, conditional input** |
| Big Loop teleportation | **NONE** |
| Quantum many-body physical Hilbert evolution | **NOT IMPLEMENTED** |
| Original Yang–Mills Wilson spectral-weight certificate | **HOLD** |
| P=NP proof | **NOT IMPLIED** |

Reproduce: `python3 -I -B independent/y137-finite-bigbang-mtp-20261117/pilot.py`.

## Scientific boundaries and next gates

This is a mathematically defined toy, not evidence of physical expansion speeds, the shape of the actual universe, quark or gluon production, neutron-star equations of state, Hawking radiation, a black-hole-to-Big-Bang cycle, or regional MTP clock errors in nature. The angular-looking six sectors are a chosen finite cube partition, not measured cosmic matter sectors. The code uses integer temperature tokens and a hypothetical conserved reservoir—not cosmological thermodynamics or QCD. It keeps 96 occupied pixels and expands only **addressed vacuum cells**; expanding the *actual physical Hilbert space* needs a certified many-body isometry with explicit local dynamics and gauge constraints. `S3_original_gap=UNCHANGED` reports that the previous original Hamiltonian and certificates were not edited; it does not certify a mass gap of this new toy model.

**Next rigorous checks:** preregister 1/3/9/27 MTP per-shell laws, define a finite-volume local Hilbert-space embedding, derive quantum gauge-invariant transitions and temperature thresholds rather than assigning them, check entropy/energy transport and reversibility as appropriate, verify signal propagation restrictions separately from pixel displacement, compare with actual cosmological observations, and only then attempt a new gauge-theory spectral certificate.