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
