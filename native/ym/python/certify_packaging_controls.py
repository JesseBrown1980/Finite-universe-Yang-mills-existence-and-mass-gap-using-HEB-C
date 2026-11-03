#!/usr/bin/env python3
"""Controls for the certify step's receipt packaging (fix of 2026-10-29), on synthetic
outcomes only: no stage B input, no sealed receipt and no real assemble is used.

The assemble job's "Certify" step is taken from a workflow generated into a temporary
directory by full_space_certify_workflow.py (the generator under test, or the one at a
given git revision), run under `bash -e` as GitHub runs it, in a scratch workspace whose
full_space_certify.py and certify_timing.py are stubs that print a chosen receipt and
exit with a chosen status. For every outcome the fixed step must write CERTIFY_ADMISSION,
CERTIFY_PLAN_PARAMS, CERTIFY_EXIT and a sidecar that verifies, and must exit 0 only for
PASS. Integer-only, json=0.
usage: certify_packaging_controls.py REPO_ROOT [OLD_REV]
  OLD_REV: also run the INCONCLUSIVE case against the generator at that revision, to show
  the defect it had (expected: no sidecar).
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

D = "native/ym/results/3x3_full_space"
FILES = ["HEBC-YM-3X3-FULLSPACE-CORES-T1-TF.hbp", "HEBC-YM-3X3-FULLSPACE-CORES-T1-TF.sha256",
         "HEBC-YM-3X3-FULLSPACE-STAGE-A-R9.hbp", "HEBC-YM-3X3-FULLSPACE-STAGE-A-R9.sha256",
         "CERTIFY-ADMIT-MANIFEST-PART1.hbp", "CERTIFY-ADMIT-MANIFEST-PART1.sha256",
         "CERTIFY-ADMIT-MANIFEST-PART2.hbp", "CERTIFY-ADMIT-MANIFEST-PART2.sha256", "CERTIFY-ERRATUM-1.md"]

OUTCOMES = {
    "pass": ("CERTIFY_CORRECTNESS|CERTIFIED|json=0\nCERTIFY_VERDICT|PASS|N_full_t1=8|N_full_tF=8|json=0\n", 0, 0),
    "inconclusive": ("CERTIFY_CORRECTNESS|NOT_CERTIFIED|json=0\nCERTIFY_VERDICT|INCONCLUSIVE|json=0\n", 2, 1),
    "mismatch": ("CERTIFY_CORRECTNESS|CERTIFIED|json=0\nCERTIFY_VERDICT|MISMATCH|N_full_t1=9|N_full_tF=8|json=0\n", 1, 1),
    "crash": ("", 1, 1),
    "pass_line_but_rc1": ("CERTIFY_VERDICT|PASS|N_full_t1=8|N_full_tF=8|json=0\n", 1, 1),
}


def generate(gen_py, repo, outdir, fixed):
    args = [sys.executable, gen_py, *[os.path.join(repo, D, f) for f in FILES[:4]], outdir, "3x3-fullspace",
            "52533422", "71900000", os.path.join(repo, D)]
    if fixed:
        args += ["--split=100", "--cols=60", "--erratum=" + os.path.join(repo, D, "CERTIFY-ERRATUM-1.md")]
    args += ["40392589541", "40392589603"]
    subprocess.run(args, check=True, capture_output=True, cwd=repo)
    wf = yaml.safe_load(open(os.path.join(outdir, "hebc-ym-3x3-fullspace-certify.yml")))
    return next(s["run"] for s in wf["jobs"]["assemble"]["steps"] if s.get("name") == "Certify")


def workspace(repo, receipt, rc):
    w = tempfile.mkdtemp(prefix="pk_")
    os.makedirs(os.path.join(w, D))
    for f in FILES:
        shutil.copy2(os.path.join(repo, D, f), os.path.join(w, D, f))
    py = os.path.join(w, "native/ym/python")
    os.makedirs(py)
    for f in ("full_space_certify_workflow.py", "certify_admit.py"):
        shutil.copy2(os.path.join(repo, "native/ym/python", f), os.path.join(py, f))
    stub = "import sys\nsys.stdout.write(%r)\n%sraise SystemExit(%d)\n" % (
        receipt, "raise RuntimeError('synthetic crash')\n" if not receipt else "", rc)
    open(os.path.join(py, "full_space_certify.py"), "w").write(stub)
    open(os.path.join(py, "certify_timing.py"), "w").write("raise SystemExit(0)\n")
    os.makedirs(os.path.join(w, "admit"))
    open(os.path.join(w, "admit/ADMIT-FILES.sha256"), "w").write("0" * 64 + "  parts/x\n")
    open(os.path.join(w, "admit/ADMIT.hbp"), "w").write("ADMIT_TOTAL|artifacts=0|files_sha256=00|result=PASS|json=0\n")
    for d in ("c1/shards/cellx", "wsector/shards/s", "wfinal/shards/f", "wsample/shards/c",
              "wsector/http0", "wfinal/http0", "wsample/http0"):
        os.makedirs(os.path.join(w, d))
    for k in ("wsector", "wfinal", "wsample"):
        open(os.path.join(w, k, "http0", "x.hbp"), "w").write("HTTP0|x|json=0\n")
    open(os.path.join(w, "c1/shards/cellx/run.hbp"), "w").write("x\n")
    return w


def run(block, w):
    for k, v in {"${{ needs.sectors.result }}": "success", "${{ needs.finals.result }}": "success",
                 "${{ needs.sample.result }}": "success", "${{ github.repository }}": "x/y",
                 "${{ github.run_id }}": "0", "${{ github.sha }}": "0" * 40, "${{ secrets.GITHUB_TOKEN }}": ""}.items():
        block = block.replace(k, v)
    r = subprocess.run(["bash", "-e", "-c", block], cwd=w, capture_output=True, text=True)
    rec = os.path.join(w, "CERTIFY-3X3-FULLSPACE.hbp")
    side = os.path.join(w, "CERTIFY-3X3-FULLSPACE.sha256")
    text = open(rec).read() if os.path.exists(rec) else ""
    side_ok = os.path.exists(side) and open(side).read().split()[:1] == [hashlib.sha256(open(rec, "rb").read()).hexdigest()]
    return r.returncode, text, side_ok


def main():
    repo = os.path.abspath(sys.argv[1])
    old = sys.argv[2] if len(sys.argv) > 2 else None
    out, ok_all = [], True
    tmp = tempfile.mkdtemp(prefix="gen_")
    block = generate(os.path.join(repo, "native/ym/python/full_space_certify_workflow.py"), repo, tmp, True)
    for name, (receipt, rc, want_exit) in OUTCOMES.items():
        w = workspace(repo, receipt, rc)
        code, text, side_ok = run(block, w)
        has = {k: (k + "|") in text for k in ("CERTIFY_ADMISSION", "CERTIFY_PLAN_PARAMS", "CERTIFY_EXIT")}
        ok = (code != 0) == (want_exit != 0) and side_ok and all(has.values())
        ok_all &= ok
        out.append("PACKAGING_CONTROL|generator=fixed|case=%s|assemble_rc=%d|step_exit=%d|want_exit=%s|sidecar_verifies=%d|admission=%d|plan_params=%d|exit_line=%d|ok=%d|json=0"
                   % (name, rc, code, "0" if want_exit == 0 else "nonzero", side_ok, has["CERTIFY_ADMISSION"],
                      has["CERTIFY_PLAN_PARAMS"], has["CERTIFY_EXIT"], ok))
        shutil.rmtree(w)
    if old:
        # a scratch copy of the repo's python dir and inputs, with the old generator in place
        orepo = tempfile.mkdtemp(prefix="old_")
        shutil.copytree(os.path.join(repo, "native/ym/python"), os.path.join(orepo, "native/ym/python"))
        os.makedirs(os.path.join(orepo, D))
        for f in FILES:
            shutil.copy2(os.path.join(repo, D, f), os.path.join(orepo, D, f))
        g = os.path.join(orepo, "native/ym/python/full_space_certify_workflow.py")
        open(g, "w").write(subprocess.run(["git", "-C", repo, "show", "%s:native/ym/python/full_space_certify_workflow.py" % old],
                                          check=True, capture_output=True, text=True).stdout)
        t2 = tempfile.mkdtemp(prefix="gen_old_")
        oblock = generate(g, orepo, t2, True)
        w = workspace(repo, OUTCOMES["inconclusive"][0], 2)
        code, text, side_ok = run(oblock, w)
        defect_shown = code != 0 and not side_ok and "CERTIFY_ADMISSION|" not in text
        ok_all &= defect_shown
        out.append("PACKAGING_CONTROL|generator=%s|case=inconclusive|step_exit=%d|sidecar_verifies=%d|admission=%d|defect_reproduced=%d|json=0"
                   % (old, code, side_ok, "CERTIFY_ADMISSION|" in text, defect_shown))
    out.append("PACKAGING_CONTROLS_TOTAL|result=%s|json=0" % ("PASS" if ok_all else "FAIL"))
    print("\n".join(out))
    sys.exit(0 if ok_all else 2)


if __name__ == "__main__":
    main()
