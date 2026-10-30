# zlight: an instant global hash layer versus light at c = 1 (2026-10-30)

A pre-registered simulation test, authorized by the operator (OP-JESSE). Integer only, Rust 1.81,
clippy `-D warnings` exit 0, output in HBP with SHA-256 sidecars (json=0).

## Question

The operator's statement: when a matrix "plays", its hashes change instantly everywhere, because each
depends on all the combined hashes (the **z** layer), while light, colour and energy still travel at
**c = 1** per step. Firing a laser should change the hash at the target before the light gets there.
Does such an instant layer exist in a lattice simulation, and can a local observer use it?

## Model

- 64×64 torus of canonical balanced trits (`tribit::Zero`, from the kernel's `tribit/mod.rs`).
- One local, linear rule over GF(3): each cell becomes the balanced sum of itself and its four
  neighbours, so nothing can move faster than one cell per step.
- A "laser" adds a trit message at a source cell at step 0.
- Six universes: V0 has no laser; V1–V5 vary the source position (20, 24 or 28 cells from the
  target) and the message (+1 or −1).
- Three hashes are tracked against V0:
  - the **global root**, a Merkle root over every cell;
  - the **target's local hash**, of its own cell only;
  - the **target hash including the global root**.

## Pre-registered predictions and results

The predictions were sealed in `PREREG.hbp` (`37f24de9…`) before the program was built. The
results are in `RESULT.hbp`.

| prediction | result |
|---|---|
| P1: the global root changes at step 0 for every laser | held, step 0 for V1–V5 |
| P2: the target's local hash changes exactly when light arrives (step = distance), never earlier | held, at steps 20, 20, 24, 24 and 28 |
| P3: before arrival (steps 0–19) the target's own cell is identical in all six universes | held, 1 distinct state out of 6 |
| P4: at step 0 the global root already differs across all six universes (it encodes aim and message) | held, 6 distinct |
| P5: a target hash that includes the global root changes at step 0 and distinguishes all six | held, step 0 and 6 distinct |

## What this shows, and what it does not

- **Shown, in this simulation:** two layers coexist. The z layer (the global hash) changes
  instantly and already carries where the laser was aimed and what it carried. Light reaches the
  target only at c = 1.
- **The instant layer can only be used by something that reads the global state**, as the
  simulator does. An observer limited to its own cell gets zero information before the light
  arrives.
- **Not shown:** that the physical universe works this way. The closest established parallels
  are pilot-wave (Bohmian) mechanics, where an instant global hidden layer coexists with no
  faster-than-light signalling, and the no-signalling theorem. A physical claim would need a
  physical experiment.
- **Unrelated to the Exponential Time Hypothesis.** This test is about hashing in a lattice, not
  about the time complexity of SAT. It neither depends on ETH nor replaces it.

## Reproduction and provenance

| item | SHA-256 |
|---|---|
| `src/main.rs` | `407a8162c7ca0b10fe9ac07c07b65fb5b1c7df70f2650a16c97e92ec5bb696ec` |
| built `zlight.exe` (Windows, x86_64-pc-windows-msvc) | `07f9bf6cffbb0fb287329361345f61c90553455a5c220829a100334f2425dcbe` |
| `tribit/mod.rs` used through `#[path]` | `50e4cb85f3b8cf91f9e6b162f990eb51e5f984661259563a21188f3a1d560da0` |
| `torusl/src/sha.rs` used through `#[path]` | `d5ff519597eb04ff2200dbb8b8f753d9eb4c2f352199dc8fef2d47456ab16db8` |

- `src/main.rs` reaches those two modules through absolute `#[path]`s on the acer host
  (`C:/asolaria-acer/…/tribit/mod.rs` and this repo's `native/ym/crates/torusl/src/sha.rs`). To
  rebuild elsewhere, point both at copies with the hashes above.
- This directory is not a workspace member, so CI does not build it.
- Check the records with `sha256sum -c PREREG.hbp.sha256 RESULT.hbp.sha256`.
- One observation is recorded but not interpreted: at step 28 only 2 states are distinct. The
  rule is linear mod 3, so some arriving waves cancel at that cell and step.
