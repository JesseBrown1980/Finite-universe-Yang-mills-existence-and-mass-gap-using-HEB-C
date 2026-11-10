#!/usr/bin/env python3
"""Negative controls for the global-lock measurement.  Each planted fault must make
gl_measure.py stop with FAILED|check=<the predeclared name>.  The expected names are
fixed in CONTROLS-PREDICT.hbp, written before this script runs; its sha256 is
printed in CONTROLS_BEGIN.  A check renamed after the prediction was frozen is listed in
CHECK-RENAMES.hbp (old name, new name); the frozen file keeps the old name and each
CONTROL row prints both.  Integer only, json=0.

usage: gl_controls.py   (writes rows to stdout)
"""
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED = HERE / "CONTROLS-PREDICT.hbp"
RENAMES = HERE / "CHECK-RENAMES.hbp"


def emit(label, **f):
    print(label + "|" + "|".join(str(k) + "=" + str(v) for k, v in f.items()) + "|json=0", flush=True)


def main():
    rows = [s for s in PRED.read_text().splitlines() if s.startswith("CONTROL_PREDICT|")]
    ren = {}
    for s in RENAMES.read_text().splitlines():
        if s.startswith("CHECK_RENAME|"):
            g = dict(item.split("=", 1) for item in s.split("|")[1:] if "=" in item)
            ren[g["old"]] = g["new"]
    emit("CONTROLS_BEGIN", predict_file=PRED.name,
         predict_sha256=hashlib.sha256(PRED.read_bytes()).hexdigest(), controls=len(rows),
         renames_file=RENAMES.name, renames_sha256=hashlib.sha256(RENAMES.read_bytes()).hexdigest(),
         renames=len(ren))
    bad = 0
    for s in rows:
        f = dict(item.split("=", 1) for item in s.split("|")[1:] if "=" in item)
        argv = [sys.executable, "-I", str(HERE / "gl_measure.py"), f["lattice"], f["r"],
                "kf=" + f["kf"], "k3=" + f["k3"]]
        if f["sabotage"] != "none":
            argv.append("sabotage=" + f["sabotage"])
        p = subprocess.run(argv, capture_output=True, text=True)
        fails = [ln for ln in p.stdout.splitlines() if ln.startswith("FAILED|check=")]
        got = fails[0].split("|")[1][6:] if fails else "NONE"
        want = ren.get(f["expect_check"], f["expect_check"])
        ok = (got == want) and (p.returncode != 0) == (f["expect_check"] != "NONE")
        bad += 0 if ok else 1
        emit("CONTROL", name=f["name"], lattice=f["lattice"], r=f["r"], sabotage=f["sabotage"],
             expect_check=f["expect_check"], expect_check_current_name=want, observed_check=got, exit_code=p.returncode,
             stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),
             result="AS_PREDICTED" if ok else "NOT_AS_PREDICTED")
    emit("CONTROLS_END", not_as_predicted=bad, result="PASS" if bad == 0 else "FAIL")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
