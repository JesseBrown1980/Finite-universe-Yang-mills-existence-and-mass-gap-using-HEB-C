# Tries to reach exit 0 on the corrected allpairs with a count gate at OPEN or FAIL, or with no rows read. Each case states its exit before it runs, and
# REVIEW.hbp holds the whole list's hash before this runs. Runs the recorded pin executable and this seat's build of the same source, at default cap and cap 1.
# usage: attack_gates.py EXE_A EXE_B FIXTURE_GZ OUT_HBP   Integer only, json=0.
import gzip, hashlib, os, struct, subprocess, sys

EXE_A, EXE_B, GZ, OUT = sys.argv[1:5]
TMP = os.path.dirname(os.path.abspath(OUT)) + "/gates.bin"
base = gzip.open(GZ, "rb").read()
eol = base.index(b"\n")
LINE = base[:eol]
PAY = base[4096:]
FIELDS = LINE.split(b"|")
log = open(OUT, "w", encoding="utf-8", newline="\n")
bad = 0
exit0_with_open_or_fail = 0
exit0_no_rows = 0


def sha(b):
    return hashlib.sha256(b).hexdigest()


def merkle(pl):
    return sha("".join(sha(pl[i:i + (16 << 20)]) for i in range(0, len(pl), 16 << 20)).encode())


def with_line(line, after=b"", pay=PAY):
    head = line + b"\n" + after
    return head.ljust(4096, b"\0") + pay


def sub(a, b, line=LINE):
    assert line.count(a) == 1, a
    return line.replace(a, b)


