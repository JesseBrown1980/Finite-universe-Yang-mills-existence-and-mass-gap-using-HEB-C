# Residual leaves and the low spectrum at coupling 12 (3x4 S3 lattice)

Date: 2026-11-12. Seat: ACER-CLAUDE-FABLE52 (pid `61089a99becaa89b`, parent seat pid `8467a937cba309f7`), directed by
OP-JESSE, with GPT-6 as reviewer. Coupling r = 12, a rehearsal coupling. Nothing here is computed at r = 9 or within
1 of it. The floor-certificate freeze and its r = 9 run are a separate lane and stay on HOLD.

## What this folder is

A record of one day's measurements on **frozen certificate data**: the floor certificates at cutoffs m0 = 7, 8, 9
for the three weight words `1`, `8,7,6,5,4`, `6,5,4,3`. The pinned writer and verifier were not modified. A scratch
copy of the verifier prints, per row, the residual it already computes (a "leaf") and the canonical row text whose
SHA-256 is the certificate's row hash. Every prediction file in `specs/` was written and hashed before its run.

## Results

| # | Question | Outcome | Files |
|---|---|---|---|
| V0 | Residual-carrying functions walked through 19,683 Host8 rooms: more triples than chance? | No: 10 of 10 statistics inside both nulls (prediction held). Instrument limits recorded. | `specs/SPEC-AND-PREDICTION.hbp`, `results/RESULT-cert_*.hbp` |
| V1 | Law 62 inner-light residue of the leaves (shipped functions, float scaffold) | Reads record layout and magnitudes only (prediction held) | `results/RESULT-INNER-LIGHT-V1.hbp` |
| V2 | Lighthouse as the prompt: do rows 1, 2, 3 apart close on a centre mod 3, 9, 27? | Chance rate at cutoffs 7, 8, 9 (prediction held; one odd cell shown to be chance) | `results/RESULT-LHP-*.hbp` |
| V3 | Three certificates of one matrix: do they classify the same rows alike? | Yes, far beyond chance and beyond magnetic number: 27%, 88%, 76% three-way agreement at cutoffs 7, 8, 9 against 11% (prediction held) | `results/RESULT-PUMP-V3-*.hbp` |
| V4 | Is that agreement the row's structure class? | No: 2.7x and 2.1x the within-class null at cutoffs 8, 9 (prediction FALSIFIED) | `results/RESULT-PUMP-V4-*.hbp` |
| V5 | Is the residual field the next mode e1/e0? | No: correlation 0.09 and -0.05 (FALSIFIED) | `results/RESULT-MODE-V5-*.hbp` |
| V6 | Is it the row's coupling into the discarded sector? | No for the long words (0.03, 0.31); yes for the cap-limited word `1` (0.88) (FALSIFIED) | `results/RESULT-LEAK-V6-*.hbp` |
| V9 | Is it the writer's fixed-point rounding? | No (0.03, 0.26) (FALSIFIED) | `results/RESULT-ROUNDING-V9-*.hbp` |
| V10 | Does the reduced matrix keep a three-value low cluster and a jump at cutoffs 8 and 9? | Yes: intervals about 0.176, 0.181, then 5.5; stable in cutoff, weight word and floor parameter (prediction held) | `results/RESULT-CLUSTER-V10*.hbp` |
| V11 | Where does each low value cross zero? (descriptive) | Same spacings in the Hamiltonian's own units | `results/RESULT-CROSSING-V11.hbp` |
| V12-V14 | Exact counts and exact Ritz bounds, invariant sector, cutoff 9, word `6,5,4,3` | level 1 in [104.4146, 104.51), level 2 in [104.55, 104.68), level 3 in [104.70, 104.85), level 4 >= 110 (3 of 3 predictions held) | `results/RESULT-COUNT-V13-*.hbp`, `results/RESULT-RITZ-V14-*.hbp`, `STEP1-BRIDGE-NOTE.md` |
| V15 | Nine leaves: structure no pair explains? Near-exact pairwise control (27 surrogates, 0.03-0.13% off) | All-nine-equal inside (FALSIFIED); distinct patterns 149 below 160-174 (held against near-exact controls only) | `results/RESULT-NINE-V15.hbp` |
| V16 | Nine leaves: exact pairwise control by balanced cube moves from the real table (all 36 pair tables exact, integers only) | The real 149 distinct patterns lie INSIDE 145-159 in three chains of 40,000 steps (FALSIFIED: no structure above pairs is shown). GPT-6's hosted chains agree. Limit: the chains stay within about 65 rows of the real table; mixing is not established | `results/RESULT-CUBE-V16-*.hbp`, `scripts/cube_v16.py` |
| V17 | Where the rows sit on Pascal's pyramid (composition of the leaves per row; descriptive) | Nine leaves: 109 rows at a corner, 497 on an edge, 76 in the interior, against about 0.1, 53 and 628 for independent leaves | `results/RESULT-PASCAL-V17-*.hbp`, `scripts/pascal_v17.py` |
| V19, V19B | Density, pull, gate and push in the room block (729, 2,187, 6,561 functions); V19B: every function reads an instant hash of the whole block. Control: uniform random digits, 9 per cell | Real residuals outside the control range in 3 of 9 cells, one of them in the mode with no interaction | `results/RESULT-FIELD-V19*.hbp`, `scripts/field_v19*.py` |
| V19C | Same, with each function keeping its own digits in shuffled order, 27 controls per cell | Inside in 6 of 6 cells (prediction held): digit order makes no measurable difference, with or without the global hash. The V19/V19B departures came from digit frequencies | `results/RESULT-FIELD-V19C.hbp`, `scripts/field_v19c.py` |
| V20, V21 | What equation gives the shared leaf pattern of V3/V4? Proposed from the writer's Gauss-Seidel sweep: leaf(a) = const + c U(a), U(a) = sum over rows j after a in key order of A(a,j) v(j) / v(a) | Rank correlation 0.951 to 0.983 in 6 of 6 cells (total coupling 0.04 to 0.15); V21 is the exact integer redo of V20 and agrees within 0.001. The pattern is the trace of the sweep order | `results/RESULT-GS-V2*.hbp`, `scripts/gs_v21.py` |
| V22 | Reverse the writer's sweep on the same matrix (scratch copy of the writer, switches in the solver routine only; all 9 variant certificates pass the verifier copy) | The leaf pattern flips with the sweep: leaf vs earlier rows 0.939, 0.983, 0.955 at cutoffs 7, 8, 9, vs later rows negative. 64 inner sweeps weaken it (0.31 to 0.60). The certified floors agree within 0.0001 across the three routes (3 of 3 predictions held, exact integers) | `results/RESULT-SWEEP-V22.hbp`, `scripts/gsvar.sh`, `leaves/V22_*` |
| V18 | Pascal-pyramid layer at 9, 27, 81, 243 leaves (27 weight words x cutoffs 7, 8, 9 x couplings 21/2, 12, 14; 243 certificates, all pass the verifier copy) | The rows stay on the rim at every size (balanced rows 76, 85, 36, 37 of 682; 19 rows read the same on all 243 leaves). Prediction held. By V20-V22 this is the sweep footprint shared by every leaf | `results/RESULT-POWERS-V18.hbp`, `scripts/powers_v18.py`, `scripts/expand243.sh` (the 243 leaf files, 60 MB, are regenerated by that script) |
| V23 | Toy: how a pull falls off with distance under two delivery rules | Instant global hash: no falloff (ratios 0.989, 1.012). Local delivery: 4.664 and 4.375 per doubling of distance, tending to inverse square (near ratio outside the sealed band) | `results/RESULT-PULL-V23.hbp`, `scripts/pull_v23.py` |

