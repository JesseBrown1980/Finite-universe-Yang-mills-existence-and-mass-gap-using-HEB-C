# Integer copy of native/ym/results/3x4_stream/perron/allpairs/failclosed/review-opus55/attack/reader_controls.py, written by native/scripts/make_integer_pairs.py: 0 divisions moved to qdiv and 2 text pairs. The original stays as evidence.
# Controls for this seat's reader, before its one pass over the 3x4 store, and the n-prefix sweep on allpairs.
# 1. Each off-diagonal entry of 2x2 in turn: value-1 with diagonal+1, merkle repaired. Both fingerprints must report it.
# 2. Each row of 2x2: weight+1. A moved column on sampled rows. A symmetric change passes the pair lanes by design.
# 3. Sampled faults on 2x3 and 3x3, including columns on either side of a window boundary.
# 4. Reader windows against allpairs' ALLPAIRS_PASS rows at several caps.
# 5. n lowered to every k < n on 2x2 and 2x3, with entries= and nl= removed so no count gate can stop it: allpairs must fail each.
# usage: reader_controls.py OUT_HBP   Integer only, json=0.
import hashlib, os, re, struct, subprocess, sys, time

ROOT = "C:/tmp/opus55/allpairs-review-20261103"
RECORDED = "D:/ym-3x4-room-run/p0-ball/allpairs/allpairs.exe"
READER = ROOT + "/bin/review-reader.exe"
TMP = ROOT + "/attack/stores/control.bin"
RD = "D:/ym-3x4-room-run/p0-ball/"
KEYS = ["--r", "%x" % int.from_bytes(os.urandom(15), "big"), "--k0", os.urandom(8).hex(), "--k1", os.urandom(8).hex()]
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


class Store:
    def __init__(self, path):
        self.b = bytearray(open(path, "rb").read())
        eol = self.b.index(b"\n")
        self.line = self.b[:eol].decode()
        self.f = dict(x.split("=", 1) for x in self.line.split("|") if "=" in x)
        self.n = int(self.f["n"])
        self.payload = int(self.f["payload_bytes"])
        self.rows = []
        p = 4096
        for h in range(self.n):
            w, mag, cnt = struct.unpack_from("<IHH", self.b, p)
            self.rows.append((p, w, cnt))
            p += 8 + 8 * cnt

    def ents(self, h):
        p, _, cnt = self.rows[h]
        return [struct.unpack_from("<Ii", self.b, p + 8 + 8 * k) + (p + 8 + 8 * k,) for k in range(cnt)]

    def fault(self, edits):
        """edits: (pos, packed bytes). Writes a copy with the merkle repaired."""
        c = bytearray(self.b)
        for pos, data in edits:
            c[pos:pos + len(data)] = data
        new = self.line.replace("payload_merkle=" + self.f["payload_merkle"], "payload_merkle=" + merkle(bytes(c[4096:4096 + self.payload])))
        c[:len(new)] = new.encode()
        with open(TMP, "wb") as o:
            o.write(c)


def reader(cap=470000000):
    r = subprocess.run([READER, TMP] + KEYS + ["--cap", str(cap)], capture_output=True, text=True)
    last = [x for x in r.stdout.splitlines() if x.startswith("REVIEW_READER|")][-1]
    return r.returncode, dict(x.split("=", 1) for x in last.split("|") if "=" in x), r.stdout


def lanes_report(f):
    return f["fingerprint_equal"] == "0" and f["keyed_sum61"] != "0" and int(f["buckets_nonzero"]) >= 1


t0 = time.monotonic_ns()
s = Store(RD + "small/2x2/dev.bin")
# 1.
ran = ok = 0
for h in range(s.n):
    e = s.ents(h)
    dia = next(x for x in e if x[0] == h)
    for x in e:
        if x[0] == h:
            continue
        s.fault([(x[2], struct.pack("<Ii", x[0], x[1] - 1)), (dia[2], struct.pack("<Ii", h, dia[1] + 1))])
        code, f, _ = reader()
        ran += 1
        good = code == 2 and lanes_report(f) and f["row_sum_nonzero"] == "0" and f["verdict"] == "FAIL"
        ok += good
        if not good:
            emit("READER_CONTROL_BAD|L=2x2|fault=value|h=%d|j=%d|json=0" % (h, x[0]))
