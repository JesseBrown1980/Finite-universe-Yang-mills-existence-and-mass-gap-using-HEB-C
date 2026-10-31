# 3×4 Sx+Sy+ on local Host8 rooms: run log (in progress)

**Status: IN PROGRESS. Nothing here is sealed, and production is not admitted.**
`PRODUCTION-ADMISSION.md` (hosted-runner lane, `BUDGET = 12 GiB`) is unchanged and its
HOLD stands. This record is the local room-backed lane: the same operator and the same
inertia method, with the matrix kept in 8-byte Host8 rooms instead of runner RAM. Every
figure below comes from a named command and receipt. Figures still awaiting a run are
marked PENDING or CONJECTURE.

| item | value |
|---|---|
| machine | ACER, Intel i5-8300H (4 cores / 8 threads), 16 GiB RAM, Windows 11 |
| toolchain | Rust 1.81.0 (msvc), `cargo +1.81 clippy --release -- -D warnings` exit 0 for both new bins |
| new binaries | `ymroom` (builder, `crates/torusl/src/bin/ymroom.rs`), `roomschur` (runner, `crates/sturmrs/src/bin/roomschur.rs`) |
| reference binaries | `ymsec`, `shellschur` (unchanged) |
| receipt | `HEBC-YM-3X4-ROOM-RUN.hbp`, SHA-256 in `HEBC-YM-3X4-ROOM-RUN.sha256` |
| operator direction | matrix on the 2 TB USB stick (wrap-around risk accepted by the operator); representative keys in the 50M-room store |

## Why a room-backed lane

`benchmarks/onfly_3x4.hbp` records `full_inertia_certificate=NOT_FEASIBLE_with_current_tools`
for 3×4. The stored sector matrix (about 40 GB at 12 bytes per entry) exceeds runner RAM
and disk, and `ymsec` keeps a 13 GB `Vec<bool>` over 6¹³ tree configurations. Here the
matrix is one 8-byte room per entry, written once and streamed in index order on every
Gauss–Seidel sweep. Only the swept columns' enclosures stay in RAM, because Gauss–Seidel
reads arbitrary neighbour rows and a drive answers those at about 70 reads/s.

## Method

1. **Pass A (`ymroom passa`).** The `ymstream` scan over the whole gauge-fixed space
   keeps each least key of a G-orbit (all of them, since Sx+Sy+ has trivial characters)
   with its weight `|G|/|stab| × conjugation weight` and its magnetic number. This is the
   same weight `ymsec` stores (`img.len() × lat.weight`).
2. **Pass B (`ymroom build`).** Each representative's electric row is rebuilt in index
   order. Every move target is canonicalised under G and mapped to its index by binary
   search over the sorted keys. Rows go out as rooms: a header room `w:u32|mag:u16|cnt:u16`,
   then `cnt` rooms `j:u32|z:i32`. The build checks W-self-adjointness over every entry
   (signed hash sum = 0), records a 16 MiB-chunk SHA-256 merkle of the payload, and reads
   the header block back after writing.
3. **Runner (`roomschur`).** This is `shellschur`'s arithmetic copied unchanged:
   checked i128, outward floor/ceil, the Varah start box, and the BigInt dense LDLᵀ. Its
   output lines (`SHELL_SCHUR`, `SCOL`, core fingerprint) are the same, so the two can be
   compared record for record. K columns are swept in one pass over the rooms, each with
   its own counter and stop rule, so each column's update sequence is the one
   `shellschur` performs for it alone. Enclosures are stored as checked i64, and a value
   outside i64 stops the run. Every sweep recomputes the payload merkle against the
   header. Admission: `K·COL_BYTES + RESERVE ≤ BUDGET`, with `COL_BYTES = 16n` and
   `RESERVE = 41n + 3·64 MiB` (exact allocation sizes).

## Tests and results so far

