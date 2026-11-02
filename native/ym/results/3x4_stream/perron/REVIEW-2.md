# Review 2, verbatim

Relayed by the operator on November 2, 2026. The reviewer read the PR at head `155acdd`.

---

I'll review PR #79 directly from the repository: the derivation, the certificate code and the receipts.

The derivation reads correctly so far. Two places need the code checked: whether `t_cert` is rounded down, and whether the bound uses the row matrix itself rather than its weighted form.

I wouldn't merge PR #79 yet. The proof and the checking code hold up. What's missing is the 3×4 evidence itself, and one assumption that hasn't been tested on 3×4. I reviewed the latest head, 155acdd, today.

**What holds up**
- **Removing the flat states (interlacing).** Taking out the 8 flat states gives E₉ ≥ the lowest level of what's left. The proof is correct.
- **The lower bound from d (Barta / Collatz–Wielandt).** It holds for any positive d, because no couplings are positive. A badly solved d only gives a weaker bound, so the solver doesn't need to be trusted.
- **The upper bounds on E₈.**
  - E₈ ≤ 72 for every r: 8 flat states, each with diagonal 72 and no couplings between them.
  - The step from r = 9 to every r ≥ 9 is valid, since the magnetic term only raises levels.
  - At r = 9, the ball count gives E₈ < 70.031 (8 levels below it, 0 ambiguous).
- **The arithmetic.** 93.061051 − 72 = 21.061 and 93.061051 − 70.031 = 23.030 are both right.
- **The `perroncert check` code.** I read it line by line:
  - Each ratio is rounded down (`div_euclid` by a positive d), so the rounding can only weaken the bound.
  - It refuses to certify if any coupling is positive, any non-flat d is ≤ 0, or any flat d is nonzero.
  - Couplings into flat states drop out because d = 0 there, which is exactly "flats removed".
  - The diagonal comes from the row's own entry plus the magnetic term.
  - It checks that d has one entry per row and recomputes the store's merkle hash on every pass.
  - At JE = 1000 and JB = 9000 the i128 sums are far from overflowing.
- **Units.** The value called t_cert_milli is actually in millionths of J_E at this scale, so 93061051 means 93.061051. That's correct, just confusingly named.

**What blocks the merge**
1. **The 3×4 run isn't in the PR.** At 155acdd the result file still says `perron_3x4_run=NOT_RUN` and `second_seat_review=NOT_DONE`. The PERRONCERT line, the d file's hash, the `check_d_stream.py` output and the Hugging Face location of d aren't committed. I can't check t_cert = 93.061051 until they are.
2. **The whole-space statement rests on an assumption not tested on 3×4.** The jump from the sector store to "E₉ of the whole space" needs each sector row to be −1 per move into another sector state, with diagonal 72 minus the moves that land back on the same state. If that holds, the bound covers all sectors. It's derived and was checked on 2×2 and 2×3, and the 3×4 ball comparison agrees, but nothing has checked the 3×4 rows themselves. The passA.bin decode test would settle it: decode a random sample of rows and recompute them from the configurations with code that doesn't share `ymroom`'s row builder. Without it, the honest claim is the 9th level of the Sx+Sy+ sector only, where the sector has 7 flat states.
3. **No second seat has checked it.** All three checkers (`perroncert check`, `check_d.py`, `check_d_stream.py`) come from the seat that produced the run. Once d and passA.bin are on Hugging Face, an independent check needs one more pass over the 45.5M rows. I can't do it from here until those files exist.
4. **The rule text doesn't match the run.** The draft rule says to solve at 93, but the run started from a d solved at 93.7. That's harmless, since any positive d is valid. The rule should say so before the result is sealed.

**Wording to fix before merge**
- Say plainly that this is the gap above the 8 flat states, E₉ − E₈. It is not the vacuum gap E₂ − E₁. Readers will otherwise take "gap" to mean the mass gap.
- Rename `t_cert_milli` or state the scale in the PERRONCERT line.

If 1 and 4 are fixed, I'd accept the sector-only claim. The whole-space claim of 21.061 for all r ≥ 9 and 23.030 at r = 9 also needs 2 and 3.

I haven't posted anything on GitHub. I can post this as a review comment on #79 if you want.
