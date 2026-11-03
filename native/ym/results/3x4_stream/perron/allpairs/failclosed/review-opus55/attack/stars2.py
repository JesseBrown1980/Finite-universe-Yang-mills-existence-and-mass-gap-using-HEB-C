# Directed versions of stars.py: a row of the largest count placed exactly on the tool's 64 MiB chunk boundary.
#   header_then_boundary  the row's 8-byte header is the last room of the chunk, all 65,535 entries in the next chunk
#   starts_at_boundary    the row starts exactly at the chunk boundary, so the previous row ends there
#   spans_boundary        half of the row's entries on each side
# Closed small blocks at the front set the position, and a pair split across the store sets it to 8 modulo 16.
# Each: the clean store must pass, and one changed value in that row, past the boundary, must give one mismatch, named.
# usage: stars2.py OUT_HBP   Integer only, json=0.
import bisect, hashlib, os, struct, subprocess, sys, time

ROOT = "C:/tmp/opus55/allpairs-review-20261103"
RECORDED = "D:/ym-3x4-room-run/p0-ball/allpairs/allpairs.exe"
READER = ROOT + "/bin/review-reader.exe"
TMP = ROOT + "/attack/stores/stars2.bin"
KEYS = ["--r", "%x" % int.from_bytes(os.urandom(15), "big"), "--k0", os.urandom(8).hex(), "--k1", os.urandom(8).hex()]
BOUND = 64 << 20
log = open(sys.argv[1], "w", encoding="utf-8", newline="\n")
bad = 0


def emit(s):
    log.write(s + "\n")
    log.flush()
    print(s, flush=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def merkle(pl):
    hx = "".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20))
    return sha(hx.encode())


def row(w, cols):
    return struct.pack("<IHH", w, 3, len(cols)) + b"".join(struct.pack("<Ii", j, z) for j, z in cols)


def build(a, b, split):
    """a closed 2-cliques (48 bytes), b closed 4-cliques (160 bytes), and when split a pair whose two rows sit at the two ends."""
    parts, starts, pos, idx = [], [], 0, 0

    def add(r):
        nonlocal pos
        parts.append(r)
        starts.append(pos)
        pos += len(r)

    N = 65534 + 128
    total_prefix = 2 * a + 4 * b + (1 if split else 0)
    last = total_prefix + N  # index of the split pair's second row
    if split:
        add(row(1, [(0, 1), (last, -1)]))
        idx = 1
    for _ in range(a):
        add(row(1, [(idx, 1), (idx + 1, -1)]))
        add(row(1, [(idx, -1), (idx + 1, 1)]))
        idx += 2
    for _ in range(b):
        for q in range(4):
            add(row(1, [(idx + t, 3 if t == q else -1) for t in range(4)]))
        idx += 4
    base = idx
    hubs = sorted(base + 512 * i + 7 for i in range(128))
    hubset = set(hubs)
    leaves = [base + i for i in range(N) if base + i not in hubset]
    neg = {j: struct.pack("<Ii", j, -1) for j in hubs + leaves}
    for h in range(base, base + N):
        if h in hubset:
            d = struct.pack("<Ii", h, 65534)
            parts.append(struct.pack("<IHH", 1, 3, 65535) + b"".join(neg[j] if j != h else d for j in sorted(leaves + [h])))
        else:
            d = struct.pack("<Ii", h, 128)
            parts.append(struct.pack("<IHH", 1, 3, 129) + b"".join(neg[j] if j != h else d for j in sorted(hubs + [h])))
        starts.append(pos)
        pos += len(parts[-1])
    n = base + N
    pairs = a + 6 * b + 128 * 65534
    entries = 4 * a + 16 * b + 128 * 65535 + 65534 * 129
    if split:
        add(row(1, [(0, -1), (last, 1)]))
        n += 1
        pairs += 1
        entries += 4
    return b"".join(parts), starts, n, entries, pairs, hubs


def wrap(payload, n, entries):
    line = "YMROOMHDR|L=x|sector=x|n=%d|entries=%d|payload_bytes=%d|payload_merkle=%s|w_self_adjoint=PASS|json=0\n" % (n, entries, len(payload), merkle(payload))
    return line.encode().ljust(4096, b"\0") + payload


