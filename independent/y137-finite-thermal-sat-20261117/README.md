# #137 microcanonical thermal thresholds and global-table #3SAT scaling

Research draft, 2026-11-17. Stacked on #291 (six-pyramid Big Bang / freeze–MTP–play). This experiment asks two specific questions that were left open: can a finite state count generate a cooling/binding **preference** without choosing its threshold by hand, and does global-table factorization make general NP-complete problems cheap?

## 1. Exact finite microcanonical pair
A bath of **R distinguishable two-level excitation modes**, with E integer energy quanta, has exactly C(R,E) bath configurations. An unbound pair has **g** equal-weight permitted separation directions and energy 0; one bound arrangement has energy −1 and releases one unit into the bath. The fixed-total-energy microstate weights are

    U(R,E,g)=g*C(R,E)
    B(R,E,g)=C(R,E+1).

Binding has greater microcanonical probability **iff R−E > g*(E+1)** for E<R. No binding-temperature threshold is entered in the code. **R, unit binding energy, equal microstate weights and g** are model assumptions, not experimentally derived QCD constants. High occupations of a two-state bath can have negative-temperature characteristics; do not interpret the full E range as ordinary kelvin.

For R=24, strict binding-preferred integer E cutoffs are 2 at g=6, 5 at g=3, and 11 at g=1; for R=48, cutoffs are 5, 11, 23 (at g=6, E=6 is a tie). This illustrates how cooling and reduced free-separation directions can yield a statistical tendency to bind. The exact 2×2 lazy heatbath stochastic kernel follows from the same U,B state counts, passes detailed balance and has a **Markov** spectral gap 1/2; **not** a Yang–Mills quantum energy gap.

Independent exhaustive enumeration of all 2^R bath bit patterns for R=4,6,8,10 and all g/E independently confirms **192 cases**. A saturated two-cell matrix still permits swapping labels, so density saturation by itself does **not** force a Big Crunch or Big Loop.

## 2. Original Big Bang replay overlay (no dynamics modified)
`overlay_bigbang.py` imports **the unchanged PR #291 96-pixel code** and exactly replays its 48 atomic steps and verified 84/77/7 MTP error receipts, active R=6, 2,072 new vacuum addresses. In eight selected snapshots, it checks physical pixel pairs whose Manhattan positions are equal or adjacent; computes the number of available empty-neighbor routes g; maps their original toy thermal counters to bath excitation E=floor((T_i+T_j)/2); and evaluates the derived preference. These are **candidate observations only**. The test **does not commit a bond**, change any original motion or energy, establish QCD particle production, or derive a spontaneous Big Loop.

## 3. Exact global-table 3-SAT model-counting scaling
`sat_scaling.py` constructs two deterministically planted, satisfiable 3-CNF families for n=6,9,12,15,18,21. The `BOUNDED_WINDOW` family has clauses on adjacent triples; `CROSS_COUPLED` relates distant variables in the catalog. An exact integer variable-elimination solver counts all satisfying assignments with complete factor tables. It records **maximum joined factor width**, peak intermediate table entries, total scanned branch assignments, and SHA256 source/result hashes.

A separate full 2^n oracle confirms all eight n≤15 cases, plus 7/6/0/1 model-count negative controls.

| Case n=21 | Max joined variables | Largest intermediate table | Branch assignments scanned |
|---|---:|---:|---:|
| Bounded-window 3-SAT | 3 | 8 | 158 |
| Cross-coupled 3-SAT | 16 | 32,768 | 193,022 |

These are deterministic work counts, **not** real-time benchmarks, worst-case complexity lower bounds or a comparison against modern optimized SAT solvers. A more effective elimination ordering can change the cross-coupled width. A global hash certifies a complete input/result, but cannot generally reconstruct the original input or prove P=NP. `P=NP` remains unproved.

## 4. Physical and mathematical scope
- Original physical 3×4 S3 source-conditional mass-gap certificate, energy windows, Wilson 7-loop operator: **UNMODIFIED**.
- Original first excitation Wilson spectral-weight certificate: **HOLD**; no source-action margin change.
- Real QCD transition temperatures, actual spacetime metric distortion, gravitational/black-hole physics and cosmology: **NOT TESTED**.
- Big Loop: conditional restart from PR #291 remains preset; no spontaneous collapse mechanism derived.
- A quantum Hilbert state-space is not created by the classical Markov model; PR #291's small isometric expansion toy is separate.

Run each exact-int script with isolated Python `-I -B`; the hosted workflow replays all parents, enforces repository no-float policy and SHA256 result receipts. DRAFT pending independent review.

Next gate: introduce a conservative **binding transition** into the actual six-sector simulator, with a modeled finite bath, detailed balance, local causal movement and an independently authenticated energy ledger. Do not call this an achieved QCD theorem.
