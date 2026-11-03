# Replays the allpairs side of the author's run_controls.py into this review folder and compares every line with the recorded CONTROLS.hbp.
# Runs the recorded executable and the author's mutate_pairs.py, unchanged, on copies. fullrebuild is outside this review, so its 9 outcomes are not replayed.
# usage: replay_controls.py OUT_HBP   Integer only, json=0.
import os, re, subprocess, sys

ROOT = "C:/tmp/opus55/allpairs-review-20261103"
AP = "C:/tmp/opus55/ym-review-wt/native/ym/results/3x4_stream/perron/allpairs/"
EXE = "D:/ym-3x4-room-run/p0-ball/allpairs-pin-0fd24d3/allpairs.exe"
MUT = AP + "mutate_pairs.py"
FX = ROOT + "/diff/tmp/fx"
RD = "D:/ym-3x4-room-run/p0-ball/"
ALL = ["entry", "rowsum", "weight", "column", "swap", "mag", "sym2"]
CASES = [
    ("2x2", RD + "small/2x2/dev.bin", 40, 470000000, ALL),
    ("2x2", RD + "small/2x2/dev.bin", 150, 100, ALL),
    ("2x3", RD + "small/2x3/dev.bin", 1500, 470000000, ALL),
    ("2x3", RD + "small/2x3/dev.bin", 2600, 1000, ALL),
    ("3x3", RD + "c33/dev33.bin", 200000, 1000000, ["entry", "rowsum", "column", "sym2"]),
]
os.makedirs(FX, exist_ok=True)
rec = [ln for ln in open(AP + "CONTROLS.hbp", encoding="utf-8").read().splitlines()]
want = [ln for ln in rec if ln.startswith("ALLPAIRS|") or ln.startswith("MUTATED|")]
got = []


def tool(path, cap):
    r = subprocess.run([EXE, path, "0", str(cap)], capture_output=True, text=True)
    row = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")]
    return r.returncode, row[-1] if row else ""


def norm(s):
    return re.sub(r"\|secs=\d+", "", s)


exits = []
seen = set()
for name, base, rown, cap, modes in CASES:
    code, line = tool(base, cap)
    got.append(line)
    exits.append(("clean", code))
    for mode in modes:
        out = "%s/m-%s-%s-%d.bin" % (FX, name, mode, rown)
        m = subprocess.run([sys.executable, "-I", MUT, base, out, mode, str(rown)], capture_output=True, text=True)
        if m.returncode:
            raise SystemExit(m.stderr)
        got.append(m.stdout.strip())
        code, line = tool(out, cap)
        got.append(line)
        exits.append((mode, code))
        os.remove(out)
    if name not in seen:
        seen.add(name)
        out = "%s/raw-%s.bin" % (FX, name)
        b = bytearray(open(base, "rb").read())
        b[4096 + 12] ^= 1
        open(out, "wb").write(b)
        code, line = tool(out, cap)
        got.append(line)
        exits.append(("raw", code))
        os.remove(out)
os.rmdir(FX)
same = sum(1 for a, b in zip(want, got) if norm(a) == norm(b))
diff = [(i, a[:160], b[:160]) for i, (a, b) in enumerate(zip(want, got)) if norm(a) != norm(b)]
with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
    f.write("REPLAY_CONTROLS|recorded_lines=%d|replayed_lines=%d|identical_after_removing_secs=%d|allpairs_runs=%d|json=0\n" % (len(want), len(got), same, len(exits)))
    for d in diff[:10]:
        f.write("REPLAY_DIFF|i=%d|recorded=%s|replayed=%s|json=0\n" % d)
print(open(sys.argv[1], encoding="utf-8").read())
sys.exit(0 if not diff and len(want) == len(got) else 1)
