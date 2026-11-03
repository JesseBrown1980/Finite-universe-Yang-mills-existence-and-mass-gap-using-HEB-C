# Independent three-per-level operator test — 2026-10-30

Local Python reference, isolated from the Yang–Mills host and all PRs. All tests ran
with Python 3; this is not a Rust 1.81 or physical experiment.

## Pre-registration and results

The `PREREG.hbp` contains seven prediction groups and was hashed before the
`probe.py` run. `RESULT.hbp` records **7/7 PASS** under the frozen model.

The model uses 3×3 exact integer operators R, r=R+R² and j=I+R+R²,
applying each to one ternary address axis in order. Here **r acts on the
selected address axis**, not on nearest ring neighbors. This differs from
the Acer and cloud implementations, which define r as the ring-neighbor
operator. Be careful when comparing their travel times.

The post-hoc `pair_check.py` independently enumerates ring-neighbor r against
ordered-level j, matching the cloud seat’s counts exactly. It tests all
ordered *distinct* pairs for 27, 81 and 243 cells. Pairs are classified as
j first, r first, or tied. This test is **not pre-registered**.

| Sites | j first | r first | tied |
|---:|---:|---:|---:|
| 27 | 594 | 30 | 78 |
| 81 | 6,132 | 108 | 240 |
| 243 | 57,732 | 348 | 726 |

`j` reaches all cells in N ticks because the model schedules levels in fixed
least-significant-to-most-significant order. A global all-ones tensor
product operator J would connect all cells in one mathematical application,
which is a *nonlocal* operation when sites are embedded in a 1D physical ring.
Neither observation demonstrates faster-than-light signaling.

The unnormalized 3×3 all-ones matrix has `J²=3J` over integers and `J²=0`
modulo 3. Thus J is noninvertible, and dictionary language about j being
an "inverse" of r is not an algebraic inverse under this realization.

## Reproduce without altering the evidence

Run `sh run.sh` (Python 3 and sha256sum required). It copies the source and
prereg into a temporary directory, computes an independent result, compares
that output byte-for-byte with `RESULT.hbp`, regenerates the pair-count check,
and validates the SHA-256 manifest and seal. Existing evidence is left intact.

## Provenance

- HBI: `PERLEVEL.hbi`
- HBP: `PREREG.hbp`, `RESULT.hbp`, `PAIR-CHECK.hbp`
- SHA: `SHA256SUMS`, `PREREG.hbp.sha256`
- SH: `run.sh`
- HASH: `PERLEVEL.seal` = SHA-256 of the exact bytes of `SHA256SUMS` followed by `PERLEVEL.hbi`.

No JSON. Not uploaded or committed to GitHub. No changes to the ongoing
segmented Yang–Mills P2/P3 run, P4, PR #37, #39, or #40.
