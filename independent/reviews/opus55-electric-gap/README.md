# The second seat's evidence on gap(E) = 6

**November 3, 2026.** The second seat attacked branch `electric-gap-20261103` at head `689d85d`. Verdict: not refuted. Its runs were local, on host acer, with Python 3.13.14 and rustc 1.81. Its findings are applied in [`ELECTRIC_SPECTRUM_2X2_REPORT.md`](../../ELECTRIC_SPECTRUM_2X2_REPORT.md), dated beside each claim.

| File | What it holds | Tag |
|---|---|---|
| [`own_chars.py`](own_chars.py) | Its character path: its own incidence and character table, dim Inv by characters and by the rank of the group-average projector, and tables by vertex elimination | Code |
| [`tables.log`](tables.log), [`chars_full.log`](chars_full.log) | Full tables with Burnside and reflection closure: 1×3, 1×5, 2×2, 2×3, 3×2, 3×4, 4×3, 3×5, 4×4 | MEASURED, second seat |
| [`chars_low.log`](chars_low.log) | Tables truncated at cost 15: 3×6, 3×7, 4×4, 4×5, 4×6, 5×5, 5×6, 6×6, 4×7, 5×7, 6×7, 7×7, 8×8 | MEASURED, second seat |
| [`seven_tori_rerun.log`](seven_tori_rerun.log) | Full tables on 1×1, 1×2, 1×4, 2×1, 2×4, 2×5, 3×3. The second seat's report gives its readings for these seven. The unit applying its findings ran `own_chars.py` on them on November 3, and this log is that run | MEASURED, the applying unit |
| [`real.rs`](real.rs) | Its real-matrix tool: its own gauge fixing, P(E) on one vector per translation orbit, and prefix traces, in checked i128 | Code |
| [`real13.log`](real13.log), [`real15.log`](real15.log), [`real22.log`](real22.log), [`real23.log`](real23.log) | `real.rs` on 1×3, 1×5, 2×2, 2×3. On 2×3: dim 47,449, nnz 1,726,321, 7,970 vectors, `columns_nonzero=0`. The line `done` at the end of `real23.log` is from its launcher | MEASURED, second seat |
| [`readback.py`](readback.py) | The multiplicities from those prefix traces, against the character table | Code |
| [`engine_digits.py`](engine_digits.py), [`run_digits.sh`](run_digits.sh) | GPT-6's engine, its bytes unchanged, through its own `run()` with a digits argument | Code |
| [`engine_digits_runs.log`](engine_digits_runs.log) | That engine at T = 19700, 18300, 22700, 25700, 28700, each with more than 40 digits | MEASURED, second seat |
| [`verdict_probe.py`](verdict_probe.py) | Its probe of the prediction check, which changes the value on each needle row | Code |
| [`ownla.rs`](ownla.rs) | Its own build of E from orbits, and its modular linear algebra: `build`, `rank`, `charpoly`, `annihilate` | Code |
| [`rank_full_p1.log`](rank_full_p1.log), [`rank_full_p2.log`](rank_full_p2.log), [`rank_full_p3.log`](rank_full_p3.log) | The rank of E − c on its own 1,393 matrix for every c in 0..48, at 3 large primes. The nullities sum to 1,393 at each prime | MEASURED, second seat |
| [`charpoly_full.log`](charpoly_full.log) | The characteristic polynomial of its full matrix against the product of (x − c)^m, at 3 primes | MEASURED, second seat |
| [`charpoly_sectors.log`](charpoly_sectors.log) | The same on the 4 sectors, on its own sector matrices and on GPT-6's pinned files: 38 primes for pp and 33 for each other sector, above the coefficient bound 2·49ⁿ | MEASURED, second seat |

## Bytes

[`SHA256SUMS`](SHA256SUMS) covers every file here apart from this README and itself. Each is byte for byte what the second seat left in its scratch folder, with one change: `chars_full.log` and `chars_low.log` had Windows line ends, and they are filed with those CRs removed. Their source hashes are `3360b4c0f13ec93f8a0161e2fb15ca4cdcce2b0dbd2ce5183ff2f327e66546fe` and `ec554f187744957c38096b5234718442251b1dfa1f3e1822039b8dc9e54dfce1`. The paths in `run_digits.sh` name that scratch folder. To keep this folder small, `rank_sectors.log`, 100,656 bytes with hash `484aad3f5e50e1b8880f01f7faff5ca7c735268ac9f60cccf4829e9200d14a83`, the matrices and the binaries stay in that folder, on this machine at `C:/tmp/opus55/attack-electric-20261103`.

## Replay

```bash
cd independent/reviews/opus55-electric-gap
python3 -I -X utf8 own_chars.py table 3 3
python3 -I -X utf8 own_chars.py low 5 5 15
rustc +1.81 -O -o /tmp/real real.rs
/tmp/real 2 2 0,6,12,15,18,21,24,27,30,33,36,42,48 3
python3 -I -X utf8 readback.py real23.log tables.log
```

[`electric-spectrum-2x2.yml`](../../../.github/workflows/electric-spectrum-2x2.yml) checks the hashes and replays `own_chars.py` on all 28 tori against these logs. Mode `g` of [`electric_spectrum_2x2.py`](../../electric_spectrum_2x2.py) reads the logs into [`electric_gap_formula.measure`](../../electric_gap_formula.measure). The `real.rs` runs and the digits runs stay local receipts, and their hosted replay is OPEN.
