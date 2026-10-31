# Segmented-store P2/P3: frozen specification (reviewed; NOT YET RUN, execution needs separate authorization)

Seat ACER-CLAUDE-FABLE5, 2026-10-30. This freezes, before any run, how identity gates P2 and P3
are checked for the local segmented-store sources. Integer only, json=0. Chain: HBI → HBP → SHA →
SH → HASH (`SEGP2P3-SPEC.hbi`, `SEGP2P3-SPEC.hbp`, `SHA256SUMS`, `segp2p3.sh`, `SEGP2P3.seal`).
The production HOLD is unchanged by any outcome. No 3×4 gap verdict follows from any outcome.

## 1. Code under test (bound)

| item | value |
|---|---|
| commit | `2e4846e7440000b2b0ee6b0fabbea65afbfbe17c` |
| executables | the four in `native/ym/target/release` whose provenance passed (rebuild attempt 2, `PROVENANCE_PASS`) |
| `shellschur.exe` | `29b6b55078796ad223b31373f063196a7b3a24a5f2396496b129b96c36542dd3` |
| `roomschur.exe` | `a8007c1545a2d8827964fad71a761c1a38744671173bf393f0517e1297434eff` |
| `ymroom.exe` | `a0bc359d88aca652e5b4ec9e192741d8a1c8c501658e7fd0e33055b410c12cc8` |
| `ymsec.exe` | `9fa8232d917892df9c0b071903f258849d40dcd477f984a438fab6a561168607` |
| sources | `segio.rs` `e9253ea2…`, `ymroom.rs` `2a8409b1…`, `roomschur.rs` `f213b009…`, `shellschur.rs` `9bd8d245…` (executed copy CRLF `809d6330…`, no effect on the executable, measured) |
| host | acer (Windows, x86_64-pc-windows-msvc), run directory `D:/ym-3x4-room-run/segp2p3` (must not exist at start) |

**What changed from the CI-tested sources (`c07eef7`), measured by diff:** only the store open.
`ymroom build` and `roomschur` open their device through `segio` (and `ymroom build` adds a
`sync`). `ymroom text`, `ymsec` and `shellschur` code paths are unchanged. So CI's P2
(`ymroom text` vs `ymsec`) does not exercise the segmented code; this spec adds a store-level
identity test that does.

## 2. P2: builder identity (2×3, 2×4, 3×3; Sx+Sy+)

Per lattice, in `p2/<L>/`:

1. **Text identity.** `ymsec LX LY 1 1 ymsec.txt` and `ymroom text LX LY ymroom.txt`. Equal bytes and
   SHA-256, **and** equal to the CI anchor from receipt `ci-40936173167`:
   2×3 `2bc797fe…`, 2×4 `a34d2523…`, 3×3 `ad0168f9…` (full values in the HBP).
2. **Store identity across segment geometries.** `ymroom passa`, then three `ymroom build` runs
   from the same `passa.bin`, each with a fresh zero `keys` file, at offset 0:
   - `single`: one file, as the CI backend builds it;
   - `G1`: `seg:` store, segment length 40,000,000 B (the length the local 3×3 gate used);
   - `G2`: `seg:` store, segment length 1,048,583 B (prime, aligned to nothing; many boundaries).
   Segment count = ⌈size/seglen⌉ + 1, so one whole spare segment follows the store.
3. **AGREE for the lattice** needs all of:
   - every build exits 0 with `w_self_adjoint=PASS` and `header_readback=EXACT`;
   - the `YMROOMHDR` line (with `payload_merkle`, `keys_sha256`, `payload_bytes`) is identical
     across all three geometries;
   - the segmented store's logical bytes (segments concatenated in index order, first *size*
     bytes) equal the single-file store byte for byte;
   - every byte after the store, to the end of the last segment, is still zero (no stray write);
   - text identity and CI anchor as in step 1.
   A fully computed difference in any compared item is **MISMATCH**. A missing, failed or
   duplicated row is **INCONCLUSIVE**.

## 3. Segment-integrity controls (planted)

On a 2×3 store built in control geometry G3 (segment length 16,411 B, prime). First check that it
equals the single-file 2×3 store, and that it has at least 6 segments. Each case runs
`roomschur` on a copy with `ROOMSCHUR_COLS=0:1`, t = 60,000,000 (2×3 core 74 at that t, per CI).

| case | planted fault | required |
|---|---|---|
| K0 | none | completes, `payload_merkle` = P2 2×3 value (not detected) |
| K1 | middle segment missing | detected |
| K2 | one byte flipped inside a middle segment | detected |
| K3 | two adjacent middle segments swapped | detected |
| K4 | a middle segment 1 byte short | detected |
| K5 | store opened with 2 fewer segments than needed | detected |

"Detected" means at least one of: exit code not 0 or 2; no `SHELL_SCHUR_COLS` line; or a
`payload_merkle` different from the P2 2×3 value. All six must come out as required, or the whole
run is INCONCLUSIVE.

