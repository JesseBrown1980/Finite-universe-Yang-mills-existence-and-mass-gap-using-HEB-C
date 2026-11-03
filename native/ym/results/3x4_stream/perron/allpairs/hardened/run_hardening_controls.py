# Adversarial controls for defects D3 to D8 of the second seat's review of allpairs, and the 62 header cases before them. Each case runs on three
# executables: the original at 8faadb0, the corrected at 0fd24d3, and the hardened one. The old two show each defect, and the hardened one has to
# reject it. Every outcome is predicted below, in this file, before any run.
#
# usage: run_hardening_controls.py --base fixture-2x2.rooms.gz --out DIR [--predict-only] [--full-block] --original EXE --corrected EXE --hardened EXE
#
# Writes HARDENING-CONTROLS.hbp into DIR. --full-block also flips all 32,768 bits of the header block on the hardened executable.
# Exits 1 if any outcome differs from its prediction. The public store is never touched. Integer only, json=0.
import gzip, hashlib, math, os, struct, subprocess, sys, tempfile

BASE_SHA = "b31e730606db130585f9560f7adab87444d744876c3a8e36f6f9ef2bf0aa431f"
K_3X4 = "bf5a1a43f99f4acd5f73f7da55e628e5bedbd5b4b29ef1b21c87b789d0d13b79"
MIB = 1 << 20
FLIP_BYTES_AFTER_LINE = 64


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def sha(b):
    return hashlib.sha256(b).hexdigest()


base = gzip.open(arg("--base"), "rb").read()
if sha(base) != BASE_SHA:
    raise SystemExit("fixture hash")
EOL = base.index(b"\n")
if base[:4096].count(b"\n") != 1 or any(base[EOL + 1:4096]):
    raise SystemExit("fixture header layout")
LINE = base[:EOL].decode()
FLD = dict(x.split("=", 1) for x in LINE.split("|") if "=" in x)
M, K = FLD["payload_merkle"], FLD["keys_sha256"]
HB = sha(base[:4096])
N, PAY = int(FLD["n"]), int(FLD["payload_bytes"])
BODY = base[4096:4096 + PAY]
ZERO = "0" * 64
CANON = "outside canonical form"

ROWS, _p = [], 0
for _ in range(N):
    _w, _mag, _cnt = struct.unpack_from("<IHH", BODY, _p)
    _v = struct.unpack_from("<" + "Ii" * _cnt, BODY, _p + 8)
    ROWS.append([_w, _mag, [(_v[2 * k], _v[2 * k + 1]) for k in range(_cnt)]])
    _p += 8 + 8 * _cnt
USED = _p


def merkle(pl):
    return sha("".join(sha(pl[i:i + (16 * MIB)]) for i in range(0, len(pl), 16 * MIB)).encode())


def block(line):
    head = line.encode() + b"\n"
    if len(head) > 4096:
        raise SystemExit("header length")
    return head + bytes(4096 - len(head))


def ser(rows, total=0):
    out = bytearray()
    for w, mag, ent in rows:
        out += struct.pack("<IHH", w, mag, len(ent))
        for j, z in ent:
            out += struct.pack("<Ii", j, z)
    if total:
        out += bytes(total - len(out))
    return bytes(out)


def clone():
    return [[w, mag, list(ent)] for w, mag, ent in ROWS]


def add_diag(rows, h, d):
    k = [q for q, x in enumerate(rows[h][2]) if x[0] == h][0]
    rows[h][2][k] = (h, rows[h][2][k][1] + d)


def fixture_with(pl):
    """The fixture's header with its merkle repaired to fit this payload."""
    return block(LINE.replace("payload_merkle=" + M, "payload_merkle=" + merkle(pl))) + pl


def full_store(rows, lattice, nl, stream, keys=K):
    """A store with every header field, in the layout ymroom writes, except for the length of its padding."""
    pl = ser(rows, stream - 4096)
    entries = sum(len(r[2]) for r in rows)
    line = "YMROOMHDR|L=%s|sector=Sx+Sy+|n=%d|nl=%d|rooms=%d|entries=%d|payload_bytes=%d|stream_bytes=%d|chunk=16MiB|payload_merkle=%s|keys_sha256=%s|w_self_adjoint=PASS|json=0" % (lattice, len(rows), nl, len(rows) + entries, entries, len(pl), stream, merkle(pl), keys)
    return block(line) + pl


TWO = [[108, 3, [(0, 1), (1, -1)]], [108, 3, [(0, -1), (1, 1)]]]


def ok(e="PASS", c="PASS", rows=N, **more):
    return dict(exit=0, verdict="PASS", header_entries=e, whole_space_count=c, rows_read=rows, **more)


