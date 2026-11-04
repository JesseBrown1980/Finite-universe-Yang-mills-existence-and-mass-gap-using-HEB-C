# Yang–Mills 3×4 certificate evidence on HTTP-0's 3^16 portal

**Status (November 4, 2026):** An exact-source Yang–Mills certificate index for HTTP-0. This addition does not alter or rerun the finite-lattice Hamiltonian, and does not upgrade a HOLD or OPEN result to PASS.

The companion [HEB-C HTTP-0 portal](https://github.com/JesseBrown1980/qoled-internet-HEB-C-revisted-HTTP---free-0-hbi-hbp-sha-sh-hash) uses a **3^16 = 43,046,721**-address sparse namespace, already holding [three Taylor–Green/Clay time steps](https://github.com/JesseBrown1980/continuum-Clay-variation/blob/main/bridge/taylor-green/README.md). These are **virtual evidence locators**, not independently calculated field states.

Yang–Mills uses the **fifth ternary digit (3^4=81)** to select a separate domain. Clay's 729 measured entries have this digit set to zero; Yang–Mills entries have it set to one. Their source-data addresses **81, 82 and 83** cannot collide. There are now **732 populated slots**, leaving 43,045,989 deliberately unpopulated.

## Three exact, pinned receipts

The source commit is **5517268b511d5f28e307b21fc53eede3200ed7b9**. Both SHA-256 and the original Git blob SHA-1 are registered, and the read-only verifier compares the actual bytes and measured fields.

| Address | Evidence | Retained statement | Scope |
|---|---|---|---|
| **81** | [PERRON-RESULT.hbp](../native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp) | **94.070673 J_E** Perron lower and **94.070936 J_E** upper bracket | Original result retains **gap_verdict=OPEN** |
| **82** | [FULLREBUILD-RUN.hbp](../native/ym/results/3x4_stream/perron/FULLREBUILD-RUN.hbp) | **45,508,080 rows rebuilt**, zero recorded mismatches, 34/34 sectors | Recorded measured PASS, **not rerun by HTTP-0** |
| **83** | [ALLPAIRS-RUN.hbp](../native/ym/results/3x4_stream/perron/allpairs/ALLPAIRS-RUN.hbp) | **1,632,625,631 pairs**, four passes, no recorded mismatches | Recorded measured PASS, **not rerun by HTTP-0** |

The receipts are already published. Their integrity checks do **not** replace a new independent reconstruction of the Hamiltonian. The formal 3×4 gap-verdict gate and operator approval are separate.

## Independently verifiable source-to-address conversion

The [standalone Python audit](../native/scripts/verify_http0_ym43.py) independently computes SHA-256 and Git blob SHA-1 for all three pinned files, checks the exact recorded integer fields, verifies the ternary addresses, and rejects intentionally corrupted or missing copies. It uses only Python's standard library and integer arithmetic.

Run from the Yang–Mills repository root:

~~~bash
python3 native/scripts/verify_http0_ym43.py .
~~~

The [native Rust HTTP-0 implementation](https://github.com/JesseBrown1980/qoled-internet-HEB-C-revisted-HTTP---free-0-hbi-hbp-sha-sh-hash/blob/main/src/ym43.rs) independently checks the same evidence. In the HTTP-0 repository:

~~~bash
cargo +1.81.0 run --release --locked --offline -- --ym43-verify /path/to/pinned/yang-mills
cargo +1.81.0 run --release --locked --offline -- --ym43-lookup /path/to/pinned/yang-mills 81
~~~

To serve trusted records, set **HEB_C_YM43_ROOT** to that pinned source directory *before* starting the loopback HTTP-0 portal.

| Read-only HTTP-0 endpoint | Behavior |
|---|---|
| /bridge/43m/catalog | All models' occupied-source counts, explicitly distinguished |
| /ym/43m/contract | Address layout, source pin and OPEN qualification |
| /ym/43m/availability | HTTP 200 if all three source receipts validate; otherwise 503 |
| /ym/43m/address/81 | Exact Perron source and its OPEN status |
| /ym/43m/address/82 | Exact all-rows rebuild receipt |
| /ym/43m/address/83 | Exact all-pairs verification receipt |
| /bridge/43m/lookup/81 | Shared address dispatcher; same Yang–Mills result |
| Any unpopulated address | 404, never a fabricated certificate |
| Malformed or out-of-range address | 400 |

The legacy **/bridge/43m/address/** path remains Clay-specific and intentionally returns 404 for Yang–Mills addresses; use **/bridge/43m/lookup/** to dispatch across domains.

## Proof obligations and limits

This connection is a **proof-evidence interoperability layer**. The source records concern S₃ Yang–Mills Hamiltonian certificates on a fixed 3×4 finite spatial lattice. The Clay/Clasy shell map and Taylor–Green lattice gas have different dynamics; assigning records within the same virtual namespace does not equate their state spaces or spectral gaps.

The Yang–Mills finite-system scope remains unchanged. The spacing-to-zero continuum limit at fixed finite physical volume stays OPEN.

Verification: [Yang–Mills source auditor workflow](../.github/workflows/http0-ym43.yml) · [HTTP-0 pinned-source workflow](https://github.com/JesseBrown1980/qoled-internet-HEB-C-revisted-HTTP---free-0-hbi-hbp-sha-sh-hash/blob/main/.github/workflows/ym43.yml).