## 4. P3: runner identity (3×3, Sx+Sy+)

Inputs: shell side reads `p2/3x3/ymsec.txt`; room side reads the P2 3×3 **G1 segmented store**.
Parameters exactly as CI: JE 1000, JB 9000, FDIG 12 (F = 10¹²), TOL 1000, MAXSWEEP 4000,
SHELL_MAX −1; roomschur `ROOMSCHUR_K=8`, `ROOMSCHUR_BUDGET=12884901888`.

| t (milli-units) | frozen core | chunks S |
|---|---:|---:|
| 60,000,000 | 101 | 2 |
| 72,000,000 | 1,137 | 16 |
| 90,000,000 | 2,940 | 40 |

Chunk *i* is `[⌊i·core/S⌋, ⌊(i+1)·core/S⌋)`, **the same chunks on both sides**. This resolves
the split-versus-unsplit `SHELL_SCHUR_COLS` discrepancy (seen in the local cross-check) by
construction, with **no new comparator exclusion**.

- **Chunk runs:** `SHELLSCHUR_COLS=a:b shellschur …` and `ROOMSCHUR_COLS=a:b roomschur …`. Each
  chunk gets a binding line (`INPUT_MATRIX` / `INPUT_ROOMS`), re-hashed at chunk time. Binding lines
  go to separate `.bind` files and are not fed to the merge.
- **Chunk integrity, per side:** all S present, each with exactly one `SHELL_SCHUR_COLS` line;
  exits 0 or 2; ranges an exact partition of `0..core`; `core=` equal to the frozen value; every
  binding line equal to the expected SHA-256.
- **Merges:** `SHELLSCHUR_MERGE=…` and `ROOMSCHUR_MERGE=…` over the S chunk files. Merged `core`
  must equal the frozen value.
- **Evidence per side:** each chunk's output plus its binding line, in chunk order, then the merge
  output. This is the CI shape.
- **Store binding:** every room `SHELL_SCHUR_COLS` line carries the same `payload_merkle`, equal to
  the P2 3×3 value. The matrix and the store's logical bytes are re-hashed before and after each
  threshold and must be unchanged.
- **Comparison:** `schur_record_compare_stream.py` (`7b224b21…`, imports `schur_record_compare.py`
  `977e5e81…`), copied from `main` `6c34c35`. **v2 decides**; v1 (`--v1`) is reported verbatim as
  the strict result. These are the reviewer-accepted v2 rules: every SCOL record and every summary
  field is compared, excluding only `matrix=` and `ms=`, plus the three room-only fields on
  `SHELL_SCHUR_COLS` lines.
- **Verdict per threshold:**
  - **AGREE:** v2 AGREE (exit 0) and every integrity gate passes.
  - **MISMATCH:** v2 MISMATCH (exit 2) with every integrity gate passing.
  - **INCONCLUSIVE:** anything else.
  P3 is AGREE only if all three thresholds are AGREE.
- **AMBIGUOUS:** a shared AMBIGUOUS result (expected at 90M: negative 37, 9 ambiguous) is reported
  with its counts and `spectral_pass=0`. AGREE there is implementation agreement only, never a
  spectral-count PASS.

## 5. Control C-SF60 (same binary, single-file vs segmented store)

At t = 60M with the same two chunks and merge, `roomschur` reads the single-file 3×3 store. Its
SCOL lines must be byte-identical to those from the segmented store, and v2 must give AGREE.
Otherwise the run is INCONCLUSIVE.

## 6. Synthetic controls (run now, pure logic, no store or executable)

| control | result | file |
|---|---|---|
| comparator stream equivalence vs v2 and frozen v1 (`9f60d56`, `8cbe0015…`) | 60 cases, 120 comparisons, PASS (same as CI `EQUIV.hbp`) | `COMPARATOR-CONTROLS.hbp` |
| verdict logic (`segp2p3_verdict.py`) | 24/24 PASS (incl. every verdict row `spectral_pass=0`, P3 scoped to G1) | `SEGP2P3-VERDICT-CONTROLS.hbp` |

Both are re-run at the start of execution and must reproduce these totals exactly.

## 7. Failure behaviour

- **Preconditions:** spec SHA256SUMS and seal verify; the four executable hashes match; no
  chain/build process is running; D: has ≥ 20 GB free; the run directory is new. Any failure ends
  with all verdicts INCONCLUSIVE and nothing built.
- **Every verdict comes from `segp2p3_verdict.py`** reading the evidence rows only. A missing,
  duplicated or malformed row is INCONCLUSIVE, never a pass.
- **End integrity:** the four executable hashes and the spec files must be unchanged at the end,
  or everything is INCONCLUSIVE.
- **Scope of writes:** nothing outside `D:/ym-3x4-room-run/segp2p3` is written. The production
  stores (`D:/ASOLARIA-HOST8-ROOMS-300G`) and the operator's checkout are only read; the
  executables in the checkout are read and executed.
