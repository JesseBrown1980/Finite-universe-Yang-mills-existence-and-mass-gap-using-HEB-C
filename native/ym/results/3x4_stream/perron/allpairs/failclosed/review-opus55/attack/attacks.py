# Named attacks on allpairs, each on a copy in this folder. Each prediction is appended to REVIEW.hbp before its run, the outcome after.
# Runs the recorded executable and this seat's own build on every store, and this seat's reader beside them.
# usage: attacks.py [group ...]   Integer only, json=0.
import gzip, hashlib, os, re, struct, subprocess, sys, time

ROOT = "C:/tmp/opus55/allpairs-review-20261103"
RECORDED = "D:/ym-3x4-room-run/p0-ball/allpairs/allpairs.exe"
OWN = ROOT + "/bin/allpairs-own.exe"
READER = ROOT + "/bin/review-reader.exe"
RV = ROOT + "/REVIEW.hbp"
ST = ROOT + "/attack/stores"
RD = "D:/ym-3x4-room-run/p0-ball/"
B2X2 = RD + "small/2x2/dev.bin"
B2X3 = RD + "small/2x3/dev.bin"
B3X3 = RD + "c33/dev33.bin"
os.makedirs(ST, exist_ok=True)
GROUPS = sys.argv[1:]
KEYS = ["--r", "%x" % int.from_bytes(os.urandom(15), "big"), "--k0", os.urandom(8).hex(), "--k1", os.urandom(8).hex()]
counts = {"met": 0, "not_met": 0}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def row(tag, **kv):
    s = tag + "|at=" + now() + "".join("|%s=%s" % (k, v) for k, v in kv.items()) + "|json=0"
    with open(RV, "a", encoding="utf-8", newline="\n") as f:
        f.write(s + "\n")
    print(s, flush=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def merkle(pl):
    hx = "".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20))
    return sha(hx.encode())


def load(path):
    b = open(path, "rb").read()
    eol = b.index(b"\n")
    fields = [tuple(x.split("=", 1)) for x in b[:eol].decode().split("|")[1:]]
    d = dict(fields)
    payload = b[4096:4096 + int(d["payload_bytes"])]
    return fields, payload


def rows_of(payload, n):
    rows, p = [], 0
    for _ in range(n):
        w, mag, cnt = struct.unpack_from("<IHH", payload, p)
        p += 8
        v = struct.unpack_from("<" + "Ii" * cnt, payload, p)
        p += 8 * cnt
        rows.append([w, mag, [(v[2 * i], v[2 * i + 1]) for i in range(cnt)]])
    return rows, p


def ser(rows):
    out = bytearray()
    for w, mag, ent in rows:
        out += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            out += struct.pack("<Ii", j, z)
    return bytes(out)


def getf(f, k):
    return dict(f).get(k)


def setf(f, k, v):
    return [(a, (str(v) if a == k else b)) for a, b in f]


def delf(f, *keys):
    return [(a, b) for a, b in f if a not in keys]


def file_of(fields, payload, after=b""):
    line = "YMROOMHDR|" + "|".join("%s=%s" % kv for kv in fields) + "\n"
    head = line.encode().ljust(4096, b"\0") if len(line) <= 4096 else line.encode()
    return head + payload + after


def repaired(fields, payload, pad_to=None):
    """Fields with payload_bytes and payload_merkle recomputed for this payload, padded with zeros to pad_to."""
    if pad_to is not None:
        payload = payload.ljust(pad_to, b"\0")
    f = setf(setf(fields, "payload_merkle", merkle(payload)), "payload_bytes", len(payload))
    f = setf(f, "stream_bytes", len(payload) + 4096)
    return f, payload


def tool(exe, path, cap=None):
    a = [exe, path, "0"] + ([str(cap)] if cap is not None else [])
    r = subprocess.run(a, capture_output=True, text=True)
    last = ""
    for ln in r.stdout.splitlines():
        if ln.startswith("ALLPAIRS|"):
            last = ln
    f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
    return r.returncode, last, f, r.stdout


