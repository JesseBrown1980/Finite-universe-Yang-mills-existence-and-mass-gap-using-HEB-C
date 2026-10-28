#!/usr/bin/env python3
"""Run the frozen 3x3 full-space certify step on one local machine (Host8), as a
separate execution beside the GitHub run. Integer-only, json=0.

It executes the same code as the generated workflow, taken from the workflow file itself
at run time (not retyped):
  - admission: certify_admit.py manifest (fresh API metadata must equal the frozen
    manifests), download of every artifact by id, certify_admit.py admit (all-or-nothing);
    the admitted-file hash must equal the GitHub run's (EXPECTED_ADMIT below);
  - the 50 watcher jobs: the workflow's "Re-execute through HTTP-0" block, verbatim except
    that ${{ matrix.spec }} is filled in and the HTTP-0 port 8100 is replaced by a per-job
    port so jobs can run in parallel; every job from an empty root (HEBC_YM_FRESH=1),
    through scripts/http0_jobs.sh (hebc_ym_http0 serve);
  - assembly: the consumer checks and the workflow's "Certify" block, verbatim except for
    the GitHub expressions (needs.*.result from the local job outcomes, repository, run
    id = host8) and one added receipt line, CERTIFY_EXECUTION, naming this host.

usage (from the repository root, branch ym-3x3-certify):
  python3 native/ym/scripts/host8_certify.py WORKDIR [JOBS] [BASE_PORT]
    WORKDIR    empty directory with room for ~10 GB (zips 1.7 GB, admitted files 6.3 GB)
    JOBS       watcher jobs at once (default 50)
    BASE_PORT  first HTTP-0 port (default 18100; job i uses BASE_PORT + i)
Requires: gh (authenticated), curl, rustup with 1.81.0, python3 with PyYAML.
"""
import concurrent.futures as cf
import os
import re
import shutil
import subprocess
import sys
import time

import yaml

REPO = "JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C"
WF = ".github/workflows/hebc-ym-3x3-fullspace-certify.yml"
DIR = "native/ym/results/3x3_full_space"
RUNS = ("40392589541", "40392589603")
TOTALS = ("272", "20", "32")
EXPECTED_ADMIT = "c8f390ac1517cd47878e06993b1ec4a937f0c89c62c5d6c55b4f160f1b351d15"


def log(s):
    print(s, flush=True)


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=True, check=True, text=True, **kw)


def gh_get(path, out, tries=6):
    for n in range(tries):
        with open(out + ".part", "wb") as f:
            r = subprocess.run(["gh", "api", path], stdout=f)
        if r.returncode == 0:
            os.replace(out + ".part", out)
            return
        time.sleep((n + 1) * (n + 1) * 5)
    raise SystemExit("HOST8|error=download_failed|path=%s|json=0" % path)


