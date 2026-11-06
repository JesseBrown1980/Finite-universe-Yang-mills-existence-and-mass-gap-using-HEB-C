# ymcheck: exact-integer Go checker for the 3x4 Perron certificate

`ymcheck` reads the YMROOMHDR room store once from standard input and checks one or more `d` files
in that same pass. It was written only from the owner's published FORMAT and CHECK specification
and the owner's later decision on the store layout (both quoted at the end of this file). It uses
only the Go standard library, and its arithmetic is integer-only.

## Store layout (the owner's payload-only decision)

The store is the 4096-byte header plus `payload_bytes`. Nothing after that is store.

```
stream offset 0                    4096                 4096+R               4096+payload_bytes        end of input
              | header (4096 B)    | rows h = 0..n-1    | zero tail          | room-file bytes ...      |
                                   |<------------- payload_bytes ----------->|
                                   |<------------ covered by the merkle ---->|
```

- Rows come first, in index order. `R` is the payload offset where row n-1 ends (reported as
  `rows_end_payload_offset`).
- Every payload byte after the last row, up to `payload_bytes`, must be zero. These bytes are inside
  the merkle, exactly as the spec defines it. Their count is reported as `payload_zero_tail_bytes`.
  A nonzero byte there fails with `payload_zero_tail_nonzero`.
- Bytes after header + `payload_bytes` belong to the room file. The checker reads them to end of
  input, so a writer such as `cat ... | ./checker` never gets SIGPIPE. It counts them
  (`after_payload_bytes`) but never interprets them and never requires them to be zero. They stay
  pinned only by the per-sector SHA-256 list.

The owner's decision, verbatim (it supersedes the spec's "then zero padding" line):

> "Payload-only: The store is the 4096-byte header plus payload_bytes. Rows come first; every byte
> after the last row up to payload_bytes must be zero (inside the merkle). Bytes after payload_bytes
> belong to the room file, are not read as store, and stay pinned by the sector SHA-256."

Why the decision was needed: the earlier version of this checker (sha256 `7d40a3866da67164f8ee277280f374161c0ab891f9441934a3039adccb8d7256`)
required the n rows to fill `payload_bytes` exactly, and every byte after the payload to be zero.
On the real store it stopped with `payload_has_bytes_after_row_n:payload_offset=26850139376`. The
measurements reported with that run:

| Region | Stream offsets | Bytes | Content |
|---|---|---|---|
| header | 0 .. 4,095 | 4,096 | YMROOMHDR line |
| rows | 4,096 .. 26,850,143,471 | 26,850,139,376 | the 45,508,080 rows |
| zero tail | 26,850,143,472 .. 26,850,885,631 | 742,160 | all zero |
| room-file bytes | 26,850,885,632 .. end of sector-374 | 349,114,368 | Host8 room stubs, about 255 of 256 bytes nonzero |

If those measurements hold, the real run's STORE row should show
`rows_end_payload_offset=26850139376|payload_zero_tail_bytes=742160|after_payload_bytes=349114368`.

| Path | What it is |
|---|---|
| `cmd/ymcheck/main.go` | the checker (the only file the CI result depends on) |
| `cmd/ymcheck/main_test.go` | unit tests: 128/256-bit arithmetic, floor division, comparison vs `math/big`; splitter under random chunking |
| `cmd/ymgen/*.go` | synthetic store generator (with `-ztail` zero tails and `-pad`/`-pad-fill` room-file bytes), byte flipper, re-merkler, room-byte streamer (`fill`), big-int reference checker (`ref`), exact eigenvalue tool (`eigen`), streaming benchmark (`bench`) |
| `controls.sh` | builds everything, runs every control, writes `CONTROLS.hbp` |
| `CONTROLS.hbp` | every control: command, expected, actual, verdict |
| `ci/ym-go-checker.yml` | ready-to-copy GitHub Actions workflow for the real run |
| `bench/run-bench.sh` | throughput / peak-memory benchmark on a streamed 2.5 GB store |

## Build (any machine with Go 1.22 or later; built and tested with go1.24.7)

```bash
go vet ./...
go test -count=1 ./cmd/ymcheck
go build -trimpath -o checker ./cmd/ymcheck
sha256sum cmd/ymcheck/main.go          # compare with the hash reported with the result
./controls.sh                          # about 40 s; exits 0 only if all controls match
```

## Run on a CI runner

