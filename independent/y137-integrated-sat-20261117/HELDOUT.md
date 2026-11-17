# #300 — Held-out DIMACS SAT decisions and exact model counts

November 17, 2026. This research branch is stacked on the independently hosted integrated SAT PR #299. The authenticated 3×4 S3 Hamiltonian and original Wilson calculation are unchanged.

## Preregistered held-out pilot

The integrated solver in engine.py supports --heldout DIR. It generates and stores ordinary 3-CNF DIMACS files using a distinct SHA-derived deterministic fixture family. The parser checks 3-CNF declaration, variable indices, three distinct variables per clause, integer syntax, clause termination, counts and EOF. The solver receives CNF clauses only.

The 21 cases are complete XOR n=24,48,96; XOR+residual mixed n=12,24,36; planted SAT n=12,18,24,30; unplanted random 3-CNF n=12,18,24,30; hub-connected n=12,18,24,30; and explicit UNSAT contradiction controls n=12,24,36. Contradiction fixtures contain all eight rejecting assignments on one triple, intentionally easy, not hard random UNSAT. Cases are new relative to #295/#299, but seeds are public and reusable, so they are a development set rather than a final blinded benchmark.

Each HBP record contains frozen source SHA, literal DIMACS-byte SHA, proof chain, result SHA, model count or HOLD, witness, all agent and watcher metrics, variable-order comparison, generation nanoseconds and source bytes, elapsed nanoseconds, and whole-process peak RSS. An independent verifier reconstructs every generated input, validates both SHA commitments, checks original CNF witnesses, and independently counts models when claimed EXACT.

## Established SAT decision comparators

Ubuntu 24.04 packages are pinned to MiniSat 1:2.2.1-8build1 and PicoSAT 965-2. The workflow checks both solver exit codes and ensures their decisions agree for all 21 frozen inputs, with integer elapsed nanoseconds including CLI startup and peak KiB RSS per invocation. They answer SAT/UNSAT, not full exact #SAT. The source-independent counting oracle certifies model counts where feasible. CI install, independent checker, serialization and SHA costs remain separately disclosed.

Negative controls include malformed DIMACS, wrong header, missing terminator, extra clause, altered SHA, deliberately wrong motif, incomplete XOR and contradictory clauses.

Acceptance must come from the hosted run and archived receipts, not from the code's stated expectations. The next stage is a genuinely unseen external benchmark corpus, stronger external #SAT solvers, robust scaling comparisons and a multi-representation selector. Original first Wilson spectral weight HOLD; 4D continuum OPEN; P=NP OPEN.