| # | test | result | time |
|---|---|---|---|
| 1 | builder identity: `ymroom text` vs `ymsec L 1 1`, byte compare, 2×3 | **EXACT** (2,646 states, nnz 74,956, sha16 `2bc797fe8bafeb4c`) | 120 ms |
| 2 | same, 2×4 | **EXACT** (58,040 states, nnz 2,606,690, sha16 `a34d252302eea905`) | 5.9 s |
| 3 | same, 3×3 | **EXACT** (288,645 states, nnz 15,408,669, sha16 `ad0168f973d120a0`) | 37.6 s |
| 4 | 3×3 room build | entries 15,408,669 = ymsec nnz; `w_self_adjoint=PASS`; header readback EXACT | 93.8 s |
| 5 | 3×3 runner, `roomschur` at JE=1000 JB=9000 t=60,000,000 F=10¹² | core 101, negative 7, positive_core 94, 19 sweeps, PASS | 669 s (CPU shared with pass B) |
| 6 | same threshold, `shellschur` on the ymsec text matrix, record compare | was PENDING; now **AGREE** at t=60,000,000 (see 2026-10-29 update) | — |
| 7 | **3×4 pass A** | **45,508,080 states, 7 flat**, the same as CI pilot run 40391283682 (`Sx+Sy+ states=45508080`, `flat_states=7`); `passA.bin` SHA-256 `eefd7752…6e3cbc` | **1,399.3 s (23.3 min)**, 8 workers |
| 8 | 3×4 pass B (keys to 50M rooms, matrix to USB) | was running; finished **FAIL** (header readback mismatch, see update) | 16,998.9 s |

## Storage measurements (read-only probes, before any write)

| device | sequential read | 4 KiB random read |
|---|---|---|
| USB `General UDisk` 2 TB (PhysicalDrive2) | 10 MB/s | 61–65 IOPS |
| D: `WD10SPZX` HDD (PhysicalDrive0) | 55–196 MB/s | 72–78 IOPS |

## Writes made (ledger)

- `D:/asolaria-rooms-1m-50000000/stubs.hbi`: rooms 0 to 45,508,079 now hold the sorted
  representative keys. Prior SHA-256 `8cff9efd…af7d54`, with a verified backup at
  `D:/ym-3x4-room-run/stubs.hbi.backup`.
- USB PhysicalDrive2: the unallocated tail from offset 579,820,584,960. F: ends at
  537,871,960,064. Before writing, the MBR/E: region and 32 samples across F: were hashed
  (`USBSNAP-BEFORE.hbp`). The same snapshot is retaken after the build.

## Next (CONJECTURE until run)

- Pass B finishes in about 5 h at the current rate, giving about 3.35×10⁹ rooms (about 27 GB).
- One 3×4 sweep streams the matrix from the USB at its measured 10 MB/s: about 45 min.
  The memory pilot (`RESERVE`, `COL_BYTES`, peak working set, sweep time) runs first. A
  production count over the 137-column core at t = 60,000,000 follows only on its
  receipts.

## Update 2026-10-29

Rows above are kept as written; corrections sit beside them. Receipts for everything
below are in `receipts/` (checksums in `receipts/SHA256SUMS`). The large run outputs
(`roomschur-seg-t*.out`, `shellschur-cols-t*.out`, up to 1.6 GB) are not committed;
their SHA-256 values are in the receipts.

### Pass B on the USB stick: FAIL

`ymroom build` wrote all 26,850,885,632 stream bytes with 0 OS write errors, then exited 2
with `header_readback=MISMATCH`. The header, the first 16 MiB and 17 samples across the
declared extent all read back as zeros. All 33 sampled regions of the stick are
unchanged, and all logged Pass B stream writes were confined to the declared extent
`[579,820,584,960, 606,671,470,592)`. No claim is made about unsampled regions. The
likely cause (CONJECTURE) is that the stick's real capacity is smaller than it reports.
`receipts/usb-attempt/`.

### Pass B on D: (300 GB Host8 store, sectors 341..374): build integrity PASS (scoped)

Operator direction: put the matrix in the 300 GB store on D:. A new `segio` module lets
`ymroom` and `roomschur` treat a run of equal-length sector files as one stream. It never
grows or truncates a sector file.

