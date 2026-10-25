# HTTP-0 finite-S₃ interaction observatory: exact operator, controlled integer wave update

**Status:** Isolated development branch, based on the existing PR #10 HTTP-0 / SG-RAM backend. No changes to the PR #10 branch or `main`. No new continuum theorem or physical Yang–Mills claim.

## Motivation and boundary

A separate seat reports a `server.py` loopback UI at `127.0.0.1:5099` using relaxation and exponential-decay fits of the same finite 1,393-state Hamiltonian. It reported approximate spectral gap readings for ratios 0, 1, 2, 3, 5, and 6, with existing rigorous integer Sturm bounds as comparison. The relaxation source and its running localhost endpoint **are not included or independently reproduced here**; a claim that its output equals an exact eigenvalue requires verifying the projection, fit, time discretization, and error bounds. Exponential imaginary-time relaxation is not real-time unitary evolution.

This branch creates a **separate**, deliberately specified integer-discrete wave-equation control experiment on exactly the same finite gauge-invariant operator rather than reconstructing or inventing a physical continuum dynamics.

## What is actually executed

The native Rust 1.81 module `wave_torus2.rs` uses the existing `Torus2::build()` and `Torus2::apply(JE,JB,q)` methods to act on **all 1,393** physical Gauss-orbit components, with the original orbit weights and magnetic plaquette potential.

Initial conditions: `q(-1)=q(0)=(1_000_000_000,...,1_000_000_000)` (a uniform amplitude on the gauge-reduced basis). For a chosen integer `JE,JB∈[0,10]` and up to 243 steps, set

```text
D = 4*(48*JE + 12*JB) + 1                 # positive integer
q(t+1) = 2*q(t) - q(t-1) - round_nearest(H q(t) / D)
H = JE*E + JB*M
```

Every quantity in the update is signed Rust `i128`; all divisions round to an **integer** using integer arithmetic. The scheme is an exploratory discrete second-order equation `q''=-Hq/D`, not a time-continuum unitary Schrödinger simulation. The integer step size is model- and parameter-dependent, so *do not compare apparent temporal frequencies across couplings as if there were a common physical clock*. The code fails closed on overflow or amplitude guard. It never populates 23 billion virtual states; physical RAM and finite CPU work are still used.

Each iteration records a trace in text `HBP`-style `HEBC-WAVE|...|json=0` lines:

- Weighted norm `Σ_i w_i q_i²`.
- Magnetic Rayleigh quotient in milliunits `1000 Σ_i w_i M_i q_i² / Σ_i w_i q_i²`, integer floor.
- Electric Rayleigh quotient in milliunits `1000 Σ_i w_i q_i (E q)_i / Σ_i w_i q_i²`, integer floor, checked nonnegative.
- Fraction of squared weighted amplitude on the eight `M_i=0` flat orbits, in milliunits.
- Number of nonzero amplitudes, min/max, exact state SHA-256, changed-frame count.

These observables are **derived from the deliberately chosen state update**. A changing observable establishes activity of this discrete model, not physical particle creation, confinement, Yang–Mills continuum evolution or a certified energy eigenvalue. SHA authenticates the stored state bytes; it is not a spectral measurement.

## Controls and hypothesis

Three 27-frame native controls run with the **same initial uniform field**:

1. `(JE,JB)=(1,0)`: the uniform state is in `ker E`; therefore the electric-only state remains unchanged exactly. This is an essential negative control.
2. `(0,1)`: the diagonal magnetic term varies across the orbits; this gives nontrivial field changes but **no electric hopping**.
3. `(1,1)`: both terms act, producing a different trace from the pure magnetic control. Electric graph variation should be measurable after the field becomes nonuniform.

A byte-identical rerun of the mixed trace checks determinism. This **does not demonstrate a non-Abelian continuum physical interaction**, only the action of the noncommuting finite electric/magnetic contributions on the same finite field. If either control is identical to the mixed trace, or magnetic/electric response cannot be measured, the test does not pass.

## HTTP-0 transport and local page

The HTTP-0 name denotes the existing **virtual namespace**; transport is ordinary localhost HTTP/1.1. The Rust binary `hebc_http0_sgram` serves a static web UI:

- `GET /` or `GET /observatory` — interactive local observatory
- `GET /wave/:JE/:JB/:STEPS` — recompute all requested integer frames from source
- Original `/health`, `/qtrit`, `/finite-gap`, `/run` and `/verify` routes unchanged

The interactive page has a tiny client-side script **only for buttons and chart rendering**; all physics/state updates run in compiled Rust on the backend. It is not an API requiring JSON. Only bounded integer inputs are accepted. This is a loopback research tool, not a multi-user secured web service; do not expose the unprotected port on a public network.

```bash
cd native
cargo +1.81.0 test --all-targets --offline --locked
cargo +1.81.0 clippy --all-targets --offline --locked -- -D warnings
cargo +1.81.0 build --release --offline --locked --bins
target/release/hebc_http0_sgram serve /tmp/hebc-wave 5097 40
# Local web browser: http://127.0.0.1:5097/observatory
# Test route: curl http://127.0.0.1:5097/wave/1/1/27
```

## Evidence standard

The branch workflow rebuilds the original operator, runs three controls, tests the actual localhost webpage and wave route, checks 28 frames including step 0, rejects 244-step requests, verifies a byte-identical rerun and checks that no runtime output falsely claims `real_time_unitary=1` or `continuum_YM_proven=1`.

**Do not identify this toy wave equation with the relaxation/eigenvalue solver.** The rigorously certified `E₀,E₁` inequalities remain in PRs #9–#15 and the ladder ledger. If a follow-up experiment wants a real-time quantum correlation function or certified extraction of spectral gaps from a relaxation trace, it must specify a suitable evolution operator and error control independently of this wave equation.

**Scope:** periodic spatial 2×2 torus, finite group `S₃`, 1,393 gauge-reduced states, integer-only experiment. No SU(2)/SU(3) continuum theory, volume-uniform lower bound, 4D existence, or Clay Yang–Mills solution.