```bash
HF=https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store/resolve
STORE_REV=160726aaaf87386090b2b0b9ecf2815ca2634009

curl -sSfL -o d93000000.bin       "$HF/d2630edf882f3d9fa125f25680fd9b6a04c98d31/perron/d93000000.bin"
curl -sSfL -o d93700000-pass5.bin "$HF/b33f5a0bf3392ba795f39fe726570ad61311b3d4/perron/start/d93700000-pass5.bin"
printf '%s  %s\n' \
  956b73bc6f4ec5712184eb52f67d8e0adab467c1ea843ba257126278368210da d93000000.bin \
  34e71facb2689a46a44cb347604f0b361760020c8810748f6e9cc513daa53686 d93700000-pass5.bin | sha256sum -c -
```

Disk form, for a runner with about 30 GB free (download, `sha256sum -c SECTORS-341-374.sha256`, then):

```bash
cat sector-341.rooms sector-342.rooms ... sector-374.rooms | ./checker d93000000.bin d93700000-pass5.bin
# equivalently: cat sector-{341..374}.rooms | ./checker ...
```

Streaming form, which needs no disk for the store. A standard `ubuntu-latest` runner does not have
27 GB free.

```bash
set -o pipefail
for s in $(seq 341 374); do curl -sSfL "$HF/$STORE_REV/sector-$s.rooms"; done \
  | ./checker -progress \
      -expect-n 45508080 -expect-payload-bytes 26850881536 \
      -expect-merkle ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b \
      d93000000.bin d93700000-pass5.bin
```

The `-expect-*` pins tie the header to the values the owner published. The payload merkle then
covers every store byte after the header: the rows and the zero tail. Together these make the
store self-verifying even without the per-sector hashes. The room-file bytes after
`payload_bytes` are not store, and the checker does not verify them. Only the per-sector SHA-256
list pins them. The workflow in `ci/` hashes each sector on the fly with `tee` and compares it
with `SECTORS-341-374.sha256`.

For the control vector, the expected row is
`CERT|d=d93000000.bin|...|t_cert=93061051|row=44742735|mag=3|...`.

## Interface and output

- stdin: the concatenated store. Arguments: one or more d files (little-endian `int64`, one per row). Flags must come before the d files.
- Flags: `-seed` (default 20261102) for the symmetry vectors, `-workers`, `-hashers`, `-progress` (stderr), and the pins `-expect-n`, `-expect-payload-bytes`, `-expect-merkle`.
- Success (exit 0): one row per d file, in argument order, then one STORE row.

```
CERT|d=<file>|d_sha256=<hex>|t_cert=<int>|row=<h>|mag=<m>|rows_at_min=<count>|json=0
STORE|n=<n>|payload_bytes=<b>|merkle=PASS|flat_rows=<k>|min_nonzero_mag=<m>|max_mag=<M>|row_sums_zero=PASS|w_symmetry=PASS|seed=<s>|entries=<total>|nonflat_rows=..|diag_not_once_rows=..|min_w=..|max_w=..|rows_end_payload_offset=<R>|payload_zero_tail_bytes=<b-R>|after_payload_bytes=<count>|payload_merkle=<hex>|w_symmetry_lhs=<exact integer>|secs=<s>|json=0
```

  `row` is the smallest index that attains the minimum, and `rows_at_min` counts all such rows.
  `rows_end_payload_offset` is the payload offset where row n-1 ends. `payload_zero_tail_bytes` is
  the number of zero bytes from there up to `payload_bytes`. `after_payload_bytes` counts the bytes
  read after header + `payload_bytes`. These three replace the earlier `padding_bytes` field.
  `diag_not_once_rows` counts rows whose diagonal entry does not appear exactly once. This is
  for information only; the spec does not make it a condition. `w_symmetry_lhs` is the common
  exact value of both sides of the identity.
- Any failed condition: exactly one line `FAIL|reason=<reason>|json=0` on stdout, exit status 2, and no CERT or STORE row for any d file.

## Design

**Single pass.** A reader goroutine takes the 4096-byte header, then reads the payload in
16 MiB leaves exactly as the merkle defines them. Each leaf goes to the SHA-256 workers and to a
splitter. The splitter walks the row boundaries, reading only `cnt`, enforces exactly `n` rows
inside `payload_bytes`, and hands batches of whole rows to the row workers. Rows that straddle a
leaf are copied into a carry buffer. Once row n-1 ends, the splitter records that offset and
requires every remaining payload byte, in that leaf and any later leaf, to be zero. After
`payload_bytes`, the reader drains the rest of the input to end of file and only counts it.
Results print only after every goroutine has finished and every check has passed.