| item | value |
|---|---|
| exit / header readback | 0 / EXACT |
| rows / rooms / entries | 45,508,080 / 3,356,267,422 / 3,310,759,342 |
| stream bytes | 26,850,885,632 of 27,200,000,000 capacity (margin 349,114,368) |
| W-self-adjoint | PASS |
| payload merkle | `ec03c5f8…072a0b`, equal to the USB attempt's (both 8 workers: repeatability, not worker invariance) |
| stream SHA-256 | `d8f2f4f5…aae9c254`, recomputed by a separate Python reader |
| time | 15,547 s, 8 workers |
| peak working set (Pass B process only) | 2,552,578,048 B |
| untouched checks | sector 374 tail unchanged; store seal `ROOMS-MAKE.hbp` unchanged; key rooms re-hashed equal |

The 34 prior sector hashes are in `receipts/d300/LEDGER.hbp`. Those sectors can be
regenerated from the store seed. Other tests that read sectors 341..374 now see matrix bytes.

### Segmented reader on 3×3

`roomschur` was given the same segmented 3×3 store and produced the same summaries as the
single-file runs: t=60e6 core 101 PASS, t=72e6 core 1,137 PASS, t=90e6 core 2,940
AMBIGUOUS (exit 2 by design). `receipts/gate3x3-seg/GATE3X3-SEG.hbp`.

### shellschur vs roomschur, record by record

| t | outcome |
|---|---|
| 60,000,000 | **AGREE**: 10,201 vs 10,201 `SCOL` records, keyed equal and in the same order, summary equal (excluding `matrix=`, `ms=`) |
| 72,000,000 | PENDING (running) |
| 90,000,000 | PENDING (queued). Agreement there would be agreement between implementations, not a spectral PASS. |

An earlier shellschur run is INCONCLUSIVE because I put an argument in the wrong
position (`SHELL_MAX=12`). The comparator treats a missing key or a differing field as
MISMATCH. It treats a crash, a duplicate key, truncated output or an unreadable file as
INCONCLUSIVE. Split-versus-non-split controls agreed on 3 of 3 completed cases; the
fourth was INCONCLUSIVE because my own timeout cut it off.

### Still open

- The 3×4 memory pilot runs only if all three comparisons AGREE. It has not started.
- No 3×4 gap verdict. Production HOLD (`PRODUCTION-ADMISSION.md`) unchanged.

### Update 2026-10-29 13:55

The t=72,000,000 row above said PENDING; it has now completed with **AGREE**: 1,292,769 vs
1,292,769 `SCOL` records, keyed equal and in the same order, summary equal (excluding
`matrix=`, `ms=`). This is agreement between implementations only. t=90,000,000 is running.
The full comparison gate stays INCONCLUSIVE and the 3×4 pilot stays blocked until it
completes. No 3×4 gap verdict, and production HOLD is unchanged.

## 2026-10-30: local evidence after t=90M (LOCAL EVIDENCE ONLY)

Everything below is local evidence. The segmented-store sources (commit `2e4846e`) have no P2/P3 of their own, and the local pilot is not the frozen P4 pilot. Binary provenance is open. There is no 3x4 gap verdict, and production HOLD is unchanged.

- **Three-threshold comparison:** AGREE at 60M, 72M and 90M, within the scope of `compare.py` (`57b4c811`). At 90M: 8,643,600 SCOL records, `seq_sha256` `371f8014...` on both sides, both AMBIGUOUS (core 2940, negative 37, ambiguous 9). That is agreement between implementations, not a spectral PASS. `GATE|all_three_AGREE=1` at 2026-10-29T22:27:51.
- **Local pilot (exploratory):** K=4, budget 9e9, runs to convergence, D: 300G sectors 341..374. Exit 0, 17,372 s, 548 SCOL lines, 19 sweeps. Peak working set of the roomschur process was 4,257,034,240 B, against the 4,979,674,992 B admission projection. `payload_merkle` `ec03c5f8...` equals the value Pass B recorded for D:. It cannot set the admission values; only the frozen P4 can.
- **Clean rebuild, attempt 1:** provenance INCONCLUSIVE. sturmrs failed with exit 101 on a cargo vendor checksum error. The clone had `core.autocrlf=true`, which wrote CRLF into vendored files. This is a procedure fault, not a mismatch.
- **v2 cross-check (b028a03 stream comparator):** raw MISMATCH at 60M and 72M in both modes. The only finding is `cols_line_keys:1_only_shell,0_only_room`, with no `more=`. It is classified as not comparable under the full-v2 input contract; it is not relabelled AGREE.
- **Source line endings:** the `shellschur.rs` that was executed had CRLF line endings (`809d6330`, 378 CR). The committed blob is LF (`9bd8d245`). With the CRs removed, the executed copy is identical to the committed blob. The other three sources are identical as they stand.
- **Embedded build path:** `shellschur.exe` and `roomschur.exe` embed absolute vendored-crate panic paths under this repo's checkout path. The exclusion decision for the rebuild comparison is pending with the operator.
- **Frozen P4, attempt 3:** dispatched as run 41053502633 on `main` at `6c34c35`. Result pending.
- **Large raw outputs** are kept outside git and bound by SHA-256 in `receipts/RAW-ARTIFACTS-OFFGIT.hbp`. The new receipt files are covered by `receipts/SHA256SUMS-2026-10-30`, and the original `receipts/SHA256SUMS` is unchanged and still verifies.

