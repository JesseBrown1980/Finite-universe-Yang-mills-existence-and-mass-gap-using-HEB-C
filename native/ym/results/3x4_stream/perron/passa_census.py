# Census of passA.bin alone, with no store read: the total weight, the magnetic numbers, and the flat rows.
# Answers two review questions: is the orbit space complete, and is M >= 3 on every non-flat row? json=0.
import array, sys

path, free_links = sys.argv[1], int(sys.argv[2])
raw = open(path, "rb").read()
if len(raw) % 16:
    raise SystemExit("PASSA_FAIL|reason=length|json=0")
n = len(raw) // 16
u = array.array("I")
u.frombytes(raw)
del raw
if u.itemsize != 4 or sys.byteorder != "little":
    raise SystemExit("PASSA_FAIL|reason=platform|json=0")
total = 0
hist = {}
flats = []
prev = -1
for h in range(n):
    i = 4 * h
    key = u[i] | (u[i + 1] << 32)
    w, m = u[i + 2], u[i + 3]
    if key <= prev or w <= 0:
        raise SystemExit(f"PASSA_FAIL|reason=keys_or_weight|row={h}|json=0")
    prev = key
    total += w
    hist[m] = hist.get(m, 0) + 1
    if m == 0:
        flats.append((h, w))
expected = 6**free_links
ok = int(total == expected)
print(f"PASSA_CENSUS|n={n}|sum_w={total}|expected_6_pow_free={expected}|sum_w_matches={ok}|keys_strictly_ascending=1|min_nonflat_M={min(k for k in hist if k > 0)}|max_M={max(hist)}|flat_rows={','.join(str(f[0]) for f in flats)}|flat_weights={','.join(str(f[1]) for f in flats)}|sum_flat_w={sum(f[1] for f in flats)}|json=0")
print("PASSA_M_HIST|" + "|".join(f"M{k}={hist[k]}" for k in sorted(hist)) + "|json=0")
sys.exit(0 if ok else 2)
