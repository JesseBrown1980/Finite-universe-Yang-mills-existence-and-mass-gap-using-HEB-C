# HEB-C HTTP-0 / SG-RAM headless backend test ground

Status: separate feature branch / draft PR, not a continuum Yang–Mills proof.

## Design

- Native Rust 1.81 backend at native/src/bin/hebc_http0_sgram.rs, reusing the original HEB-C virtual address formula, pinned Clasy81 kernel and Stage 2G finite S3 torus bounds. Does not modify their equations.
- HTTP-0 means an internal virtual address/dispatch contract, **not** a wire-level protocol. Optional loopback transport is conventional HTTP/1.1 bound to 127.0.0.1 only.
- SG-RAM here denotes stateless-cell, disk-backed evidence. Active Clasy 81-mode computations use real CPU and RAM. The 23,000,000,000 virtual coordinates use no per-coordinate storage or execution.
- No JSON/JavaScript/GPU dependencies; results end with json=0.
- Each completed Clasy run saves run.hbp, index.hbi, run.anchor and run.measure in its own ordinal/ticks disk shard. The verifier re-executes the original kernel and compares every file byte-for-byte; it does not trust unsigned self-consistent hashes as origin authentication.
- An existing shard is replayed rather than overwritten. Exclusive staging directory creation prevents two local writers from sharing an unfinished shard. Interruption can leave staging evidence, which is never automatically accepted.

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

## Performance boundary

Prior user measurements on the **original** HEB-C server gave roughly 161 ms for the HTTP /torus2/1/1 computation, compared with roughly 334 ms for the direct torus2-spectrum CLI. The CLI also wrote receipts, so those are **not equal-work performance comparisons**. A tiny /gap operation took roughly 2.2 ms direct versus 9.8 ms over HTTP. Namespace address lookup is constant-sized but not literally zero CPU. Earlier measurements gave approximately 5 MB RAM and no GPU usage for that server configuration; neither is a new benchmark of this SG-RAM implementation.

## Scientific limits

All computations here reuse the finite periodic 2x2 S3 lattice and the separate Clasy81 finite-field kernel. No derived map between their physics is assumed. No uniform infinite-volume gap, string tension, quantum gravity, 4D continuum Yang–Mills theory, or faster-than-light transfer follows.