def bad(e, c, rows=N, **more):
    return dict(exit=2, verdict="FAIL", header_entries=e, whole_space_count=c, rows_read=rows, **more)


def stop(reason):
    return dict(exit=1, verdict="FAIL", reason=reason)


def hok(**more):
    return ok(store_identity="PASS", header_rooms="PASS", padding="PASS", padding_nonzero=0, identity_differs="-", **more)


def hbad(e, c, identity, rows=N, room="PASS", pad="PASS", **more):
    return bad(e, c, rows, store_identity=identity, header_rooms=room, padding=pad, **more)


CASES = []


def case(name, defect, build, original, corrected, hardened, cap=None):
    CASES.append(dict(name=name, defect=defect, build=build, cap=cap, want=dict(original=original, corrected=corrected, hardened=hardened)))


def edited(*edits):
    def build():
        line = LINE
        for a, b in edits:
            if line.count(a) != 1:
                raise SystemExit("edit does not match once: " + a)
            line = line.replace(a, b, 1)
        return block(line) + BODY
    return build


def whole_line(line):
    return lambda: block(line) + BODY


ENTRIES, NL, LAT, ONE_N = "entries=2607", "nl=8", "L=2x2", "|n=211|"
PB = "payload_bytes=1044480"
case("clean", "H", edited(), ok(), ok(), hok(payload_merkle=M, header_sha256=HB, rooms=2818, padding_bytes=PAY - USED, bytes_after_stream=0, lower_repeated=0, cap_requested=470000000, cap_entries=470000000, pairs=1198))
# header_entries reads OPEN.
for name, to in (("empty", "entries="), ("word", "entries=abc"), ("negative", "entries=-2607"), ("overflow_u64", "entries=18446744073709551616")):
    case("entries_" + name, "H", edited((ENTRIES, to)), ok("OPEN"), bad("OPEN", "PASS"), hbad("OPEN", "PASS", "FAIL"))
case("entries_missing", "H", edited(("|" + ENTRIES, "")), ok("OPEN"), bad("OPEN", "PASS"), hbad("OPEN", "PASS", "FAIL"))
case("entries_plus", "H", edited((ENTRIES, "entries=+2607")), ok(), bad("OPEN", "PASS"), hbad("OPEN", "PASS", "FAIL"))
case("entries_leading_zero", "H", edited((ENTRIES, "entries=02607")), ok(), bad("OPEN", "PASS"), hbad("OPEN", "PASS", "FAIL"))
# header_entries reads FAIL.
case("entries_wrong", "H", edited((ENTRIES, "entries=2606")), bad("FAIL", "PASS"), bad("FAIL", "PASS"), hbad("FAIL", "PASS", "FAIL"))
# whole_space_count reads OPEN, from nl=.
for name, to in (("empty", "nl="), ("word", "nl=abc"), ("negative", "nl=-8"), ("inconsistent", "nl=7")):
    case("nl_" + name, "H", edited((NL, to)), ok("PASS", "OPEN"), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "FAIL"))
case("nl_missing", "H", edited(("|" + NL, "")), ok("PASS", "OPEN"), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "FAIL"))
case("nl_plus", "H", edited((NL, "nl=+8")), ok(), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "FAIL"))
case("nl_leading_zero", "H", edited((NL, "nl=08")), ok(), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "FAIL"))
# whole_space_count reads OPEN, from L=. The table holds no such lattice, so store_identity reads OPEN too.
case("L_missing", "H", edited((LAT + "|", "")), ok("PASS", "OPEN"), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "OPEN"))
for name, to in (("empty", "L="), ("no_x", "L=4"), ("word", "L=axb"), ("three_sizes", "L=2x2x2"), ("sites_overflow_u32", "L=65536x65536"), ("links_overflow_u32", "L=65536x32768")):
    case("L_" + name, "H", edited((LAT, to)), ok("PASS", "OPEN"), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "OPEN"))