def run(cap):
    r = subprocess.run([RECORDED, TMP, "0", str(cap)], capture_output=True, text=True)
    last = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")][-1]
    return r.returncode, dict(x.split("=", 1) for x in last.split("|") if "=" in x), r.stdout


def rdr():
    r = subprocess.run([READER, TMP] + KEYS, capture_output=True, text=True)
    last = [x for x in r.stdout.splitlines() if x.startswith("REVIEW_READER|")][-1]
    return r.returncode, dict(x.split("=", 1) for x in last.split("|") if "=" in x)


t0 = time.time()
# Row starts with no prefix, to solve for the prefix that puts a hub where we want it.
_, s0, _, _, _, hubs0 = build(0, 0, False)
for name, target, split in [("header_then_boundary", 8, True), ("starts_at_boundary", 0, False), ("spans_boundary", 262144, False)]:
    extra = 24 if split else 0
    choice = None
    for hub in reversed(hubs0):
        S = s0[hub] + extra
        d = BOUND - target - S
        if d < 0 or d % 16:
            continue
        u = d // 16
        for b in range(3):
            if u - 10 * b >= 0 and (u - 10 * b) % 3 == 0:
                choice = (hub, (u - 10 * b) // 3, b)
                break
        if choice:
            break
    if not choice:
        emit("STARS2_NO_POSITION|case=%s|json=0" % name)
        bad += 1
        continue
    _, a, b = choice
    pl, starts, n, entries, pairs, hubs = build(a, b, split)
    i = bisect.bisect_right(starts, BOUND - target) - 1
    s = starts[i]
    cnt = struct.unpack_from("<H", pl, s + 6)[0]
    placed = s + target == BOUND and cnt == 65535
    with open(TMP, "wb") as o:
        o.write(wrap(pl, n, entries))
    code, f, _ = run(470000000)
    ok_clean = code == 0 and f.get("verdict") == "PASS" and int(f["pairs"]) == pairs
    code2, f2, _ = run(1000000)
    ok_clean = ok_clean and code2 == 0 and int(f2["pairs"]) == pairs
    rc, rf = rdr()
    ok_reader = rf.get("fingerprint_equal") == "1" and rf.get("keyed_sum61") == "0" and rf.get("upper") == str(pairs)
    # A changed value in the row's entry just past the boundary, or its first entry when the row starts there.
    q = max(s + 8, BOUND)
    idx = (q - s - 8) // 8
    j, z = struct.unpack_from("<Ii", pl, s + 8 + 8 * idx)
    if j == i:
        idx += 1
        j, z = struct.unpack_from("<Ii", pl, s + 8 + 8 * idx)
    dq = None
    for t in range(cnt):
        jj, zz = struct.unpack_from("<Ii", pl, s + 8 + 8 * t)
        if jj == i:
            dq = (s + 8 + 8 * t, zz)
            break
    m = bytearray(pl)
    struct.pack_into("<Ii", m, s + 8 + 8 * idx, j, z - 1)
    struct.pack_into("<Ii", m, dq[0], i, dq[1] + 1)
    with open(TMP, "wb") as o:
        o.write(wrap(bytes(m), n, entries))
    code3, f3, out3 = run(470000000)
    lo, hi = min(i, j), max(i, j)
    ok_fault = code3 == 2 and f3.get("value_mismatch") == "1" and f3.get("row_sum_nonzero") == "0" and ("|i=%d|h=%d|" % (lo, hi)) in out3
    rc, rf = rdr()
    ok_fault_reader = rf.get("fingerprint_equal") == "0" and rf.get("keyed_sum61") != "0"
    good = placed and ok_clean and ok_reader and ok_fault and ok_fault_reader
    bad += 0 if good else 1
    emit("STARS2|case=%s|prefix_2cliques=%d|prefix_4cliques=%d|split_pair=%d|row=%d|row_count=%d|row_start=%d|placed=%d|clean_tool=%d|clean_reader_lanes=%d|fault_tool=%d|fault_reader_lanes=%d|pairs=%d|secs=%d|json=0" % (name, a, b, int(split), i, cnt, s, int(placed), ok_clean, ok_reader, ok_fault, ok_fault_reader, pairs, time.time() - t0))
if os.path.exists(TMP):
    os.remove(TMP)
emit("STARS2_DONE|failed=%d|secs=%d|json=0" % (bad, time.time() - t0))
log.close()
sys.exit(1 if bad else 0)
