# HEB-C HTTP-0 / SG-RAM headless backend test ground

Status: separate feature branch / draft PR, not a continuum Yang–Mills proof.

## Design

- Native Rust 1.81 backend at native/src/bin/hebc_http0_sgram.rs, reusing the original HEB-C virtual address formula, pinned Clasy81 kernel and Stage 2G finite S3 torus bounds. Does not modify their equations.
- HTTP-0 means an internal virtual address/dispatch contract, **not** a wire-level protocol. Optional loopback transport is conventional HTTP/1.1 bound to 127.0.0.1 only.
- SG-RAM here denotes stateless-cell, disk-backed evidence. Active Clasy 81-mode computations use real CPU and RAM. The 23,000,000,000 virtual coordinates use no per-coordinate storage or execution.
- No JSON/JavaScript/GPU dependencies; results end with json=0.
- Each completed Clasy run saves run.hbp, index.hbi, run.anchor and run.measure in its own ordinal/ticks disk shard. The verifier re-executes the original kernel and compares every file byte-for-byte; it does not trust unsigned self-consistent hashes as origin authentication.
- An existing shard is replayed rather than overwritten. Exclusive staging directory creation refuses a second writer for that shard; interrupted staging is not automatically accepted. Explicit offline replay-verified recovery and non-destructive quarantine commands are available, but the operator must ensure no active writer remains.

## Reproduce

From native/:

    cargo +1.81.0 test --all-targets --offline --locked
    cargo +1.81.0 clippy --all-targets --offline --locked -- -D warnings
    cargo +1.81.0 build --release --offline --locked --bins
    target/release/hebc_http0_sgram address 22999999999
    target/release/hebc_http0_sgram run /tmp/hebc-sgram 7 3
    target/release/hebc_http0_sgram verify /tmp/hebc-sgram 7 3
    target/release/hebc_http0_sgram finite-gap 1 1
    target/release/hebc_http0_sgram finite-gap 3 5
    target/release/hebc_http0_sgram serve /tmp/hebc-sgram 5097 16

Loopback smoke (while server is active):

    curl http://127.0.0.1:5097/health
    curl http://127.0.0.1:5097/qtrit/22999999999
    curl http://127.0.0.1:5097/finite-gap/1/1
    curl http://127.0.0.1:5097/finite-gap/3/5
    curl -X POST http://127.0.0.1:5097/run/8/3
    curl http://127.0.0.1:5097/verify/8/3

Service accepts at most a caller-chosen bounded number of requests, has a 2048-byte request-header limit, supports no request body, and is NOT hardened for public deployment.

## Full acceptance gates

The dedicated .github/workflows/http0-sgram-backend.yml runs Rust 1.81 all-target tests, zero-warning Clippy, release build, full live-loopback smoke on both supported Stage 2G coupling sets, HBP/HBI source replay, corrupt-shard rejection, invalid-request controls, and zero-JSON artifact check. These supplement, rather than replace, PR #9's complete first-excitation inertia certificate and the original native verifier gates.


## Explicit interrupted-shard recovery

A crash can leave an incomplete `.inflight-…` directory. **Never** automatically delete or trust it. Stop the HTTP-0 service and every other writer for the same root first; this prototype does not implement a cross-process filesystem lock. Then:

    target/release/hebc_http0_sgram recover /tmp/hebc-sgram 7 3

`recover` checks the full original HBI/HBP chain, regenerates the pinned Clasy computation and compares all four evidence files byte-exactly. It promotes the staging directory only when everything passes and no committed shard exists. Partial/corrupted staging is refused and left untouched. Explicitly quarantine such an interrupted shard:

    target/release/hebc_http0_sgram quarantine /tmp/hebc-sgram 7 3

Quarantine renames the directory into a distinct `.quarantine-…` slot for forensic preservation, then the next ordinary `run` can create fresh evidence. This is an operator action, never an automatic wipe or implicit proof of the quarantined contents. Operators must not call recovery/quarantine while another writer is live.

## Provenance-labelled finite spectral response

`finite-gap` / `GET /finite-gap/:JE/:JB` **computes Stage 2G** Collatz–Poincaré energy enclosures. The legacy `E1=[lower,upper]` field remains for clients, explicitly labelled `E1_source=STAGE2G_COLLATZ_POINCARE` and duplicated as `E1_stage2g`. A separate `E1_stage2h_strict_gt_reference` field shows **13240/1000** at (1,1) or **50840/1000** at (3,5), from the native Stage 2H certificate independently checked in PR #9. Critically `E1_stage2h_verified_this_request=0`: the light HTTP route **does not run** Stage 2H inertia, reproduce PR #9, or replace the original rigorous certificate. Do not compare their execution times as if equal work. These bounds concern the finite S3 Hamiltonian only.

## Performance boundary

Prior user measurements on the **original** HEB-C server gave roughly 161 ms for the HTTP /torus2/1/1 computation, compared with roughly 334 ms for the direct torus2-spectrum CLI. The CLI also wrote receipts, so those are **not equal-work performance comparisons**. A tiny /gap operation took roughly 2.2 ms direct versus 9.8 ms over HTTP. Namespace address lookup is constant-sized but not literally zero CPU. Earlier measurements gave approximately 5 MB RAM and no GPU usage for that server configuration; neither is a new benchmark of this SG-RAM implementation.

## Scientific limits

All computations here reuse the finite periodic 2x2 S3 lattice and the separate Clasy81 finite-field kernel. No derived map between their physics is assumed. No uniform infinite-volume gap, string tension, quantum gravity, 4D continuum Yang–Mills theory, or faster-than-light transfer follows.
