# Issue #137 — Worker 1 B7 checked signed 320-bit moment arithmetic

This exact Rust 1.81 component is stacked on source authentication (B1/B2), all real 72-move Q5 census (B3), and draft B4 reverse-pair processing, for later integration into the real 8×8 Q5 moment matrices. Stage A's `Wide([u64;5])` product/add/sub operations have been adapted to **checked** signed addition and guaranteed Q5 per-term and partial-sum limits.

## Production-only hypotheses and arithmetic safety

The accepted Q5 source stores eight unsigned packed `V1/b` lanes at 82 bits each. For `b=10^9`, one physical Q5 amplitude satisfies `0 <= a < 2^112` and likewise `b`. The complete signed coefficient passed to `CheckedMoment::add_term(a,b,coef)` must include **all** operator and orbit scaling, including the factor six exactly once; the worker explicitly enforces `|coef| < 2^46` and at most `2^31` accumulated terms. Therefore each product magnitude is bounded by `2^270` and the worst-case absolute partial sum by `2^301 < 2^304`. The final tighter gate `|partial| < 2^304` is enforced on **every** accumulation. These limits have margin inside signed two's-complement 320-bit arithmetic, which has range `[-2^319,2^319-1]`.

The accumulator first verifies its input and count, then forms a signed full-width term, checks for two's-complement overflow and verifies the post-update magnitude. A rejected term cannot mutate the accepted state. Every later Stage B signed Q5 matrix accumulation must use these checked operations or an independently verified equivalent; the Stage A wraparound helper alone cannot supply this safety.

**Scope:** The Q5 bound relies on archived source lane and operator coefficient limits. Signed K3 and Q4 amplitudes in Stage C require their own proven bounds and checks.

## Exact hosted tests

- Signed 320-bit maximum +1 and minimum −1: **REFUSE**.
- Positive and negative `2^304` boundary crossings: **REFUSE**.
- Cancellation of opposite near-boundary 320-bit values: exact zero.
- A 112-bit amplitude overflow: **REFUSE**.
- A weighted operator coefficient reaching `2^46`: **REFUSE**.
- A term count reaching `2^31` then adding another: **REFUSE**.
- Two opposing very-large signed products using `a,b<2^112`, `|coef|<2^46`: exact cancellation.
- Independent Python unlimited-integer comparison of 5,000 deterministic mixed-sign triples against the Rust five-limb result and its negative.

The dedicated workflow pins Rust 1.81, strict Clippy, source and executable SHA-256, the exact Python verdict and the GitHub execution SHA. The full Q5 moments and Wilson weight remain pending, and this source-free control must not be described as a real μ₃ result.

**Next:** cloud review of the runtime arithmetic before integration into the B5 row and independently paired-edge Q5 matrix calculations. Original `mu2_six` 16 hashes, signed Q4/K3 source authentication and the final Wilson normalization remain required.
