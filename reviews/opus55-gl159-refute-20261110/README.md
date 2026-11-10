# Independent refuter's evidence for PR #159 (global-lock GL1 and GL3 on 3x3 and 3x4)

This folder holds the 61 files the independent refuter produced while replaying and attacking PR #159, filed unedited, with the
manifest that fixes their paths, byte counts and sha256 values. This README is a filing extra; the manifest lists the 61 evidence
files and this file stands beside them.

## Provenance

| Item | Value |
|---|---|
| Where the files were made | `C:/tmp/opus55/gl159-refute/` on the local machine, a scratch folder outside git |
| `original_git_commit` | `NOT_APPLICABLE` |
| Left out of the filing | `src/` (a copy of the PR's own sources) and `__pycache__/` |
| Manifest | `REFUTER-MANIFEST.hbp`, 61 `REFUTER_FILE` rows, built 2026-11-10T14:09:04Z before any copy |
| Manifest sha256 | `c329a89f831189202af5754ab52899111ac856ed0a4b94a91af9b4ac9b693d4b` |
| Manifest commit | `68c3cc113fe4f5107badd60f1574b392d44d2d6f`, the manifest alone |
| Byte-for-byte rule | `.gitattributes` row `reviews/opus55-gl159-refute-20261110/** -text`, commit `dbb5408633e4c3d2564e745fef190e3a76e2d43b`, one commit earlier |
| Evidence commit | `2e4e8cbf0baefefc734ad85f85030b81fa379059`, the 61 files |
| Receipt | `REFUTE-GL159.hbp`, sha256 `d00cda91fa1fd83dde2193e8b5c022ef046376d28f8b1f28fa950824446f9b74` |
| Blob check at filing | 61 of 61 git blobs equal the manifest in path, bytes and sha256 (MEASURED from the index before the evidence commit) |
| Ten files of 0 bytes | filed as they are (the `.err` files of runs that wrote nothing to stderr) |

**Scope of the manifest.** The manifest fixes an integrity baseline from 2026-11-10T14:09:04Z onward: from that moment each
file is pinned by path, byte count and sha256. The history of the files before that moment is outside the manifest. The files
were made in an untracked scratch folder, so that earlier history has the status CANNOT_SEE for git.

## The two script hashes of `gl_measure.py`

| Script | Full sha256 | Where it appears |
|---|---|---|
| Uncommitted, at the first runs | `e9397ce58d0fa70e651d280e3344242aa893a50c373518d2f37f522ce571b52d` | `GL_MEASURE_BEGIN` row of the PR's `runs/levels-3x3.rows` and `runs/levels-3x4.rows`; this script produced those two files and is known by this hash alone |
| Committed in 32ebe74 and b3eeca0 | `daf78b00ed40acb350efe8a70611f07162317fca3a3f13e2b1b79fc724fa5e32` | `GL_MEASURE_BEGIN` row of the PR's `runs/levels-3x4-k3plus.rows` and of every refuter replay in `replay/` |

**What the replay equality covers.** The refuter reran the committed script (`daf78b00…`) and compared its rows with the PR's
three receipt files, with the timing fields (`ms`, `peak_kb`) removed. The equality is on the computational rows, the seven row
kinds `CENSUS`, `FLOOR_INPUTS`, `FLOOR`, `ASSEMBLY`, `LEVEL`, `ANCHOR`, `CHECKER_136_EQUIVALENCE` (MEASURED, `R_REPLAY` rows of
`REFUTE-GL159.hbp`):

| File | Rows | Computational rows, all equal | Row kinds that differ after the timing fields are removed |
|---|---|---|---|
| `runs/levels-3x3.rows` | 47 | 40 | `GL_MEASURE_BEGIN` (script hash, and the field `k3plus` the committed script adds), `BALLS` (the field `m3_plus` the committed script adds) |
| `runs/levels-3x4.rows` | 50 | 43 | the same two row kinds |
| `runs/levels-3x4-k3plus.rows` | 28 | 23 | none |

Byte-for-byte equality of whole files is 0 of 3, from the timing fields in all three and from the header and `BALLS` rows in
two. The gate `gl_accept.py replay` compares every row on the fields both files carry and names the fields one file alone
carries (`GL_MEASURE_BEGIN.k3plus`, `BALLS.m3_plus`); the shared fields of those rows are equal as well, with the two script hashes set aside. The content of the
uncommitted script `e9397ce5…` has the status CANNOT_SEE; its output rows are what the committed script reproduces.

## Blind order

| Fact | Status |
|---|---|
| Commit order: measured block committed in `32ebe74`, verdict block in `b3eeca0`, `32ebe74` an ancestor of `b3eeca0`, measured block identical as a prefix of the verdict file | MEASURED (`R_BLIND_ORDER`) |
| Frozen prediction sha256 `93350dd4…` at all five commits; erratum sha256 `c358974c…` from `26756c9` on | MEASURED |
| Push order on GitHub: whether `32ebe74` reached GitHub before the verdict commit existed | CANNOT_SEE. GitHub shows no push event or check run for `32ebe74`; the PR was opened at 13:06:42Z, after both commits |

## The 3x4 r=81 GL1 verdict rests on the k3plus trial

The GL1 verdict MET at 3x4, r=81 uses the E9 enclosure from the extended trial run (`k3plus=1`).

| Item | Value |
|---|---|
| Input file | `independent/global-lock-20261110/measure/runs/levels-3x4-k3plus.rows` |
| Input sha256, bytes | `c82ed05ffd0ba335e4c7ffa644f33dcd94a5c6ee52615211a7d579efe4dda6b6`, 3756 |
| Command | `gl_measure.py 3x4 27,81 k3plus=1`, script `daf78b00…` (the committed one) |
| Refuter's replay of it | `replay/levels-3x4-k3plus.rows`, sha256 `8616eeb801ea3a3abc48f1a579e5c85d06fb232a00d8af3b2a2542338b7c2848`, 23 computational rows equal |
| k3plus run alone, E8 | [71.778424535883, 71.778424786442] |
| k3plus run alone, E9 | [314.513872043217, 314.514955693997] |
| k3plus run alone, c_hat = r(3r − (E9 − E8)) | [21.340976192766, 21.428772201225], inside the frozen [21, 1765/81 = 21.790123457]: MET |
| Default trial (`runs/levels-3x4.rows`), E9 | [314.508880163653, 314.517227871621] |
| Default trial alone, c_hat | [21.156929805222, 21.833114445909]; the upper end lies above 1765/81, so the default trial alone leaves this row NOT_RESOLVED |
| Refuter's own certificate (other trial, other code) | c_hat in [21.279115140, 21.714875202], inside the frozen interval: MET (`R_GL1_INDEP`) |

The c_hat values in the two "alone" rows are integer arithmetic on the filed LEVEL rows (numerators over 10^12).

## Self-check limits the refuter found in the PR's code

These are measured outcomes of the refuter's planted faults (`plant.py`, outputs in `plant/`), each run through the PR's own
checks:

| Planted fault | Outcome under the PR's own checks |
|---|---|
| Floor raised 5% above the certified value (`floor105`) | exit 0 at 3x3 r=243 |
| P2max under-reported by 5% (`p2_95`) | exit 0 at 3x3 r=243 |
| One M4 → M≥6 exterior edge dropped (`drop_edge`) | exit 0 at 3x3 r=243 |
| E7 reported as E8 (`e8_as_e7`) | exit 0 at 3x3 r=243 and at r=729 |
| E10 reported as E9 (`e9_as_e10`) | exit 1 at r=243, where an on-file anchor exists; exit 0 at r=729, where none exists |
| Check `electric_term_psd_gershgorin` | at s_E = +1 its first form reads 0 ≥ 0; E ≥ 0 holds by representation theory (link spectrum 0, 3, 6) |

The acceptance gates that answer these are in `independent/global-lock-20261110/measure/` (`gl_accept.py`,
`gl_accept_plants.py`), with their results in `ACCEPTANCE-GATES.hbp` there.

## How this folder is checked in CI

`independent/global-lock-20261110/measure/verify_refuter_manifest.sh` checks the manifest's sha256, then every listed file's
path, byte count and sha256, then that the folder (all subfolders) holds only the listed files plus `REFUTER-MANIFEST.hbp`,
`README.md` and an optional `FILED.hbp`. The workflow is `.github/workflows/gl159-acceptance-gates.yml`.

## Running the refuter's code from this folder

`fullspace.py` adds the original scratch path to its import path and then imports `indep_gl` from its own folder; run it from
this folder as `python3 -B fullspace.py LXxLY r[,r...] [rows file]`. `plant.py`, `plant_run.sh`, `replay.sh` and the other
shell files carry the refuter's local paths and are kept as the record of what was run.