## 2026-10-30: clean rebuild attempt 2 (binary provenance PASS)

- **Pre-registration.** Before compiling, everything was frozen in `receipts/rebuild-2e4846e-attempt2/` as HBI → HBP → SHA → SH → HASH. The seal is `f44d920c2a09606534083a1d5321b70060c7d76dd4f0857bf6b087f901f7a830`. The exclusions were only the COFF timestamp, the debug-directory timestamps, the CodeView RSDS GUID/age and the PDB path. The comparator controls passed 8/8.
- **Procedure.** The operator's checkout was renamed to `.hold`. A fresh clone of `2e4846e` (`core.autocrlf=false`) was made at the identical absolute path, so the embedded vendored-crate panic paths match. Its 1,561 tracked files are byte-identical to the commit. It built from scratch with exit 0, the clone was moved aside, and the checkout was restored. `before_equals_after=1` covers the executables, HEAD, status, `main.rs`, the run log and every tracked file's raw hash.
- **Result.** `PROVENANCE_PASS`: 0 bytes differ outside the exclusions in all four executables (shellschur, roomschur, ymroom, ymsec). This is binary provenance, not a mathematical result.
- **CRLF.** The 34 CRLF-only build inputs, including `shellschur.rs` (`809d6330` vs `9bd8d245`), had no effect on the executables for this build. The source-byte difference stays recorded.
- **First launch.** It aborted at the precondition checks because of a launcher PATH fault. Nothing moved. The abort row is kept, with `LAUNCH1_NOTE` beside it.
- The rebuilt executables and the temporary clone stay outside git, bound in `receipts/RAW-ARTIFACTS-OFFGIT-rebuild2.hbp`.
- **Pending:** segmented-store P2/P3 and the frozen P4 result. There is no 3x4 gap verdict, and production HOLD is unchanged.

## 2026-10-30: segmented-store P2/P3 specification (reviewed, NOT RUN)

- **Spec and procedure.** Frozen in `receipts/segp2p3-spec/` as HBI → HBP → SHA → SH → HASH. The seal is `d6666f9781890a99d031a33315e1b6fa90becb93bdd9704e7d886ee486acfd33`. The superseded pre-review draft seal `f4e557a3…` is kept beside it; it was never committed or run.
- **P2.** Text identity plus the CI anchors, and store identity: single file vs G1 (40,000,000 B segments) vs G2 (1,048,583 B segments), byte for byte, with a zero tail.
- **Segment-fault controls.** Planted faults K0–K5 on a 2x3 G3 (16,411 B) store.
- **P3.** 3x3 on the G1 store with CI's frozen parameters and the same 2/16/40 chunks on both sides. Comparator v2 (stream) decides, v1 is reported verbatim, and there are no new exclusions.
- **Single-file vs segmented store control at 60M.**
- **Scope.** P3 is scoped to G1 only, and G2 gets builder bytes only. Store identity is not read-path identity. Every verdict row carries `spectral_pass=0`.
- **Synthetic controls:** comparator equivalence 60/60 (120 comparisons) and verdict logic 24/24.
- **Not run.** Execution needs separate operator authorization. Duration is CONJECTURE: at least 61,000 s, plausibly 20–35 h. Production HOLD is unchanged, and there is no 3x4 gap verdict.