**Header.** The first `\n` must fall inside the first 4096 bytes. After it there may only be NUL,
space or newline bytes. The text may end in NUL/space/CR padding but holds no other NUL. It must
start with `YMROOMHDR|`. The keys `n`, `payload_bytes` and `payload_merkle` must each appear
exactly once, as a decimal, a decimal, and 64 lowercase hex characters. Other fields are ignored.

**Exactness.** There are no non-integer types anywhere; `grep -i float` over the Go sources is
empty (control A03). The bounds are proved in comments and enforced by types:

- `z*d[j]`: an exact 64x64 to 128-bit signed product (`math/bits.Mul64` with sign correction).
  Its magnitude is at most 2^31·2^63 = 2^94; a row has at most 65535 entries, so the row sum is
  below 2^110 and cannot overflow 128 bits.
- `1000*JB*mag*d[h]` is below 9e6·65535·2^63 < 2^103, so it fits.
- `1000*JE*sum` and the final addition are checked. If the exact magnitude would reach 2^127,
  the program fails closed with `arithmetic_overflow` instead of wrapping (control D12; control
  B11 shows a 127-bit numerator computed exactly and equal to the `math/big` reference).
- Floor division by `d[h] > 0` rounds toward minus infinity. The magnitude is divided with
  `bits.Div64`, and if the numerator is negative with a nonzero remainder the quotient is
  `-(q+1)` (control B10: -20000000/3 gives -6666667). The quotient is held in 128 bits and
  printed exactly.
- Row sums of `z` stay below 2^47 in an `int64`.

**Symmetry identity.** `x_j` and `y_j` are the high and low 32-bit halves of the j-th SplitMix64
output for the seed, each arithmetic-shifted into [-2^30, 2^30). Per row, `sum z*y` and `sum z*x`
are accumulated exactly in 128 bits (below 2^77). Then `w*x_h` (below 2^62) times that row sum is
added into a signed 256-bit accumulator, one for each side. The total stays below 2^172, so the
accumulators cannot overflow. The two sides are compared word for word, not modulo anything.

**Merkle.** For each 16 MiB leaf (the last may be shorter), its SHA-256 is written as lowercase
hex. The ASCII digests are concatenated, the SHA-256 of that text is taken, and the result is
compared with the header (and with `-expect-merkle` if given). Controls B06.m2/m3 recompute it
with coreutils (`split -b 16777216 --filter=sha256sum`).

**Fail closed.** These conditions each print FAIL and exit 2:

- parse error, short stream, row-count mismatch (the payload ends before row n-1 or inside a row)
- a nonzero byte between the end of row n-1 and `payload_bytes` (`payload_zero_tail_nonzero`)
- column out of range, positive off-diagonal entry
- flat row with d != 0, non-flat row with d <= 0
- merkle mismatch, row sum != 0, symmetry identity failing
- arithmetic overflow, d length != 8n, no non-flat rows, pin mismatch, missing or unreadable d file,
  a read error on standard input

Bytes after `payload_bytes` never cause a failure, whatever they contain.

`fail()` takes the output lock and never releases it. The result rows are written once, under
the same lock, as the very last action.

**Memory.** Each d file is held as `[]int64`, which is 8n bytes, 364 MB for n = 45,508,080. On
top of that are about a dozen 16 MiB leaves in flight plus GC slack. The expected peak for the
real run with two d files is about 1.5 to 2 GB.

**Speed** (4-core Xeon 2.8 GHz, two d files, store streamed through a pipe):

- 2^22 rows x 73 entries (2.48 GB, 3.06e8 entries): about 250 MB/s with random column access
  and about 500 MB/s with local access. Peak RSS was 463 MB.
- Extrapolated compute time for the real 26.85 GB store: about 1 to 2 minutes, plus download time.

## Controls

`./controls.sh` regenerates `CONTROLS.hbp`. It runs:

- build, vet, unit tests and the no-float grep
- correct stores (300 rows with flat rows, weights 1..7, and duplicate and zero entries; header
  and padding variants; multi-leaf stores with rows straddling leaves; worker-count determinism;
  the 34-sector pipe form)