case("L_plus", "H", edited((LAT, "L=+2x2")), ok(), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "OPEN"))
case("L_leading_zero", "H", edited((LAT, "L=02x2")), ok(), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "OPEN"))
case("L_zero_size", "H", edited((LAT, "L=0x4"), (NL, "nl=0")), bad("PASS", "FAIL"), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "OPEN"))
case("L_codes_overflow_u128", "H", edited((LAT, "L=7x7"), (NL, "nl=98")), ok("PASS", "OPEN"), bad("PASS", "OPEN"), hbad("PASS", "OPEN", "OPEN"))
# whole_space_count reads FAIL, under a lattice the table holds.
case("L_other_lattice", "H", edited((LAT, "L=2x3"), (NL, "nl=12")), bad("PASS", "FAIL"), bad("PASS", "FAIL"), hbad("PASS", "FAIL", "FAIL"))
case("both_missing", "H", edited(("|" + ENTRIES, ""), ("|" + NL, "")), ok("OPEN", "OPEN"), bad("OPEN", "OPEN"), hbad("OPEN", "OPEN", "FAIL"))
# A repeated key gives two answers. The original reads the first.
for name, a, b, key in (
    ("entries_repeated_same", ENTRIES, ENTRIES + "|" + ENTRIES, "entries"),
    ("entries_repeated_other", ENTRIES, ENTRIES + "|entries=1", "entries"),
    ("nl_repeated_other", NL, NL + "|nl=7", "nl"),
    ("L_repeated_other", LAT, LAT + "|L=2x3", "L"),
    ("n_repeated_other", ONE_N, "|n=211|n=1|", "n"),
    ("payload_repeated_other", PB, PB + "|payload_bytes=8", "payload_bytes"),
    ("merkle_repeated_other", "payload_merkle=" + M, "payload_merkle=" + M + "|payload_merkle=" + ZERO, "payload_merkle"),
    ("w_repeated_other", "w_self_adjoint=PASS", "w_self_adjoint=PASS|w_self_adjoint=FAIL", "w_self_adjoint"),
):
    case(name, "H", edited((a, b)), ok(), stop("header repeats %s=" % key), stop("header repeats %s=" % key))
# n= and payload_bytes= outside canonical form.
case("n_plus", "H", edited((ONE_N, "|n=+211|")), ok(), stop(CANON), stop(CANON))
case("n_leading_zero", "H", edited((ONE_N, "|n=0211|")), ok(), stop(CANON), stop(CANON))
case("payload_plus", "H", edited((PB, "payload_bytes=+1044480")), ok(), stop(CANON), stop(CANON))
case("payload_leading_zero", "H", edited((PB, "payload_bytes=01044480")), ok(), stop(CANON), stop(CANON))
# A store with no rows.
case("n_zero", "H", edited((ONE_N, "|n=0|")), bad("FAIL", "FAIL", 0), stop("n is 0"), stop("n is 0"))
case("n_zero_no_counts", "H", edited((ONE_N, "|n=0|"), ("|" + ENTRIES, ""), ("|" + NL, "")), ok("OPEN", "OPEN", 0), stop("n is 0"), stop("n is 0"))
case("n_zero_other_merkle", "H", edited((ONE_N, "|n=0|"), ("|" + ENTRIES, ""), ("|" + NL, ""), ("payload_merkle=" + M, "payload_merkle=" + ZERO)), ok("OPEN", "OPEN", 0), stop("n is 0"), stop("n is 0"))
case("empty_minimal_header", "H", whole_line("YMROOMHDR|n=0|payload_bytes=0|w_self_adjoint=PASS|json=0"), ok("OPEN", "OPEN", 0), stop("n is 0"), stop("n is 0"))
# n= that differs from the rows. The padding past the last row reads as a row of zeros.
case("n_below_rows", "H", edited((ONE_N, "|n=210|")), bad("FAIL", "FAIL", 210), bad("FAIL", "FAIL", 210), hbad("FAIL", "FAIL", "FAIL", 210, "FAIL", "FAIL"))
case("n_above_rows", "H", edited((ONE_N, "|n=212|")), bad("PASS", "PASS", 212), bad("PASS", "PASS", 212), hbad("PASS", "PASS", "FAIL", 212, "FAIL", "FAIL"))
case("n_above_u32", "H", edited((ONE_N, "|n=4294967296|")), stop("n does not fit"), stop("n does not fit"), stop("exceeds rooms="))
# Fields read through roomio.
case("n_missing", "H", edited(("|n=211", "")), stop("missing n="), stop("missing n="), stop("missing n="))
case("n_word", "H", edited((ONE_N, "|n=abc|")), stop("missing n="), stop("missing n="), stop("missing n="))
case("payload_missing", "H", edited(("|" + PB, "")), stop("missing payload_bytes="), stop("missing payload_bytes="), stop("missing payload_bytes="))
case("payload_word", "H", edited((PB, "payload_bytes=abc")), stop("missing payload_bytes="), stop("missing payload_bytes="), stop("missing payload_bytes="))
case("payload_short", "H", edited((PB, "payload_bytes=1044472")), stop("merkle"), stop("merkle"), stop("stream_bytes="))
case("payload_long", "H", edited((PB, "payload_bytes=1044488")), stop("read rooms"), stop("read rooms"), stop("stream_bytes="))
case("merkle_missing", "H", edited(("|payload_merkle=" + M, "")), stop("merkle"), stop("merkle"), stop("merkle"))
case("merkle_changed", "H", edited(("payload_merkle=" + M, "payload_merkle=" + ZERO)), stop("merkle"), stop("merkle"), stop("merkle"))
case("w_fail", "H", edited(("w_self_adjoint=PASS", "w_self_adjoint=FAIL")), stop("not a YMROOMHDR"), stop("not a YMROOMHDR"), stop("not a YMROOMHDR"))
case("w_missing", "H", edited(("|w_self_adjoint=PASS", "")), stop("not a YMROOMHDR"), stop("not a YMROOMHDR"), stop("not a YMROOMHDR"))
case("magic_changed", "H", edited(("YMROOMHDR|", "YMROOMHDX|")), stop("not a YMROOMHDR"), stop("not a YMROOMHDR"), stop("not a YMROOMHDR"))
case("no_line_end", "H", lambda: base[:EOL] + b"x" + base[EOL + 1:], stop("no header line"), stop("no header line"), stop("no header line"))
case("short_file", "H", lambda: base[:100], stop("read header"), stop("read header"), stop("read header"))
case("unread_fields_removed", "H", edited(("|sector=Sx+Sy+", ""), ("|rooms=2818", ""), ("|stream_bytes=1048576", ""), ("|chunk=16MiB", ""), ("|keys_sha256=" + K, ""), ("|json=0", "")), ok(), ok(), stop("rooms="))

