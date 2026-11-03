# Stores of chosen shape for the hardened allpairs: the row cap on windows, the walk over equal columns, peak memory against the source header's formula.
# Stores stay under hard/tmp and are deleted after each case. Each store's expected values are written here, and REVIEW.hbp holds this file's hash before it runs.
# usage: shapes.py rowcap EXE OLD_EXE OUT | quadratic EXE OUT | memory EXE OUT   Integer only, json=0.
import hashlib, os, struct, subprocess, sys, time

R = "C:/tmp/opus55/allpairs-review-20261103/"
TMP = R + "hard/tmp/s"
os.makedirs(TMP, exist_ok=True)
MIB = 1 << 20
LEAF = 16 * MIB
BN = subprocess.BELOW_NORMAL_PRIORITY_CLASS


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write_store(path, chunks, n, rooms=None, entries=None):
    """chunks: bytes of the rows, in pieces. Pads with zeros so the stream is a multiple of 1 MiB. rooms, when given, overrides what the rows hold."""
    count_rooms = 0
    with open(path, "wb") as o:
        o.write(b"\0" * 4096)
        leaves, buf, total = [], bytearray(), 0
        for c in chunks:
            o.write(c)
            total += len(c)
            buf += c
            while len(buf) >= LEAF:
                leaves.append(sha(bytes(buf[:LEAF])))
                del buf[:LEAF]
        return_total = total
        pad = (MIB - (total + 4096) % MIB) % MIB
        o.write(b"\0" * pad)
        total += pad
        buf += b"\0" * pad
        while len(buf) >= LEAF:
            leaves.append(sha(bytes(buf[:LEAF])))
            del buf[:LEAF]
        if buf:
            leaves.append(sha(bytes(buf)))
        merkle = sha("".join(leaves).encode())
        room_count = return_total // 8 if rooms is None else rooms
        line = "YMROOMHDR|L=1x40|sector=x|n=%d|rooms=%d|entries=%d|payload_bytes=%d|stream_bytes=%d|chunk=16MiB|payload_merkle=%s|keys_sha256=0|w_self_adjoint=PASS|json=0" % (n, room_count, entries if entries is not None else room_count - n, total, total + 4096, merkle)
        o.seek(0)
        o.write(line.encode() + b"\n")
    return total


def run(exe, path, cap=None):
    t0 = time.perf_counter_ns()
    r = subprocess.run([exe, path, "0"] + ([str(cap)] if cap is not None else []), capture_output=True, text=True, creationflags=BN)
    ms = (time.perf_counter_ns() - t0) // 1000000
    rows = r.stdout.splitlines()
    last = ([x for x in rows if x.startswith("ALLPAIRS|")] or [""])[-1]
    f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
    passes = [dict(x.split("=", 1) for x in p.split("|") if "=" in x) for p in rows if p.startswith("ALLPAIRS_PASS|")]
    return r.returncode, f, passes, ms


def rule_windows(uppers, cap):
    """The rule in the brief, written from its words, with no code of the tool's: a window closes before a row that would take it past cap upper entries or max(cap, 2^20) rows, unless the row is its first."""
    row_cap = max(min(max(cap, 1), 4000000000), MIB)
    cap = min(max(cap, 1), 4000000000)
    out, start, ent, rows = [], 0, 0, 0
    for h, c in enumerate(uppers):
        if h > start and (ent + c > cap or rows >= row_cap):
            out.append((start, h))
            start, ent, rows = h, 0, 0
        ent += c
        rows += 1
    out.append((start, len(uppers)))
    return out