def reader(path, cap=470000000):
    r = subprocess.run([READER, path] + KEYS + ["--cap", str(cap)], capture_output=True, text=True)
    last = ""
    for ln in r.stdout.splitlines():
        if ln.startswith("REVIEW_READER|"):
            last = ln
    f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
    return r.returncode, f


def strip_secs(s):
    return re.sub(r"\|secs=\d+", "", s)


CAP_MATRIX = [0, 1, 2, 3, 7, 100] if os.environ.get("ATTACK_CAP_MATRIX") == "1" else []


def strip_varying(s):
    return re.sub(r"\|secs=\d+|\|cap_entries=\d+|\|passes=\d+", "", s)


def attack(name, data, predict, cap=None, reader_verdict="FAIL", keep=False, note=""):
    """predict: dict of field -> value, with 'exit' for the exit code."""
    path = "%s/%s.bin" % (ST, name)
    with open(path, "wb") as f:
        f.write(data)
    h = sha(data)
    pred = "".join("%s=%s," % kv for kv in predict.items()).rstrip(",")
    row("PREDICTION", run="attack_" + name, store_sha256=h, cap=cap, predict=pred, reader_verdict=reader_verdict, note=note)
    code, last, f, _ = tool(RECORDED, path, cap)
    code2, last2, f2, _ = tool(OWN, path, cap)
    same = int(code == code2 and strip_secs(last) == strip_secs(last2))
    rcode, rf = reader(path)
    caps_differ = []
    for c in CAP_MATRIX:
        cc, ll, ff, _ = tool(RECORDED, path, c)
        if cc != code or strip_varying(ll) != strip_varying(last):
            caps_differ.append("%d:exit=%d" % (c, cc))
    miss = []
    for k, v in predict.items():
        got = code if k == "exit" else f.get(k)
        if str(got) != str(v):
            miss.append("%s:%s!=%s" % (k, got, v))
    if rf.get("verdict") != reader_verdict:
        miss.append("reader:%s!=%s" % (rf.get("verdict"), reader_verdict))
    met = int(not miss)
    counts["met" if met else "not_met"] += 1
    if CAP_MATRIX and caps_differ:
        miss.append("caps:" + ",".join(caps_differ))
        met = 0
        counts["met"] -= 1
        counts["not_met"] += 1
    row("RESULT", run="attack_" + name, exit=code, verdict=f.get("verdict"), own_build_same=same, reader_exit=rcode, reader_verdict=rf.get("verdict"), caps_tried=len(CAP_MATRIX), caps_same=len(CAP_MATRIX) - len(caps_differ), prediction_met=met, miss=";".join(miss) or "-", line=last.replace("|", "~"))
    if not keep:
        os.remove(path)
    return code, last, f


def want_group(g):
    return not GROUPS or g in GROUPS


# ---------------------------------------------------------------------------------------------------- stores
F22, P22 = load(B2X2)
N22 = int(getf(F22, "n"))
R22, USED22 = rows_of(P22, N22)


def clone(rows):
    return [[w, m, list(e)] for w, m, e in rows]


def bump_diag(rows, h, dz):
    e = rows[h][2]
    k = [i for i, x in enumerate(e) if x[0] == h][0]
    e[k] = (h, e[k][1] + dz)


def first_pair():
    # Row h with a lower entry, and a partner.
    for h in range(N22):
        for j, z in R22[h][2]:
            if j < h:
                return h, j
    raise SystemExit("no pair")