- fast vs `math/big` reference on fixed cases and 200 random fuzz cases with defects
- tiny stores whose exact `floor(1e6*lambda_min(H'))` is found by bisection on an exact
  PSD test. `H' = (JB/JE)*M + Z` on the non-flat rows, and `W*(1e6 H' - t I)` is PSD exactly
  when `t <= 1e6*lambda_min`. The test checks that every principal minor is >= 0, using Bareiss
  determinants.
- the owner's controls: single flipped payload bytes at nine positions, with a re-merkled
  variant showing that only the merkle caught a mag-byte flip and a consistent four-value z
  change; and d files with a 0, -1 or MinInt64 non-flat entry
- one control for each other FAIL condition
- section E, the layout decision:
  - zero tails inside `payload_bytes` pass, and their count is reported. This includes the real
    store's 742,160-byte tail, a 1-byte tail, a tail that crosses a 16 MiB leaf boundary, and a
    tail that is a leaf of its own. Each is also checked against the big-int reference and
    coreutils.
  - one nonzero byte in the zero tail fails, both with the merkle recomputed (so only the new
    check can catch it) and with the original merkle.
  - random nonzero bytes after `payload_bytes` pass with the same rows as zero bytes of the same
    length, and their count is reported.
  - a store with no zero tail and no trailing bytes passes.
  - pipes: `cat` of the real shape (zero tail plus 349,114,368 room-stub bytes) exits `0 0` in
    `PIPESTATUS`, and a sanity control shows the same test does report SIGPIPE (141).

The decision changed these earlier controls, and each is marked in `CONTROLS.hbp`:

- D03.1 and D08 (nonzero bytes after the payload) now pass. They used to fail with
  `nonzero_padding`.
- D03.2 (`payload_bytes` 8 larger than the rows) now fails on the merkle, because 8 zero bytes
  are an allowed zero tail. It used to fail with `payload_has_bytes_after_row_n`. The new
  D03.2.remerkled shows that it passes once the merkle covers those bytes.
- D04.1 keeps its expectation, but its reason is now `payload_zero_tail_nonzero`.
- B05 now reads `after_payload_bytes` instead of `padding_bytes`.
- The B12 fuzz now also draws zero tails, room-file bytes, and nonzero bytes poked into the tail.

## Specification used (verbatim from the owner)

```
FORMAT
- Concatenate the 34 sector files in order into one byte stream.
- First 4096 bytes: one text line ending in \n, YMROOMHDR|...|n=45508080|...|payload_bytes=26850881536|...|
  payload_merkle=ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b|...
- From byte 4096: payload_bytes of rows, in index order h = 0..n-1, then zero padding.
- A row, little-endian: w:u32, mag:u16, cnt:u16, then cnt entries of j:u32, z:i32. Entries include the diagonal.
- Merkle: split the payload into 16 MiB leaves (the last may be shorter), SHA-256 each, join the lowercase hex
  digests as ASCII, SHA-256 that text. It must equal payload_merkle.
- d file: one little-endian i64 per row.

CHECK, with JE=1000, JB=9000
- Flat rows have mag=0. d must be 0 on them and positive on every other row.
- Every entry with j != h must have z <= 0.
- For each non-flat h: ratio(h) = floor((1000*JB*mag*d[h] + 1000*JE*sum(z*d[j])) / d[h]), summing over the row's
  entries. t_cert = the minimum ratio, in units of 1e-6 J_E.
- Also report: the number of flat rows; the smallest nonzero and the largest mag; whether sum(z) = 0 on every row; and
  whether sum_h w_h x_h sum_j z_hj y_j = sum_h w_h y_h sum_j z_hj x_j for random integer x, y from your own seed.
- Controls: a flipped payload byte and a d with one nonpositive non-flat entry must each exit nonzero with no value.
```

The owner's later layout decision (verbatim) supersedes the FORMAT line "then zero padding":

```
Payload-only: The store is the 4096-byte header plus payload_bytes. Rows come first; every byte after the last row up to
payload_bytes must be zero (inside the merkle). Bytes after payload_bytes belong to the room file, are not read as store,
and stay pinned by the sector SHA-256.
```

Interpretation choices:

- A row sum other than 0, or a failed symmetry identity, is treated as a failed condition (exit 2).
  When they hold, they are reported as `row_sums_zero=PASS` and `w_symmetry=PASS`.
- "Not read as store" means the bytes after `payload_bytes` are read only so that the input pipe
  drains, and only their count is reported. Their content never affects the result.
- A zero tail of any length, including 0 and lengths that are not a multiple of 8, is accepted.
- Entries are not required to have distinct columns. Duplicates are summed, as the formula implies.
