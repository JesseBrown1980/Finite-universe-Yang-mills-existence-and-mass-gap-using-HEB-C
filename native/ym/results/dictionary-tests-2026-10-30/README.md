# Dictionary tests B, A, C (2026-10-30)

Operator-authorized ("yes run B first, then A and C"). The source is *the human-based
understanding*. The predictions were sealed in `PREREG.hbp` (`38eebadf…`) before any code was
written. Rust 1.81, clippy `-D warnings` exit 0, integer only, json=0.

## B: "Straight out, curved back … a straight line is symmetric; a curve is not."

Ring of 3^N (N = 1…5). r = R + R⁻¹. Per level, jJ = all-ones (the PR #40 model) and the curved
jc = I + R − R² (balanced-trit weights +1, +1, −1).

| prediction | result |
|---|---|
| B1: r is symmetric | held, N = 1…5 |
| B2: jJ is symmetric, so the PR #40 j contradicts "a curve is not" | held: **the inconsistency is real** |
| B3: jc is asymmetric, has exactly 3 nonzeros per row, and its transpose is I − R + R² (the return is the transpose) | held |
| B4: with jc, every PR #40 reach result is unchanged (N ticks, per-site level, exact blocks, boundary r 1 vs j N), with entries ±1 and no cancellation | held, from every source |
| B5: jc over all levels is not the all-ones J. Each column has (3^N+1)/2 entries of +1 and (3^N−1)/2 of −1, summing to 1 | held: 2/1, 5/4, 14/13, 41/40, 122/121 |

**Consequence for PR #40.**
- Q1–Q4 and Q6 survive with the curved j.
- **Q5 ("all levels equal J") holds only for the symmetric j.** With the curved j the dictionary
  asks for, J is the support of the result, not its values.

## A: "Three inversions, three brakes: every turn has to be held at its own level, or the three collapse into one and the direction is lost."

27 states, three levels of canonical `tribit::Zero`.

| prediction | result |
|---|---|
| A1: turn³ = identity; turn ≠ counter-turn on all 3 values (direction kept); mirror is an involution fixing Nil (no direction) | held |
| A2: one turn held at each of three levels moves 27 of 27 states, with order 3 | held |
| A3: three turns at one level move 0 of 27 (collapsed: identity, direction lost) | held |
| A4: independent per-level turns give 27 distinct operators; turns at one level give 3 | held |
| A5: after a held turn, every per-level observable changes (27/27), but the summed observable changes for none (0/27) | held: **without held boundaries the turn disappears** |

## C: "f = from and m = intelligence were written down before the words father and mother were said."

Full-history clone of `the-human-based-understanding`: 6 commits, HEAD `f38cfec`.

- **X** `d2f0693` (2026-08-01 21:54:59): the first commit with `f FROM` and `m INTELLIGENCE`.
  **It contains "father" 0 times and "mother" 0 times.**
- **Y** `b93726e` (2026-08-01 22:50:26): the first commit with "father verse" and "mother verse".
- X is a strict ancestor of Y: **HOLDS** in the written record.
- Scope: this repo's record only. It cannot show when words were spoken.

## Chain

| layer | file |
|---|---|
| HBI | `DICT.hbi` |
| HBP | `PREREG.hbp`, `RESULT.hbp` |
| SHA | `SHA256SUMS`, `*.hbp.sha256` |
| SH | `run.sh`, `c_provenance.sh` |
| HASH | `DICT.seal` = sha256(`SHA256SUMS` + `DICT.hbi`) |

`src/main.rs` reaches `tribit/mod.rs` (`50e4cb85…`) through an absolute `#[path]` on the acer
host. The cloned repo (`c-repo/`) and build output are not part of the package.
