#!/usr/bin/env python3
"""Read-only cross-check: comparator v2 (streaming implementation) on local shellschur /
roomschur output files at t = 60M and 72M. Writes a NEW receipt and never modifies any input
or existing receipt. Integer-only, json=0.

Refuses to start (exit 3, nothing written) if any lane process is running, so it cannot contend
with the 90M chain or an automatically triggered pilot. Refuses (exit 4) if either comparator
file does not have the reviewed SHA-256.

usage: local_v2_crosscheck.py OUT_DIR SHELL_60M ROOM_60M SHELL_72M ROOM_72M
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(os.path.dirname(HERE), "python")
V2 = os.path.join(PY, "schur_record_compare.py")
STREAM = os.path.join(PY, "schur_record_compare_stream.py")
WANT = {
    V2: "977e5e81fc609662cad3a19299928ed8a0545a0add1dae76d04835f29e1a0c62",
    STREAM: "7b224b21598432db6511fc5a2dd11d382c5c9288967a792fd71efeafa953efa9",
}
LANE = ("shellschur", "roomschur", "ymroom", "ymsec", "hebc_ym_http0", "flatcomp", "cluster", "ddcore")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def running():
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True).stdout
        names = [l.split('","')[0].strip('"').lower() for l in out.splitlines() if l]
    else:
        out = subprocess.run(["ps", "-eo", "comm="], capture_output=True, text=True).stdout
        names = [l.strip().lower() for l in out.splitlines()]
    return sorted({n for n in names for p in LANE if n.startswith(p)})


def main(a):
    if len(a) != 5:
        raise SystemExit(__doc__)
    out_dir, pairs = a[0], [("60000000", a[1], a[2]), ("72000000", a[3], a[4])]
    busy = running()
    if busy:
        print("LOCAL_V2_CROSSCHECK|result=REFUSED|reason=lane_processes_running|processes=%s|json=0" % ",".join(busy))
        sys.exit(3)
    for f, w in WANT.items():
        if not os.path.exists(f) or sha(f) != w:
            print("LOCAL_V2_CROSSCHECK|result=REFUSED|reason=comparator_hash|file=%s|json=0" % os.path.basename(f))
            sys.exit(4)
    rec = os.path.join(out_dir, "LOCAL-V2-CROSSCHECK-60M-72M.hbp")
    if os.path.exists(rec):
        print("LOCAL_V2_CROSSCHECK|result=REFUSED|reason=receipt_exists|path=%s|json=0" % rec)
        sys.exit(5)
    lines = ["LOCAL_V2_CROSSCHECK|scope=read_only_cross_check|not_merged_with_ci_lane=1|json=0"]
    for f in (V2, STREAM):
        lines.append("COMPARATOR_FILE|file=%s|sha256=%s|json=0" % (os.path.basename(f), sha(f)))
    verdicts = []
    for t, s, r in pairs:
        for side, p in (("shell", s), ("room", r)):
            ok = os.path.exists(p)
            lines.append("INPUT|t_milli=%s|side=%s|file=%s|bytes=%d|sha256=%s|json=0"
                         % (t, side, os.path.basename(p), os.path.getsize(p) if ok else -1, sha(p) if ok else "missing"))
        res = subprocess.run([sys.executable, STREAM, s, r], capture_output=True, text=True)
        for l in res.stdout.splitlines():
            lines.append("STDOUT|t_milli=%s|%s" % (t, l))
        for l in res.stderr.splitlines():
            lines.append("STDERR|t_milli=%s|%s" % (t, l.replace("|", "/")))
        v = res.stdout.strip().splitlines()[-1].split("|")[2] if res.stdout.strip() else "NO_OUTPUT"
        verdicts.append(v)
        lines.append("RESULT|t_milli=%s|exit=%d|v2_verdict=%s|json=0" % (t, res.returncode, v))
    agree = all(v == "AGREE" for v in verdicts)
    lines.append("LOCAL_V2_CROSSCHECK_RESULT|v2_60M=%s|v2_72M=%s|cross_comparator_agreement_60M_72M=%d|json=0"
                 % (verdicts[0], verdicts[1], int(agree)))
    body = "\n".join(lines) + "\n"
    with open(rec, "w", newline="\n") as f:
        f.write(body)
    with open(rec + ".sha256", "w", newline="\n") as f:
        f.write("%s  %s\n" % (hashlib.sha256(body.encode()).hexdigest(), os.path.basename(rec)))
    sys.stdout.write(body)
    sys.exit(0 if agree else 2)


if __name__ == "__main__":
    main(sys.argv[1:])
