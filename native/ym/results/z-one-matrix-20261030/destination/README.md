# Destination-bound z token, ring return and both curved-j orientations

2026-10-30 — isolated software experiment. **No physical faster-than-light propagation, no quantum dynamics, and no Yang–Mills mass gap are established.** This directory does not modify P2/P3, P4, PR #37 or PR #40. Python 3 standard library only, exact integer and SHA-256 operations; `json=0`. No Rust 1.81 compilation is claimed for this experiment.

## Frozen experiment sequence (retain both)

1. `PREREG.hbp` (SHA-256 `955033f0…`) was written and hashed before `test_v1.py`. Its prediction that the unselected destination would remain unchanged indefinitely on a ring was **FALSE**. `RUN1.stderr` records the failed `P3 nonselected` assertion and `RUN1.exit` records exit 1. The file is retained unedited.
2. `PREREG-v2.hbp` was frozen after discovering the failure, *before modifying and rerunning* `test.py`. It narrows the observational window to **through the first selected/old destination arrival**, allowing a pulse to return around the ring later. This is a declared revision, not an independently preregistered new discovery.
3. `RESULT-v2.hbp` records three ring sizes (`3^3`, `3^4`, `3^5`), destination-bound metadata versus local physical Merkle root, token gate rejects, retargeting before release and in flight, and local no-signaling. P1–P5 pass for the revised finite-window predictions. The protocol gate is **constructed into the simulator**. It cannot demonstrate that any physical emission needs a z token.
4. B1–B4 test both signed curves `j+ = I + R − R²`, `j− = I − R + R²` (mutual transposes). Both are asymmetric, couple three positions, and have rank 3 over GF(3), giving 27 distinct images across the 27 input vectors. `J = I + R + R²` is rank 1 and produces 3 images. **No orientation is singled out** by the dictionary or these symmetric tests. For signed multi-source inputs, cancellation can occur locally even though the whole output remains nonzero for any nonzero input (rank 3).

## Subtleties that matter

- **One matrix, one universe** here means one 3^N-ring state at each tick, not physically separate universes. Counterfactual runs are compared independently.
- Before release, retargeting affects the **protocol digest**, because it explicitly contains the destination. The physical-cell Merkle root remains identical. A target whose observable includes the global protocol digest could distinguish one bit about the retargeting before light arrives; this is prohibited in the local-observer model.
- After a packet has already left the source, changing *metadata* in this model does not instantaneously redirect its physical trajectory. A protocol that changes the physical route must deliver that command causally or explain an additional signal mechanism.
- A closed ring necessarily has a return path. An unrelated ring position can be affected at a **later** time. Original V1 excluded this and failed; the V2 bounded claim is narrower.
- SHA-256 roots encode logical relationships. They do not establish an instantaneous physical interaction. Creating a token from remote cell state is an explicit global-oracle privilege, not a locally realizable measurement.
- Neither the choice of `j+` versus `j−` nor the assertion that a photon requires z can be decided by these constructed updates.

## Reproduce and verify

From this directory: `sh run.sh`. It checks `SHA256SUMS`, verifies the HBI chained entries and `ZDEST.seal`, reruns the **V2** source into a temporary file and byte-compares it with `RESULT-v2.hbp`, and verifies the original V1 run still fails for the registered reason. Outputs and archived records are never overwritten. `RUN1.stderr` contains the local machine's original path and need not be byte-identical on another machine.

**HBI → HBP → SHA → SH → HASH**: `ZDEST.hbi` is the chained filename/sha record, `PREREG*.hbp` and `RESULT-v2.hbp` are records, `SHA256SUMS` and sidecars identify their exact bytes, `run.sh` replays without mutation, and `ZDEST.seal = SHA256(SHA256SUMS bytes || ZDEST.hbi bytes)` is the local bundle seal. It is not a trusted third-party signing key or the PR #37 authorization anchor.
