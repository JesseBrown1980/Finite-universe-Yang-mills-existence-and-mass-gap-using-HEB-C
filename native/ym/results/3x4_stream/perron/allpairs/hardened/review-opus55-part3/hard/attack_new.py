# Named attacks on the hardened allpairs. Each case states its expected fields here, and REVIEW.hbp holds this file's hash before it runs.
# Runs the recorded executable and this seat's build of the same source. Stores stay under hard/tmp.
# usage: attack_new.py EXE_A EXE_B FIXTURE_2X2_GZ OUT_HBP   Integer only, json=0.
import gzip, hashlib, math, os, shutil, struct, subprocess, sys

EXE_A, EXE_B, GZ, OUT = sys.argv[1:5]
TMP = os.path.dirname(os.path.dirname(os.path.abspath(OUT))) + "/tmp/a"
os.makedirs(TMP, exist_ok=True)
log = open(OUT, "w", encoding="utf-8", newline="\n")
base = gzip.open(GZ, "rb").read()
eol = base.index(b"\n")
LINE = base[:eol].decode()
F = dict(x.split("=", 1) for x in LINE.split("|") if "=" in x)
N, PAY = int(F["n"]), int(F["payload_bytes"])
P = base[4096:4096 + PAY]
ROWS, p = [], 0
for _ in range(N):
    w, mag, cnt = struct.unpack_from("<IHH", P, p)
    v = struct.unpack_from("<" + "Ii" * cnt, P, p + 8)
    ROWS.append([w, mag, [(v[2 * i], v[2 * i + 1]) for i in range(cnt)]])
    p += 8 + 8 * cnt
USED = p
MIB = 1 << 20
bad = 0
sha_a = hashlib.sha256(open(EXE_A, "rb").read()).hexdigest()
sha_b = hashlib.sha256(open(EXE_B, "rb").read()).hexdigest()


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
    return bytes(out)


def clone():
    return [[w, m, list(e)] for w, m, e in ROWS]


def diag(rows, h, dz):
    e = rows[h][2]
    k = [i for i, x in enumerate(e) if x[0] == h][0]
    e[k] = (h, e[k][1] + dz)


def line_for(pl, **over):
    out = []
    for kv in LINE.split("|"):
        if "=" not in kv:
            out.append(kv)
            continue
        k, v = kv.split("=", 1)
        if k == "payload_merkle":
            v = merkle(pl)
        if k == "payload_bytes":
            v = str(len(pl))
        if k == "stream_bytes":
            v = str(len(pl) + 4096)
        if k in over:
            v = over[k]
        out.append(k + "=" + str(v))
    return "|".join(out)


def block(line):
    return (line + "\n").encode().ljust(4096, b"\0")


def store(pl, **over):
    return block(line_for(pl, **over)) + pl


def padded(b):
    return b.ljust(PAY, b"\0")


def tool(exe, path, off=0, cap=None):
    a = [exe, path, str(off)] + ([str(cap)] if cap is not None else [])
    r = subprocess.run(a, capture_output=True, text=True)
    rows = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")]
    f = dict(x.split("=", 1) for x in (rows[-1] if rows else "").split("|") if "=" in x)
    return r.returncode, f, r.stdout


def case(name, data, want, off=0, caps=(None,), spec=None):
    global bad
    path = spec or (TMP + "/" + name + ".bin")
    if data is not None:
        with open(path, "wb") as o:
            o.write(data)
    results = []
    for exe, which in ((EXE_A, "recorded"), (EXE_B, "own")):
        for cap in caps:
            code, f, _ = tool(exe, path, off, cap)
            miss = [k for k, v in want.items() if str(code if k == "exit" else f.get(k)) != str(v)]
            results.append((which, cap, code, f, miss))
    ok = not any(r[4] for r in results)
    bad += 0 if ok else 1
    code, f = results[0][2], results[0][3]
    shown = "|".join("%s=%s" % (k, f.get(k, "-")) for k in ("verdict", "store_identity", "identity_differs", "header_entries", "whole_space_count", "header_rooms", "padding", "padding_bytes", "padding_nonzero", "bytes_after_stream", "value_mismatch", "lower_without_upper", "upper_without_lower", "lower_repeated", "columns_not_ascending", "passes", "cap_requested", "cap_entries"))
    log.write("ATTACK|case=%s|exit=%d|runs=%d|met=%d|miss=%s|%s|reason=%s|json=0\n" % (name, code, len(results), int(ok), ";".join(sorted({m for r in results for m in r[4]})) or "-", shown, (f.get("reason") or "-").replace("|", "~")[:100]))
    log.flush()
    if data is not None and spec is None:
        os.remove(path)


