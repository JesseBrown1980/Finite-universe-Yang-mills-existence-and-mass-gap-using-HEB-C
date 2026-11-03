# Runs allpairs on clean small stores and on stores with one repaired change, against the outcomes written first in RUN.hbp. Fails closed.
# usage: run_controls.py   Writes CONTROLS.hbp beside it. Integer only, json=0.
import os, re, subprocess, sys, time

R = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(R, "allpairs.exe")
FR = os.path.join(R, "..", "fullrebuild", "fullrebuild.exe")
MUT = os.path.join(R, "mutate_pairs.py")
FX = os.path.join(R, "fx")
os.makedirs(FX, exist_ok=True)
RD = "D:/ym-3x4-room-run/p0-ball/"
ALL = ["entry", "rowsum", "weight", "column", "swap", "mag", "sym2"]
CASES = [
    ("2x2", RD + "small/2x2/dev.bin", RD + "small/2x2/passa.bin", "2", "2", 40, 470000000, ALL),
    ("2x2", RD + "small/2x2/dev.bin", RD + "small/2x2/passa.bin", "2", "2", 150, 100, ALL),
    ("2x3", RD + "small/2x3/dev.bin", RD + "small/2x3/passa.bin", "2", "3", 1500, 470000000, ALL),
    ("2x3", RD + "small/2x3/dev.bin", RD + "small/2x3/passa.bin", "2", "3", 2600, 1000, ALL),
    ("3x3", RD + "c33/dev33.bin", RD + "c33/p33.bin", "3", "3", 200000, 1000000, ["entry", "rowsum", "column", "sym2"]),
]
log = open(os.path.join(R, "CONTROLS.hbp"), "w", encoding="utf-8", newline="\n")
fails = 0


def emit(s):
    log.write(s + "\n")
    log.flush()


def run_tool(path, cap):
    r = subprocess.run([EXE, path, "0", str(cap)], capture_output=True, text=True)
    row = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")]
    return r.returncode, (row[-1] if row else ""), dict(x.split("=", 1) for x in (row[-1] if row else "").split("|") if "=" in x)


def rebuild(path, passa, lx, ly):
    r = subprocess.run([FR, path, passa, lx, ly, "2"], capture_output=True, text=True)
    row = [x for x in r.stdout.splitlines() if x.startswith("FULLREBUILD|")]
    return r.returncode, (row[-1] if row else ""), dict(x.split("=", 1) for x in (row[-1] if row else "").split("|") if "=" in x)


def want(label, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    emit("CONTROL_RESULT|%s|met=%d|%sjson=0" % (label, 1 if ok else 0, detail))


seen = set()
for name, base, passa, lx, ly, row, cap, modes in CASES:
    tag = "L=%s|row=%d|cap=%d" % (name, row, cap)
    code, line, f = run_tool(base, cap)
    emit(line)
    want("clean|" + tag, code == 0 and f.get("verdict") == "PASS")
    for mode in modes:
        out = os.path.join(FX, "m-%s-%s-%d.bin" % (name, mode, row))
        m = subprocess.run([sys.executable, "-I", MUT, base, out, mode, str(row)], capture_output=True, text=True)
        if m.returncode:
            raise SystemExit(m.stderr)
        mrow = m.stdout.strip()
        emit(mrow)
        code, line, f = run_tool(out, cap)
        emit(line)
        v = lambda k: int(f.get(k, "-1"))
        tagm = "mode=%s|%s" % (mode, tag)
        if mode == "entry":
            ok = code == 2 and v("value_mismatch") == 1 and v("row_sum_nonzero") == 0 and v("lower_without_upper") == 0 and v("upper_without_lower") == 0
        elif mode == "rowsum":
            ok = code == 2 and v("row_sum_nonzero") == 1 and v("value_mismatch") == 0 and v("lower_without_upper") == 0 and v("upper_without_lower") == 0
        elif mode == "weight":
            deg = int(re.search(r"off_diagonals=(\d+)", mrow).group(1))
            ok = code == 2 and v("value_mismatch") == deg
        elif mode == "column":
            ok = code == 2 and v("value_mismatch") == 0 and v("lower_without_upper") == 1 and v("upper_without_lower") == 1
        elif mode == "swap":
            ok = code == 2 and v("columns_not_ascending") == 1
        else:
            ok = code == 0 and f.get("verdict") == "PASS"
        want(tagm, ok, "exit=%d|" % code)
        if mode in ("mag", "sym2"):
            code2, line2, f2 = rebuild(out, passa, lx, ly)
            emit(line2)
            key, count = ("M_mismatch", 1) if mode == "mag" else ("entries_mismatch", 2)
            want("rebuild|" + tagm, code2 == 2 and int(f2.get(key, "-1")) == count, "exit=%d|" % code2)
        os.remove(out)
    if name not in seen:
        seen.add(name)
        out = os.path.join(FX, "raw-%s.bin" % name)
        b = bytearray(open(base, "rb").read())
        b[4096 + 12] ^= 1
        open(out, "wb").write(b)
        code, line, f = run_tool(out, cap)
        emit(line)
        want("unrepaired_merkle|" + tag, code == 1 and "merkle" in line and f.get("verdict") == "FAIL", "exit=%d|" % code)
        os.remove(out)
os.rmdir(FX)
emit("ALLPAIRS_CONTROLS_DONE|failed=%d|json=0" % fails)
log.close()
print("ALLPAIRS_CONTROLS_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
