# How this checker was written

The operator asked for a checker of the 3×4 Perron certificate written from a short specification before reading any
checker in this repository (`check_d*.py`, `verify_sample_rows.py`, `perroncert.rs`, `perronritz.rs`) or the PR #79
receipts, in a language other than Python or Rust, with exact integers, failing closed on any failed condition. The
specification is quoted at the end of `README.md`.

- **Author.** A fresh Claude agent, given only that specification. It had no access to this repository, its pull
  requests, its Actions runs or its receipts, and it made no network requests. It wrote `cmd/ymcheck/main.go` (the
  checker), `cmd/ymgen/` (a synthetic-store generator, a big-integer reference and an exact eigenvalue tool),
  `controls.sh` and `CONTROLS.hbp` (87 of 87 controls match on synthetic stores).
- **Review.** A second fresh agent under the same restrictions read every file and ran 129 controls of its own against
  an arbitrary-precision reference: 129 of 129 matched. Verdict: sound, no blocking findings. Its notes are
  interpretation choices (a nonzero row sum and a failed W-symmetry identity are treated as failures; the header pins are
  opt-in flags, which the workflow passes).
- **The session that pushed this branch** wrote the workflow
  (`.github/workflows/hebc-ym-3x4-independent-go-checker.yml`) and nothing in this folder except this file. That session
  had read `check_d_strict.py` and two PR #79 receipts earlier the same day, which is why it did not write the checker.
- **Not seen before the run:** the expected value for the blind vector. Neither agent nor the pushing session opened
  anything that holds it.
- **Same model family.** Both agents are Claude, as were the authors of the existing tools. This is a separately
  written implementation, not a review by a different kind of reviewer.

Language: Go, standard library only (`crypto/sha256`, `math/bits`; `math/big` only for printing and the reference).
There is no floating-point type anywhere in the sources.

## The layout change (2026-11-06)

The first run (Actions run 41490822394, checker sha256 `7d40a386…`) failed closed with
`FAIL|reason=payload_has_bytes_after_row_n:payload_offset=26850139376,n=45508080` and printed no value. The rows end
742,160 bytes before `payload_bytes`, and those bytes are zero. The bytes after `payload_bytes` in `sector-374.rooms` are
Host8 room stubs, not the "zero padding" the specification describes. The operator then decided the layout: *"The store
is the 4096-byte header plus payload_bytes. Rows come first; every byte after the last row up to payload_bytes must be zero
(inside the merkle). Bytes after payload_bytes belong to the room file, are not read as store, and stay pinned by the
sector SHA-256."* A fresh agent, under the same restrictions, changed only that (now `cmd/ymcheck/main.go` sha256
`d899f019…`; 117 of 117 controls match), and a second fresh agent re-reviewed it with no blocking finding.