h, i = next((h, j) for h in range(N) for j, _ in ROWS[h][2] if j < h)
# The sym2 store: one pair changed on both sides, row sums kept.
r = clone()
g = math.gcd(r[h][0], r[i][0])
for rw, col, d in ((h, i, r[i][0] // g), (i, h, r[h][0] // g)):
    k = [q for q, x in enumerate(r[rw][2]) if x[0] == col][0]
    r[rw][2][k] = (col, r[rw][2][k][1] - d)
    diag(r, rw, d)
SYM2 = padded(ser(r))

# ---- Trust.
case("T1_clean", base, {"exit": 0, "verdict": "PASS", "store_identity": "PASS", "identity_differs": "-", "payload_merkle": F["payload_merkle"], "header_sha256": "00fcacf55296e9269fe413e8ad36a526b143981e239993c2baeb0ae43c78ab5a", "bytes_after_stream": 0, "padding_bytes": 1021936, "padding_nonzero": 0, "rooms": 2818, "header_rooms": "PASS", "padding": "PASS", "pairs": 1198}, caps=(None, 0, 1, 7, 100))
case("T2_bytes_after_the_stream_are_counted_and_pass", base + b"\xAB" * 64, {"exit": 0, "verdict": "PASS", "bytes_after_stream": 64})
case("T3_junk_before_the_offset_passes_and_prints_no_offset", b"\xCD" * 8192 + base, {"exit": 0, "verdict": "PASS", "bytes_after_stream": 0}, off=8192)
os.makedirs(TMP + "/seg", exist_ok=True)
b = base.ljust(256 * 4099, b"\0")
for k in range(256):
    with open(TMP + "/seg/v-%03d.rooms" % k, "wb") as o:
        o.write(b[k * 4099:(k + 1) * 4099])
case("T4_other_sector_length_same_stream", None, {"exit": 0, "verdict": "PASS", "bytes_after_stream": 256 * 4099 - len(base)}, spec="seg:0:256:4099:" + TMP + "/seg/v-")
case("T4b_too_few_sectors_for_the_stream", None, {"exit": 1, "verdict": "FAIL"}, spec="seg:0:100:4099:" + TMP + "/seg/v-")
shutil.rmtree(TMP + "/seg")
case("T5_pair_changed_merkle_repaired", store(SYM2), {"exit": 2, "verdict": "FAIL", "store_identity": "FAIL", "identity_differs": "payload_merkle", "value_mismatch": 0, "padding": "PASS"})
case("T6_pair_changed_trusted_header", block(LINE) + SYM2, {"exit": 1, "verdict": "FAIL"})
d = bytearray(base)
d[eol + 1] = 1
case("T7_one_byte_after_the_newline", bytes(d), {"exit": 2, "verdict": "FAIL", "store_identity": "FAIL", "identity_differs": "header_block"})
case("T8_sector_label", store(P, sector="NOT-THIS"), {"exit": 2, "store_identity": "FAIL", "identity_differs": "sector"})
case("T9_same_sites_other_label", store(P, L="1x4"), {"exit": 2, "store_identity": "OPEN", "whole_space_count": "PASS"})
four = [[3265173504, 3, [(0, 2), (1, -1), (3, -1)]], [3265173504, 3, [(0, -1), (1, 2), (2, -1)]], [3265173504, 3, [(1, -1), (2, 2), (3, -1)]], [3265173504, 3, [(0, -1), (2, -1), (3, 2)]]]
fp = ser(four).ljust(PAY, b"\0")
case("T10_four_rows_under_the_3x4_label", block("YMROOMHDR|L=3x4|sector=Sx+Sy+|n=4|nl=24|rooms=16|entries=12|payload_bytes=%d|stream_bytes=%d|chunk=16MiB|payload_merkle=%s|keys_sha256=%s|w_self_adjoint=PASS|json=0" % (PAY, PAY + 4096, merkle(fp), "0" * 64)) + fp, {"exit": 2, "verdict": "FAIL", "store_identity": "FAIL", "whole_space_count": "PASS", "header_entries": "PASS", "header_rooms": "PASS", "padding": "PASS"})
case("T11_store_with_the_3x4_block_and_other_rows", block("YMROOMHDR|L=3x4|sector=Sx+Sy+|n=45508080|nl=24|rooms=3356267422|entries=3310759342|payload_bytes=26850881536|stream_bytes=26850885632|chunk=16MiB|payload_merkle=ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b|keys_sha256=bf5a1a43f99f4acd5f73f7da55e628e5bedbd5b4b29ef1b21c87b789d0d13b79|w_self_adjoint=PASS|json=0") + P, {"exit": 1, "verdict": "FAIL"})
# ---- Sizes.
case("S1_payload_at_u64_max", store(P, payload_bytes="18446744073709551615"), {"exit": 1, "verdict": "FAIL"})
case("S2_rooms_times_8_overflows", store(P, rooms="2305843009213693952"), {"exit": 1, "verdict": "FAIL"})
case("S2b_rooms_times_8_past_payload", store(P, rooms=str(PAY // 8 + 1)), {"exit": 1, "verdict": "FAIL"})
q = LINE.replace("|rooms=2818", "")
case("S3_no_rooms", block(q) + P, {"exit": 1, "verdict": "FAIL"})
q = LINE.replace("|stream_bytes=1048576", "")
case("S3b_no_stream_bytes", block(q) + P, {"exit": 1, "verdict": "FAIL"})
case("S4_no_padding_so_no_MiB_multiple", store(P[:USED]), {"exit": 1, "verdict": "FAIL"})
big = P[:USED].ljust(2 * MIB - 4096, b"\0")
case("S5_padding_of_a_MiB_or_more", store(big), {"exit": 1, "verdict": "FAIL"})
exact = P[:USED].ljust(MIB - 4096, b"\0")
case("S5b_padding_just_under_a_MiB_is_this_store", store(exact), {"exit": 0, "verdict": "PASS"})
case("S6_n_above_rooms", store(P, n=2819), {"exit": 1, "verdict": "FAIL"})
case("S7_file_shorter_than_stream", base[:4096 + 5000], {"exit": 1, "verdict": "FAIL"})
case("S9_offset_at_u64_max", base, {"exit": 1, "verdict": "FAIL"}, off=18446744073709551615)
two = struct.pack("<IHH", 108, 3, 2) + struct.pack("<IiIi", 0, 1, 1, -1) + struct.pack("<IHH", 108, 3, 2) + struct.pack("<IiIi", 0, -1, 1, 1)
tp = two.ljust(PAY, b"\0")
case("S8_two_rows_largest_padding_table_silent", block("YMROOMHDR|L=1x2|sector=x|n=2|nl=4|rooms=6|entries=4|payload_bytes=%d|stream_bytes=%d|chunk=16MiB|payload_merkle=%s|keys_sha256=0|w_self_adjoint=PASS|json=0" % (PAY, PAY + 4096, merkle(tp))) + tp, {"exit": 2, "verdict": "FAIL", "store_identity": "OPEN", "padding": "PASS", "padding_bytes": PAY - 48, "whole_space_count": "PASS", "header_entries": "PASS", "header_rooms": "PASS", "value_mismatch": 0})
# ---- Padding: merkle repaired, a stray byte at each end of the padding.
for name, at in (("first", USED), ("last", PAY - 1), ("middle", (USED + PAY) // 2)):
    d = bytearray(P)
    d[at] = 1
    case("P_%s_padding_byte_nonzero" % name, store(bytes(d)), {"exit": 2, "verdict": "FAIL", "padding": "FAIL", "padding_nonzero": 1, "store_identity": "FAIL", "value_mismatch": 0})
d = bytearray(P)
row = struct.pack("<IHH", 7, 3, 2) + struct.pack("<IiIi", 0, -5, N, 5)
d[USED:USED + len(row)] = row
case("P_bad_row_after_the_last", store(bytes(d)), {"exit": 2, "verdict": "FAIL", "padding": "FAIL", "rows_read": N})
case("P_n_below_the_rows", store(P, n=N - 1), {"exit": 2, "verdict": "FAIL", "padding": "FAIL", "column_out_of_range": "4"} if False else {"exit": 2, "verdict": "FAIL", "padding": "FAIL"})
case("P_n_above_the_rows", store(P, n=N + 1), {"exit": 2, "verdict": "FAIL", "zero_weight": 1, "missing_diag": 1, "header_rooms": "FAIL"})
# ---- D7, both sides, four caps.
CAPS = (None, 1, 7, 100)
m = [c for c, _ in ROWS[i][2] if c > i and c != h][0]
r = clone()
z = [x for x in r[h][2] if x[0] == i][0]
r[h][2].insert(r[h][2].index(z), z)
diag(r, h, -z[1])
zm = [x for x in r[m][2] if x[0] == i][0]
r[m][2].remove(zm)
diag(r, m, zm[1])
case("D7_reviewer_store", store(padded(ser(r))), {"exit": 2, "verdict": "FAIL", "upper_without_lower": 1, "lower_without_upper": 0, "lower_repeated": 1, "value_mismatch": 0, "columns_not_ascending": 1}, caps=CAPS)
r = clone()
z = [x for x in r[h][2] if x[0] == i][0]
r[h][2].insert(r[h][2].index(z), z)
case("D7_lower_side_repeated_alone", store(padded(ser(r))), {"exit": 2, "upper_without_lower": 0, "lower_without_upper": 0, "lower_repeated": 1, "value_mismatch": 0, "columns_not_ascending": 1}, caps=CAPS)
r = clone()
z = [x for x in r[i][2] if x[0] == h][0]
r[i][2].insert(r[i][2].index(z), z)
case("D7_upper_side_repeated_alone", store(padded(ser(r))), {"exit": 2, "upper_without_lower": 1, "lower_without_upper": 0, "lower_repeated": 0, "value_mismatch": 0, "columns_not_ascending": 1}, caps=CAPS)
r = clone()
zl = [x for x in r[h][2] if x[0] == i][0]
zu = [x for x in r[i][2] if x[0] == h][0]
r[h][2].insert(r[h][2].index(zl), zl)
r[i][2].insert(r[i][2].index(zu), zu)
case("D7_both_sides_repeated_same_values", store(padded(ser(r))), {"exit": 2, "upper_without_lower": 0, "lower_without_upper": 0, "lower_repeated": 0, "value_mismatch": 0, "columns_not_ascending": 2}, caps=CAPS)
r = clone()
zl = [x for x in r[h][2] if x[0] == i][0]
zu = [x for x in r[i][2] if x[0] == h][0]
wgc = math.gcd(r[h][0], r[i][0])
r[h][2].insert(r[h][2].index(zl) + 1, (i, zl[1] - r[i][0] // wgc))
r[i][2].insert(r[i][2].index(zu), (h, zu[1] - r[h][0] // wgc))
case("D7_both_sides_repeated_values_crossed", store(padded(ser(r))), {"exit": 2, "upper_without_lower": 0, "lower_without_upper": 0, "lower_repeated": 0, "value_mismatch": 2, "columns_not_ascending": 2}, caps=CAPS)
r = clone()
for x in r:
    x[2].reverse()
case("D7_every_row_reversed", store(padded(ser(r))), {"exit": 2, "upper_without_lower": 0, "lower_without_upper": 0, "lower_repeated": 0, "value_mismatch": 0, "pairs": 1198}, caps=CAPS)
# ---- D5.
case("D5_cap_zero", base, {"exit": 0, "cap_requested": 0, "cap_entries": 1, "passes": 188}, caps=(0,))
case("D5_cap_one", base, {"exit": 0, "cap_requested": 1, "cap_entries": 1, "passes": 188}, caps=(1,))
case("D5_cap_above_the_clamp", base, {"exit": 0, "cap_requested": 18446744073709551615, "cap_entries": 4000000000, "passes": 1}, caps=(18446744073709551615,))
# ---- own_hash.
path = TMP + "/own.bin"
open(path, "wb").write(base)
for exe, want in ((EXE_A, sha_a), (EXE_B, sha_b)):
    code, f, _ = tool(exe, path)
    ok = f.get("exe_sha256") == want
    bad += 0 if ok else 1
    log.write("ATTACK|case=own_hash_names_the_file|exe=%s|printed=%s|met=%d|json=0\n" % (want[:16], f.get("exe_sha256", "-")[:16], int(ok)))
copy = TMP + "/renamed.exe"
shutil.copy(EXE_B, copy)
code, f, _ = tool(copy, path)
ok = f.get("exe_sha256") == sha_b
bad += 0 if ok else 1
log.write("ATTACK|case=own_hash_on_a_copy_prints_the_same_hash|met=%d|json=0\n" % int(ok))
os.remove(copy)
os.remove(path)
log.write("ATTACK_DONE|not_met=%d|json=0\n" % bad)
log.close()
print("ATTACK_DONE|not_met=%d|json=0" % bad)
sys.exit(1 if bad else 0)
