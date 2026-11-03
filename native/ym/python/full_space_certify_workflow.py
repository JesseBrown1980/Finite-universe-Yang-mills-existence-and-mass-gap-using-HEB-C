#!/usr/bin/env python3
"""Write the certify GitRAM workflow for a sealed full-space stage B
(CERTIFY-SPEC.md). Every job goes through the HEB-C HTTP-0 server
(scripts/http0_jobs.sh). Integer-only, json=0.

Input admission (added before the 3x3 certify run, reviewer 2026-10-28): an `admit` job
fetches every artifact of every part by artifact id, re-checks fresh API metadata against
the frozen manifests (certify_admit.py manifest), verifies all of them all-or-nothing
(certify_admit.py admit) and uploads the admitted files. Every job that consumes stage B
inputs downloads only admitted bundles and checks them file by file against
ADMIT-FILES.sha256 (certify_admit.py check) before use.

usage: full_space_certify_workflow.py CORES CORES_SHA STAGE_A STAGE_A_SHA OUT NAME T1 TF ADMIT_DIR
         --split=S --cols=C [--erratum=FILE] RUN_ID [RUN_ID ...]
  ADMIT_DIR holds CERTIFY-ADMIT-MANIFEST-PART<n>.hbp (+ .sha256) for part n = 1.. in RUN_ID order.
  SPLIT and COLS are required and must be the values the stage B parts were generated with
  (erratum 1: the 3x3 parts used SPLIT=100, COLS=60). They are passed explicitly to both
  `full_space_certify.py plan` and `full_space_certify.py assemble`.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

BUILD = '''      - name: Toolchain 1.81
        run: |
          rustup toolchain install 1.81.0 --profile minimal
          rustup override set 1.81.0
      - name: Build offline from vendored sources
        working-directory: native/ym
        run: cargo build --release --offline --locked'''


def admitted_receipt():
    return '''      - uses: actions/download-artifact@v4
        with:
          name: admit-receipt
          path: admit'''


def group_of(spec):
    kind, rest = spec.split("/", 1)
    kind = kind.replace("countmerge", "count")
    return (kind + "/" + rest).replace("/", "_")


def main():
    cores, cores_sha, stage_a, stage_a_sha, out, name, t1, tf, admit_dir = sys.argv[1:10]
    rest = sys.argv[10:]
    opt = dict(a[2:].split("=", 1) for a in rest if a.startswith("--"))
    runs = [a for a in rest if not a.startswith("--")]
    split, cols = int(opt["split"]), int(opt["cols"])
    erratum = opt.get("erratum")
    mans = [os.path.join(admit_dir, "CERTIFY-ADMIT-MANIFEST-PART%d.hbp" % i) for i in range(1, len(runs) + 1)]
    groups, totals = set(), [0, 0, 0]
    for m in mans:
        for line in open(m):
            f = dict(x.split("=", 1) for x in line.rstrip("\n").split("|")[1:] if "=" in x)
            if line.startswith("CMANIFEST|") and f["kind"] == "cell":
                groups.add(f["group"])
            if line.startswith("CMANIFEST_TOTAL|"):
                assert f["result"] == "PASS"
                totals = [totals[0] + int(f["cells"]), totals[1] + int(f["merges"]), totals[2] + int(f["finals"])]
    groups = sorted(groups)
    plan = subprocess.run([sys.executable, os.path.join(HERE, "full_space_certify.py"), "plan", cores, cores_sha, str(split), str(cols)],
                          capture_output=True, text=True, check=True).stdout
    rows = [dict(x.split("=", 1) for x in l.split("|")[1:] if "=" in x) for l in plan.splitlines() if "kind=" in l]
    def grp(r):
        return group_of(r["spec"]) if r["kind"] == "final" and r["spec"].split("/", 1)[0].endswith("countmerge") else "none"
    inc = {k: "\n".join(f'          - {{id: "{k[0]}{i + 1:02d}", spec: "{r["spec"]}", grp: "{grp(r)}"}}'
                        for i, r in enumerate(x for x in rows if x["kind"] == k)) for k in ("sector", "final", "sample")}
    root = os.path.join(HERE, "..", "..", "..")
    rel = lambda p: os.path.relpath(os.path.abspath(p), os.path.abspath(root))
    wf = os.path.join(out, f"hebc-ym-{name}-certify.yml")
    watch = '''          set -euo pipefail
          B=native/ym/target/release/hebc_ym_http0; R=$RUNNER_TEMP/root; spec="${{ matrix.spec }}"
          kind=${spec%%/*}; rest=${spec#*/}
          case $kind in *countmerge) mode=${kind%countmerge} ;; *countcols) mode=${kind%countcols} ;; *count) mode=${kind%count} ;; *sector) mode=${kind%sector} ;; esac
          sec="${mode}sector/$(echo $rest | cut -d/ -f1-4)"; id=$(echo $spec | tr / _)
          if [ "$kind" = "${mode}countmerge" ]; then
            cid=$(echo "${mode}count/$rest" | tr / _); mkdir -p $R/scol/$cid
            for d in c*/shards; do cp -r $d/${mode}countcols_$(echo $rest | tr / _)_* $R/scol/$cid/ 2>/dev/null || true; done
            ls $R/scol/$cid | grep -q . || { echo "CERTIFY_WATCH|error=no_cells|spec=$spec|json=0"; exit 1; }
          fi
          if [ "$kind" = "${mode}sector" ]; then specs="$spec"; else specs="$sec $spec"; fi
          OUT_ID=out/http0/$id.hbp bash native/ym/scripts/http0_jobs.sh $B $R 8100 $specs
          mkdir -p out/shards; cp -r $R/shards/$id out/shards/'''
    jobs = []
    for kind, label, needs_cells in (("sector", "sectors", False), ("final", "finals", True), ("sample", "sample", False)):
        jobs.append(f'''  {label}:
    name: Watch {kind} ${{{{ matrix.id }}}} ${{{{ matrix.spec }}}}
{"    needs: admit" if needs_cells else ""}
    strategy:
      fail-fast: false
      max-parallel: 20
      matrix:
        include:
{inc[kind]}
    runs-on: ubuntu-latest
    timeout-minutes: 355
    steps:
      - uses: actions/checkout@v4
{(admitted_receipt() + chr(10) + """      - uses: actions/download-artifact@v4
        if: matrix.grp != 'none'
        with:
          name: admitted-cells-${{ matrix.grp }}
          path: c1
      - name: Check admitted cells
        if: matrix.grp != 'none'
        run: python3 native/ym/python/certify_admit.py check admit/ADMIT-FILES.sha256 cells/${{ matrix.grp }}/ c1""") if needs_cells else ""}
{BUILD}
      - name: Re-execute through HTTP-0
        env:
          HEBC_YM_FRESH: "1"
        run: |
{watch}
      - uses: actions/upload-artifact@v4
        with:
          name: watch-{kind}-${{{{ matrix.id }}}}
          retention-days: 30
          if-no-files-found: error
          path: out''')
    sealed = admitted_receipt() + '''
      - uses: actions/download-artifact@v4
        with:
          name: admitted-parts
          path: root/parts
      - uses: actions/download-artifact@v4
        with:
          pattern: admitted-cells-*
          path: c1
          merge-multiple: true
      - name: Check every admitted input before assembly
        run: |
          set -euo pipefail
          test "${{ needs.admit.result }}" = success
          python3 native/ym/python/certify_admit.py check admit/ADMIT-FILES.sha256 parts/ root/parts
          python3 native/ym/python/certify_admit.py check admit/ADMIT-FILES.sha256 cells/ c1 strip'''
    relm = [rel(m) for m in mans]
    fetch = "\n".join(f'''          mkdir -p zips/{i}
          for p in 1 2 3 4; do get "repos/$R/actions/runs/{r}/artifacts?per_page=100&page=$p" -q '.artifacts[]|[.id,.name,.size_in_bytes,.digest,.expired,.workflow_run.id,.workflow_run.head_sha]|@tsv'; done > fresh-{i}.tsv
          head=$(grep '^CMANIFEST_TOTAL|' {relm[i - 1]} | sed -E 's/.*\\|head=([0-9a-f]+)\\|.*/\\1/')
          python3 native/ym/python/certify_admit.py manifest .github/workflows/hebc-ym-{name}-stage-b-part{i}.yml {r} $head {i} fresh-{i}.tsv > fresh-{i}.hbp
          cmp fresh-{i}.hbp {relm[i - 1]}
          for id in $(grep '^CMANIFEST|' {relm[i - 1]} | sed -E 's/.*\\|artifact_id=([0-9]+)\\|.*/\\1/'); do get "repos/$R/actions/artifacts/$id/zip" > zips/{i}/$id.zip; done''' for i, r in enumerate(runs, 1))
    pairs = " ".join(f"{relm[i]} zips/{i + 1}" for i in range(len(runs)))
    uploads = "\n".join(f'''      - uses: actions/upload-artifact@v4
        with:
          name: admitted-cells-{g}
          retention-days: 30
          if-no-files-found: error
          path: adm/cells/{g}''' for g in groups)
    admit_job = f'''  admit:
    name: Admit every stage B artifact (all-or-nothing, before any use)
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4
      - name: Frozen manifests, fresh metadata, fetch by artifact id
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          set -euo pipefail
          R=$GITHUB_REPOSITORY
          get() {{ local n=0; until gh api "$1" "${{@:2}}" > "$RUNNER_TEMP/get.out"; do n=$((n+1)); [ $n -ge 6 ] && return 1; sleep $((n*n*5)); done; cat "$RUNNER_TEMP/get.out"; }}
{chr(10).join(f"          (cd $(dirname {m}) && sha256sum -c $(basename {m} .hbp).sha256)" for m in relm)}
{fetch}
      - name: Admit (phases 1, 2a, 2b)
        run: |
          set -euo pipefail
          python3 native/ym/python/certify_admit.py admit adm {totals[0]} {totals[1]} {totals[2]} {pairs} | tee admit.hbp
          grep -q '^ADMIT_TOTAL|.*|result=PASS|' admit.hbp
          cp admit.hbp adm/ADMIT.hbp
      - uses: actions/upload-artifact@v4
        with:
          name: admit-receipt
          retention-days: 90
          if-no-files-found: error
          path: |
            adm/ADMIT-FILES.sha256
            adm/ADMIT.hbp
      - uses: actions/upload-artifact@v4
        with:
          name: admitted-parts
          retention-days: 30
          if-no-files-found: error
          path: adm/parts
{uploads}
'''
    watched = "\n".join(f'''      - uses: actions/download-artifact@v4
        with:
          pattern: watch-{k}-*
          path: w{k}
          merge-multiple: true''' for k in ("sector", "final", "sample"))
    text = f'''# {name} certify: the N-Nest tree over the sealed stage B parts (runs {", ".join(runs)}).
# Generated by native/ym/python/full_space_certify_workflow.py from CERTIFY-SPEC.md.
# Depth 4 sectors rebuilt, depth 2 finals re-executed, depth 3 cells checked by hash plus a
# hash-selected sample re-executed, depths 1 and 0 recomputed; every job through HTTP-0.
name: HEB-C YM {name} certify

on:
  workflow_dispatch:
  push:
    branches: [ym-3x3-certify]
    paths: ['{rel(wf)}']

permissions:
  contents: read
  actions: read

concurrency:
  group: hebc-ym-{name}-certify-${{{{ github.ref }}}}
  cancel-in-progress: false

jobs:
{admit_job}
{chr(10).join(jobs)}

  assemble:
    name: Assemble, gate and verdict
    needs: [admit, sectors, finals, sample]
    if: always()
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
{sealed}
{watched}
      - name: Certify
        env:
          GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        run: |
          # packaging fix (2026-10-29): GitHub runs this step under bash -e, which stopped the
          # step at a non-zero assemble before the admission line and the sidecar were
          # written. -e is switched off for the whole step; every outcome writes them, and the
          # step's exit status is decided only from the receipt's own verdict line.
          set +e
          set -uo pipefail
          test "${{{{ needs.sectors.result }}}}" = success || echo "CERTIFY|watch_sectors=${{{{ needs.sectors.result }}}}|json=0"
          R=root; mkdir -p $R/cells $R/watch
          cp {rel(cores)} $R/cores.hbp; cp {rel(cores_sha)} $R/cores.sha256
          cp {rel(stage_a)} $R/stageA.hbp; cp {rel(stage_a_sha)} $R/stageA.sha256
          for d in c*/shards; do cp -r $d/* $R/cells/; done
          mv wsector/shards $R/watch/sectors; mv wfinal/shards $R/watch/finals; mv wsample/shards $R/watch/sample
          mkdir -p $R/watch/http0; for k in wsector wfinal wsample; do cp $k/http0/*.hbp $R/watch/http0/; done
          python3 native/ym/python/certify_timing.py ${{{{ github.repository }}}} ${{{{ github.run_id }}}} {" ".join(runs)} > $R/timing.hbp || true
          CERTIFY_RUNS={",".join(runs)} python3 native/ym/python/full_space_certify.py assemble $R {t1} {tf} {split} {cols} > CERTIFY-{name.upper()}.hbp 2> assemble.stderr
          rc=$?
          cat CERTIFY-{name.upper()}.hbp; cat assemble.stderr >&2
          echo "CERTIFY_ADMISSION|admit_files_sha256=$(sha256sum admit/ADMIT-FILES.sha256 | cut -c1-64)|{"|".join(f"manifest_part{i + 1}_sha256=$(sha256sum {relm[i]} | cut -c1-64)" for i in range(len(runs)))}|admit_total=$(grep '^ADMIT_TOTAL|' admit/ADMIT.hbp | cut -d'|' -f2-4)|json=0" >> CERTIFY-{name.upper()}.hbp
          echo "CERTIFY_PLAN_PARAMS|split={split}|cols={cols}|{("erratum=" + rel(erratum) + "|erratum_sha256=$(sha256sum " + rel(erratum) + " | cut -c1-64)|") if erratum else ""}generator_sha256=$(sha256sum native/ym/python/full_space_certify_workflow.py | cut -c1-64)|certify_py_sha256=$(sha256sum native/ym/python/full_space_certify.py | cut -c1-64)|admit_py_sha256=$(sha256sum native/ym/python/certify_admit.py | cut -c1-64)|workflow_commit=${{{{ github.sha }}}}|json=0" >> CERTIFY-{name.upper()}.hbp
          v=$(grep -c '^CERTIFY_VERDICT|PASS|' CERTIFY-{name.upper()}.hbp)
          echo "CERTIFY_EXIT|assemble_rc=$rc|verdict_pass_lines=$v|json=0" >> CERTIFY-{name.upper()}.hbp
          sha256sum CERTIFY-{name.upper()}.hbp > CERTIFY-{name.upper()}.sha256
          # green only for a receipt whose verdict is PASS from an assemble that exited 0;
          # INCONCLUSIVE, MISMATCH and a crash (no verdict line) all fail the step
          if [ "$rc" -eq 0 ] && [ "$v" -eq 1 ]; then exit 0; else exit 1; fi
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: certify-{name}
          retention-days: 90
          path: |
            CERTIFY-{name.upper()}.hbp
            CERTIFY-{name.upper()}.sha256
'''
    open(wf, "w").write(text)
    n = {k: sum(1 for r in rows if r["kind"] == k) for k in ("sector", "final", "sample")}
    print("CERTIFY_WORKFLOW|name=%s|runs=%s|split=%d|cols=%d|sectors=%d|finals=%d|sample=%d|out=%s|json=0"
          % (name, ",".join(runs), split, cols, n["sector"], n["final"], n["sample"], rel(wf)))


if __name__ == "__main__":
    main()
