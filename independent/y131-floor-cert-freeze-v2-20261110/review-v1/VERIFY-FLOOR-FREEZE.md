# Verification of the floor-certificate freeze (r = 9, periodic 3x4 S3)

Seat: local Opus 5.5, second seat of FABLE5. Date: 2026-11-10. Target: branch `cloud-seat-floor-cert-freeze-20261110`,
head `e74d8a46e86034096fd9c9231c87f594f17a93bf`, folder `independent/y131-floor-cert-freeze-20261110/`.
The authoritative record is `VERIFY-FLOOR-FREEZE.hbp` (sha256 in the `.sha256` sidecar). Every value here is MEASURED unless tagged.

**Verdict: HOLD.** The pins, the build and every r-independent hash reproduce. Erratum E1 means rows 001, 006 and 007
cannot be run exactly as written. It needs the owner's ruling before the r = 9 run.

## 1. Pin integrity
- FREEZE-PIN.sha256: 27 of 27 entries match, checked both in the working tree and at git-blob grain.
- Prediction record: 109 rows, with ids 001-109 in sequence, plus `PREDICTION_END`. Its sha256 is `d06ff237…84041`.
  The tag counts match `PREDICTION_END`.
- PIN rows inside the record: 19 of 21 path pins match files in the folder. Row 016 is the binary, which is rebuilt.
  Row 034 sits on branch `cloud-seat-137-amplitude-freeze-20261109`, and it matches (`0b97fa83…`).
- Issue #137, comment 6770516737: it names commit `e74d8a4`, 109 rows and the same sha256. It matches.
- The branch has no PR and no check runs.

## 2. Predictions (rows 058-073)
Main already holds #131's r = 9 bracket, [94.070673, 94.070936], for λ_min(QHQ). Each row is classified against that:
- **Blind** (no value was seen before the freeze): 061, 062, 063, 067 and 069.
  - 062 and 069 can be decided only if m0 = 12 runs.
  - 063 can be decided only if m0 = 13 runs.
