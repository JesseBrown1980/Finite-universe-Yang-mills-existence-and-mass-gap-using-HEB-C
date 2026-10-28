# 3×3 certify step on Host8 (a separate execution beside GitHub run 40688572522)

`native/ym/scripts/host8_certify.py` runs the same certify step on one machine.

- **Same code.** The admission, the 50 watcher blocks and the `Certify` block are read
  from the generated workflow file at run time. They are not retyped.
- **What it changes.** Exactly three things:
  1. The matrix spec is filled in.
  2. The HTTP-0 port 8100 becomes a per-job port, so all 50 jobs can run at once.
  3. The GitHub expressions are replaced: `needs.*.result` comes from the local job
     outcomes, and the run ID is `host8`. One receipt line, `CERTIFY_EXECUTION`, names
     the host.
- **Every job.** Every job goes through `hebc_ym_http0 serve`, from an empty root.

## Commands (repository root, branch `ym-3x3-certify`, clean tree)

```bash
git fetch origin && git checkout ym-3x3-certify && git pull --ff-only
gh auth status                      # gh must be logged in (it downloads the artifacts)
pip install pyyaml                  # if missing
python3 native/ym/scripts/host8_certify.py /path/to/empty/workdir 50 2>&1 | tee host8-certify.log
```

The working directory needs about 10 GB: 1.7 GB of ZIPs and 6.3 GB of admitted files.
The receipt is written to `<workdir>/asm/CERTIFY-3X3-FULLSPACE.hbp` with its `.sha256`.

## What must hold

- **Admission.** Fresh API metadata must equal both frozen manifests. Admission must
  reproduce the GitHub run's admitted-file hash, `c8f390ac…1d15`. If not, the script
  stops and the run is INCONCLUSIVE.
- **Reading the receipt.** It is read in the frozen order of `CERTIFY-SPEC.md`, the same
  as GitHub's. Host8's watchers use a binary built on Host8, so its `HTTP0_IDENTITY`
  binary hash differs from GitHub's. The one-binary rule applies within each run.
- **Comparing the two runs.** `run.hbp`, `index.hbi`, `run.anchor` and `spec` must agree,
  byte for byte, with GitHub's for every watcher. `run.measure` holds wall-clock timings
  and differs from run to run.
- **Disagreement.** If the two runs disagree, that is reconciled. Neither one is
  selected.

## Harness check (cloud container, 2026-10-28)

Sector `s01` (`sector/3/3/-1/-1`) was run through this harness from an empty root in
73 s. Against GitHub's `watch-sector-s01` artifact:

- `run.hbp`, `index.hbi`, `run.anchor` and `spec` are **byte-identical**;
- `run.measure` differs only in the wall-clock `ms` values;
- the HTTP-0 request log is identical apart from the `HTTP0_IDENTITY` binary hash.
