# Issue #137 Stage E — actual four-moment Schur-to-W-normalization test

**Research draft, November 16, 2026.** This test is downstream of the accepted Stage C full signed moment and Stage D exact-rational four-moment Schur bracket. No numerical Stage E outcome is asserted until the dedicated hosted calculation succeeds.

## Exact input and locked references

- Source matrix: the two original authentic signed `mu3_six` matrices, at energy numerators **69909875505** and **69949729820**, parsed through the independently accepted Stage D hash, provenance, divisibility, and signed-source checks.
- Historical `U0, mu0, mu1, mu2`: their original frozen SHA-256 sources checked through `d_real_four_moment.accepted_old_moments`.
- Four-moment exact matrix enclosure: `lo4 <= S(z) <= hi4` from the real `mu3=mu3_six/6`; verify strict nesting inside the older three-moment bracket by exact positive-definite matrix differences.
- 3-moment energy windows: `E1=[69.909429421,69.909586556]`, `E2=[69.949264147,69.949433884]`, reconstructed via exact inertia and retained as conservative inputs. Stage E does not yet attempt a new four-moment energy-window tightening.
- Accepted first-excitation transfer: `ra.angle`, `fw.compose`, exact 8-flat `W`, exact `B*B=72 I`, accepted full-Q norm enclosures, higher-level `E3_lo`, and Wilson fixed-sample threshold `1/700`.
- Historical regression: `CENTRE_MOVED` at 3 moments must reproduce **0.014153976076** for the combined normalized error.

## Four separate actual tests

The program re-evaluates **UPPER_KEPT**, **LOWER_KEPT**, **CENTRE_KEPT** and **CENTRE_MOVED** at each energy using the *actual* four-moment matrices rather than assuming that a 60%-width bracket gives a 60%-error bound. For each matrix: exact directional residual, Rayleigh/width action with a seven-dimensional weighted complement PSD domination test, energy-window drift, full Q-state rotation error, and full W-normalization transfer, including the moved-vector triangle cost where applicable.

It prints both the historical three-moment and new four-moment combined error in units of `10^-12`. Every outcome retains the strict gate `700 * error < 10^12`. If this sufficient gate were met, the result is labelled **CANDIDATE_REQUIRES_INDEPENDENT_REVIEW**; issue #137 remains open pending the independent Wilson certificate. A larger result is reported as HOLD.

## Controls, receipts, and scope

The hosted workflow tests unchanged strict integer/no-floating-point policies and the Stage D forged-matrix SHA / energy-swap refusals. This script additionally requires exact three-moment energy-window and best-error regression, real Stage D width ratios **600184** and **600451** per million, strict matrix nesting and rejection of an intentionally inverted bracket.

A hosted receipt contains the four original/new cell comparisons, two per-energy authenticated input hashes, source-code SHA-256, original `mu3` receipt SHA-256, CI commit SHA and result SHA-256. There are no edits to accepted source, results, README or protected `main`.

**Scientific acceptance:** numerical improvement is reported only after the actual run; finite 3×4 S₃ at `r=9`, conditional on the frozen Q-floor and accepted physical-source certificates. The independent charge-conjugation seat is tracked separately in [issue #233](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/issues/233).
