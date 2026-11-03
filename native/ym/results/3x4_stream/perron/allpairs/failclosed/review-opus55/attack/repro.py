# Reproducers for the defects in ALLPAIRS-REVIEW.md. Needs only the public fixture and an allpairs executable. Stores go to a temporary folder beside this script.
# usage: python3 -I -X utf8 repro.py ALLPAIRS_EXE FIXTURE_2X2_GZ [OUT_DIR]
# Prints one row per case: what the review measured at source f4ea7e85 and what this executable does now. Exit 0 when every case behaves as measured at f4ea7e85.
# A fixed tool will differ on the D rows; the C rows are controls and must keep their values. Integer only, json=0.
import gzip, hashlib, math, os, re, shutil, struct, subprocess, sys, tempfile

EXE, GZ = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else tempfile.mkdtemp(prefix="repro-", dir=os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT, exist_ok=True)
base = gzip.open(GZ, "rb").read()
if hashlib.sha256(base).hexdigest() != "b31e730606db130585f9560f7adab87444d744876c3a8e36f6f9ef2bf0aa431f":
    raise SystemExit("fixture hash")
eol = base.index(b"\n")
FIELDS = [tuple(x.split("=", 1)) for x in base[:eol].decode().split("|")[1:]]
D = dict(FIELDS)
N, PAY = int(D["n"]), int(D["payload_bytes"])
P = base[4096:4096 + PAY]
ROWS, p = [], 0
for _ in range(N):
    w, mag, cnt = struct.unpack_from("<IHH", P, p)
    v = struct.unpack_from("<" + "Ii" * cnt, P, p + 8)
    ROWS.append([w, mag, [(v[2 * i], v[2 * i + 1]) for i in range(cnt)]])
    p += 8 + 8 * cnt
USED = p
bad = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def merkle(pl):
    return sha("".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20)).encode())


def ser(rows):
    out = bytearray()
    for w, mag, ent in rows:
        out += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            out += struct.pack("<Ii", j, z)
    return bytes(out).ljust(PAY, b"\0")


def clone():
    return [[w, m, list(e)] for w, m, e in ROWS]


def diag(rows, h, dz):
    e = rows[h][2]
    k = [i for i, x in enumerate(e) if x[0] == h][0]
    e[k] = (h, e[k][1] + dz)


def store(pl, repair=True, drop=(), **over):
    f = []
    for k, v in FIELDS:
        if k in drop:
            continue
        if k == "payload_merkle" and repair:
            v = merkle(pl)
        f.append((k, str(over.get(k, v))))
    return ("YMROOMHDR|" + "|".join("%s=%s" % x for x in f) + "\n").encode().ljust(4096, b"\0") + pl