def admit(work):
    mans = [os.path.join(DIR, "CERTIFY-ADMIT-MANIFEST-PART%d.hbp" % i) for i in (1, 2)]
    for m in mans:
        sh("cd %s && sha256sum -c %s" % (DIR, os.path.basename(m)[:-4] + ".sha256"))
    pairs = []
    for i, (run, man) in enumerate(zip(RUNS, mans), 1):
        tsv = os.path.join(work, "fresh-%d.tsv" % i)
        with open(tsv, "w") as f:
            for p in (1, 2, 3, 4):
                f.write(subprocess.run(["gh", "api", "repos/%s/actions/runs/%s/artifacts?per_page=100&page=%d" % (REPO, run, p),
                                        "-q", ".artifacts[]|[.id,.name,.size_in_bytes,.digest,.expired,.workflow_run.id,.workflow_run.head_sha]|@tsv"],
                                       check=True, capture_output=True, text=True).stdout)
        head = re.search(r"\|head=([0-9a-f]+)\|", [l for l in open(man) if l.startswith("CMANIFEST_TOTAL|")][0]).group(1)
        fresh = subprocess.run([sys.executable, "native/ym/python/certify_admit.py", "manifest",
                                ".github/workflows/hebc-ym-3x3-fullspace-stage-b-part%d.yml" % i, run, head, str(i), tsv],
                               capture_output=True, text=True).stdout
        if fresh != open(man).read():
            raise SystemExit("HOST8|error=fresh_metadata_differs_from_frozen_manifest|part=%d|json=0" % i)
        zd = os.path.join(work, "zips", str(i))
        os.makedirs(zd, exist_ok=True)
        ids = re.findall(r"\|artifact_id=([0-9]+)\|", "".join(l for l in open(man) if l.startswith("CMANIFEST|")))
        for aid in ids:
            gh_get("repos/%s/actions/artifacts/%s/zip" % (REPO, aid), os.path.join(zd, aid + ".zip"))
        log("HOST8_FETCH|part=%d|zips=%d|json=0" % (i, len(os.listdir(zd))))
        pairs += [man, zd]
    adm = os.path.join(work, "adm")
    r = subprocess.run([sys.executable, "native/ym/python/certify_admit.py", "admit", adm, *TOTALS, *pairs],
                       capture_output=True, text=True)
    log(r.stdout.strip())
    if r.returncode != 0 or "|result=PASS|" not in r.stdout.splitlines()[-1]:
        raise SystemExit("HOST8|admission=FAIL|verdict=INCONCLUSIVE|json=0")
    open(os.path.join(adm, "ADMIT.hbp"), "w").write(r.stdout)
    got = re.search(r"files_sha256=([0-9a-f]+)", r.stdout).group(1)
    log("HOST8_ADMIT|files_sha256=%s|github_run_files_sha256=%s|match=%d|json=0" % (got, EXPECTED_ADMIT, got == EXPECTED_ADMIT))
    if got != EXPECTED_ADMIT:
        raise SystemExit("HOST8|admission=differs_from_github_run|verdict=INCONCLUSIVE|json=0")
    return adm


def step(job, name):
    return next(s["run"] for s in job["steps"] if s.get("name") == name)


