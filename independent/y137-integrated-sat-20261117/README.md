# Integrated MTP–Fischer–N-Nest exact SAT engine — first acceptance slice

Date: 2026-11-17. This is a research prototype **stacked on #295**. The original 3×4 S3 Hamiltonian and Wilson-source computation are unchanged.

## One freeze–propose–score–verify–commit loop

1. **Freeze:** read immutable three-literal CNF tuples; commit the ASCII tuple representation with SHA-256. The source generator is used only to prepare blind input clauses. The planted solution is never passed into the integrated solver.
2. **MTP proposal:** group clauses by their unordered three-variable supports; exhaustively test eight local assignments. Propose only complete four-clause parity gadgets; retain every residual clause.
3. **Fischer selection:** rank candidate equation insertions using their support widths and pivot positions; rank residual-search variable choices by projected participation and expression footprint. These are new *SAT-specific deterministic heuristics inspired by the Fischer move-scoring concept*, not an assertion that original BHFISCHER CPL terms were a SAT cost model.
4. **N-Nest watchers:** independently reconstruct the four canonical XOR clauses for each proposed gadget. A wrong proposed parity is rejected and corrected before commitment. Verify global equation rank by left-pivot elimination, independent of the right-pivot engine. Verify all affine free-variable expressions and the full original-CNF witness. Recompute frozen source hash before and after.
5. **Commit:** emit a source SHA, per-reduction proof-chain SHA, exact model count or bounded HOLD, witness value and SHA, result SHA, total instrumented work metric, wall time, and Linux whole-process VmHWM.

All parity variables are represented as exact affine functions of independent free Boolean variables. Residual generic clauses are checked against these expressions during a bounded decision-tree model count. If every remaining residual clause is already satisfied, the algorithm multiplies by the exact number of free assignments. If the declared node cap is reached, it reports HOLD with no model count. This is a sound exact branch-counting prototype with an explicit exponential worst case.

## Source and independent replay

The source fixtures are those from [#295's hierarchical SAT experiment](../y137-hierarchical-mtp-sat-20261117/README.md). Cases: parity n=48,72,384; mixed n=12,24,36,48,72; generic n=12,18,24. The independent verifier imports **only the prior clean-room source reconstruction** (its own generator and left-pivot checker), not the new engine. It checks every receipt's source hash, complete original clauses, exact counts when returned, witness, proof chain and rank. The prior #295 hosted verifier remains the baseline reference.

The benchmark includes a **fixed-free-variable-order comparator** that is metered separately and included in the total work proxy when evaluated. This is an initial ordering baseline. A credible solver-scale comparison still requires standardized DIMACS input and external SAT/#SAT solvers on unseen structured, mixed, random, high-connectivity, SAT and UNSAT families. SAT decisions and full exact model counts must be reported separately.

## Explicit controls and accounting

- Injected wrong local parity guess: watcher rejects and corrects it.
- Missing fourth parity clause: fails motif recognition and remains a residual source constraint.
- Opposite parity clauses on one triple: complete formula has exactly zero solutions.
- Source mutation: changes frozen SHA and cannot be accepted as the original snapshot.
- Rank and expressions: second elimination direction recomputes the accepted linear system.
- Search: every visited decision-tree node and tested literal is counted; exceeding cap returns HOLD.
- Peak resident memory is reported as Linux process high-water RSS including Python overhead; estimated operation counts are **defined proxies**, not full CPU instruction counts. External CI start-up, installing tools, and future benchmarking harness costs must be counted when comparing total systems.

**Status on creation:** engineering candidate, pending hosted checks. The preceding #295 structured parity pilot is independently hosted; this particular integration has its own acceptance gate. P=NP is an open mathematical question. First Wilson spectral weight remains HOLD.

## Run on the stacked branch

    python3 -I -B independent/y137-integrated-sat-20261117/engine.py > integrated.hbp
    python3 -I -B independent/y137-integrated-sat-20261117/verify.py integrated.hbp

Next planned gate: canonical DIMACS parser, representation choices beyond XOR, established SAT solver baselines, systematic held-out scaling curves (total discovery + scoring + watcher + search + memory), then domain-specific reusable checker interfaces for physics.
