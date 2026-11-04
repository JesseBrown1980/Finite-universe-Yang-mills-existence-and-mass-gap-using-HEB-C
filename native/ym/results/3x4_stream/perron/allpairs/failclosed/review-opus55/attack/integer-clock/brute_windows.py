# Integer copy of native/ym/results/3x4_stream/perron/allpairs/failclosed/review-opus55/attack/brute_windows.py, written by native/scripts/make_integer_pairs.py: 0 divisions moved to qdiv and 2 text pairs. The original stays as evidence.
# Second seat's brute-force check of allpairs' windows on small stores. Own parser, nothing imported from the tool.
# For each cap it derives the windows, the upper entries each window stores and the lower entries that land in it, compares
# them with every ALLPAIRS_PASS row the tool prints, and checks the pair predicate over all entries once per store.
# usage: brute_windows.py EXE OUT_HBP   Integer only, json=0. Exit 1 on any disagreement.
import bisect, struct, subprocess, sys, time
from array import array

EXE, OUT = sys.argv[1], sys.argv[2]
RD = "D:/ym-3x4-room-run/p0-ball/"
fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368]
CASES = [
    ("2x2", RD + "small/2x2/dev.bin", list(range(0, 1301)) + [470000000, 4000000000, 5000000000]),
    ("2x3", RD + "small/2x3/dev.bin", [0] + fib + [100, 1000, 18000, 36154, 36155, 36156, 470000000, 4000000000]),
    ("3x3", RD + "c33/dev33.bin", [100000, 500000, 1000000, 3000000, 3780006, 7560011, 7560012, 7560013, 470000000]),
]
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0


def emit(s):
    log.write(s + "\n")
    log.flush()
    print(s, flush=True)


def load(path):
    b = open(path, "rb").read()
    eol = b.index(b"\n")
    f = dict(x.split("=", 1) for x in b[:eol].decode().split("|") if "=" in x)
    n, payload = int(f["n"]), int(f["payload_bytes"])
    p = 4096
    wt, off = array("I", [0] * n), array("Q", [0] * (n + 1))
    cols, vals = array("I"), array("i")
    upper, partner_lower = array("Q", [0] * n), array("Q", [0] * n)
    nent = 0
    for h in range(n):
        w, _mag, cnt = struct.unpack_from("<IHH", b, p)
        p += 8
        wt[h] = w
        pairs = struct.unpack_from("<" + "Ii" * cnt, b, p)
        p += 8 * cnt
        cols.extend(pairs[0::2])
        vals.extend(pairs[1::2])
        for j in pairs[0::2]:
            if j > h:
                upper[h] += 1
            elif j < h:
                partner_lower[j] += 1
        nent += cnt
        off[h + 1] = nent
    if p > 4096 + payload:
        raise SystemExit("rows run past the payload")
    return n, wt, off, cols, vals, upper, partner_lower


def pair_check(n, wt, off, cols, vals):
    # Every lower entry looks up its partner, every upper entry is marked once. Binary search in this seat's own arrays.
    found = 0
    mismatch = 0
    lonely_lower = 0
    for h in range(n):
        for k in range(off[h], off[h + 1]):
            i = cols[k]
            if i >= h:
                continue
            a, b = off[i], off[i + 1]
            q = bisect.bisect_left(cols, h, a, b)
            if q < b and cols[q] == h:
                found += 1
                if wt[i] * vals[q] != wt[h] * vals[k]:
                    mismatch += 1
            else:
                lonely_lower += 1
    upper_total = sum(1 for h in range(n) for k in range(off[h], off[h + 1]) if cols[k] > h)
    return upper_total, found, mismatch, lonely_lower, upper_total - found


def windows(n, upper, partner_lower, cap):
    cap = max(1, min(cap, 4000000000))
    out = []
    start, held, seen = 0, 0, 0
    for h in range(n):
        c = upper[h]
        if held + c > cap and h > start:
            out.append((start, h, held, seen))
            start, held, seen = h, 0, 0
        held += c
        seen += partner_lower[h]
    if n:
        out.append((start, n, held, seen))
    return out


def run(path, cap):
    r = subprocess.run([EXE, path, "0", str(cap)], capture_output=True, text=True)
    rows = []
    last = {}
    for ln in r.stdout.splitlines():
        f = dict(x.split("=", 1) for x in ln.split("|") if "=" in x)
        if ln.startswith("ALLPAIRS_PASS|"):
            rows.append((int(f["rows_from"]), int(f["rows_to"]), int(f["upper_stored"]), int(f["lookups"]), int(f["found"])))
        elif ln.startswith("ALLPAIRS|"):
            last = f
    return r.returncode, rows, last


for name, path, caps in CASES:
    t0 = time.monotonic_ns()
    n, wt, off, cols, vals, upper, partner_lower = load(path)
    up, found, mismatch, lonely_lower, lonely_upper = pair_check(n, wt, off, cols, vals)
    emit("BRUTE_PAIRS|L=%s|n=%d|upper=%d|found=%d|mismatch=%d|lower_without_upper=%d|upper_without_lower=%d|secs=%d|json=0" % (name, n, up, found, mismatch, lonely_lower, lonely_upper, (time.monotonic_ns() - t0) // 10**9))
    if mismatch or lonely_lower or lonely_upper:
        bad += 1
    runs = 0
    dis = 0
    max_passes = 0
    for cap in caps:
        code, rows, last = run(path, cap)
        want = windows(n, upper, partner_lower, cap)
        got3 = [(a, b, c, d) for a, b, c, d, _ in rows]
        ok = code == 0 and last.get("verdict") == "PASS" and got3 == want and all(e == d for _, _, _, d, e in rows)
        ok = ok and int(last.get("pairs", -1)) == up and int(last.get("passes", -1)) == len(want)
        ok = ok and sum(w[2] for w in want) == up and sum(w[3] for w in want) == up
        ok = ok and want[0][0] == 0 and want[-1][1] == n and all(want[i][1] == want[i + 1][0] for i in range(len(want) - 1))
        runs += 1
        max_passes = max(max_passes, len(want))
        if not ok:
            dis += 1
            bad += 1
            emit("BRUTE_DISAGREE|L=%s|cap=%d|exit=%d|tool_passes=%s|want_passes=%d|first_tool=%s|first_want=%s|json=0" % (name, cap, code, last.get("passes"), len(want), got3[:2], want[:2]))
    emit("BRUTE_WINDOWS|L=%s|caps_run=%d|disagreements=%d|max_passes=%d|secs=%d|json=0" % (name, runs, dis, max_passes, (time.monotonic_ns() - t0) // 10**9))
emit("BRUTE_DONE|failed=%d|json=0" % bad)
log.close()
sys.exit(1 if bad else 0)
