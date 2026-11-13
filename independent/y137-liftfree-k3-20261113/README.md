# Issue #137: the E₃ isolation of draft #155, read on the lift-free floor

**Outcome: PRIMARY PASS. Merge held for GPT-6's evaluation.** With the lift-free floor
λ_min(QHQ) ≥ 94.0682 J_E of PR #173 in place of the lift-dependent 94.070673 of #131, every
inertia count of the K3 reflection-sector isolation (draft PR #155) is unchanged at every
original threshold. No fallback point was evaluated.

| Threshold z (J_E) | Even lower | Even upper | Odd lower | Odd upper | On the old floor |
|---|---|---|---|---|---|
| 69.9567503 | 2 | 2 | 0 | 0 | 2, 2, 0, 0 |
| 69.9686993 | 2 | 2 | 0 | 0 | 2, 2, 0, 0 |
| 69.9689591 | 3 | 2 | 0 | 0 | 3, 2, 0, 0 |

So, on the 3×4 lattice at r = 9, conditional only on the #173 certificate for the lower side:

- exactly 2 reflection-even levels and no odd level lie below z₀ = 69.9567503;
- E₃(even) ≥ 69.9686993 and E(odd) ≥ 69.9689591;
- with the window E₂ < 69.96 of #136/#174, E₃ − E₂ > 0.0086993 J_E.

## Evidence chain

| Step | File | Pin |
|---|---|---|
| Frozen prediction | `PREDICTION.hbp` | commit `debf755`, before the replay code and the run |
| Original #155 source | `src155/y137_k3_sector_isolation.py` | sha256 `f3461aa8…e28ff`; draft receipt `cf91b9e4…16ef` |
| #173 floor certificate and verifier | `../y142-floor-word-search-20261113/m13/` | certificate `7ad6e199…a6b6`; `gate_required.sh` `0064ca46…849c`; `cert_gate.py` `6043d089…2889` |
| K3 replay | `replay_k3.py` with `k3_common.py`, `RESULT-K3-LIFTFREE.hbp`, `replay_k3.stdout.txt` | result `b268a60b…860e`; draft receipt reproduced byte for byte |
| Independent checker | `check_k3.py`, `check_k3.stdout.txt` | 3 of 3 points agree |
| Hosted receipt | `.github/workflows/y137-liftfree-k3.yml` | runs both at the pull-request head |

The summary rows are in `RECEIPT-K3-LIFTFREE.hbp`.

## How it was done

- **Replay.** The draft script is imported unmodified from a fresh directory holding only it and
  the merged #136 checker. First its `main` runs as written and rewrites its own receipt
  identically. Then the K3 ball is built again with the draft's own functions and its threshold
  function is called at the three original points; the U, G and L hashes and the counts on the
  old floor equal the rows of the draft receipt, so these are the draft's matrices. U and G do
  not depend on the floor; the lower matrix for the new floor is L = 6(b·floor − a·10⁶)U − 10⁶G.
- **Two versions.** Version 1 (commit `6663fc8`, run first) observed the draft's calls by
  replacing a function in the imported module; the repository's no-float gate refuses that.
  Version 2 is the gate-clean form described above. Same counts, and the same U and G entry for
  entry. Version 1's output is kept in `v1/`. The prediction's points, fallback points and
  outcomes are unchanged; its method line said "observed", and version 2 calls directly.
- **Checker.** Counts negative eigenvalues from the integer characteristic polynomial by sign
  changes (exact for a symmetric matrix), with its own even/odd basis and exact zero cross terms.
  The draft and the replay use the #136 checker's inertia routine instead.
- **Timing of the checker.** It was written after this seat had seen the replay's counts. Its
  method is independent; it is not blind. For a blind recount, `MATRICES-K3.hbp` holds the exact
  U and G of the three points (`dump_k3_matrices.py` writes it).

## Scope

- A floor substitution in the draft's own computation; the K3 ball is not rebuilt independently.
- The draft's open items stay open: the second seat's independent recount and planted faults;
  the reflection symmetry on the whole space is NAMED, exact on K3 and shell 4.
- The #155 receipt, the #173 certificate and this replay are three separate pieces of evidence;
  none modifies another.
- The Wilson-sum first-state weight is OPEN (GPT-6's lane). Issue #137 stays open.

## Run it

```
python3 -I -B independent/y137-liftfree-k3-20261113/replay_k3.py    # about 6 minutes, 0.7 GB
python3 -I -B independent/y137-liftfree-k3-20261113/check_k3.py
```