def run_watch(task):
    kind, mid, spec, grp, port, block, work, adm, repo = task
    jd = os.path.join(work, "jobs", "%s-%s" % (kind, mid))
    os.makedirs(os.path.join(jd, "tmp"))
    os.symlink(os.path.join(repo, "native"), os.path.join(jd, "native"))
    if grp != "none":
        os.symlink(os.path.join(adm, "cells", grp), os.path.join(jd, "c1"))
    text = block.replace("${{ matrix.spec }}", spec)
    assert text.count(" 8100 ") == 1
    text = text.replace(" 8100 ", " %d " % port)
    env = dict(os.environ, HEBC_YM_FRESH="1", RUNNER_TEMP=os.path.join(jd, "tmp"))
    t0 = time.monotonic_ns()
    with open(os.path.join(jd, "job.log"), "w") as f:
        rc = subprocess.run(["bash", "-c", text], cwd=jd, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    sec = (time.monotonic_ns() - t0) // 1000000000
    return kind, mid, spec, rc, sec, jd


def main():
    work = os.path.abspath(sys.argv[1])
    jobs_at_once = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    base = int(sys.argv[3]) if len(sys.argv) > 3 else 18100
    repo = os.getcwd()
    if os.path.exists(work) and os.listdir(work):
        raise SystemExit("HOST8|error=workdir_not_empty|json=0")
    os.makedirs(work, exist_ok=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise SystemExit("HOST8|error=tree_not_clean|json=0")
    log("HOST8|repo_head=%s|workflow=%s|jobs_at_once=%d|json=0" % (head, WF, jobs_at_once))
    sh("rustup toolchain install 1.81.0 --profile minimal >/dev/null && cd native/ym && cargo +1.81.0 build --release --offline --locked")
    adm = admit(work)

    wf = yaml.safe_load(open(WF))
    tasks, i = [], 0
    for label, kind in (("sectors", "sector"), ("finals", "final"), ("sample", "sample")):
        job = wf["jobs"][label]
        block = step(job, "Re-execute through HTTP-0")
        for m in job["strategy"]["matrix"]["include"]:
            tasks.append((kind, m["id"], m["spec"], m.get("grp", "none"), base + i, block, work, adm, repo))
            i += 1
    log("HOST8_PLAN|watchers=%d|json=0" % len(tasks))
    results = []
    with cf.ThreadPoolExecutor(max_workers=jobs_at_once) as ex:
        for r in ex.map(run_watch, tasks):
            kind, mid, spec, rc, sec, jd = r
            log("HOST8_WATCH|kind=%s|id=%s|spec=%s|rc=%d|seconds=%d|json=0" % (kind, mid, spec, rc, sec))
            results.append(r)
    status = {k: ("success" if all(r[3] == 0 for r in results if r[0] == k) else "failure") for k in ("sector", "final", "sample")}

    asm = os.path.join(work, "asm")
    os.makedirs(asm)
    os.symlink(os.path.join(repo, "native"), os.path.join(asm, "native"))
    shutil.copytree(os.path.join(adm, "parts"), os.path.join(asm, "root", "parts"))
    os.makedirs(os.path.join(asm, "c1", "shards"))
    for g in sorted(os.listdir(os.path.join(adm, "cells"))):
        shutil.copytree(os.path.join(adm, "cells", g, "shards"), os.path.join(asm, "c1", "shards"), dirs_exist_ok=True)
    os.makedirs(os.path.join(asm, "admit"))
    for f in ("ADMIT-FILES.sha256", "ADMIT.hbp"):
        shutil.copy2(os.path.join(adm, f), os.path.join(asm, "admit", f))
    for kind in ("sector", "final", "sample"):
        for sub in ("shards", "http0"):
            os.makedirs(os.path.join(asm, "w" + kind, sub), exist_ok=True)
        for r in results:
            if r[0] == kind and r[3] == 0:
                shutil.copytree(os.path.join(r[5], "out"), os.path.join(asm, "w" + kind), dirs_exist_ok=True)
    for prefix, local, strip in (("parts/", "root/parts", ""), ("cells/", "c1", "strip")):
        sh("cd %s && python3 native/ym/python/certify_admit.py check admit/ADMIT-FILES.sha256 %s %s %s"
           % (asm, prefix, local, strip))

    block = step(wf["jobs"]["assemble"], "Certify")
    subs = {"${{ needs.sectors.result }}": status["sector"], "${{ needs.finals.result }}": status["final"],
            "${{ needs.sample.result }}": status["sample"], "${{ github.repository }}": REPO,
            "${{ github.run_id }}": "host8"}
    for k, v in subs.items():
        block = block.replace(k, v)
    if "${{" in block:
        raise SystemExit("HOST8|error=unsubstituted_expression|json=0")
    mark = "          sha256sum CERTIFY-3X3-FULLSPACE.hbp > CERTIFY-3X3-FULLSPACE.sha256".strip()
    assert block.count(mark) == 1
    exe = ('echo "CERTIFY_EXECUTION|host=host8|repo_head=%s|watchers=%d|sectors=%s|finals=%s|sample=%s|'
           'watch_seconds_total=%d|json=0" >> CERTIFY-3X3-FULLSPACE.hbp\n'
           % (head, len(results), status["sector"], status["final"], status["sample"], sum(r[4] for r in results)))
    block = block.replace(mark, exe + mark)
    r = subprocess.run(["bash", "-c", block], cwd=asm, env=dict(os.environ, GH_TOKEN=os.environ.get("GH_TOKEN", "")))
    log("HOST8_ASSEMBLE|rc=%d|receipt=%s|json=0" % (r.returncode, os.path.join(asm, "CERTIFY-3X3-FULLSPACE.hbp")))


if __name__ == "__main__":
    main()
