# Calibrates how t_cert - t depends on (level - t) on the small stores, to choose the warm-start threshold.
# Uses the pinned perroncert. Integers on the tool side; the fit here only informs a choice, it certifies nothing.
import os, re, subprocess, sys

RD = "D:/ym-3x4-room-run/p0-ball"
EXE = RD + "/perroncert.exe"
OUT = RD + "/warmcal"
os.makedirs(OUT, exist_ok=True)
CASES = [
    ("2x2", RD + "/small/2x2/dev.bin", (46466796 + 46468750) // 2, [44000000, 45000000, 46000000, 46300000, 46420000]),
    ("2x3", RD + "/small/2x3/dev.bin", (58441406 + 58443359) // 2, [56000000, 57000000, 58000000, 58300000, 58400000]),
]
rows = []
for name, dev, lam, ts in CASES:
    pts = []
    for t, sw in zip(ts, ["600", "600", "800", "1200", "3000"]):
        p = subprocess.run([EXE, "solve", dev, "0", "1000", "9000", str(t), sw], capture_output=True, text=True)
        last = [x for x in p.stdout.splitlines() if x.startswith("PERRONCERT|") or x.startswith("PERRONCERT_ERROR")]
        if p.returncode != 0 or not last or last[-1].startswith("PERRONCERT_ERROR"):
            print("FAIL", name, t, p.returncode, last[-1:] or p.stdout[-200:])
            sys.exit(2)
        f = dict(x.split("=", 1) for x in last[-1].split("|")[1:] if "=" in x)
        tc = int(f["t_cert_milli"])
        ex, m = tc - t, lam - t
        pts.append((t, tc, ex, m, f["min_mag"]))
        rows.append(f"WARMCAL|L={name}|lambda1_mid_milli={lam}|t_milli={t}|t_cert_milli={tc}|min_mag={f['min_mag']}|n={f['n']}|json=0")
    (t1, _, e1, m1, _), (t2, _, e2, m2, _) = pts[-2], pts[-1]
    # 1/ex = a/m + b, two nearest points, units of J_E
    x1, x2 = 1000000 / e1, 1000000 / e2
    y1, y2 = 1000000 / m1, 1000000 / m2
    a = (x2 - x1) / (y2 - y1)
    b = x1 - a * y1
    rows.append(f"WARMCAL_FIT|L={name}|a={a:.4f}|b={b:.4f}|tag=CONJECTURE|json=0")
with open(OUT + "/WARMCAL.hbp", "w", newline="\n") as f:
    f.write("\n".join(rows) + "\n")
print("\n".join(rows))
