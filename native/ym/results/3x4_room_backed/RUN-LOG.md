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
| 6 | same threshold, `shellschur` on the ymsec text matrix, record compare | **PENDING** | — |
| 7 | **3×4 pass A** | **45,508,080 states, 7 flat**, the same as CI pilot run 40391283682 (`Sx+Sy+ states=45508080`, `flat_states=7`); `passA.bin` SHA-256 `eefd7752…6e3cbc` | **1,399.3 s (23.3 min)**, 8 workers |
| 8 | 3×4 pass B (keys to 50M rooms, matrix to USB) | running; see the last `PASSB_PROGRESS` row of the receipt | about 2,550 rows/s so far |

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