# D3. Payload after the last row was hashed and left unread.
pad_ff = bytearray(BODY)
pad_ff[USED:PAY] = b"\xff" * (PAY - USED)
case("D3_padding_all_ff", "D3", lambda: fixture_with(bytes(pad_ff)), ok(), ok(), hbad("PASS", "PASS", "FAIL", pad="FAIL", padding_nonzero=PAY - USED, identity_differs="payload_merkle"))
pad_one = bytearray(BODY)
pad_one[PAY - 1] = 1
case("D3_padding_last_byte", "D3", lambda: fixture_with(bytes(pad_one)), ok(), ok(), hbad("PASS", "PASS", "FAIL", pad="FAIL", padding_nonzero=1, identity_differs="payload_merkle"))
hidden_row = struct.pack("<IHH", 7, 3, 2) + struct.pack("<IiIi", 0, -5, N, 5)
pad_row = bytearray(BODY)
pad_row[USED:USED + len(hidden_row)] = hidden_row
case("D3_bad_row_after_the_last", "D3", lambda: fixture_with(bytes(pad_row)), ok(), ok(), hbad("PASS", "PASS", "FAIL", pad="FAIL", padding_nonzero=sum(1 for b in hidden_row if b), identity_differs="payload_merkle"))
case("D3_rooms_one_above", "D3", edited(("rooms=2818", "rooms=2819")), ok(), ok(), hbad("PASS", "PASS", "FAIL", room="FAIL", pad="FAIL"))
for name, a, b, reason in (
    ("rooms_missing", "|rooms=2818", "", "rooms="),
    ("rooms_word", "rooms=2818", "rooms=abc", "rooms="),
    ("rooms_too_large", "rooms=2818", "rooms=99999999", "does not fit"),
    ("rooms_too_small", "rooms=2818", "rooms=100", "exceeds rooms="),
    ("stream_missing", "|stream_bytes=1048576", "", "stream_bytes="),
    ("stream_wrong", "stream_bytes=1048576", "stream_bytes=1048577", "stream_bytes="),
):
    case("D4_" + name, "D4", edited((a, b)), ok(), ok(), stop(reason))

# D4. Memory grew with padding, and sizes were taken as given.
PAD_MIB = 256
case("D4_padding_256MiB", "D4", lambda: full_store(TWO, "1x2", 4, PAD_MIB * MIB), ok(rows=2, pairs=1), ok(rows=2, pairs=1), stop("1 MiB or more of padding"))
TIB_LINE = "YMROOMHDR|L=1x2|sector=Sx+Sy+|n=2|nl=4|rooms=137438952960|entries=137438952958|payload_bytes=1099511623680|stream_bytes=1099511627776|chunk=16MiB|payload_merkle=%s|keys_sha256=%s|w_self_adjoint=PASS|json=0" % (ZERO, K)
case("D4_claims_1TiB", "D4", lambda: block(TIB_LINE) + BODY, stop("read rooms"), stop("read rooms"), stop("shorter"))
FLATS = 100000
flat_rows = [[1, 0, [(h, 0)]] for h in range(FLATS)]
case("D4_many_flat_rows", "D4", lambda: full_store(flat_rows, "1x100000", 200000, 2 * MIB), dict(exit=2, verdict="FAIL", flats=FLATS, _line_min=200000), dict(exit=2, verdict="FAIL", flats=FLATS, _line_min=200000), dict(exit=2, verdict="FAIL", flats=FLATS, flat_w_listed=64, store_identity="OPEN", header_rooms="PASS", padding="PASS", _line_max=4096))