- **Partly blind** (λ was known; how close the certificate gets was not): 058, 059, 060, 064, 066 and 070.
- **Controls** (follow from soundness together with #131's bracket): 065, 068, 071 and 073.
- **Read and report:** 072.

The folder's own committed outputs hold no r = 9 value. MAP gives `≤ 77.52 at r = 9` for the domino floor. It
gets that number by monotonicity from r = 10.5, not from a run at r = 9.

## 3. Floats
- `no_float_gate.py .` (Windows Python 3.13.2): exit 0, 524 code files, 0 failed. Every Python file in the folder,
  and main.rs, has 0 findings. So no FLOAT-EVIDENCE row is needed, and none was added.
- Run-time trace (`scripts/fztrace.py`, an AST instrumentation of every operation). It was run on cert_gate (five
  runs), indep_verify (two), class_verify, orbit_verify, lint_hbp and peak_rss.
  - Scale: about 9.7 × 10⁹ checked events, with 0 float events.
  - Positive control: the tracer caught `10 ** e` with e < 0, `/` and `pow(2, -1)`.
  - Scope: small m0 at excluded r, which runs the same code paths as m0 = 11-13.
  - peak_rss.py receives a rusage object whose `ru_utime` is a float. The script reads only `ru_maxrss`, which is an int.

## 4. Rust (WSL, 1.81.0)
- `cargo +1.81 build --release --locked`: exit 0, with one warning (`fmat` is never used). The binary sha256 is
  `0432b826…8709`, the same as row 016 and `repro_build.txt`.
- `cargo +1.81 clippy --release -- -D warnings`: **exit 101, 22 errors** (erratum E5). The package records no clippy run.
- f32, f64, `as f…` casts, float literals and unsafe: 0 of each.

## 5. Certificate logic (Theorem S, in my words)
**What it proves.** Take t below the analytic tail cap, an integer vector v ≥ 1 on the core {M ≤ m0}, and a positive
tail weight f(M). Suppose every class row of F(t)v is ≥ 0 in exact integers. Then λ_min(QHQ) ≥ t on the whole
nonflat orbit space.

The proof chain:
1. Ground-state substitution with f gives H_TT ≥ diag(δ).
2. The colouring bound G(M) gives δ_k ≥ cap > t on every tail orbit.
3. Since the inverse is operator-monotone, (H_TT − t)⁻¹ ≤ diag(1/(δ − t)).
4. So the Schur complement satisfies S(t) ≥ F(t), and F(t) is a w-symmetric Z-matrix.
5. The Collatz–Wielandt test gives F(t) ≥ 0.
6. The congruence then gives QHQ − t ≥ 0.

Being constant on classes makes the representative rows equal to all orbit rows, so no lift is needed.

**Assumptions:**
- detailed balance w_i c_ij = w_j c_ji;
- the 48 lattice maps commute with H, M and w;
- the Lemma 0 move table is complete;
- for m0 ≥ 4, no tail orbit is one move from a flat.

**Steps that could fail:**
- core enumeration or canonical form (gated by the census and class_bijection);
- the per-link table or the colouring cap (gated by tail_cap_claim, recomputed by the verifier);
- the tail histogram of each two-step target;
- the direction of the ceiling in the Schur term;
- i128 overflow (overflow-checks are on, so overflow panics);
- binding of the certificate to the binary (the r = 9 pins; row 009 states the limit);
- class-dependence of the rows (row_hash plus the image gate).

I found no error in the chain.

**Checks:**
- Every LEDGER output I regenerated is byte-identical:
  - smoke, r = 12, m0 = 7: selftest, certificate and keys;
  - all 14 plant certificates at m0 = 6, r = 21/2;
  - the honest certificate at m0 = 11, r = 21/2 (`a217a469…`).
- Row hashes and keys for m0 = 11 and 12 equal rows 025-029. The m0 = 13 keys equal row 027.
- The m0 = 11 gate receipt is identical to row 030 except for its MEM line.
- Plant verdicts match the PLANTS_RECEIPT pattern.

**My own planted faults:**

| Fault | What it does | Result |
|---|---|---|
| F1 | doubles one entry of v | refused by row_check (26 rows) |
| F2 | raises t above the Ritz value | refused by row_check (682 rows) |
| F3 | swaps v between two classes | refused by row_check (25 rows) |
| F4 | deletes the Schur term in the pinned verifier | refused by gate_required.sh's sha256 pin |

## 6. Cost of the r = 9 run
Measured on a shared 8-core WSL machine with 7.8 GB of RAM:

| m0 | step | time | peak memory |
|---:|---|---:|---:|
| 11 | writer rowhash | 107 s | 174 MB |
| 11 | writer cert, one f | 297 s | 440 MB |
| 11 | verifier, one certificate | 13 min 52 s | 405 MB |
| 12 | writer rowhash | 196 s | 311 MB |
| 13 | writer rowhash | 296 s | 444 MB |

- Figures recorded by the package: writer 810,940 kB at m0 = 12, verifier 733 MB at m0 = 12, and about 1.1 GB
  expected at m0 = 13.
- Estimated total (CONJECTURE): about 45-60 min for step 1, 1.5-2 h for step 2 and 2-3 h for step 3. Steps 2 and 3
  run only if the earlier steps leave the comparison undecided.
- Disk: about 0.9 MB per certificate at m0 = 11, and key files of 0.3-0.7 MB.

## Errata
- **E1 (needs an owner ruling).** `FB rowhash --dir RUNxx` panics (exit 101) when RUNxx does not exist. main.rs
  never creates the directory, yet rows 001, 006 and 007 require RUNxx to be absent before that command. With an
  empty directory made just before the command, it succeeds and the hashes match the pins.
- **E2.** `gate_required.sh` and `r_scan.sh` hard-code the cloud path
  `/tmp/claude-0/-home-user/b2fb539a-…/scratchpad/floor`, and the run needs Linux (fork, wait4, /proc). Staging the
  folder at that path in WSL works.
- **E3.** The commit does not hold 286 disclosed files or 6 seat folders. On the committed set, the lint gives
  errors=294; the package's receipt says 0. The blindness disclosure is CANNOT_SEE from the commit.
- **E4.** Row 070 gives the verifier MEM as 403,336 kB; the pinned receipt says 403,696 kB.
- **E5.** The clippy gate fails, as in section 4.

## Open items
- The owner's ruling on E1, or a new freeze.
- The m0 = 13 prerequisite: verifier `--rows-only` on m0 = 13 and its memory peak (not run here).
- The verifier's run time and memory at m0 = 12 (not run here).
- The disclosed seat folders: publish them, or record that they are kept off the commit.
- A clippy-clean build: a source change, so it needs a new freeze.
- The r = 9 run itself: not started.

My WSL scratch copies under `/tmp` disappeared mid-session (the whole of `/tmp` was emptied, with uptime unchanged).
The numbers above were captured from the run outputs first. The staging path was then removed so the r = 9 run starts clean.
