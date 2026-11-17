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


## Hosted acceptance — November 17, 2026

[Hosted run #44186890988](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44186890988) **PASS**. The original 11-case regression, strict integer/no-float gates, independent source and exact-count verification, SHA receipts, and two external SAT solver decisions all passed. Of **21** new cases, **20 have independently verified exact counts** and **one is an honest node-budget HOLD**. MiniSat and PicoSAT agree on **17 SAT / 4 UNSAT** decisions.

| Family / n | Exact #SAT count or HOLD | Fischer branch nodes | Fixed-order nodes |
|---|---|---|---|
| XOR / 24,48,96 | 4, 1, 4 | 1, 1, 1 | 1, 1, 1 |
| Mixed / 12,24,36 | 14, 200, 1,824 | 51, 645, 8,591 | 61, 1,081, 10,075 |
| Planted / 12,18,24,30 | 5, 11, 119, HOLD | 555, 1,607, 7,199, 20,000 | 375, 4,109, 20,000, 20,000 |
| Random / 12,18,24,30 | 2, 7, 241, 0 | 367, 1,219, 5,723, 16,887 | 419, 7,909, 20,000, 20,000 |
| Hub / 12,18,24,30 | 10, 42, 144, 128 | 135, 769, 2,599, 8,945 | 299, 1,833, 8,659, 20,000 |
| Explicit UNSAT / 12,24,36 | 0, 0, 0 | 15, 15, 63 | 15, 15, 15 |

Node counts of 20,000 are bounded stops, not completed fixed-order counts. The Fischer-inspired ordering improves search nodes across the three held-out mixed cases and all four held-out hub cases, while planted n=12 and explicit UNSAT n=36 demonstrate counterexamples. It succeeds on several test cases where fixed order reaches the cap. The XOR family needs one search node after source-derived parity recognition; its complete metered work units at n=24/48/96 are **11,121 / 43,182 / 187,890**. This is evidence of finite-size structured scaling rather than a general asymptotic complexity law.

Ubuntu 24.04 MiniSat **1:2.2.1-8build1** and PicoSAT **965-2** were installed and their outcomes agreed. Their external elapsed time includes CLI startup; these decision solvers are not exact model counters. Independent exact #SAT recomputation passed for every returned count. The archived workflow artifact contains source CNFs, solver versions, external decision TSV, SHA receipts and HBP transcripts.

**Next gate:** strengthen exact #SAT comparisons with established external counting algorithms, evaluate genuinely independent benchmark distributions, repeat measurements under equal hardware budgets, and fit and falsify scaling models with verification and preprocessing costs included. The original first Wilson spectral weight remains HOLD; P=NP remains OPEN.
