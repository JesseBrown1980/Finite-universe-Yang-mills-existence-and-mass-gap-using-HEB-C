# Exact integer-numerator HEB-C wave update — no rounding

**Separate draft, stacked on PR #16.** The previous integer-typed PR #16 wave update used `rounded_ratio(Hq,D)`. Integer *types* did not make that evolution unrounded; the division discarded fractional information. This branch **removes that numerical rounding in the actual recurrence**.

## Exact identity, not an approximation

The 1,393-state gauge-invariant finite-S₃ Hamiltonian is `H=JE·E+JB·M`, with every nonzero matrix coefficient an integer and positive Gauss-orbit weights. Define the chosen **discrete wave-equation control** by

```text
x[-1] = x[0] = constant field 1
D = 4*(48*JE + 12*JB) + 1   # positive integer
x[t+1] = 2*x[t] - x[t-1] - H*x[t]/D
```

The preexisting implementation rounded `H*x[t]/D` to an integer **at each step**, changing this recurrence. We now represent the exact mathematical amplitudes as `x[t]=N[t]/D^t`, with an integer numerator vector `N[t]`. The entire evolution is:

```text
N[0]   = all ones
N[1]   = D*N[0] - H*N[0]
N[t+1] = (2*D*I-H)*N[t] - D²*N[t-1]
```

**Every matrix operation is integer addition, subtraction or multiplication. No division, approximate float, fixed-point rounding, or numerical truncation appears in the time update.** `D^t` is an *exact symbolic integer denominator*, not rounded to a float or computed into a fixed-width register.

This implements the exact rational recurrence of the stated **discrete model**. It does **not** imply exact real-time unitary quantum evolution or a physical clock. It remains a finite model, separate from exact Sturm spectral-gap certificates.

## Implementation

- `native/src/wave_torus2.rs` is a self-contained Rust 1.81 signed arbitrary-precision integer implementation (base `10^9` limbs); it adds no external dependencies to the offline Cargo build.
- Matrix-vector action uses the original native sparse 1,393-state electric operator and diagonal magnetic potential on each integer frame.
- `JE∈[0,10]`, `JB∈[0,10000]`, `steps∈[1,243]`; larger magnetic rungs are now accepted without converting ratios to floats.
- Each deterministic HBP-style trace records `denominator_base=D`, `denominator_power=t`, canonical state-numerator SHA-256, exact numbers of electric-active/magnetic-active/flat-active entries, and integer numerator length. Counts are **not** energy expectation values, decay rates or certified gaps.
- The browser chart has integer-only BigInt plotting. It plots active-site counts; it no longer labels a truncated integer Rayleigh quotient as a precise energy.
- The electric-only constant initial state remains a stationary control. Magnetic-only and coupled trajectories are expected to differ. A changed field is a result of the *chosen recurrence*, not evidence of physical particle production.
- Runs with the same exact integer input repeat deterministically; 244-step requests and out-of-range couplings fail closed.

## Reproduce

```bash
git switch http0-wave-exact-integer-no-rounding
cd native
cargo +1.81.0 test --all-targets --offline --locked
cargo +1.81.0 clippy --all-targets --offline --locked -- -D warnings
cargo +1.81.0 build --release --offline --locked --bins
target/release/hebc_http0_sgram serve /tmp/hebc-integer-wave 5097 48
# Browser: http://127.0.0.1:5097/observatory
# curl: http://127.0.0.1:5097/wave/1/243/27
```

The dedicated CI workflow verifies exact arithmetic self-tests (including integer magnitudes beyond `i128`), a 243-step `(JE,JB)=(2,5)` trajectory, a high magnetic rung `(1,243)`, the electric-only negative control, full 1,393-state sparse action, determinism, HTTP test routes, zero JSON, and the frontend BigInt gate.

**Critical scope:** This is an arithmetic correction to an exploratory discrete wave model. It neither speeds up the independent Rust sector-based relaxation detector automatically nor creates a continuum Yang–Mills theory. The existing original PR #16 rounding experiment remains in its historical unmerged branch for comparison; this new branch is the unrounded candidate.