## Scope that travels with every number

- **Floating point.** V1, V5, V6, V7, V9, V10, V11 and the witness/trial vectors of V12-V14 use numpy floats as
  diagnostics. The certifying programs `count_v13.py` and `ritz_v14.py`, the leaves, the row text and all counts
  are exact integers and rationals. The float diagnostics are evidence to be redone in integers, not certificates.
- **Update, later on November 12 (GPT-6, PRs #168, #169, #170, merged; summarized here as reported, not re-run by this seat).** The counting inequality was verified independently for the invariant sector. The full 111,906-orbit core at cutoff 9 was built. Exact variational counts give at least 5 levels of the whole non-flat space below 105.5 and at least 7 below 110. So the jump to 110 is a property of the invariant sector only; it is NOT a jump of the complete non-flat spectrum. Lower bounds for the non-invariant sectors are open.
- **Symmetry sector.** The exact lower bounds of V12-V14 hold for symmetry-invariant states only (the 48-class
  matrix, 2,880 classes at cutoff 9). The full non-flat space has 111,906 orbits at that cutoff. A state that
  changes sign under a lattice symmetry may lie below the invariant sector's second level. That question is OPEN.
- **The bridge.** The level-counting inequality in `STEP1-BRIDGE-NOTE.md` is a hand derivation, obtained
  independently by this seat and by GPT-6 on the same day. It awaits a third-party check.
- **Comparison matrix.** The spectra are those of the certificate's Schur comparison matrix. They bound the
  Hamiltonian from below level by level through the bridge; they are not themselves Hamiltonian eigenvalues.
- **One coupling.** Everything is at r = 12 on the 3x4 S3 lattice, non-flat space. No statement about r = 9, the
  flat sectors, larger lattices or a continuum limit follows.
- **Independent reproduction.** GPT-6 reproduced the cutoff 7, 8, 9 spacings (GitHub Actions run 43222707802) and
  the nine-leaf counts within 1 or 2 (run 43231913054). The tercile boundary convention is not yet aligned.

## Open items

1. The other symmetry sectors (the gap of the whole non-flat space).
2. Third-party check of the bridge; independent recomputation of the exact counts.
3. Integer redo of the float diagnostics, with enclosures.
4. Other couplings and the word `8,7,6,5,4` for the exact enclosure.
5. The shared row pattern of V3/V4 is the footprint of the writer's sweep order (V20-V22, reversal test passed, cutoff 7 included). Still to do: an exact replay of the writer's last sweep; the single-weight certificate at cutoff 7.
6. V19C with the frozen and global-hash controls on matched seeds.

## Layout

`specs/` sealed predictions with SHA-256 sidecars; `scripts/` the programs as run (the `leaf*.sh` and `pump3.sh`
scripts make the scratch verifier copies and the certificates under WSL); `certificates/` the nine certificates
and the three launcher receipts; `leaves/` the extracted leaves and certificate headers; `results/` outputs with
hashes; `office-rows/` the HBP rows recorded in the seat's back-end office. The canonical row texts (2 MB, 8.7 MB,
9.2 MB) are not stored: they are regenerated by `scripts/leaf5.sh` and `scripts/leaf6.sh`, and their SHA-256 values
equal the row hashes in the certificate headers
(`6cfcff14...`, `714b8ba3...`, `865dae92...`).

## Next: a static charge pair

`DESIGN-CHARGE-PAIR-V24.md` is a design note only (nothing run): a pair of sign charges equals the same orbit matrix with the sign of the moves on a path between the charges reversed; four checks the build must pass; what the floor certificate cannot do there. It awaits a second seat's review.
