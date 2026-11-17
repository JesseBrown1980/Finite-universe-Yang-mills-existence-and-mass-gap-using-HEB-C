# #137 Hierarchical MTP agents and global SAT dependency compression

November 17, 2026 — exact-integer research experiment, to be stacked on finite Yang–Mills research draft #294. This is a controlled computational experiment, **not** a claim that P=NP or a claim about the physical universe. The original S3 Hamiltonian and its first Wilson-weight HOLD are untouched.

## Question and benchmark contract

Can three explicitly metered MTP-inspired evaluator levels, viewing the same source-committed global table, combine distant logical dependencies without exponential intermediate storage? Can the same evaluator recognize when its representation is incomplete and decline to claim a full solution? All construction, local preprocessing, local/global reconciliation, independent checks, and SHA receipts are part of the measured computation. The source is not replaced by an unseen stored answer table.

### Agent implementation (deterministic, not trained neural models)

1. **MTP1** groups clauses by exact three-variable support, reading only source CNF. One deliberately incorrect predicted parity is planted per *parity* instance.
2. **MTP3** verifies each three-variable clause group against all eight truth assignments. It recognizes a parity constraint only when the entire group has precisely four valid assignments of one parity. It corrects the wrong MTP1 guess and rejects incomplete/non-parity motifs. No generator label or seed assignment is passed to the solver.
3. **MTP27** performs exact row-space compression in batches of at most 27 validated constraints using GF(2) elimination. A global evaluator reconciles all block bases, computes rank and the exact number of solutions for fully compiled parity-only systems, and reconstructs a satisfying witness. This algebra is standard binary Gaussian elimination.
4. **Independent verifier:** constructs clauses anew using the published seeded specification, uses *leftmost-pivot* Gaussian elimination rather than the pilot's rightmost incremental/block algorithm, and checks the original 3-CNF assignment for all sizes. It separately enumerates complete 2^n truth vectors for 2 parity and 6 generic instances up to n=21, plus an exact mixed-family n=12 oracle.
5. **Exact fail-closed gate:** ordinary and mixed clause families lacking a validated compact form retain their unknown residuals. Generic exact #SAT uses conventional variable elimination only while its **actually allocated intermediate tables** fit within the declared 32,768-entry cap. It emits HOLD above that cap; no exponential memory is allocated speculatively.

The planted parity family uses clauses encoding triples `(i, i+1, i+n/3)` plus an additional one-third as many long-range triples. Every parity triple is encoded into four standard 3-CNF clauses, with constraint parity derived from a deterministic hidden generating assignment. The solver only receives clauses. Every source SHA and recovered witness is checked. The family is deliberately structured; it is not a randomly selected or cryptographically difficult family.

### Principal measurements

| Family / variables | CNF clauses | Exact answer | Joined factor width under tested ordinary elimination order | Other measured result |
|---|---:|---:|---:|---|
| Long-range parity / 24 | 128 | Recovered exactly | 18 | Hierarchical exact parity count and witness |
| Long-range parity / 384 | 2,048 | **2 solutions** (rank 383) | 258 | Source 36,160 bytes; 512 parity gadgets; hierarchical local+global row XOR 5,077 vs ordinary forward 5,995 and reverse 8,587 |
| Long-range parity / 1,152 | **6,144** | **1 solution** (rank 1,152) | **770** | Source 114,384 bytes; hierarchical XOR 5,918 vs ordinary forward 5,998; no expanding truth table allocated |
| Generic globally linked / 21 | 42 | **9,183 solutions** | 16 | Conventional exact factor elimination: 32,768 peak intermediate entries, 193,022 branch scans, 779,326 factor lookups |
| Generic globally linked / 24 | 48 | **HOLD** | 18 | Projected 131,072 entries exceed 32,768 cap; 32,768 maximum actually allocated |
| Generic globally linked / 72 | 144 | **HOLD** | 50 | No false XOR recognition; projected intermediate table would contain 2^49 entries under the tested elimination order |
| Mixed parity + ordinary / 12 | 30 | **36** by independent truth-vector oracle | — | Parity-only relaxation permits 64, so declaring 64 for the original mixed problem would be wrong |
| Mixed parity + ordinary / 72 | 180 | **HOLD** | — | 36 parity equations compiled, 36 ordinary groups remain unresolved |

The `naive_factor_peak_projected_entries` figure is a symbolic prediction for **one specific** variable-elimination ordering. It is neither actually allocated nor a worst-case lower bound for every algorithm: parity-aware Gaussian elimination processes these exact examples compactly. Even a conventional, non-MTP parity recognizer could obtain the same compression.

### Cost transparency

The pilot reports, per instance, source serialization bytes, clause insertion count, literal truth-table checks, motif assignment evaluations, local/global/forward-flat/reverse-flat binary row-XOR counts, an explicit conservative per-XOR bit-work counter, the scope-preflight work, exact verification literal checks, wall-clock nanoseconds measured **from source generation through verification**, and estimated compact representation payload bits. Linux `/proc/self/status` also reports the whole Python process high-water RSS, around 100 MiB on the local run; this includes the interpreter and is not a direct compact-table allocation measurement. The logical-payload estimate excludes Python object overhead and is labeled accordingly. The independent verifier deliberately allocates up to 2^21 truth bits for the small generic oracle; that exponential work is explicitly identified as a *control*, not solver preprocessing.

The reported total metered work unit is a defined combination of checked logical operations rather than a complete CPU instruction count. Consequently, the evidence supports compactness for these parity-structured input families, while **neither the benchmark nor a few measured timings establish polynomial worst-case bounds for arbitrary SAT**.

### Negative controls

- Conflicting parity gadgets on one triple yield **exact UNSAT**; a missing clause never gets falsely compiled into XOR.
- In each structured case, one lower-shell parity misprediction is detected and corrected by independently recomputing the eight-entry truth table.
- Generic cross-coupled clauses yield zero false XOR motif recognitions and exceed the fixed table cap beginning at n=24, with a truthful HOLD instead of a fabricated count.
- Mixed formulas demonstrate why compressing some constraints does not certify the rest; the independent oracle finds 36 solutions at n=12 compared with the parity-only upper bound of 64.
- Source/result SHA256 authenticates the executed input and witness but does not invert an unknown preimage or solve generic SAT.

### Relation to prior research

The baseline generic factor-table method and its earlier n=21 complexity evidence are in research PR #292. The MTP-style freeze/evaluate/play design appears in PR #290. The optical pilot in #294 tests forward-only causal MTP corrections; it provides no NP-complete complexity claim. The accepted source-conditional original 3×4 S3 finite mass-gap theorem is unchanged; actual first-excitation Wilson spectral weight **HOLD**, 4D continuum OPEN.

**Mathematical verdict:** polynomially manageable structured parity constraints, precise error catching, and cheap source-verifiable witnesses in this tested family; no evidence of a uniform polynomial-time solver for unrestricted 3-SAT, and **P=NP remains unresolved**. The next genuine performance challenge is a *mixed* compiler that substitutes recognized parity constraints into residual arbitrary clauses and exactly accounts for its remaining work, competing against modern SAT/SMT solvers rather than only naïve factor tables.