# ---------------------------------------------------------------------------------------------------- H: header only
if want_group("H"):
    pl = bytearray(P22)
    pl[12] ^= 1
    f = delf(setf(setf(F22, "n", 0), "entries", 0), "nl")
    attack("H1_n0_damaged_payload_merkle_not_repaired", file_of(f, bytes(pl)), {"exit": 0, "verdict": "PASS", "merkle": "PASS", "rows_read": 0, "passes": 0, "pairs": 0, "whole_space_count": "OPEN", "header_entries": "PASS"}, note="merkle_printed_PASS_but_never_computed")
    attack("H1b_n0_nl_kept", file_of(setf(setf(F22, "n", 0), "entries", 0), bytes(pl)), {"exit": 2, "verdict": "FAIL", "whole_space_count": "FAIL"})
    attack("H1c_minimal_header_no_payload", b"YMROOMHDR|n=0|payload_bytes=0|w_self_adjoint=PASS\n".ljust(4096, b"\0"), {"exit": 0, "verdict": "PASS", "merkle": "PASS", "rows_read": 0}, reader_verdict="FAIL")
    attack("H1d_n0_payload_past_eof", b"YMROOMHDR|n=0|payload_bytes=99999999999|payload_merkle=00|w_self_adjoint=PASS\n".ljust(4096, b"\0"), {"exit": 0, "verdict": "PASS", "merkle": "PASS"}, reader_verdict="FAIL")
    attack("H2_entries_and_nl_removed_clean_rows", file_of(delf(F22, "entries", "nl"), P22), {"exit": 0, "verdict": "PASS", "header_entries": "OPEN", "whole_space_count": "OPEN"}, reader_verdict="FAIL")
    r = clone(R22)
    for x in r:
        x[0] *= 2
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    attack("H3_weights_doubled_control_nl_kept", file_of(f, p), {"exit": 2, "verdict": "FAIL", "whole_space_count": "FAIL", "value_mismatch": 0}, reader_verdict="FAIL")
    attack("H3a_weights_doubled_nl_removed", file_of(delf(f, "nl"), p), {"exit": 0, "verdict": "PASS", "whole_space_count": "OPEN", "sum_w": 15552}, reader_verdict="FAIL")
    attack("H3b_weights_doubled_nl_wrong", file_of(setf(f, "nl", 7), p), {"exit": 0, "verdict": "PASS", "whole_space_count": "OPEN"}, reader_verdict="FAIL")
    attack("H3c_weights_doubled_L_garbage", file_of(setf(f, "L", "2y2"), p), {"exit": 0, "verdict": "PASS", "whole_space_count": "OPEN"}, reader_verdict="FAIL")
    h, j = first_pair()
    r = clone(R22)
    zhj = [z for c, z in r[h][2] if c == j][0]
    zjh = [z for c, z in r[j][2] if c == h][0]
    r[h][2] = [x for x in r[h][2] if x[0] != j]
    r[j][2] = [x for x in r[j][2] if x[0] != h]
    bump_diag(r, h, zhj)
    bump_diag(r, j, zjh)
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    attack("H4_pair_deleted_control_entries_stale", file_of(f, p), {"exit": 2, "verdict": "FAIL", "header_entries": "FAIL", "value_mismatch": 0}, reader_verdict="FAIL")
    attack("H4a_pair_deleted_entries_garbage", file_of(setf(f, "entries", "abc"), p), {"exit": 0, "verdict": "PASS", "header_entries": "OPEN", "pairs": 1197}, reader_verdict="FAIL")
    attack("H4b_pair_deleted_entries_rewritten", file_of(setf(f, "entries", 2605), p), {"exit": 0, "verdict": "PASS", "header_entries": "PASS", "whole_space_count": "PASS", "pairs": 1197, "entries": 2605}, reader_verdict="FAIL", note="reader_fails_on_stale_rooms_field_only")
    attack("H6_n_raised_by_one_reads_padding_as_a_row", file_of(setf(F22, "n", N22 + 1), P22), {"exit": 2, "verdict": "FAIL", "zero_weight": 1, "missing_diag": 1}, reader_verdict="FAIL")
    attack("H7_relabel_L_1x4", file_of(setf(F22, "L", "1x4"), P22), {"exit": 0, "verdict": "PASS", "L": "1x4", "whole_space_count": "PASS"}, reader_verdict="PASS", note="count_gate_sees_only_V")
    attack("H8_relabel_sector", file_of(setf(F22, "sector", "NOT-THIS-SECTOR"), P22), {"exit": 0, "verdict": "PASS", "sector": "NOT-THIS-SECTOR"}, reader_verdict="PASS")
    attack("H9_rooms_stream_keys_wrong", file_of(setf(setf(setf(F22, "rooms", 1), "stream_bytes", 1), "keys_sha256", "bad"), P22), {"exit": 0, "verdict": "PASS"}, reader_verdict="FAIL", note="reader_checks_rooms")
    d = bytearray(file_of(F22, P22))
    d[3000:3008] = b"GARBAGE!"
    attack("H11_garbage_in_header_block_after_newline", bytes(d), {"exit": 0, "verdict": "PASS"}, reader_verdict="PASS")
    attack("H10_w_self_adjoint_FAIL", file_of(setf(F22, "w_self_adjoint", "FAIL"), P22), {"exit": 1, "verdict": "FAIL"}, reader_verdict="PASS", note="reader_does_not_read_that_field")
    attack("H10b_w_self_adjoint_missing", file_of(delf(F22, "w_self_adjoint"), P22), {"exit": 1, "verdict": "FAIL"}, reader_verdict="PASS")
    attack("H12_n_not_a_number", file_of(setf(F22, "n", "abc"), P22), {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")
    attack("H13_n_2_pow_32", file_of(setf(F22, "n", 1 << 32), P22), {"exit": 1, "verdict": "FAIL", "reason": "n does not fit in u32"}, reader_verdict="FAIL")
    attack("H14_merkle_field_missing", file_of(delf(F22, "payload_merkle"), P22), {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")
    attack("H15_no_newline_in_block", b"YMROOMHDR|n=1".ljust(4096, b"x") + P22, {"exit": 1, "verdict": "FAIL", "reason": "no header line"}, reader_verdict="FAIL")
    attack("H16_file_shorter_than_header", b"YMROOMHDR|n=1\n", {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")
    attack("H17_empty_file", b"", {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")

# ---------------------------------------------------------------------------------------------------- P: payload edges
if want_group("P"):
    pl = bytearray(P22)
    for i in range(USED22, len(pl)):
        pl[i] = 0xFF
    f, p = repaired(F22, bytes(pl))
    attack("P1_padding_nonzero_merkle_repaired", file_of(f, p), {"exit": 0, "verdict": "PASS", "pairs": 1198}, reader_verdict="FAIL")
    attack("P1b_padding_nonzero_merkle_not_repaired", file_of(F22, bytes(pl)), {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")
    # An asymmetric row hidden after the last row, in the padding.
    hidden = ser([[7, 3, [(0, -5), (N22, 5)]]])
    pl = bytearray(P22)
    pl[USED22:USED22 + len(hidden)] = hidden
    f, p = repaired(F22, bytes(pl))
    attack("P2_bad_row_hidden_in_padding", file_of(f, p), {"exit": 0, "verdict": "PASS", "rows_read": N22}, reader_verdict="FAIL")
    f, p = repaired(F22, P22[:USED22 - 8])
    attack("P3_payload_cut_inside_rows", file_of(f, p), {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")
    attack("P4_payload_past_eof", file_of(setf(F22, "payload_bytes", len(P22) + 8), P22), {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")
    f, p = repaired(F22, P22[:USED22])
    attack("P5_no_padding_at_all", file_of(f, p), {"exit": 0, "verdict": "PASS"}, reader_verdict="PASS")
    f, p = repaired(F22, P22[:USED22 + 3])
    attack("P6_payload_ends_three_bytes_past_a_room", file_of(f, p), {"exit": 0, "verdict": "PASS"}, reader_verdict="FAIL")
    attack("P7_file_cut_mid_payload", file_of(F22, P22)[:4096 + 5000], {"exit": 1, "verdict": "FAIL"}, reader_verdict="FAIL")
    attack("P8_bytes_after_payload", file_of(F22, P22, after=b"\xAB" * 64), {"exit": 0, "verdict": "PASS"}, reader_verdict="PASS", note="reader_prints_the_raw_tail_count_and_does_not_gate_on_it")

# ---------------------------------------------------------------------------------------------------- R: rows, merkle repaired
if want_group("R"):
    h, i = first_pair()
    # R1: a lower entry doubled in row h, and row m loses its partner of row i. found stays equal to stored.
    ups = [c for c, _ in R22[i][2] if c > i and c != h]
    m = ups[0]
    r = clone(R22)
    z = [x for x in r[h][2] if x[0] == i][0]
    pos = r[h][2].index(z)
    r[h][2].insert(pos, z)
    bump_diag(r, h, -z[1])
    zmi = [x for x in r[m][2] if x[0] == i][0]
    r[m][2].remove(zmi)
    bump_diag(r, m, zmi[1])
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    attack("R1_double_lower_masks_an_unpaired_upper", file_of(f, p), {"exit": 2, "verdict": "FAIL", "columns_not_ascending": 1, "upper_without_lower": 0, "lower_without_upper": 0, "value_mismatch": 0, "row_sum_nonzero": 0, "header_entries": "PASS"}, note="pair_counters_all_0_on_a_store_with_one_unpaired_entry_structure_gate_carries_it")
    r = clone(R22)
    a = [x for x in r[h][2] if x[0] == i][0]
    b = [x for x in r[i][2] if x[0] == h][0]
    r[h][2][r[h][2].index(a)] = (i, 0)
    r[i][2][r[i][2].index(b)] = (h, 0)
    bump_diag(r, h, a[1])
    bump_diag(r, i, b[1])
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    attack("R2_pair_set_to_zero_both_sides", file_of(f, p), {"exit": 2, "verdict": "FAIL", "zero_z": 2, "value_mismatch": 0})
    r = clone(R22)
    r[h][2][r[h][2].index(a)] = (i, -a[1])
    r[i][2][r[i][2].index(b)] = (h, -b[1])
    bump_diag(r, h, 2 * a[1])
    bump_diag(r, i, 2 * b[1])
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    attack("R3_pair_sign_flipped_both_sides", file_of(f, p), {"exit": 2, "verdict": "FAIL", "positive_offdiag": 2, "value_mismatch": 0})
    for col, nm in [(N22, "n"), (0xFFFFFFFF, "u32max"), (0x80000000, "2p31")]:
        r = clone(R22)
        r[N22 - 1][2].append((col, -1))
        bump_diag(r, N22 - 1, 1)
        f, p = repaired(F22, ser(r), pad_to=len(P22))
        attack("R4_column_out_of_range_" + nm, file_of(f, p), {"exit": 2, "verdict": "FAIL", "column_out_of_range": 1, "upper_without_lower": 1})
    pl = bytearray(P22)
    last_p = USED22 - 8 - 8 * len(R22[N22 - 1][2])
    struct.pack_into("<H", pl, last_p + 6, 65535)
    f, p = repaired(F22, bytes(pl))
    attack("R5_last_row_count_65535_runs_into_padding", file_of(f, p), {"exit": 2, "verdict": "FAIL"})
    f, p = repaired(F22, bytes(pl[:USED22]))
    attack("R5b_last_row_count_65535_no_padding", file_of(f, p), {"exit": 1, "verdict": "FAIL"})
    M = 2147483647
    F0 = [("L", "x"), ("sector", "x"), ("n", 2), ("entries", 4), ("payload_bytes", 0), ("payload_merkle", ""), ("w_self_adjoint", "PASS")]
    f, p = repaired(F0, ser([[0xFFFFFFFF, 3, [(0, M), (1, -M)]], [0xFFFFFFFF, 3, [(0, -M), (1, M)]]]))
    attack("R6_largest_values_clean", file_of(f, p), {"exit": 0, "verdict": "PASS", "value_mismatch": 0, "whole_space_count": "OPEN"}, reader_verdict="FAIL")
    f, p = repaired(F0, ser([[65536, 3, [(0, 65536), (1, -65536)]], [8, 3, [(0, -(1 << 30)), (1, 1 << 30)]]]))
    attack("R7_equal_mod_2p32_differ_as_integers", file_of(f, p), {"exit": 2, "verdict": "FAIL", "value_mismatch": 1})
    F4 = setf(setf(F0, "n", 4), "entries", 10)
    f, p = repaired(F4, ser([[1, 3, [(0, 1), (1, -(1 << 31)), (2, -(1 << 31)), (3, -1)]], [2, 3, [(0, -(1 << 30)), (1, 1 << 30)]], [2, 3, [(0, -(1 << 30)), (2, 1 << 30)]], [1, 3, [(0, -1), (3, 1)]]]))
    attack("R8_row_sum_is_minus_2p32", file_of(f, p), {"exit": 2, "verdict": "FAIL", "row_sum_nonzero": 1, "value_mismatch": 0})
    r = clone(R22)
    dz = [x for x in r[5][2] if x[0] == 5][0]
    r[5][2].insert(r[5][2].index(dz), dz)
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    attack("R9_diagonal_doubled", file_of(f, p), {"exit": 2, "verdict": "FAIL", "columns_not_ascending": 1})
    r = clone(R22)
    r[7][2] = []
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    attack("R10_row_with_no_entries", file_of(f, p), {"exit": 2, "verdict": "FAIL", "missing_diag": 1})

# ---------------------------------------------------------------------------------------------------- B: what the printed line binds
if want_group("B"):
    h, i = first_pair()
    r = clone(R22)
    wa, wb = r[h][0], r[i][0]
    g = __import__("math").gcd(wa, wb)
    da, db = wb // g, wa // g
    for row_, col, d in [(h, i, da), (i, h, db)]:
        e = r[row_][2]
        k = [q for q, x in enumerate(e) if x[0] == col][0]
        e[k] = (col, e[k][1] - d)
        bump_diag(r, row_, d)
    f, p = repaired(F22, ser(r), pad_to=len(P22))
    path_a = ST + "/B1_clean.bin"
    path_b = ST + "/B1_sym2.bin"
    open(path_a, "wb").write(file_of(F22, P22))
    open(path_b, "wb").write(file_of(f, p))
    row("PREDICTION", run="attack_B1_same_line_two_stores", clean_sha256=sha(file_of(F22, P22)), mutated_sha256=sha(file_of(f, p)), merkle_clean=getf(F22, "payload_merkle"), merkle_mutated=getf(f, "payload_merkle"), lines_identical_after_removing_secs=1, exit_each=0)
    ca, la, _, _ = tool(RECORDED, path_a)
    cb, lb, _, _ = tool(RECORDED, path_b)
    same = int(strip_secs(la) == strip_secs(lb))
    counts["met" if same and ca == 0 and cb == 0 else "not_met"] += 1
    row("RESULT", run="attack_B1_same_line_two_stores", exit_clean=ca, exit_mutated=cb, lines_identical_after_removing_secs=same, prediction_met=int(same and ca == 0 and cb == 0), line_clean=la.replace("|", "~"))
    os.remove(path_a)
    os.remove(path_b)
    w = 13060694016 // 4
    fr = [[w, 3, [(0, 2), (1, -1), (3, -1)]], [w, 3, [(0, -1), (1, 2), (2, -1)]], [w, 3, [(1, -1), (2, 2), (3, -1)]], [w, 3, [(0, -1), (2, -1), (3, 2)]]]
    F5 = [("L", "3x4"), ("sector", "Sx+Sy+"), ("n", 4), ("nl", 24), ("rooms", 16), ("entries", 12), ("payload_bytes", 0), ("stream_bytes", 0), ("chunk", "16MiB"), ("payload_merkle", ""), ("keys_sha256", "0" * 64), ("w_self_adjoint", "PASS"), ("json", 0)]
    f, p = repaired(F5, ser(fr))
    attack("B2_four_row_store_labelled_3x4_all_gates_pass", file_of(f, p), {"exit": 0, "verdict": "PASS", "L": "3x4", "n": 4, "sum_w": 13060694016, "codes": 13060694016, "whole_space_count": "PASS", "header_entries": "PASS", "merkle": "PASS", "pairs": 4}, reader_verdict="PASS", note="reader_has_no_expected_merkle_here_either")

# ---------------------------------------------------------------------------------------------------- C: command line
if want_group("C"):
    good = ST + "/C_clean.bin"
    open(good, "wb").write(open(B2X2, "rb").read())

    def cli(name, args, pexit, pdetail=""):
        row("PREDICTION", run="cli_" + name, args=" ".join(args).replace("|", "~"), exit=pexit, detail=pdetail)
        r = subprocess.run([RECORDED] + args, capture_output=True, text=True, timeout=120)
        last = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")]
        last = last[-1] if last else ""
        f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
        ok = r.returncode == pexit and (not pdetail or pdetail in last or pdetail in r.stderr)
        counts["met" if ok else "not_met"] += 1
        row("RESULT", run="cli_" + name, exit=r.returncode, verdict=f.get("verdict"), passes=f.get("passes"), cap_entries=f.get("cap_entries"), reason=(f.get("reason") or "-").replace("|", "~")[:120], prediction_met=int(ok))

    cli("no_args", [], 1, "usage")
    cli("missing_offset", [good], 1, "missing OFFSET")
    cli("offset_word", [good, "abc"], 1, "bad OFFSET")
    cli("offset_negative", [good, "-1"], 1, "bad OFFSET")
    cli("offset_one", [good, "1"], 1, "not a YMROOMHDR")
    cli("offset_max", [good, "18446744073709551615"], 1)
    cli("offset_past_file", [good, "99999999"], 1)
    cli("cap_word", [good, "0", "abc"], 1, "bad CAP_ENTRIES")
    cli("cap_negative", [good, "0", "-1"], 1, "bad CAP_ENTRIES")
    cli("cap_too_big_to_parse", [good, "0", "18446744073709551616"], 1, "bad CAP_ENTRIES")
    cli("cap_zero_prints_0_runs_as_1", [good, "0", "0"], 0, "cap_entries=0|")
    cli("cap_one", [good, "0", "1"], 0, "cap_entries=1|")
    cli("cap_max_prints_unclamped", [good, "0", "18446744073709551615"], 0, "cap_entries=18446744073709551615|")
    cli("extra_argument_ignored", [good, "0", "100", "junk"], 0, "cap_entries=100|")
    cli("missing_file", [ST + "/no-such-file.bin", "0"], 1)
    cli("directory", [ST, "0"], 1)
    cli("seg_count_zero", ["seg:0:0:8:" + ST + "/x", "0"], 1)
    cli("seg_len_zero", ["seg:0:1:0:" + ST + "/x", "0"], 1)
    cli("seg_words", ["seg:a:b:c:" + ST + "/x", "0"], 1)
    cli("seg_range_wraps", ["seg:18446744073709551615:2:800:" + ST + "/x", "0"], 1)
    cli("seg_missing_file", ["seg:900:1:800:" + ST + "/x", "0"], 1)
    # A one-sector store through the seg lane, right and wrong length.
    open(ST + "/s-341.rooms", "wb").write(open(B2X2, "rb").read())
    cli("seg_one_sector_ok", ["seg:341:1:1048576:" + ST + "/s-", "0"], 0, "verdict=PASS")
    cli("seg_wrong_length", ["seg:341:1:1048575:" + ST + "/s-", "0"], 1, "length != seglen")
    b = open(B2X2, "rb").read()
    half = 524288
    open(ST + "/t-341.rooms", "wb").write(b[:half])
    open(ST + "/t-342.rooms", "wb").write(b[half:])
    cli("seg_two_sectors_ok", ["seg:341:2:524288:" + ST + "/t-", "0"], 0, "verdict=PASS")
    cli("seg_two_sectors_only_first", ["seg:341:1:524288:" + ST + "/t-", "0"], 1, "read rooms")
    for x in ["C_clean.bin", "s-341.rooms", "t-341.rooms", "t-342.rooms"]:
        os.remove(ST + "/" + x)

row("ATTACKS_DONE", groups=",".join(GROUPS) or "all", met=counts["met"], not_met=counts["not_met"], keys=" ".join(KEYS))
print("ATTACKS met=%d not_met=%d" % (counts["met"], counts["not_met"]))