emit("READER_CONTROL|L=2x2|fault=value_minus_1_row_sum_kept_each_off_diagonal_entry|runs=%d|reported_by_both_lanes=%d|secs=%d|json=0" % (ran, ok, (time.monotonic_ns() - t0) // 10**9))
bad += ran - ok
# 2.
ran = ok = 0
for h in range(s.n):
    p, w, cnt = s.rows[h]
    s.fault([(p, struct.pack("<I", w + 1))])
    code, f, _ = reader()
    ran += 1
    good = code == 2 and lanes_report(f) and f["verdict"] == "FAIL"
    ok += good
    if not good:
        emit("READER_CONTROL_BAD|L=2x2|fault=weight|h=%d|json=0" % h)
emit("READER_CONTROL|L=2x2|fault=weight_plus_1_each_row|runs=%d|reported_by_both_lanes=%d|json=0" % (ran, ok))
bad += ran - ok
# A moved column, and the symmetric change that the pair lanes pass by design.
ran = ok = 0
for h in range(0, s.n, 3):
    e = s.ents(h)
    cols = {x[0] for x in e}
    x = next((y for y in e if y[0] != h and y[0] + 1 < s.n and y[0] + 1 not in cols), None)
    if x is None:
        continue
    s.fault([(x[2], struct.pack("<Ii", x[0] + 1, x[1]))])
    code, f, _ = reader()
    ran += 1
    good = code == 2 and lanes_report(f)
    ok += good
emit("READER_CONTROL|L=2x2|fault=moved_column|runs=%d|reported_by_both_lanes=%d|json=0" % (ran, ok))
bad += ran - ok
ran = ok = 0
for h in range(1, s.n, 3):
    e = s.ents(h)
    x = next(y for y in e if y[0] < h)
    j = x[0]
    wa, wb = s.rows[h][1], s.rows[j][1]
    g = __import__("math").gcd(wa, wb)
    a, c = wb // g, wa // g
    rev = next(y for y in s.ents(j) if y[0] == h)
    dh = next(y for y in e if y[0] == h)
    dj = next(y for y in s.ents(j) if y[0] == j)
    s.fault([(x[2], struct.pack("<Ii", j, x[1] - a)), (dh[2], struct.pack("<Ii", h, dh[1] + a)), (rev[2], struct.pack("<Ii", h, rev[1] - c)), (dj[2], struct.pack("<Ii", j, dj[1] + c))])
    code, f, _ = reader()
    ran += 1
    good = code == 0 and f["fingerprint_equal"] == "1" and f["keyed_sum61"] == "0" and f["verdict"] == "PASS"
    ok += good
emit("READER_CONTROL|L=2x2|fault=symmetric_change_keeps_equality_passes_by_design|runs=%d|passed_as_predicted=%d|json=0" % (ran, ok))
bad += ran - ok

# 3. and 4. Boundaries of the windows on 2x3 and 3x3.
for name, path, cap in [("2x3", RD + "small/2x3/dev.bin", 1000), ("3x3", RD + "c33/dev33.bin", 1000000)]:
    s = Store(path)
    with open(TMP, "wb") as o:
        o.write(s.b)
    r = subprocess.run([RECORDED, TMP, "0", str(cap)], capture_output=True, text=True)
    tool = [dict(x.split("=", 1) for x in ln.split("|") if "=" in x) for ln in r.stdout.splitlines() if ln.startswith("ALLPAIRS_PASS|")]
    code, f, out = reader(cap)
    rw = [dict(x.split("=", 1) for x in ln.split("|") if "=" in x) for ln in out.splitlines() if ln.startswith("REVIEW_WINDOW|")]
    same = len(tool) == len(rw) and all(a["rows_from"] == b["rows_from"] and a["rows_to"] == b["rows_to"] and a["upper_stored"] == b["upper_stored"] and a["lookups"] == b["lower_into_window"] for a, b in zip(tool, rw))
    emit("READER_WINDOWS_AGAINST_TOOL|L=%s|cap=%d|tool_passes=%d|reader_windows=%d|all_equal=%d|json=0" % (name, cap, len(tool), len(rw), same))
    bad += 0 if same else 1
    # A fault on the last row of each window and on the first row of the next, on both sides of a pair, at this cap.
    bounds = [int(w["rows_to"]) for w in tool][:-1]
    if name == "2x3":
        bounds = bounds[:6]
    ran = ok = tool_ok = 0
    for B in bounds:
        for h in (B - 1, B):
            e = s.ents(h)
            dia = next(x for x in e if x[0] == h)
            for x in (next((y for y in e if y[0] > h), None), next((y for y in e if y[0] < h), None)):
                if x is None:
                    continue
                s.fault([(x[2], struct.pack("<Ii", x[0], x[1] - 1)), (dia[2], struct.pack("<Ii", h, dia[1] + 1))])
                code, f, _ = reader(cap)
                ran += 1
                ok += int(code == 2 and lanes_report(f))
                rr = subprocess.run([RECORDED, TMP, "0", str(cap)], capture_output=True, text=True)
                last = [ln for ln in rr.stdout.splitlines() if ln.startswith("ALLPAIRS|")][-1]
                g = dict(y.split("=", 1) for y in last.split("|") if "=" in y)
                lo, hi = min(h, x[0]), max(h, x[0])
                named = ("|i=%d|h=%d|" % (lo, hi)) in rr.stdout
                tool_ok += int(rr.returncode == 2 and g["value_mismatch"] == "1" and g["row_sum_nonzero"] == "0" and named)
    emit("WINDOW_BOUNDARY_FAULTS|L=%s|cap=%d|boundaries=%d|faults=%d|reader_reported=%d|allpairs_reported_one_mismatch_named=%d|json=0" % (name, cap, len(bounds), ran, ok, tool_ok))
    bad += (ran - ok) + (ran - tool_ok)

# 5. n lowered, every prefix, no count gate left to stop it.
for name, path in [("2x2", RD + "small/2x2/dev.bin"), ("2x3", RD + "small/2x3/dev.bin")]:
    s = Store(path)
    fields = [x for x in s.line.split("|") if not x.startswith("entries=") and not x.startswith("nl=")]
    passes = []
    oor_zero = 0
    for k in range(1, s.n):
        line = "|".join(("n=%d" % k) if x.startswith("n=") else x for x in fields)
        c = bytearray(s.b)
        c[:4096] = (line + "\n").encode().ljust(4096, b"\0")
        with open(TMP, "wb") as o:
            o.write(c)
        r = subprocess.run([RECORDED, TMP, "0"], capture_output=True, text=True)
        last = [ln for ln in r.stdout.splitlines() if ln.startswith("ALLPAIRS|")][-1]
        if r.returncode == 0:
            passes.append(k)
        if "column_out_of_range=0|" in last:
            oor_zero += 1
    emit("N_PREFIX_SWEEP|L=%s|n=%d|k_tried=%d|k_that_pass=%d|first=%s|k_with_no_out_of_range_column=%d|json=0" % (name, s.n, s.n - 1, len(passes), passes[:5], oor_zero))
    bad += len(passes)
if os.path.exists(TMP):
    os.remove(TMP)
emit("READER_CONTROLS_DONE|failed=%d|keys=%s|secs=%d|json=0" % (bad, " ".join(KEYS), (time.monotonic_ns() - t0) // 10**9))
log.close()
sys.exit(1 if bad else 0)