# D5. The printed cap was the argument, and the window used the clamped value.
case("D5_cap_zero", "D5", edited(), ok(cap_entries=0, passes=188), ok(cap_entries=0, passes=188), hok(cap_requested=0, cap_entries=1, passes=188), cap="0")
case("D5_cap_max", "D5", edited(), ok(cap_entries=18446744073709551615, passes=1), ok(cap_entries=18446744073709551615, passes=1), hok(cap_requested=18446744073709551615, cap_entries=4000000000, passes=1), cap="18446744073709551615")
case("C_cap_one", "C", edited(), ok(cap_entries=1, passes=188), ok(cap_entries=1, passes=188), hok(cap_requested=1, cap_entries=1, passes=188), cap="1")

# D6. The output named no store, so two stores printed one line, and a store passed under another's label.
W4 = 13060694016 // 4
FOUR = [[W4, 3, [(0, 2), (1, -1), (3, -1)]], [W4, 3, [(0, -1), (1, 2), (2, -1)]], [W4, 3, [(1, -1), (2, 2), (3, -1)]], [W4, 3, [(0, -1), (2, -1), (3, 2)]]]
case("D6_four_rows_labelled_3x4", "D6", lambda: full_store(FOUR, "3x4", 24, MIB, K_3X4), ok(rows=4, pairs=4, sum_w=13060694016), ok(rows=4, pairs=4, sum_w=13060694016), hbad("PASS", "PASS", "FAIL", 4, identity_differs="entries,n,payload_bytes,payload_merkle,rooms,stream_bytes", pairs=4, sum_w=13060694016))
PH, PI = next((h, j) for h in range(N) for j, _ in ROWS[h][2] if j < h)
pair_rows = clone()
_g = math.gcd(pair_rows[PH][0], pair_rows[PI][0])
for _rw, _col, _d in ((PH, PI, pair_rows[PI][0] // _g), (PI, PH, pair_rows[PH][0] // _g)):
    _k = [q for q, x in enumerate(pair_rows[_rw][2]) if x[0] == _col][0]
    pair_rows[_rw][2][_k] = (_col, pair_rows[_rw][2][_k][1] - _d)
    add_diag(pair_rows, _rw, _d)
PAIR_BODY = ser(pair_rows, PAY)
case("D6_one_pair_changed_both_sides", "D6", lambda: fixture_with(PAIR_BODY), ok(), ok(), hbad("PASS", "PASS", "FAIL", identity_differs="payload_merkle"))
case("D6_lattice_outside_the_table", "D6", lambda: full_store(TWO, "1x2", 4, MIB), ok(rows=2, pairs=1), ok(rows=2, pairs=1), hbad("PASS", "PASS", "OPEN", 2, identity_differs="-", pairs=1))

# D7. A doubled lookup cancelled an unpaired entry in the counter.
d7 = clone()
D7_M = [c for c, _ in ROWS[PI][2] if c > PI and c != PH][0]
_z = [x for x in d7[PH][2] if x[0] == PI][0]
d7[PH][2].insert(d7[PH][2].index(_z), _z)
add_diag(d7, PH, -_z[1])
_zm = [x for x in d7[D7_M][2] if x[0] == PI][0]
d7[D7_M][2].remove(_zm)
add_diag(d7, D7_M, _zm[1])
D7_BODY = ser(d7, PAY)
for _cap in ("470000000", "100", "13"):
    case("D7_doubled_lookup_cap_" + _cap, "D7", lambda: fixture_with(D7_BODY),
         bad("PASS", "PASS", upper_without_lower=0, lower_without_upper=0, columns_not_ascending=1, value_mismatch=0),
         bad("PASS", "PASS", upper_without_lower=0, lower_without_upper=0, columns_not_ascending=1, value_mismatch=0),
         hbad("PASS", "PASS", "FAIL", upper_without_lower=1, lower_repeated=1, lower_without_upper=0, columns_not_ascending=1, value_mismatch=0, identity_differs="payload_merkle"), cap=_cap)

# D8. Fields the tool only printed or left unread, each alone. The sweep below flips every bit.
for name, a, b, key in (
    ("sector_changed", "sector=Sx+Sy+", "sector=OTHER", "sector"),
    ("sector_missing", "|sector=Sx+Sy+", "", "sector"),
    ("chunk_changed", "chunk=16MiB", "chunk=1MiB", "chunk"),
    ("keys_changed", "keys_sha256=" + K, "keys_sha256=" + ZERO, "keys_sha256"),
    ("json_changed", "|json=0", "|json=1", "json"),
    ("extra_field", "|json=0", "|json=0|extra=1", "extra"),
):
    case("D8_" + name, "D8", edited((a, b)), ok(), ok(), hbad("PASS", "PASS", "FAIL", identity_differs=key))
_after = bytearray(base)
_after[EOL + 1] = 1
case("D8_byte_after_the_line", "D8", lambda: bytes(_after), ok(), ok(), hbad("PASS", "PASS", "FAIL", identity_differs="header_block"))
_end_block = bytearray(base)
_end_block[4095] = 1
case("D8_last_byte_of_the_block", "D8", lambda: bytes(_end_block), ok(), ok(), hbad("PASS", "PASS", "FAIL", identity_differs="header_block"))

# A control every executable must keep.
_one = bytearray(BODY)
_one[12] ^= 1
case("C_changed_byte_unrepaired", "C", lambda: block(LINE) + bytes(_one), stop("merkle"), stop("merkle"), stop("merkle"))


def text(w):
    return ",".join("%s=%s" % (k, w[k]) for k in sorted(w))


PRED = ["HARDENING_PREDICTION|case=%s|defect=%s|cap=%s|original=%s|corrected=%s|hardened=%s|json=0" % (c["name"], c["defect"], c["cap"] or "-", text(c["want"]["original"]).replace("|", "%7C"), text(c["want"]["corrected"]).replace("|", "%7C"), text(c["want"]["hardened"]).replace("|", "%7C")) for c in CASES]
PRED_SHA = sha("\n".join(PRED).encode())
FLIP_BITS = (EOL + 1 + FLIP_BYTES_AFTER_LINE) * 8
SUMMARY = "HARDENING_PREDICTION_SHA|cases=%d|outcomes=%d|flip_bits=%d|hardened_flips_at_exit_0=0|padding_mib=%d|old_peak_at_least_bytes=%d|hardened_peak_below_bytes=%d|base_sha256=%s|sha256=%s|json=0" % (len(CASES), 3 * len(CASES), FLIP_BITS, PAD_MIB, PAD_MIB * MIB, 32 * MIB, BASE_SHA, PRED_SHA)
if len({c["name"] for c in CASES}) != len(CASES):
    raise SystemExit("repeated case name")
if "--predict-only" in sys.argv:
    print("\n".join(PRED))
    print(SUMMARY)
    sys.exit(0)

os.makedirs(arg("--out"), exist_ok=True)
log = open(os.path.join(arg("--out"), "HARDENING-CONTROLS.hbp"), "w", encoding="utf-8", newline="\n")
TOOLS = [("original", arg("--original")), ("corrected", arg("--corrected")), ("hardened", arg("--hardened"))]
fails = 0
SHOWN = ("verdict", "header_entries", "whole_space_count", "header_rooms", "padding", "padding_nonzero", "store_identity", "identity_differs", "rows_read", "pairs", "value_mismatch", "lower_without_upper", "upper_without_lower", "lower_repeated", "columns_not_ascending", "cap_requested", "cap_entries", "passes", "flats", "flat_w_listed")


def emit(s):
    log.write(s + "\n")
    log.flush()


LAUNCHER = "import os,sys
pid=os.fork()
if pid==0:
    os.execv(sys.argv[2],sys.argv[2:])
_,st,ru=os.wait4(pid,0)
open(sys.argv[1],'w').write('%d %d'%(ru.ru_maxrss*1024,os.waitstatus_to_exitcode(st)))
"


def peak_of(exe, path, cap):
    """Runs the tool with its output in files, and returns (exit code, output, peak resident bytes). The peak is the OS's own count."""
    out_path = path + ".out"
    with open(out_path, "wb") as so:
        cmd = [exe, path, "0"] + ([cap] if cap else [])
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD), ("peak", ctypes.c_size_t), ("ws", ctypes.c_size_t), ("a", ctypes.c_size_t), ("b", ctypes.c_size_t), ("c", ctypes.c_size_t), ("d", ctypes.c_size_t), ("e", ctypes.c_size_t), ("f", ctypes.c_size_t)]

            k = ctypes.WinDLL("kernel32", use_last_error=True)
            k.K32GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
            k.K32GetProcessMemoryInfo.restype = wintypes.BOOL
            p = subprocess.Popen(cmd, stdout=so, stderr=subprocess.DEVNULL)
            p.wait()
            m = PMC()
            m.cb = ctypes.sizeof(PMC)
            if not k.K32GetProcessMemoryInfo(int(p._handle), ctypes.byref(m), m.cb):
                raise SystemExit("peak memory")
            peak, code = m.peak, p.returncode
        else:
            # ru_maxrss of a child carries the resident size of the process that forked it, and this script may hold the whole store.
            # A small launcher forks the tool instead. Measured by hosted-first-failed/instrument_test.py.
            res = path + ".peak"
            subprocess.run([sys.executable, "-I", "-S", "-c", LAUNCHER, res] + cmd, stdout=so, stderr=subprocess.DEVNULL, check=True)
            peak, code = (int(v) for v in open(res).read().split())
            os.remove(res)
    text_out = open(out_path, "r", encoding="utf-8", errors="replace").read()
    os.remove(out_path)
    return code, text_out, peak