def run(name, data, cap=None):
    path = os.path.join(OUT, name + ".bin")
    open(path, "wb").write(data)
    r = subprocess.run([EXE, path, "0"] + ([str(cap)] if cap is not None else []), capture_output=True, text=True)
    last = ([x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")] or [""])[-1]
    os.remove(path)
    return r.returncode, last, dict(x.split("=", 1) for x in last.split("|") if "=" in x)


def case(tag, data, want, cap=None):
    global bad
    code, last, f = run(tag, data, cap)
    miss = [k for k, v in want.items() if str(code if k == "exit" else f.get(k)) != str(v)]
    bad += 1 if miss else 0
    print("REPRO|case=%s|exit=%d|as_measured_at_f4ea7e85=%d|differs=%s|sha16=%s|line=%s|json=0" % (tag, code, int(not miss), ",".join(miss) or "-", sha(data)[:16], last.replace("|", "~")), flush=True)
    return last


h, i = next((h, j) for h in range(N) for j, _ in ROWS[h][2] if j < h)
# D1: n=0. No pass runs, so the merkle is never computed and PASS is printed anyway.
case("D1_header_only_n0", b"YMROOMHDR|n=0|payload_bytes=0|w_self_adjoint=PASS\n".ljust(4096, b"\0"), {"exit": 0, "verdict": "PASS", "merkle": "PASS", "rows_read": 0})
dam = bytearray(P)
dam[12] ^= 1
case("D1_changed_byte_unrepaired_n0", store(bytes(dam), repair=False, drop=("nl",), n=0, entries=0), {"exit": 0, "verdict": "PASS", "merkle": "PASS", "rows_read": 0})
# D2: a count gate that cannot read its field stays OPEN, and OPEN passes.
r = clone()
for x in r:
    x[0] *= 2
dbl = ser(r)
case("C2_weights_doubled_gate_can_read", store(dbl), {"exit": 2, "verdict": "FAIL", "whole_space_count": "FAIL"})
case("D2_weights_doubled_nl_removed", store(dbl, drop=("nl",)), {"exit": 0, "verdict": "PASS", "whole_space_count": "OPEN", "sum_w": 15552})
case("D2_weights_doubled_nl_wrong", store(dbl, nl=7), {"exit": 0, "verdict": "PASS", "whole_space_count": "OPEN"})
case("D2_weights_doubled_L_garbage", store(dbl, L="2y2"), {"exit": 0, "verdict": "PASS", "whole_space_count": "OPEN"})
r = clone()
a = [z for c, z in r[h][2] if c == i][0]
b = [z for c, z in r[i][2] if c == h][0]
r[h][2] = [x for x in r[h][2] if x[0] != i]
r[i][2] = [x for x in r[i][2] if x[0] != h]
diag(r, h, a)
diag(r, i, b)
gone = ser(r)
case("C2_pair_removed_gate_can_read", store(gone), {"exit": 2, "verdict": "FAIL", "header_entries": "FAIL"})
case("D2_pair_removed_entries_garbage", store(gone, entries="abc"), {"exit": 0, "verdict": "PASS", "header_entries": "OPEN", "pairs": 1197})
# D3: payload after the last row is hashed and never read.
pad = bytearray(P)
for k in range(USED, PAY):
    pad[k] = 0xFF
case("D3_padding_nonzero", store(bytes(pad)), {"exit": 0, "verdict": "PASS", "rows_read": N})
hid = bytearray(P)
row = struct.pack("<IHH", 7, 3, 2) + struct.pack("<IiIi", 0, -5, N, 5)
hid[USED:USED + len(row)] = row
case("D3_bad_row_after_the_last", store(bytes(hid)), {"exit": 0, "verdict": "PASS", "rows_read": N})
# D5: the printed cap is the argument, the window uses the clamped value.
case("D5_cap_zero_label", store(P), {"exit": 0, "cap_entries": 0, "passes": 188}, cap=0)
case("C5_cap_one", store(P), {"exit": 0, "cap_entries": 1, "passes": 188}, cap=1)
case("D5_cap_max_label", store(P), {"exit": 0, "cap_entries": 18446744073709551615, "passes": 1}, cap=18446744073709551615)
# D6: two stores, one line. The output never names the merkle it checked.
r = clone()
g = math.gcd(r[h][0], r[i][0])
da, db = r[i][0] // g, r[h][0] // g
for rw, col, d in ((h, i, da), (i, h, db)):
    k = [q for q, x in enumerate(r[rw][2]) if x[0] == col][0]
    r[rw][2][k] = (col, r[rw][2][k][1] - d)
    diag(r, rw, d)
la = case("D6_clean", store(P), {"exit": 0, "verdict": "PASS"})
lb = case("D6_one_pair_changed_both_sides", store(ser(r)), {"exit": 0, "verdict": "PASS"})
strip = lambda s: re.sub(r"\|secs=\d+", "", s)
same = int(strip(la) == strip(lb))
bad += 0 if same else 1
print("REPRO|case=D6_lines_identical_after_removing_secs|identical=%d|json=0" % same, flush=True)
w4 = 13060694016 // 4
four = [[w4, 3, [(0, 2), (1, -1), (3, -1)]], [w4, 3, [(0, -1), (1, 2), (2, -1)]], [w4, 3, [(1, -1), (2, 2), (3, -1)]], [w4, 3, [(0, -1), (2, -1), (3, 2)]]]
fp = b"".join(struct.pack("<IHH", w_, m_, len(e_)) + b"".join(struct.pack("<Ii", j_, z_) for j_, z_ in e_) for w_, m_, e_ in four)
fl = "YMROOMHDR|L=3x4|sector=Sx+Sy+|n=4|nl=24|rooms=16|entries=12|payload_bytes=%d|payload_merkle=%s|w_self_adjoint=PASS|json=0\n" % (len(fp), merkle(fp))
case("D6_four_row_store_labelled_3x4", fl.encode().ljust(4096, b"\0") + fp, {"exit": 0, "verdict": "PASS", "L": "3x4", "n": 4, "pairs": 4, "sum_w": 13060694016, "whole_space_count": "PASS", "header_entries": "PASS", "merkle": "PASS"})
# D7: a doubled lower entry makes found equal stored while another upper entry has no partner. Only the column gate reports it.
m = [c for c, _ in ROWS[i][2] if c > i and c != h][0]
r = clone()
z = [x for x in r[h][2] if x[0] == i][0]
r[h][2].insert(r[h][2].index(z), z)
diag(r, h, -z[1])
zm = [x for x in r[m][2] if x[0] == i][0]
r[m][2].remove(zm)
diag(r, m, zm[1])
case("D7_counters_read_0_on_an_unpaired_entry", store(ser(r)), {"exit": 2, "verdict": "FAIL", "columns_not_ascending": 1, "upper_without_lower": 0, "lower_without_upper": 0, "value_mismatch": 0})
# D8: the header block is under no hash.
case("D8_sector_label_changed", store(P, sector="NOT-THIS-SECTOR"), {"exit": 0, "verdict": "PASS", "sector": "NOT-THIS-SECTOR"})
case("D8_rooms_and_stream_bytes_wrong", store(P, rooms=1, stream_bytes=1), {"exit": 0, "verdict": "PASS"})
# Controls that must keep their values after any fix.
case("C_clean", store(P), {"exit": 0, "verdict": "PASS", "pairs": 1198, "header_entries": "PASS", "whole_space_count": "PASS"})
one = bytearray(P)
one[12] ^= 1
case("C_changed_byte_unrepaired", store(bytes(one), repair=False), {"exit": 1, "verdict": "FAIL"})
if not sys.argv[3:]:
    shutil.rmtree(OUT, ignore_errors=True)
print("REPRO_DONE|cases_differing_from_f4ea7e85=%d|json=0" % bad)
sys.exit(1 if bad else 0)