def rowcap(exe, old, out):
    log = open(out, "w", encoding="utf-8", newline="\n")
    n = MIB + 6
    bad = 0
    blocks = bytearray()
    for k in range(n // 2):
        a, b = 2 * k, 2 * k + 1
        blocks += struct.pack("<IHHIiIi", 1, 3, 2, a, 1, b, -1) + struct.pack("<IHHIiIi", 1, 3, 2, a, -1, b, 1)
    path = TMP + "/rc-blocks.bin"
    write_store(path, [bytes(blocks)], n, entries=2 * n)
    uppers = [1 - h % 2 for h in range(n)]
    for cap in (1000000, MIB + 1, MIB - 1, 2000000, 524291, 524290):
        want = rule_windows(uppers, cap)
        code, f, ps, ms = run(exe, path, cap)
        got = [(int(p["rows_from"]), int(p["rows_to"])) for p in ps]
        ok = got == want and code == 2 and f.get("value_mismatch") == "0" and f.get("lower_without_upper") == "0" and f.get("upper_without_lower") == "0" and f.get("lower_repeated") == "0" and f.get("pairs") == str(n // 2) and sum(int(p["found"]) for p in ps) == n // 2 and f.get("store_identity") == "OPEN"
        bad += 0 if ok else 1
        log.write("ROWCAP|store=two_row_blocks|n=%d|cap=%d|want_windows=%s|got_windows=%s|exit=%d|met=%d|json=0\n" % (n, cap, str(want).replace(" ", ""), str(got).replace(" ", ""), code, int(ok)))
        log.flush()
    os.remove(path)
    # Rows of no entries: only the row cap can close a window, at any cap.
    path = TMP + "/rc-rows.bin"
    write_store(path, [struct.pack("<IHH", 1, 3, 0) * n], n, entries=0)
    uppers = [0] * n
    for cap in (1, 1000, MIB):
        want = rule_windows(uppers, cap)
        code, f, ps, ms = run(exe, path, cap)
        got = [(int(p["rows_from"]), int(p["rows_to"])) for p in ps]
        ok = got == want and code == 2 and f.get("missing_diag") == str(n) and len(got) == 2
        bad += 0 if ok else 1
        log.write("ROWCAP|store=rows_of_no_entries|n=%d|cap=%d|want_windows=%s|got_windows=%s|exit=%d|met=%d|json=0\n" % (n, cap, str(want).replace(" ", ""), str(got).replace(" ", ""), code, int(ok)))
        log.flush()
    # Control: the executable from before the cap, on the same store, must show one window, so this test can tell them apart.
    code, f, ps, ms = run(old, path, 1000)
    got = [(int(p["rows_from"]), int(p["rows_to"])) for p in ps]
    ok = got == [(0, n)]
    bad += 0 if ok else 1
    log.write("ROWCAP_CONTROL|exe=before_the_row_cap|cap=1000|got_windows=%s|one_window=%d|met=%d|json=0\n" % (str(got).replace(" ", ""), int(got == [(0, n)]), int(ok)))
    os.remove(path)
    log.write("ROWCAP_DONE|not_met=%d|json=0\n" % bad)
    log.close()
    print("ROWCAP_DONE|not_met=%d|json=0" % bad)
    return bad


def pair_rows(a, b, k):
    ra = struct.pack("<IHH", 1, 3, k + 1) + struct.pack("<Ii", a, k) + struct.pack("<Ii", b, -1) * k
    rb = struct.pack("<IHH", 1, 3, k + 1) + struct.pack("<Ii", a, -1) * k + struct.pack("<Ii", b, k)
    return ra + rb


def quadratic(exe, out):
    log = open(out, "w", encoding="utf-8", newline="\n")
    bad = 0
    times = {}
    for k, pairs in ((4096, 1), (16384, 1), (32768, 1), (65534, 1), (65534, 8)):
        path = TMP + "/q.bin"
        data = [pair_rows(2 * p, 2 * p + 1, k) for p in range(pairs)]
        n = 2 * pairs
        write_store(path, data, n, entries=2 * pairs * (k + 1))
        code, f, ps, ms = run(exe, path)
        ok = code == 2 and f.get("value_mismatch") == "0" and f.get("lower_without_upper") == "0" and f.get("upper_without_lower") == "0" and f.get("lower_repeated") == "0" and f.get("columns_not_ascending") == str(2 * pairs * (k - 1)) and f.get("pairs") == str(pairs * k)
        bad += 0 if ok else 1
        times[(k, pairs)] = ms
        log.write("QUADRATIC|k=%d|pairs=%d|store_bytes=%d|ms=%d|exit=%d|columns_not_ascending=%s|value_mismatch=%s|lower_repeated=%s|upper_without_lower=%s|met=%d|json=0\n" % (k, pairs, os.path.getsize(path), ms, code, f.get("columns_not_ascending", "-"), f.get("value_mismatch", "-"), f.get("lower_repeated", "-"), f.get("upper_without_lower", "-"), int(ok)))
        log.flush()
        os.remove(path)
    # The same bytes per row, with every column different: one star row and its partners.
    k = 65534
    star = struct.pack("<IHH", 1, 3, k + 1) + struct.pack("<Ii", 0, k) + b"".join(struct.pack("<Ii", j, -1) for j in range(1, k + 1))
    rest = b"".join(struct.pack("<IHH", 1, 3, 2) + struct.pack("<IiIi", 0, -1, j, 1) for j in range(1, k + 1))
    path = TMP + "/q.bin"
    write_store(path, [star, rest], k + 1, entries=(k + 1) + 2 * k)
    code, f, ps, ms = run(exe, path)
    log.write("QUADRATIC_BASE|k=%d|distinct_columns=1|ms=%d|exit=%d|columns_not_ascending=%s|json=0\n" % (k, ms, code, f.get("columns_not_ascending", "-")))
    os.remove(path)
    a, b, c = times[(16384, 1)], times[(65534, 1)], times[(65534, 8)]
    log.write("QUADRATIC_RATIO|k_65534_over_k_16384_x100=%d|pairs_8_over_pairs_1_x100=%d|largest_row_pair_ms=%d|rows_per_pair_bytes=%d|json=0\n" % (100 * b // max(a, 1), 100 * c // max(b, 1), b, 2 * (8 + 8 * 65535)))
    log.write("QUADRATIC_DONE|not_met=%d|json=0\n" % bad)
    log.close()
    print("QUADRATIC_DONE|not_met=%d|ms_k65534=%d|json=0" % (bad, b))
    return bad


def probe(exe, path, cap, name, formula, log):
    out = R + "hard/tmp/s/" + name + ".out"
    arg = '"%s" 0' % path + ("" if cap is None else " %d" % cap)
    r = subprocess.run(["pwsh", "-NoProfile", "-File", R + "attack/mem_probe.ps1", "-Exe", exe, "-ArgLine", arg, "-Out", out], capture_output=True, text=True)
    row = [x for x in r.stdout.splitlines() if x.startswith("MEM_PROBE|")]
    f = dict(x.split("=", 1) for x in row[-1].split("|") if "=" in x) if row else {}
    o = open(out, encoding="utf-8").read().splitlines()
    last = ([x for x in o if x.startswith("ALLPAIRS|")] or [""])[-1]
    g = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
    ws, priv = int(f.get("peak_working_set_bytes", -1)), int(f.get("peak_private_bytes_sampled", -1))
    log.write("MEM_SHAPE|store=%s|cap=%s|exit=%s|passes=%s|peak_working_set_mib=%d|peak_private_sampled_mib=%d|header_formula_mib=%d|ws_over_formula_x100=%d|padding=%s|padding_bytes=%s|rows_read=%s|json=0\n" % (name, cap if cap is not None else "default", f.get("exit", "-"), g.get("passes", "-"), ws // MIB, priv // MIB, formula // MIB, 100 * ws // max(formula, 1), g.get("padding", "-"), g.get("padding_bytes", "-"), g.get("rows_read", "-")))
    log.flush()
    os.remove(out)
    if os.path.exists(out + ".err"):
        os.remove(out + ".err")
    return ws


def memory(exe, out):
    log = open(out, "w", encoding="utf-8", newline="\n")
    buffers = 4 * 64 * MIB
    # 1. A header whose rooms= claims the whole payload, over two rows and 2 GiB of zeros. check_sizes passes it; the pass reads the padding.
    path = TMP + "/m1.bin"
    two = struct.pack("<IHHIiIi", 1, 3, 2, 0, 1, 1, -1) + struct.pack("<IHHIiIi", 1, 3, 2, 0, -1, 1, 1)
    write_store(path, [two, bytes(64 * MIB - 48 - 4096)] + [bytes(64 * MIB)] * 31, 2, rooms=(2048 * MIB - 4096) // 8, entries=4)
    probe(exe, path, None, "rooms_claim_2GiB_of_zeros", 8 * 1 + 1 + 8 * 2 + buffers, log)
    os.remove(path)
    log.write("MEM_SHAPES_DONE|buffers_counted_mib=%d|json=0\n" % (buffers // MIB))
    log.close()
    print(open(out, encoding="utf-8").read())
    return 0


mode = sys.argv[1]
if mode == "rowcap":
    sys.exit(1 if rowcap(sys.argv[2], sys.argv[3], sys.argv[4]) else 0)
if mode == "quadratic":
    sys.exit(1 if quadratic(sys.argv[2], sys.argv[3]) else 0)
if mode == "memory":
    sys.exit(memory(sys.argv[2], sys.argv[3]))