def fields_of(output):
    rows = [x for x in output.splitlines() if x.startswith("ALLPAIRS|")]
    row = rows[-1] if rows else ""
    return row, dict(x.split("=", 1) for x in row.split("|") if "=" in x)


def meets(want, code, row, f):
    for k, v in want.items():
        if k == "exit":
            if code != v:
                return False
        elif k == "reason":
            if v not in f.get("reason", ""):
                return False
        elif k == "_line_min":
            if len(row) < v:
                return False
        elif k == "_line_max":
            if len(row) > v:
                return False
        elif f.get(k) != str(v):
            return False
    return True


for tool, exe in TOOLS:
    emit("HARDENING_TOOL|tool=%s|sha256=%s|json=0" % (tool, sha(open(exe, "rb").read())))
for row in PRED:
    emit(row)
emit(SUMMARY)

tmp = tempfile.mkdtemp(prefix="hardening-")
path = os.path.join(tmp, "case.bin")
tally = {t: dict(cases=0, met=0, gate_open_or_fail=0, gate_open_or_fail_exit0=0, stops=0, exit0=0, exit0_all_gates_pass=0, verdict_agrees_with_exit=0) for t, _ in TOOLS}
by_defect = {}
exit0_cases = []
lines_for_two_stores = {}
for c in CASES:
    data = c["build"]()
    open(path, "wb").write(data)
    del data
    d = by_defect.setdefault(c["defect"], {t: dict(cases=0, met=0, exit0=0) for t, _ in TOOLS})
    for tool, exe in TOOLS:
        want = c["want"][tool]
        code, output, peak = peak_of(exe, path, c["cap"])
        row, f = fields_of(output)
        met = meets(want, code, row, f)
        fails += 0 if met else 1
        t = tally[tool]
        t["cases"] += 1
        t["met"] += met
        gates = [f.get(k, "-") for k in ("header_entries", "whole_space_count", "header_rooms", "padding", "store_identity")]
        opened = "OPEN" in gates or "FAIL" in gates
        t["gate_open_or_fail"] += opened
        t["gate_open_or_fail_exit0"] += opened and code == 0
        t["stops"] += code == 1
        t["exit0"] += code == 0
        all_pass = all(g == "PASS" for g in gates) if tool == "hardened" else all(g == "PASS" for g in gates[:2])
        t["exit0_all_gates_pass"] += code == 0 and all_pass
        t["verdict_agrees_with_exit"] += (code == 0) == (f.get("verdict") == "PASS")
        d[tool]["cases"] += 1
        d[tool]["met"] += met
        d[tool]["exit0"] += code == 0
        if tool == "hardened" and code == 0:
            exit0_cases.append(c["name"])
        if c["name"] in ("clean", "D6_one_pair_changed_both_sides"):
            lines_for_two_stores.setdefault(tool, []).append("|".join(x for x in row.split("|") if not x.startswith("secs=")))
        reason = want.get("reason", "-")
        emit("HARDENING_CASE|case=%s|defect=%s|tool=%s|met=%d|exit=%d|%s|line_bytes_over_4096=%d|reason_has=%s|json=0" % (c["name"], c["defect"], tool, 1 if met else 0, code, "|".join("%s=%s" % (k, f.get(k, "-")) for k in SHOWN), 1 if len(row) > 4096 else 0, reason if reason in f.get("reason", "") else "-"))
        if c["name"] == "D4_padding_256MiB":
            limit_ok = peak >= PAD_MIB * MIB if tool != "hardened" else peak < 32 * MIB
            fails += 0 if limit_ok else 1
            emit("HARDENING_MEMORY|case=%s|tool=%s|peak_bytes=%d|old_at_least=%d|hardened_below=%d|met=%d|json=0" % (c["name"], tool, peak, PAD_MIB * MIB, 32 * MIB, 1 if limit_ok else 0))
        if not met:
            emit("HARDENING_DIFFERS|case=%s|tool=%s|exit=%d|want=%s|row=%s|json=0" % (c["name"], tool, code, text(want).replace("|", "%7C"), row[:600]))