def run(exe, cap, data):
    open(TMP, "wb").write(data)
    r = subprocess.run([exe, TMP, "0"] + ([cap] if cap else []), capture_output=True, text=True)
    last = ([x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")] or [""])[-1]
    f = dict(x.split("=", 1) for x in last.split("|") if "=" in x)
    return r.returncode, f


CASES = []


def case(name, want, data):
    CASES.append((name, want, data))


# Written forms of entries=, nl= and L=. Each must leave its gate at OPEN, so exit 2.
for tag, form in [("trailing_space", b"entries=2607 "), ("leading_space", b"entries= 2607"), ("full_width", "entries=２６０７".encode()), ("cr", b"entries=2607\r"), ("hex", b"entries=0xA2F"), ("dot", b"entries=2607.0"), ("exp", b"entries=2.607e3"), ("second_eq", b"entries=2607=")]:
    case("entries_" + tag, 2, with_line(sub(b"entries=2607", form)))
for tag, form in [("key_space", b"entries =2607"), ("space_key", b" entries=2607"), ("upper", b"ENTRIES=2607"), ("no_eq", b"entries2607"), ("nul_key", b"\0entries=2607"), ("bad_utf8_key", b"entries\xff=2607")]:
    case("entries_key_" + tag, 2, with_line(sub(b"entries=2607", form)))
for tag, form in [("space", b"nl=8 "), ("full_width", "nl=８".encode()), ("dot", b"nl=8.0"), ("hex", b"nl=0x8"), ("upper", b"NL=8"), ("nul", b"nl=8\0")]:
    case("nl_" + tag, 2, with_line(sub(b"nl=8", form)))
for tag, form in [("upper_x", b"L=2X2"), ("space", b"L=2x2 "), ("times", "L=2×2".encode()), ("three", b"L=2x2x1"), ("key_space", b" L=2x2"), ("empty_side", b"L=x4"), ("zero", b"L=0x2")]:
    case("L_" + tag, 2, with_line(sub(b"L=2x2", form)))
case("entries_true_count_off_by_one", 2, with_line(sub(b"entries=2607", b"entries=2608")))
case("both_gates_gone", 2, with_line(sub(b"|nl=8", b"", sub(b"|entries=2607", b""))))
case("gates_only_after_the_newline", 2, with_line(sub(b"|nl=8", b"", sub(b"|entries=2607", b"")), after=b"entries=2607|nl=8|"))
# A real header with an OPEN gate and every counter clean, at each field position.
fs = [x for x in FIELDS[1:] if not x.startswith(b"entries=")]
for at in (0, 3, len(fs)):
    case("entries_absent_order_%d" % at, 2, with_line(b"|".join([FIELDS[0]] + fs[:at] + [b"x=1"] + fs[at:])))
# No rows read. Each must stop, exit 1.
for tag, n in [("zero", b"n=0"), ("double_zero", b"n=00"), ("plus_zero", b"n=+0"), ("minus_zero", b"n=-0"), ("empty", b"n=")]:
    case("n_" + tag, 1, with_line(sub(b"|n=211|", b"|" + n + b"|")))
case("n_zero_full_counts_zero", 1, with_line(sub(b"entries=2607", b"entries=0", sub(b"|n=211|", b"|n=0|"))))
case("n_zero_lattice_of_one_code", 1, with_line(sub(b"L=2x2", b"L=1x1", sub(b"nl=8", b"nl=2", sub(b"entries=2607", b"entries=0", sub(b"|n=211|", b"|n=0|"))))))
case("n_zero_minimal", 1, b"YMROOMHDR|n=0|payload_bytes=0|w_self_adjoint=PASS\n".ljust(4096, b"\0"))
case("n_zero_payload_past_eof", 1, b"YMROOMHDR|L=1x1|nl=2|entries=0|n=0|payload_bytes=99999999999|payload_merkle=00|w_self_adjoint=PASS\n".ljust(4096, b"\0"))
case("n_one_payload_zero", 1, with_line(sub(b"payload_bytes=1044480", b"payload_bytes=0", sub(b"|n=211|", b"|n=1|"))))
case("n_u32_max", 1, with_line(sub(b"|n=211|", b"|n=4294967295|")))
case("n_2p32", 1, with_line(sub(b"|n=211|", b"|n=4294967296|")))
case("n_u64_max", 1, with_line(sub(b"|n=211|", b"|n=18446744073709551615|")))
case("n_2p64", 1, with_line(sub(b"|n=211|", b"|n=18446744073709551616|")))
# Repeats. Each must stop, exit 1, in a field the tool reads or one it leaves unread.
for k, v in [(b"n", b"211"), (b"entries", b"2607"), (b"nl", b"8"), (b"L", b"2x2"), (b"payload_bytes", b"1044480"), (b"w_self_adjoint", b"PASS"), (b"chunk", b"16MiB"), (b"json", b"0"), (b"sector", b"x"), (b"unknown", b"1")]:
    case("repeat_same_" + k.decode(), 1, with_line(LINE + b"|" + k + b"=" + v + (b"|" + k + b"=" + v if k == b"unknown" else b"")))
case("repeat_empty_key", 1, with_line(LINE + b"|=1|=2"))
case("repeat_at_the_end_after_cr", 1, with_line(LINE + b"|entries=1\r"))
# Forms that pass by design, stated here because a reader may ask. Rows untouched, gates at PASS.
case("clean", 0, with_line(LINE))
case("entries_moved_to_the_end", 0, with_line(sub(b"|entries=2607", b"") + b"|entries=2607"))
case("fields_reversed", 0, with_line(b"|".join([FIELDS[0]] + FIELDS[:0:-1])))
case("crlf_line_end", 0, with_line(LINE + b"\r"))
case("contradiction_after_the_newline", 0, with_line(LINE, after=b"entries=1|nl=7|n=0|"))
case("look_alike_key_unread", 0, with_line(LINE + b"|n =5|entries =1|\0nl=7"))
case("parts_with_no_equals_repeat", 0, with_line(LINE + b"|n|n|entries|entries"))
case("same_sites_other_label", 0, with_line(sub(b"L=2x2", b"L=1x4")))
case("bad_utf8_in_unread_value", 0, with_line(sub(b"sector=Sx+Sy+", b"sector=\xff\xfe")))
# Real rows under a false label, with every weight times 6, merkle repaired: sum_w 46656 = 6^6, so V=5 passes both gates. Open under D6 and D8.
rows, p = [], 0
n = 211
buf = bytearray(PAY)
for _ in range(n):
    w, mag, cnt = struct.unpack_from("<IHH", buf, p)
    struct.pack_into("<I", buf, p, w * 6)
    p += 8 + 8 * cnt
m6 = merkle(bytes(buf))
old = LINE.split(b"payload_merkle=")[1].split(b"|")[0]
case("weights_times_6_label_1x5", 0, with_line(sub(old, m6.encode(), sub(b"nl=8", b"nl=10", sub(b"L=2x2", b"L=1x5"))), pay=bytes(buf)))

for name, want, data in CASES:
    rows = []
    for tool, exe in (("pin", EXE_A), ("own", EXE_B)):
        for cap in (None, "1"):
            code, f = run(exe, cap, data)
            e, c = f.get("header_entries", "-"), f.get("whole_space_count", "-")
            rows.append((tool, cap or "default", code, f.get("verdict", "-"), e, c, f.get("rows_read", "-")))
            if code == 0 and ("OPEN" in (e, c) or "FAIL" in (e, c)):
                exit0_with_open_or_fail += 1
            if code == 0 and f.get("rows_read", "0") in ("0", "-"):
                exit0_no_rows += 1
    ok = all(r[2] == want for r in rows) and len({r[2:] for r in rows}) == 1
    bad += 0 if ok else 1
    r = rows[0]
    log.write("GATE_ATTACK|case=%s|want_exit=%d|exit=%d|verdict=%s|header_entries=%s|whole_space_count=%s|rows_read=%s|four_runs_agree=%d|met=%d|sha16=%s|json=0\n" % (name, want, r[2], r[3], r[4], r[5], r[6], int(len({x[2:] for x in rows}) == 1), int(ok), sha(data)[:16]))
    log.flush()
os.remove(TMP)
log.write("GATE_ATTACK_DONE|cases=%d|runs=%d|not_met=%d|exit0_with_open_or_fail=%d|exit0_with_no_rows=%d|json=0\n" % (len(CASES), 4 * len(CASES), bad, exit0_with_open_or_fail, exit0_no_rows))
log.close()
print("GATE_ATTACK_DONE|cases=%d|runs=%d|not_met=%d|exit0_with_open_or_fail=%d|exit0_with_no_rows=%d|json=0" % (len(CASES), 4 * len(CASES), bad, exit0_with_open_or_fail, exit0_no_rows))
sys.exit(1 if bad or exit0_with_open_or_fail or exit0_no_rows else 0)