- **Launch:** detached, with Git's `/usr/bin` on PATH (attempt-1 rebuild lesson), from a working
  directory outside the checkout.

## 8. Expected artifacts

`SEGP2P3.hbp` (+ `.sha256`) with rows `PRECONDITIONS`, `P2_TEXT`, `P2_BUILD`, `P2_SINGLE`,
`P2_STORE`, `SEG_CONTROL_STORE`, `SEG_CONTROL`, `P3_CHUNKS`, `P3_MERGE`, `P3_MERKLE`, `P3_INPUTS`,
`P3_CMP`, `P3_CMP_STDOUT`, `CSF60`, `CONTROLS`, `END_INTEGRITY`, then `SEGP2_VERDICT` ×3,
`SEGP3_VERDICT` ×3 and `SEGP2P3_VERDICT`. All raw outputs stay under the run directory; large
files are bound by SHA-256 when receipts are committed.

## 9. Cost (CONJECTURE until measured)

Measured references, unsplit, this host:
- roomschur: 513 s, 5,733 s and 21,745 s at 60M, 72M and 90M;
- shellschur cols + merge: 836 s, 8,784 s, and about 31,000 s at 90M.

Splitting repeats each runner's pass 0 per chunk, so the split total is at least the unsplit
total: about 17 h as a lower bound, plausibly 20–35 h, run sequentially.

Peak memory:
- **Measured:** the 90M shellschur merge process peaked at 2,643,677,184 B (working set).
- **Not recorded:** the shellschur column process and roomschur on the 3×3 store. The run will
  not sample memory (it is not an admission gate), so these stay CONJECTURE.

## 10. Not decided here

- The production HOLD.
- Any 3×4 gap verdict.
- The frozen P4 result (run 41053502633), which is independent.
- Merge of PR #37 (stays draft).

## 11. Review decisions (operator, 2026-10-30), frozen before any run

1. **CI text-hash difference = MISMATCH**, but only when complete, valid output was produced from
   the frozen inputs and configuration. Missing, malformed, incomplete or unverified evidence is
   INCONCLUSIVE.
2. **P3 is scoped to G1 only.** G2 (and G3) get byte-level builder verification under P2, not
   runner-identity certification under P3. Store identity is not read-path identity:
   - P2 shows the segmented stores' bytes equal the single-file store.
   - That does not show that `roomschur` reads G2 identically; only G1 is certified for reading.
   - Every `SEGP3_VERDICT` row carries `scope=G1_segmented_store`. The overall row carries
     `P3_scope=G1_segmented_store_only` and `G2=P2_builder_bytes_only_not_runner_certified`.
3. **Sequential execution on this host**, after final review and separate authorization. The
   duration stays CONJECTURE. A timeout, OOM, crash or incomplete run fails closed:
   - a tool exit other than 0 or 2, or a missing, malformed or duplicated row, gives INCONCLUSIVE;
   - **if the run ends without a `SEGP2P3_VERDICT` row, the result is INCONCLUSIVE**;
   - thresholds, frozen cores and partition sizes are never changed to make a run fit.
   - No synthetic terminal row is ever written to complete a run.
4. **This spec is committed to draft PR #37** in one append-only commit. Existing receipts and
   manifests stay unchanged.

**Never a spectral PASS.** P2/P3 test implementation identity only. No P2/P3 row ever reports a
spectral PASS: not at 60M, not at 72M, even where both implementations agree. Every verdict row
carries `spectral_pass=0`. At 90M the expected shared result (9 ambiguous columns, negative 37) is
implementation agreement only.

**Every comparator dependency is frozen** in `code/` and in `SHA256SUMS`. v2 decides, v1 is
reported verbatim, and **no new mathematical-field exclusion is authorized**.

| file | role | SHA-256 |
|---|---|---|
| `schur_record_compare_stream.py` | deciding v2 implementation (stream) | `7b224b21598432db6511fc5a2dd11d382c5c9288967a792fd71efeafa953efa9` |
| `schur_record_compare.py` | v2 rules, imported by the stream module | `977e5e81fc609662cad3a19299928ed8a0545a0add1dae76d04835f29e1a0c62` |
| `schur_record_compare_v1_9f60d56.py` | frozen v1 reference (`9f60d56`) | `8cbe0015df4310cf…` (full value in `SHA256SUMS`) |
| `schur_record_compare_stream_controls.py` | stream-equivalence controls | `b4e92e79bbf19cc0…` (full value in `SHA256SUMS`) |
| `schur_record_compare_controls.py` | synthetic cases used by the controls | `8f6334e0ff34d94a…` (full value in `SHA256SUMS`) |

**Superseded draft seal (kept beside, not erased):** `f4e557a3e6734101186ec67fd5e5af187c350ee4174878ac1a3b5eead8b8f67d`.
That seal covered the pre-review draft. It was reported to the operator and never committed or
executed. The seal in `SEGP2P3.seal` replaces it for execution.
