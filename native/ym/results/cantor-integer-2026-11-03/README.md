# Cantor-27 on the finite S₃ sector, in integers only

The operator's word, November 3, 2026: "Floating point should be redone to integer only. Not like redone as if erase the evidence, but say, hey, we need to do this again in integer only so that it works. We can't use float, that's crazy."

This repeats the experiment of [PR #61](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/61) in integers. That floating-point run stays as evidence, verbatim, in [`float-run-2026-10-31/`](float-run-2026-10-31/). This folder holds the result.

**The experiment.** The 211-state (+,+) sector of the 2×2 torus, matrix `902a8a01…`, with H_t = E + (r + f(c_t)/27) M and U_t = exp(−i H_t / 27), over the 729 slots of the Cantor signal `1f48fa50…`: 32 positive, 32 negative, 665 free. It starts from basis state 0. The controls are `cantor`, `zero`, `inverted` and `rotated_one`, at r = 9 and r = 243.

## The result

Each value below is the lower end of an enclosure one unit wide at 10⁻³⁰, computed in integers. Beside it is what the floating-point run printed.

| r | Control | Magnetic expectation, integers | Float printed | Return probability, integers | Float printed |
|---:|---|---|---|---|---|
| 9 | cantor | 0.177488422687791699361036607529 | 0.17748842268798898 | 0.581532731677717996167188552095 | 0.58153273167831554 |
| 9 | zero | 0.172446813091562530971725047756 | 0.17244681309177573 | 0.582203126990414006699406587182 | 0.58220312699108889 |
| 9 | inverted | 0.167743442711107016852223699013 | 0.16774344271130415 | 0.582770561500305255488500035329 | 0.58277056150091255 |
| 9 | rotated_one | 0.172723358203558329767359725485 | 0.17272335820374957 | 0.582093230296073413302047888687 | 0.58209323029667459 |
| 243 | cantor | 0.000177321420091194090633831170 | 0.00017732142009024333 | 0.928274174435032699691370284996 | 0.92827417443351368 |
| 243 | zero | 0.000177302996652460230723870156 | 0.00017730299665134853 | 0.928274162308954637785772641952 | 0.92827416230730719 |
| 243 | inverted | 0.000177286659408544535187772455 | 0.00017728665940762762 | 0.928274149048095830859591901970 | 0.92827414904657268 |
| 243 | rotated_one | 0.000177361794783637589386536260 | 0.0001773617947827547 | 0.928274148479071756826389496872 | 0.92827414847754863 |

Driven against zero, the fidelity is 0.999952759247705351690287734347 at r = 9, where the float run printed 0.99995275924991289, and 0.999999999726955680982303403308 at r = 243, where it printed 0.99999999972367326.

**What this says about the float run.** Its worst distance from the integer enclosures is 0.000000000002207538309712265652 at r = 9 and 0.000000000003282420982303403308 at r = 243, so its printed values were right to about 12 digits. The integer values are exact to 30.

## How it stays in integers

1. **No square roots.** In orbit-function form H has integer entries, with w_i z_ij = w_j z_ji, and is self-adjoint in the weighted inner product. The probabilities are |Φ_b|² and Σ w_i m_i |Φ_i|² / w_b, with no root anywhere.
2. **No rounding hidden.** Each slot is the Taylor sum of exp(X), with X = −i (27H − 27c) / 729, in fixed point with a unit of 2⁻²⁵⁶. Each division is an integer floor, off by under one unit, and the bound counts it.
3. **No growth of error.** The exact step is unitary in the weighted norm, so each slot's error adds to the last with no amplification. One slot's error is at most K·3^⌈x⌉·⌈√(2Σw)⌉ units from rounding and ⌈√w_b⌉ + 1 from truncation, where x bounds ‖X‖ from the largest row sum. The tool computes this bound in integers and refuses to print a result when it fails. Here it is 2²⁸ units at r = 9 and about 2¹¹² at r = 243, each far below the printed scale.

[`cantorint`](../../crates/evolvers/src/bin/cantorint.rs) took 15 s at r = 9 and 44 s at r = 243, on 4 threads.

## What checks it

Predicted first, in [`PREDICTION.hbp`](PREDICTION.hbp), committed before any of this code. All 49 requirement rows are met, in [`COMPARE.hbp`](COMPARE.hbp).

| Check | Result |
|---|---|
| A separately written path, [`verify_cantorint.py`](verify_cantorint.py): Python integers, 200 bits, no spectral shift, its own signal construction | Prints the same enclosures on all four controls at r = 9: [`SECOND-PATH.hbp`](SECOND-PATH.hbp) |
| The same tool at 300 bits, r = 9 | The same enclosures: [`RESULT-r9-P300.hbp`](RESULT-r9-P300.hbp) |
| The norm at every slot, and the way back through all 729 slots | Within the bound on all four controls at both couplings |
| Unit tests | 6 pass: the 384-bit integers against big integers on 20,000 random cases, two half-steps against one, and a two-level system against its closed form |
| Series cut short, precision too low, self-adjointness broken | Exit 2 on each: [`TEETH.hbp`](TEETH.hbp) |
| One pulse's sign wrong | Moves the value about 3 × 10⁻⁴ from the float row, past the predicted 10⁻⁹ |
| Hosted replay | [`cantor-integer-replay.yml`](../../../../.github/workflows/cantor-integer-replay.yml) rebuilds both couplings on Rust 1.81 and compares every row, and runs the second path |

**Scope.** This is an exact account of one finite-dimensional evolution in one 211-state sector, under a drive chosen for the test. It reads as a stress test of the sector's response, and the spectral certificates in this repository stand apart from it.
