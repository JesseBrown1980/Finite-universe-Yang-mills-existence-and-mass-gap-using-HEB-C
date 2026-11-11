#!/usr/bin/env python3
# mkreport.py -- writes VERIFY-FLOOR-FREEZE-V2-FINAL4.hbp (+ .sha256) from the verifier seat's outputs. Integers only.
import sys, os, re, hashlib
V = "/root/floor-v4-verify"
OUTD = sys.argv[1]
os.makedirs(OUTD, exist_ok=True)


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError:
        return "ABSENT"


def last(p):
    try:
        return [x for x in open(p, encoding="utf-8", errors="replace").read().split("\n") if x][-1]
    except (OSError, IndexError):
        return "ABSENT"


def grab(p, pat):
    try:
        return [x for x in open(p, encoding="utf-8", errors="replace").read().split("\n") if re.search(pat, x)]
    except OSError:
        return []


def clean(s, n=300):
    return s.replace("|", ":").replace(" ", "_")[:n]


rows = []


def row(tag, **kv):
    rows.append(tag + "|" + "|".join("%s=%s" % (k, v) for k, v in kv.items()) + "|json=0")


row("VERIFY_HEAD", seat="opus55_second_seat_of_ACER-CLAUDE-FABLE5_pid_8467a937cba309f7", model="claude-opus-5-5",
    host="acer_WSL2_Ubuntu_root_(same_machine_as_the_build_seat)", toolchain="rustc_1.81.0_eeb90cda1_cargo_1.81.0_clippy_0.1.81_python3.12",
    lane="wsl.exe_-u_root_bash_scripts_under_C:/tmp/opus55/floor-v2-verify4", workdir=V, commit="5eecb540431a1b5665605f68ed81bc701719dcd1",
    branch="local-opus55-floor-cert-freeze-v2-20261110", second_environment="NO_same_host_as_the_build_seat;_separate_clone_and_export_only")
for line in open(sys.argv[2], encoding="utf-8").read().split("\n"):
    if line.strip() and not line.startswith("#"):
        rows.append(line if line.endswith("json=0") else line + "|json=0")
# F (full-size fallback) from its own files
F = V + "/out/F13"
ex = open(V + "/out/F13.exit").read().split() if os.path.exists(V + "/out/F13.exit") else ["NOT_FINISHED"]
fin = last(V + "/out/F13.stdout.txt")
row("F_FULLSIZE_RUN", status=("COMPLETE" if ex[0] != "NOT_FINISHED" else "INCOMPLETE"), exit=ex[0], end=(ex[1] if len(ex) > 1 else "NONE"),
    args="--test-r_21/2_--test-m0_11,12,13_--test-f_1;8,7,6,5,4;6,5,4,3_--test-census_--test-hang_1:cert,2:cert_--test-g0_99372/1000",
    final=clean(fin, 420), stdout_sha256=sha(V + "/out/F13.stdout.txt"), receipt_sha256=sha(F + "/FLOOR-RUN-RECEIPT.hbp"),
    sampler=clean(open(V + "/out/F13.sampler").read().strip() if os.path.exists(V + "/out/F13.sampler") else "ABSENT"))
for p in ("^PREREQ", "^LIMIT", "kind=rowsonly", "^STEP\\|m0=13", "^CERTROW", "^DECISION\\|after_m0=13"):
    for x in grab(F + "/FLOOR-RUN-RECEIPT.hbp", p) or grab(F + "/log/run.log", p):
        row("F_LINE", src=clean(x, 520))
for x in grab(F + "/log/m13_rowsonly.txt", "^MEM\\|"):
    row("F_ROWSONLY_MEM", line=clean(x))
for x in sorted(os.listdir(F + "/log")) if os.path.isdir(F + "/log") else []:
    if x.startswith("m13_gate_") and x.endswith("_a1.txt"):
        for y in grab(F + "/log/" + x, "^MEM\\||^VERDICT\\||^RITZ_CLASS_VECTOR"):
            row("F_GATE_LINE", log=x, line=clean(y, 200))
ck = V + "/out/F13.recheck.txt"
row("F_CHECKER", status=("COMPLETE" if os.path.exists(ck + ".exit") else "NOT_RUN_OR_INCOMPLETE"),
    exit=(open(ck + ".exit").read().strip() if os.path.exists(ck + ".exit") else "NONE"), last=clean(last(ck), 420), sha256=sha(ck))
p = os.path.join(OUTD, "VERIFY-FLOOR-FREEZE-V2-FINAL4.hbp")
open(p, "w", encoding="utf-8", newline="\n").write("# final-head verification 4 of the floor freeze v2 (commit 5eecb540); pipe rows; json=0\n" + "\n".join(rows) + "\nEND|rows=%d|json=0\n" % len(rows))
open(p + ".sha256", "w", newline="\n").write("%s  %s\n" % (sha(p), os.path.basename(p)))
print("WROTE|%s|rows=%d|sha256=%s" % (p, len(rows), sha(p)))
