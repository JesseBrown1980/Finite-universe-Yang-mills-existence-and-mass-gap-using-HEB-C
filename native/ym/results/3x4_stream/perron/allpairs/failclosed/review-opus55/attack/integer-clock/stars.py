# Integer copy of native/ym/results/3x4_stream/perron/allpairs/failclosed/review-opus55/attack/stars.py, written by native/scripts/make_integer_pairs.py: 0 divisions moved to qdiv and 2 text pairs. The original stays as evidence.
# Large rows across the tool's 64 MiB chunks and 16 MiB leaves, on a store this script builds. Rows with the largest count a u16 can hold.
# 128 hub rows of 65,535 entries each, and 65,534 leaf rows of 129 entries, shuffled through the index range. W = 1. Every pair exact.
# Variants shift the rows by small closed blocks at the front, so the chunk boundary lands at a different place in a row each time.
# Each variant: the clean store must pass, and one changed value in the row at the 64 MiB boundary must give one mismatch, named.
# usage: stars.py OUT_HBP [VARIANTS]   Integer only, json=0.
import hashlib, os, struct, subprocess, sys, time

ROOT = "C:/tmp/opus55/allpairs-review-20261103"
RECORDED = "D:/ym-3x4-room-run/p0-ball/allpairs/allpairs.exe"
READER = ROOT + "/bin/review-reader.exe"
TMP = ROOT + "/attack/stores/stars.bin"
KEYS = ["--r", "%x" % int.from_bytes(os.urandom(15), "big"), "--k0", os.urandom(8).hex(), "--k1", os.urandom(8).hex()]
VARIANTS = int(sys.argv[2]) if len(sys.argv) > 2 else 24
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


def build(k):
    """k closed 2-row blocks first, then the hubs and leaves. Returns payload, row starts, n, entries, pairs."""
    parts = []
    starts = []
    pos = 0
    blocks = []
    for b in range(k):
        a = 2 * b
        for h, other in ((a, a + 1), (a + 1, a)):
            cols = sorted([(h, 1), (other, -1)])
            r = struct.pack("<IHH", 1, 3, 2) + b"".join(struct.pack("<Ii", j, z) for j, z in cols)
            parts.append(r)
            starts.append(pos)
            pos += len(r)
    base = 2 * k
    N = 65534 + 128
    hubs = sorted(base + 512 * i + 7 for i in range(128))
    hubset = set(hubs)
    leaves = [base + i for i in range(N) if base + i not in hubset]
    neg = {}
    for j in hubs + leaves:
        neg[j] = struct.pack("<Ii", j, -1)
    for h in range(base, base + N):
        if h in hubset:
            d = struct.pack("<Ii", h, 65534)
            r = struct.pack("<IHH", 1, 3, 65535) + b"".join(neg[j] if j != h else d for j in sorted(leaves + [h]))
        else:
            d = struct.pack("<Ii", h, 128)
            r = struct.pack("<IHH", 1, 3, 129) + b"".join(neg[j] if j != h else d for j in sorted(hubs + [h]))
        parts.append(r)
        starts.append(pos)
        pos += len(r)
    return b"".join(parts), starts, 2 * k + N, 4 * k + 128 * 65535 + 65534 * 129, k + 128 * 65534


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


kinds = {"inside_entries": 0, "right_after_row_header": 0, "between_rows": 0}
t0 = time.monotonic_ns()
caps_clean = [1000000, 470000000]
for v in range(VARIANTS):
    k = 11 * v
    pl, starts, n, entries, pairs = build(k)
    # The row that holds the 64 MiB boundary.
    import bisect

    i = bisect.bisect_right(starts, BOUND) - 1
    s = starts[i]
    cnt = struct.unpack_from("<H", pl, s + 6)[0]
    if s == BOUND:
        kind = "between_rows"
    elif s + 8 == BOUND:
        kind = "right_after_row_header"
    else:
        kind = "inside_entries"
    kinds[kind] += 1
    data = wrap(pl, n, entries)
    with open(TMP, "wb") as o:
        o.write(data)
    ok_clean = True
    for cap in caps_clean:
        code, f, _ = run(cap)
        if code != 0 or f.get("verdict") != "PASS" or int(f["pairs"]) != pairs or f.get("whole_space_count") != "OPEN" or f.get("header_entries") != "PASS":
            ok_clean = False
    rc, rf = rdr()
    ok_reader = rf.get("fingerprint_equal") == "1" and rf.get("keyed_sum61") == "0" and rf.get("upper") == str(pairs) and rf.get("max_cnt") == "65535"
    # One changed value at or after the boundary in that row, diagonal compensated, merkle repaired.
    q = max(s + 8, BOUND)
    if q >= s + 8 + 8 * cnt:
        q = s + 8
    # Off-diagonal entry at q, or the next one.
    j, z = struct.unpack_from("<Ii", pl, q)
    if j == i:
        q += 8 if q + 8 < s + 8 + 8 * cnt else -8
        j, z = struct.unpack_from("<Ii", pl, q)
    dq = None
    for t in range(cnt):
        jj, zz = struct.unpack_from("<Ii", pl, s + 8 + 8 * t)
        if jj == i:
            dq = (s + 8 + 8 * t, zz)
            break
    m = bytearray(pl)
    struct.pack_into("<Ii", m, q, j, z - 1)
    struct.pack_into("<Ii", m, dq[0], i, dq[1] + 1)
    with open(TMP, "wb") as o:
        o.write(wrap(bytes(m), n, entries))
    code, f, out = run(470000000)
    lo, hi = min(i, j), max(i, j)
    ok_fault = code == 2 and f.get("value_mismatch") == "1" and f.get("row_sum_nonzero") == "0" and ("|i=%d|h=%d|" % (lo, hi)) in out
    rc, rf = rdr()
    ok_fault_reader = rf.get("fingerprint_equal") == "0" and rf.get("keyed_sum61") != "0"
    good = ok_clean and ok_reader and ok_fault and ok_fault_reader
    bad += 0 if good else 1
    emit("STARS_VARIANT|v=%d|k_blocks=%d|n=%d|pairs=%d|payload=%d|boundary_row=%d|row_count=%d|boundary_kind=%s|clean_tool=%d|clean_reader_lanes=%d|fault_tool=%d|fault_reader_lanes=%d|secs=%d|json=0" % (v, k, n, pairs, len(pl), i, cnt, kind, ok_clean, ok_reader, ok_fault, ok_fault_reader, (time.monotonic_ns() - t0) // 10**9))
os.remove(TMP)
emit("STARS_DONE|variants=%d|kinds=%s|failed=%d|secs=%d|json=0" % (VARIANTS, str(kinds).replace(" ", ""), bad, (time.monotonic_ns() - t0) // 10**9))
log.close()
sys.exit(1 if bad else 0)