os.remove(path)

# D6 again: two stores printing one line.
for tool, _ in TOOLS:
    same = len(lines_for_two_stores[tool]) == 2 and lines_for_two_stores[tool][0] == lines_for_two_stores[tool][1]
    want_same = tool != "hardened"
    fails += 0 if same == want_same else 1
    emit("HARDENING_TWO_STORES|tool=%s|one_line_for_two_stores=%d|met=%d|json=0" % (tool, 1 if same else 0, 1 if same == want_same else 0))

# D8: every bit of the header line, its newline and the next 64 bytes, flipped in place on one file.
flip_path = os.path.join(tmp, "flip.bin")
open(flip_path, "wb").write(base)
counts = {}


def sweep(tool, exe, bits):
    r = dict(exit0=0, exit1=0, exit2=0, other=0)
    with open(flip_path, "r+b") as fh:
        for bit in range(bits):
            at, mask = bit // 8, 1 << (bit % 8)
            fh.seek(at)
            old = fh.read(1)[0]
            fh.seek(at)
            fh.write(bytes([old ^ mask]))
            fh.flush()
            try:
                code = subprocess.run([exe, flip_path, "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300).returncode
            except subprocess.TimeoutExpired:
                code = -1
            key = "exit%d" % code if code in (0, 1, 2) else "other"
            r[key] += 1
            fh.seek(at)
            fh.write(bytes([old]))
            fh.flush()
    return r


for tool, exe in TOOLS:
    r = sweep(tool, exe, FLIP_BITS)
    counts[tool] = r
    good = r["other"] == 0 and (r["exit0"] == 0 if tool == "hardened" else r["exit0"] > 0)
    fails += 0 if good else 1
    emit("HARDENING_FLIP_SWEEP|tool=%s|bits=%d|exit0=%d|exit1=%d|exit2=%d|other=%d|met=%d|json=0" % (tool, FLIP_BITS, r["exit0"], r["exit1"], r["exit2"], r["other"], 1 if good else 0))
fewer = counts["corrected"]["exit0"] < counts["original"]["exit0"]
fails += 0 if fewer else 1
emit("HARDENING_FLIP_ORDER|original_exit0=%d|corrected_exit0=%d|hardened_exit0=%d|corrected_below_original=%d|json=0" % (counts["original"]["exit0"], counts["corrected"]["exit0"], counts["hardened"]["exit0"], 1 if fewer else 0))
if "--full-block" in sys.argv:
    r = sweep("hardened", arg("--hardened"), 4096 * 8)
    good = r["exit0"] == 0 and r["other"] == 0
    fails += 0 if good else 1
    emit("HARDENING_FULL_BLOCK|tool=hardened|bits=32768|exit0=%d|exit1=%d|exit2=%d|other=%d|met=%d|json=0" % (r["exit0"], r["exit1"], r["exit2"], r["other"], 1 if good else 0))
os.remove(flip_path)
os.rmdir(tmp)

for defect in sorted(by_defect):
    d = by_defect[defect]
    emit("DEFECT_SWEEP|defect=%s|cases=%d|original_met=%d|corrected_met=%d|hardened_met=%d|original_exit0=%d|corrected_exit0=%d|hardened_exit0=%d|json=0" % (defect, d["original"]["cases"], d["original"]["met"], d["corrected"]["met"], d["hardened"]["met"], d["original"]["exit0"], d["corrected"]["exit0"], d["hardened"]["exit0"]))
for tool, _ in TOOLS:
    emit("HARDENING_SWEEP|tool=%s|%s|json=0" % (tool, "|".join("%s=%d" % kv for kv in tally[tool].items())))
h = tally["hardened"]
allowed = {"clean", "D5_cap_zero", "D5_cap_max", "C_cap_one"}
closed = h["gate_open_or_fail_exit0"] == 0 and h["exit0"] == h["exit0_all_gates_pass"] and h["verdict_agrees_with_exit"] == h["cases"] and set(exit0_cases) == allowed
fails += 0 if closed else 1
emit("HARDENED_FAILS_CLOSED|every_open_or_fail_gives_verdict_fail_and_nonzero_exit=%d|gate_open_or_fail=%d|exit0=%d|exit0_only_on_the_clean_store_at_three_caps_and_the_default=%d|json=0" % (1 if closed else 0, h["gate_open_or_fail"], h["exit0"], 1 if set(exit0_cases) == allowed else 0))
emit("HARDENING_CONTROLS_DONE|failed=%d|json=0" % fails)
log.close()
print("HARDENING_CONTROLS_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