## 2026-10-30: segmented-store P2/P3 specification, revision 2 (NOT RUN)

- **Why.** The operator's final review gave a NO-GO on revision 1 (`d6666f97…`, never run) for verification and packaging gaps. No mathematical comparison rule changed.
- **Where.** Revision 2 is frozen in `receipts/segp2p3-spec-rev2/` with seal `570a25699b6dc6ff134372353b39f1383a1507af5cd69fb9f992c735730a8e79`. Revision 1 stays unchanged in `receipts/segp2p3-spec/`, and its manifest still verifies.
- **Corrections:**
  - End integrity requires both executable and spec integrity.
  - P2 requires complete, well-formed evidence, including `P2_SINGLE`, before any comparison, so incomplete evidence is INCONCLUSIVE, never MISMATCH.
  - Segment controls K0–K5 are checked individually, with a valid setup.
  - Comparator results (v2, v1 and the 60M single-file vs segmented store control) are bound to their retained stdout bytes by SHA-256 and parsed lines.
  - A failed segment read gives INCONCLUSIVE.
  - Aggregates give INCONCLUSIVE precedence over MISMATCH.
  - The sidecar uses the bare file name.
  - Exact matches and appended rows are CR-stripped. Measured: GNU grep 3.0 matched raw CRLF anyway; dry test: 0 CR bytes.
- **Controls.** Verdict controls 35/35; comparator equivalence unchanged at 60/60. The real command-line path was dry-tested with synthetic evidence only, and the sidecar verifies.
- **Not run.** Execution needs separate operator authorization. Production HOLD is unchanged, and there is no 3x4 gap verdict.

## 2026-10-30: segmented-store P2/P3 specification, revision 3 (NOT RUN)

- **Why.** The operator's review of revision 2 (`570a2569…`, never run) gave a NO-GO for two evidence-integrity checks. No mathematical rule changed.
- **Where.** Revision 3 is frozen in `receipts/segp2p3-spec-rev3/` with seal `7cf49f2c9cf6a9770f7ad7ac204a8d0b33c74a8539e38928073ac4b69c404e91`. Revisions 1 and 2 stay unchanged in their own directories.
- **Fix 1: control files.** The verdict module now re-opens `comparator-controls.hbp` and `verdict-controls.hbp`, re-hashes them, and checks their terminal rows. A missing or altered file is INCONCLUSIVE.
- **Fix 2: seal anchor.** The pre-registration seal is bound to an anchor supplied at launch from the operator's authorization (`segp2p3.sh <ANCHOR>`), never read from the bundle, because a module cannot contain its own bundle's seal. Both the procedure and, independently, the verdict module recompute the bundle seal and require it to equal the anchor and the seal recorded in PRECONDITIONS.
- **Controls.** Verdict controls 40/40, adding: control file deleted, control file altered, seal substituted, an unapproved internally consistent bundle, and a spec file altered after sealing. Comparator equivalence unchanged at 60/60. Dry test of the real module: AGREE with the approved anchor, INCONCLUSIVE (`seal_not_operator_anchor`) with a substituted one.
- **Not run.** Execution needs separate operator authorization naming this seal as the anchor. Production HOLD is unchanged, and there is no 3x4 gap verdict.

## 2026-10-31: segmented-store P2/P3, revision 3, RUN (P2 AGREE, P3 AGREE)

