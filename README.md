# HEB-C × Clasy X3 — finite Yang–Mills research bridge

[Open the standalone HEB-C page](index.html) · [Technical report](HEBC_CLASY_X3_INTEGRATION_REPORT.md)

This repository invokes the published [Clasy X3 81-mode shell implementation](https://github.com/JesseBrown1980/Clasy-repo-x-3-/blob/63cbf283b900457f8dfc59ac0e42d3efcbc9aedb/src/lib.rs) in a self-stepping browser executor. The operator uses exact finite-field arithmetic with P=1,000,999, K=81, W=30,722 and D81=900,647. It demonstrates 243 exact transitions with an independent Python reference, a 23,000,000,000-ID *virtual* HTTP-0 address space with 1,990,656 sampled routes, and an exact six-vertex S3 Cayley-graph spectral diagnostic.

**Mathematical scope:** The Clasy theorem is an exact finite-field shell-total invariant; the finite S3 graph Laplacian has eigenvalues 0,3,3,3,3,6 and graph gap 3. Neither result proves existence of four-dimensional quantum Yang–Mills theory with a positive mass gap. The browser does not establish gauge-invariant quantum field reconstruction or a continuum/infinite-volume gap.

**Transport scope:** 23 billion are logical labels, **not 23 billion active HTTP connections**; the experiment opens zero actual HTTP/WebRTC channels. The browser uses neither the physical Host8 disk nor GGUF/HRM inference. Do not compare its step throughput to a full Host8 D3Q27 room evolution as though they are identical workloads.

## Measured Chromium container pilot

| Measurement | Result |
|---|---:|
| Clasy 81-shell exact steps | 243 / 243 |
| Invariant deviations | 0 |
| Sampled virtual routes | 1,990,656 |
| Full run wall time | 658 ms |
| Isolated shell kernel + checks | 13.9 ms |
| Virtual route sampling | 211.8 ms |
| Final state SHA-256 | `ad8e4d756af66f9d404009243760fc6c31cf4a8e3f90633b444116e5d9a36b88` |

[Clasy X3 mathematical and continuum limitations](https://github.com/JesseBrown1980/Clasy-repo-x-3-/blob/63cbf283b900457f8dfc59ac0e42d3efcbc9aedb/X3-PROOF.md) · [Existing HTTP-0 Light Hub](https://jessebrown1980.github.io/the-light-hub-http-0/).

Open `index.html` to rerun; it automatically stops at exactly 243 transitions and exposes HBP/HBI/report downloads. Run `python tests/verify_evidence.py` to independently check the recorded evidence and the finite-group eigenbasis.
