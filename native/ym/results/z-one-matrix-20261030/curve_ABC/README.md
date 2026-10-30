# Dictionary operator tests B → A → C (independent Python witness)

Date: 2026-10-30. Tested using source meanings from the public `JesseBrown1980/the-human-based-understanding` dictionary. This **does not edit any repository or any Yang–Mills run**. No physical signal propagation or Yang–Mills mass-gap theorem is being tested.

Predictions were written to `PREREG.hbp`, then independently SHA-256 hashed (`PREREG.hbp.sha256`) before the code was written. All output is HBP with `json=0` (no JSON). The Python code uses exact integers. This environment does not have Rust or Clippy, so no Rust 1.81 compilation is claimed; a separate seat's Rust result is not silently reused as my run.

## B — the curved return, and what survives

Frozen model: baseline `j=I+R+R²` and asymmetric signed candidate `j'=I+R−R²`, with R the order-three cyclic shift. Bidirectional ring `r=R+R⁻¹` is symmetric; `j'` is not symmetric, has three nonzero entries per row, and is one **chosen** mathematical representation, not compelled by the dictionary.

Over rings `3^N`, N=1..5, from **every source**, one input pulse gives the same first-arrival ticks, same three-per-level support and same ring-boundary delays with `j'` as with `j`. Q1, Q2, Q3, Q4 and Q6 (for single-source reach) are preserved. Q5 is false: the full-level `j'` product has ±1 entries, not all +1. Because weights are signed, different simultaneous sources can cancel. Witness: on one triple, input `(1,1,0)` yields a zero at target 0. A **support-equivalence** claim about single pulses is not a general equality of matrices or a propagation bound for arbitrary signed superpositions.

## A — three inversions, three brakes

All 27 vectors `(a,b,c) ∈ {0,1,2}³` rotate three distinct digits starting at `(0,0,0)` and generate 27 distinct states. They include exactly one zero vector, so the proposed claim that held turns *never* return to the starting state is **FAIL**. Applying all three turns to the same digit instead gives only three final states with nine combinations per final state. Three fixed +1 turns at one digit return home; one +1 at each of three separate digits does not. Original registered verdict **FAIL**; no post-hoc rewrite.

## C — commit history

GitHub connector reviewed the initial six-commit history of `JesseBrown1980/the-human-based-understanding`, and the `README.md` and `index.html` blobs at the two key commits, both anchored in `C/EVIDENCE.hbp`:

- **2026-08-02 00:54:59Z** `d2f0693bff27ccd042a9d1a0433ca3e1fd17ecce`: `f = from` and `m = intelligence` present in both files; `father`, `mother` and the verses section absent.
- **2026-08-02 01:50:26Z** `b93726eb5da3cef08fc43edfd53269d6a7abfcff`: the verses and `father`/`mother` present in both. Difference **3327 seconds / 55m27s**.

This establishes **commit publication order in that repository**, not when the words were actually spoken. The original 'written before the words were said' claim stays **INCONCLUSIVE** pending independently dated original-source evidence. The `C/test_c.py` replay validates the pinned connector evidence, not a new live GitHub fetch; the immutable GitHub commit links and blob SHAs permit an external auditor to redo the source check.

## HBI → HBP → SHA → SH → HASH

- HBI `DICTIONARY.hbi`: list of source/results records and their SHA-256 fingerprints.
- HBP: `PREREG.hbp`, `B/RESULT.hbp`, `A/RESULT.hbp`, `C/EVIDENCE.hbp`, `C/RESULT.hbp`.
- SHA `SHA256SUMS`: SHA-256 of all source and evidence files; standalone original pre-registration sidecar.
- SH `verify.sh`: replays tests into isolated temporary folders (never modifies recorded results), compares bytes, checks SHA256SUMS and seal.
- HASH `DICTIONARY.seal`: SHA-256 of literal concatenation of `SHA256SUMS` bytes followed by `DICTIONARY.hbi` bytes.

Run `sh verify.sh` from this folder. No external libraries required. The seal is for this standalone test only, **not** an authorization anchor for PR #37 or #40.