- **Authorization and anchor.** Run under the operator's authorization naming seal `7cf49f2c9cf6a9770f7ad7ac204a8d0b33c74a8539e38928073ac4b69c404e91` as the anchor. All 15 files of the executed spec bundle are byte-identical to `receipts/segp2p3-spec-rev3/`, whose `SHA256SUMS` still verifies (0 failures).
- **Process.** `segp2p3.sh` ran as PID 17184 from 2026-10-30T11:24:00-03:00 to 2026-10-31T11:47:11.988-03:00, exit code 0. Two independent observers recorded the exit: the .NET watcher and the native `WaitForSingleObject` watcher with identity check on process creation time (`identity_match=1`). The native watcher's first attempt was an observer defect (PowerShell `0xFFFFFFFF` cast), not a process exit; that row is kept.
- **Integrity.** `END_INTEGRITY|exe_unchanged=1|spec_unchanged=1`. Controls: comparator PASS, segment PASS, verdict PASS, csf60 PASS; segment controls K0–K5 all `ok=1`. The run's control files are byte-identical to the frozen ones.
- **P2.** AGREE on 2x3, 2x4 and 3x3: text identical, anchor equal, store bytes identical between single and segmented (G1, G2).
- **P3.** AGREE at t = 60M, 72M and 90M (v2 comparator). At 90M (core 2,940, 40/40 chunks both sides, partition exact) both sides give 37 negative and 9 ambiguous. The v1 MISMATCH at 60M and 72M was registered in advance and is not relabelled.
- **Overall.** `SEGP2P3_VERDICT|P2=AGREE|P3=AGREE|t90_is_implementation_agreement_only=1|P3_scope=G1_segmented_store_only|G2=P2_builder_bytes_only_not_runner_certified|spectral_pass=0|binary_provenance=PASS(rebuild2)|gap_verdict_3x4=NONE|production_hold=UNCHANGED`.
- **Close-out replay.** `segp2p3_verdict.py` re-run on the evidence, run directory, spec directory and anchor: exit 0, all 7 verdict rows byte-identical to the recorded ones.
- **Where.** Evidence, controls, observer receipts, replay output and the close-out row are in `receipts/segp2p3-run/`, listed in `receipts/SHA256SUMS-2026-10-31-segp2p3run`. The run directory's 1,188 raw files (7.9 GB) stay off git, bound by `receipts/RAW-ARTIFACTS-OFFGIT-segp2p3.sha256` (sha256 `65978eb3…f373c`).
- **Scope.** P3 is implementation agreement between the segmented and the single store for G1 only, not a spectral result. There is no 3x4 gap verdict, production HOLD is unchanged, and the PR stays draft.

## 2026-10-31: J2, `roomjump` point mode on 3x4 columns 0:4 (local, D: store)

- **What ran.** `roomjump.exe` built at 18647de (sha256 `622e5072e4197fe0a282722fe8ad4b1b1ea21831145bfb2626de7003d5ce1ff5`), merged to main as 8ac8604 (PR #62). Spec `seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-`, columns 0:4, K=4, WORKERS=4, BUDGET 9e9, `ROOMJUMP_POINT=60`, `ROOMJUMP_STOP=32`, args `1000,9000,60000000,12,1000,400`. Started 2026-10-31T13:02:39-03:00, ended 15:24:10-03:00, exit 0, 8,491 s.
- **Passes.** Two setup passes (607,770 ms and 615,760 ms), then 11 point passes at about 600 s each, then 1 interval certification pass. The largest point step fell from 26,666,666,667 to 7, below `STOP=32`. The pilot (`receipts/pilot3x4-local/pilot.out`, same columns and store) needed 19 interval sweeps and 17,359 s.
- **Agreement with the pilot.** n = 45,508,080, core 137, core fingerprint `4de7413741e7a4a6`, payload merkle `ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b`: all identical. Of 548 SCOL rows, 548 intersect the pilot's interval, 0 are disjoint and 0 are missing. 158 are byte-identical, including the 154 exactly-zero columns on both sides.
- **Width.** The other 390 intervals are **wider** than the pilot's, and none is narrower: largest width 344 against 248. On 3x3, point mode was narrower than the baseline (358 against 561); on 3x4 it is not. The explanation, that one certification pass after point passes encloses more loosely than 19 refining sweeps, is CONJECTURE. A run with a second certification pass (about 600 s more) would test it, and has not been run.
- **Where.** `receipts/jump-j2-local/`: `J2.hbp`, `J2-COMPARE.hbp` (sha256 `e6b5e182…ad3398`), `j2.out` (sha256 `9a25b0d8…f373a1`), `j2.err`, `roomjump.exe.sha256`, listed in `receipts/SHA256SUMS-2026-10-31-j2`.
- **Scope.** Four columns of 137, so J2 gives no 3x4 gap verdict. It is a speed and agreement result for `roomjump` on 3x4, not a spectral result. Production HOLD is unchanged.
