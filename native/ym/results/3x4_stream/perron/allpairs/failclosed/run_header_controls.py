# Puts one header change at a time on a copy of the 2x2 store and runs allpairs on each copy, with every outcome predicted below for the
# original executable and the corrected one. The rows and the merkle stay as they are, so the header is the only difference.
#
# usage: run_header_controls.py --base fixture-2x2.rooms.gz --out DIR [--predict-only] --original EXE --corrected EXE
#
# Writes HEADER-CONTROLS.hbp into DIR. A case holds when the exit code, the verdict, both count gates and the rows read all match, or, for a
# run that stops early, when the exit code and the reason match. Exits 1 if any case differs. Integer only, json=0.
import gzip, hashlib, os, subprocess, sys, tempfile

BASE_SHA = "b31e730606db130585f9560f7adab87444d744876c3a8e36f6f9ef2bf0aa431f"


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def sha(b):
    return hashlib.sha256(b).hexdigest()


base = gzip.open(arg("--base"), "rb").read()
if sha(base) != BASE_SHA:
    raise SystemExit("fixture hash")
end = base.index(b"\n")
if base[:4096].count(b"\n") != 1 or any(base[end + 1:4096]):
    raise SystemExit("fixture header layout")
LINE = base[:end].decode()
FLD = dict(x.split("=", 1) for x in LINE.split("|") if "=" in x)
M, K = FLD["payload_merkle"], FLD["keys_sha256"]
ZERO = "0" * 64


def ok(e="PASS", c="PASS", rows=211):
    return (0, "PASS", e, c, rows, "")


def bad(e, c, rows=211):
    return (2, "FAIL", e, c, rows, "")


def stop(reason):
    return (1, "FAIL", "-", "-", "-", reason)


CANON = "outside canonical form"
CASES = [
    ("clean", [], ok(), ok()),
    # header_entries reads OPEN.
    ("entries_missing", [("|entries=2607", "")], ok("OPEN"), bad("OPEN", "PASS")),
    ("entries_empty", [("entries=2607", "entries=")], ok("OPEN"), bad("OPEN", "PASS")),
    ("entries_word", [("entries=2607", "entries=abc")], ok("OPEN"), bad("OPEN", "PASS")),
    ("entries_negative", [("entries=2607", "entries=-2607")], ok("OPEN"), bad("OPEN", "PASS")),
    ("entries_overflow_u64", [("entries=2607", "entries=18446744073709551616")], ok("OPEN"), bad("OPEN", "PASS")),
    ("entries_plus", [("entries=2607", "entries=+2607")], ok(), bad("OPEN", "PASS")),
    ("entries_leading_zero", [("entries=2607", "entries=02607")], ok(), bad("OPEN", "PASS")),
    # header_entries reads FAIL.
    ("entries_wrong", [("entries=2607", "entries=2606")], bad("FAIL", "PASS"), bad("FAIL", "PASS")),
    # whole_space_count reads OPEN, from nl=.
    ("nl_missing", [("|nl=8", "")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("nl_empty", [("nl=8", "nl=")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("nl_word", [("nl=8", "nl=abc")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("nl_negative", [("nl=8", "nl=-8")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("nl_inconsistent", [("nl=8", "nl=7")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("nl_plus", [("nl=8", "nl=+8")], ok(), bad("PASS", "OPEN")),
    ("nl_leading_zero", [("nl=8", "nl=08")], ok(), bad("PASS", "OPEN")),
    # whole_space_count reads OPEN, from L=.
    ("L_missing", [("L=2x2|", "")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("L_empty", [("L=2x2", "L=")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("L_no_x", [("L=2x2", "L=4")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("L_word", [("L=2x2", "L=axb")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("L_three_sizes", [("L=2x2", "L=2x2x2")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("L_plus", [("L=2x2", "L=+2x2")], ok(), bad("PASS", "OPEN")),
    ("L_leading_zero", [("L=2x2", "L=02x2")], ok(), bad("PASS", "OPEN")),
    ("L_zero_size", [("L=2x2", "L=0x4"), ("nl=8", "nl=0")], bad("PASS", "FAIL"), bad("PASS", "OPEN")),
    ("L_sites_overflow_u32", [("L=2x2", "L=65536x65536")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("L_links_overflow_u32", [("L=2x2", "L=65536x32768")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    ("L_codes_overflow_u128", [("L=2x2", "L=7x7"), ("nl=8", "nl=98")], ok("PASS", "OPEN"), bad("PASS", "OPEN")),
    # whole_space_count reads FAIL.
    ("L_other_lattice", [("L=2x2", "L=2x3"), ("nl=8", "nl=12")], bad("PASS", "FAIL"), bad("PASS", "FAIL")),
    # Both count gates read OPEN.
    ("both_missing", [("|entries=2607", ""), ("|nl=8", "")], ok("OPEN", "OPEN"), bad("OPEN", "OPEN")),
    # A repeated key gives two answers. The original reads the first.
    ("entries_repeated_same", [("entries=2607", "entries=2607|entries=2607")], ok(), stop("header repeats entries=")),
    ("entries_repeated_other", [("entries=2607", "entries=2607|entries=1")], ok(), stop("header repeats entries=")),
    ("nl_repeated_other", [("nl=8", "nl=8|nl=7")], ok(), stop("header repeats nl=")),
    ("L_repeated_other", [("L=2x2", "L=2x2|L=2x3")], ok(), stop("header repeats L=")),
    ("n_repeated_other", [("|n=211|", "|n=211|n=1|")], ok(), stop("header repeats n=")),
    ("payload_repeated_other", [("payload_bytes=1044480", "payload_bytes=1044480|payload_bytes=8")], ok(), stop("header repeats payload_bytes=")),
    ("merkle_repeated_other", [("payload_merkle=" + M, "payload_merkle=" + M + "|payload_merkle=" + ZERO)], ok(), stop("header repeats payload_merkle=")),
    ("w_repeated_other", [("w_self_adjoint=PASS", "w_self_adjoint=PASS|w_self_adjoint=FAIL")], ok(), stop("header repeats w_self_adjoint=")),
    # n= and payload_bytes= outside canonical form.
    ("n_plus", [("|n=211|", "|n=+211|")], ok(), stop(CANON)),
    ("n_leading_zero", [("|n=211|", "|n=0211|")], ok(), stop(CANON)),
    ("payload_plus", [("payload_bytes=1044480", "payload_bytes=+1044480")], ok(), stop(CANON)),
    ("payload_leading_zero", [("payload_bytes=1044480", "payload_bytes=01044480")], ok(), stop(CANON)),
    # A store with no rows. The original prints merkle=PASS with no merkle computed.
    ("n_zero", [("|n=211|", "|n=0|")], bad("FAIL", "FAIL", 0), stop("n is 0")),
    ("n_zero_no_counts", [("|n=211|", "|n=0|"), ("|entries=2607", ""), ("|nl=8", "")], ok("OPEN", "OPEN", 0), stop("n is 0")),
    ("n_zero_other_merkle", [("|n=211|", "|n=0|"), ("|entries=2607", ""), ("|nl=8", ""), ("payload_merkle=" + M, "payload_merkle=" + ZERO)], ok("OPEN", "OPEN", 0), stop("n is 0")),
    ("empty_minimal_header", "YMROOMHDR|n=0|payload_bytes=0|w_self_adjoint=PASS|json=0", ok("OPEN", "OPEN", 0), stop("n is 0")),
    # n= that differs from the rows. The padding past the last row reads as a row of zeros.
    ("n_below_rows", [("|n=211|", "|n=210|")], bad("FAIL", "FAIL", 210), bad("FAIL", "FAIL", 210)),
    ("n_above_rows", [("|n=211|", "|n=212|")], bad("PASS", "PASS", 212), bad("PASS", "PASS", 212)),
    ("n_above_u32", [("|n=211|", "|n=4294967296|")], stop("n does not fit"), stop("n does not fit")),
    # Fields read through roomio, which stop both executables.
    ("n_missing", [("|n=211", "")], stop("missing n="), stop("missing n=")),
    ("n_word", [("|n=211|", "|n=abc|")], stop("missing n="), stop("missing n=")),
    ("payload_missing", [("|payload_bytes=1044480", "")], stop("missing payload_bytes="), stop("missing payload_bytes=")),
    ("payload_word", [("payload_bytes=1044480", "payload_bytes=abc")], stop("missing payload_bytes="), stop("missing payload_bytes=")),
    ("payload_short", [("payload_bytes=1044480", "payload_bytes=1044472")], stop("merkle"), stop("merkle")),
    ("payload_long", [("payload_bytes=1044480", "payload_bytes=1044488")], stop("read rooms"), stop("read rooms")),
    ("merkle_missing", [("|payload_merkle=" + M, "")], stop("merkle"), stop("merkle")),
    ("merkle_changed", [("payload_merkle=" + M, "payload_merkle=" + ZERO)], stop("merkle"), stop("merkle")),
    ("w_fail", [("w_self_adjoint=PASS", "w_self_adjoint=FAIL")], stop("not a YMROOMHDR"), stop("not a YMROOMHDR")),
    ("w_missing", [("|w_self_adjoint=PASS", "")], stop("not a YMROOMHDR"), stop("not a YMROOMHDR")),
    ("magic_changed", [("YMROOMHDR|", "YMROOMHDX|")], stop("not a YMROOMHDR"), stop("not a YMROOMHDR")),
    ("no_line_end", b"no_line_end", stop("no header line"), stop("no header line")),
    ("short_file", b"short_file", stop("read header"), stop("read header")),
    # The fields this tool leaves unread: sector= it prints, and the rest it never looks at.
    ("unread_fields_removed", [("|sector=Sx+Sy+", ""), ("|rooms=2818", ""), ("|stream_bytes=1048576", ""), ("|chunk=16MiB", ""), ("|keys_sha256=" + K, ""), ("|json=0", "")], ok(), ok()),
]


def esc(s):
    return s.replace("|", "%7C")


def text(p):
    return "exit=%d,verdict=%s,header_entries=%s,whole_space_count=%s,rows_read=%s,reason=%s" % (p[0], p[1], p[2], p[3], p[4], p[5] or "-")


def describe(edit):
    if isinstance(edit, bytes):
        return edit.decode()
    if isinstance(edit, str):
        return "whole_line=" + esc(edit)
    return ";".join("%s->%s" % (esc(a), esc(b)) for a, b in edit) or "none"


PRED = ["HEADER_PREDICTION|case=%s|edit=%s|original=%s|corrected=%s|json=0" % (name, describe(edit), text(orig), text(corr)) for name, edit, orig, corr in CASES]
PRED_SHA = sha("\n".join(PRED).encode())
SUMMARY = "HEADER_PREDICTION_SHA|cases=%d|base_sha256=%s|sha256=%s|json=0" % (len(CASES), BASE_SHA, PRED_SHA)
if len({c[0] for c in CASES}) != len(CASES):
    raise SystemExit("repeated case name")
if "--predict-only" in sys.argv:
    print("\n".join(PRED))
    print(SUMMARY)
    sys.exit(0)

os.makedirs(arg("--out"), exist_ok=True)
log = open(os.path.join(arg("--out"), "HEADER-CONTROLS.hbp"), "w", encoding="utf-8", newline="\n")
TOOLS = [("original", arg("--original")), ("corrected", arg("--corrected"))]
fails = 0


def emit(s):
    log.write(s + "\n")
    log.flush()


def store_for(edit):
    if edit == b"short_file":
        return base[:100]
    if edit == b"no_line_end":
        b = bytearray(base)
        b[end] = ord("x")
        return bytes(b)
    if isinstance(edit, str):
        line = edit
    else:
        line = LINE
        for a, b in edit:
            if line.count(a) != 1:
                raise SystemExit("edit does not match once: " + a)
            line = line.replace(a, b, 1)
    head = line.encode() + b"\n"
    if len(head) > 4096:
        raise SystemExit("header length")
    return head + bytes(4096 - len(head)) + base[4096:]


def run(exe, path):
    r = subprocess.run([exe, path, "0"], capture_output=True, text=True)
    rows = [x for x in r.stdout.splitlines() if x.startswith("ALLPAIRS|")]
    row = rows[-1] if rows else ""
    return r.returncode, row, dict(x.split("=", 1) for x in row.split("|") if "=" in x)


for tool, exe in TOOLS:
    emit("HEADER_TOOL|tool=%s|sha256=%s|json=0" % (tool, sha(open(exe, "rb").read())))
for row in PRED:
    emit(row)
emit(SUMMARY)

tmp = tempfile.mkdtemp(prefix="header-")
path = os.path.join(tmp, "case.bin")
tally = {t: dict(cases=0, met=0, gate_open=0, gate_open_exit0=0, gate_fail=0, gate_fail_exit0=0, stops=0, exit0=0, exit0_both_pass=0, verdict_agrees_with_exit=0) for t, _ in TOOLS}
for name, edit, orig, corr in CASES:
    open(path, "wb").write(store_for(edit))
    for tool, exe in TOOLS:
        want = orig if tool == "original" else corr
        code, row, f = run(exe, path)
        e, c, rows = f.get("header_entries", "-"), f.get("whole_space_count", "-"), f.get("rows_read", "-")
        reason = f.get("reason", "")
        if want[0] == 1:
            met = code == 1 and f.get("verdict") == "FAIL" and want[5] in reason
        else:
            met = code == want[0] and f.get("verdict") == want[1] and e == want[2] and c == want[3] and rows == str(want[4])
        fails += 0 if met else 1
        t = tally[tool]
        t["cases"] += 1
        t["met"] += met
        opened = "OPEN" in (e, c)
        failed = "FAIL" in (e, c)
        t["gate_open"] += opened
        t["gate_open_exit0"] += opened and code == 0
        t["gate_fail"] += failed
        t["gate_fail_exit0"] += failed and code == 0
        t["stops"] += code == 1
        t["exit0"] += code == 0
        t["exit0_both_pass"] += code == 0 and e == "PASS" and c == "PASS"
        t["verdict_agrees_with_exit"] += (code == 0) == (f.get("verdict") == "PASS")
        emit("HEADER_CASE|case=%s|tool=%s|met=%d|exit=%d|verdict=%s|header_entries=%s|whole_space_count=%s|rows_read=%s|pairs=%s|merkle=%s|reason_has=%s|json=0" % (
            name, tool, 1 if met else 0, code, f.get("verdict", "-"), e, c, rows, f.get("pairs", "-"), f.get("merkle", "-"), (want[5] if want[5] and want[5] in reason else "-")))
        if not met:
            emit("HEADER_DIFFERS|case=%s|tool=%s|row=%s|json=0" % (name, tool, row[:400]))
os.remove(path)
os.rmdir(tmp)
for tool, _ in TOOLS:
    t = tally[tool]
    emit("HEADER_SWEEP|tool=%s|%s|json=0" % (tool, "|".join("%s=%d" % kv for kv in t.items())))
c = tally["corrected"]
closed = c["gate_open_exit0"] == 0 and c["gate_fail_exit0"] == 0 and c["exit0"] == c["exit0_both_pass"] and c["verdict_agrees_with_exit"] == c["cases"] and tally["original"]["verdict_agrees_with_exit"] == tally["original"]["cases"]
fails += 0 if closed else 1
emit("HEADER_CORRECTED_FAILS_CLOSED|every_open_or_fail_gives_verdict_fail_and_nonzero_exit=%d|gate_open=%d|gate_fail=%d|exit0=%d|exit0_both_pass=%d|json=0" % (1 if closed else 0, c["gate_open"], c["gate_fail"], c["exit0"], c["exit0_both_pass"]))
emit("HEADER_CONTROLS_DONE|failed=%d|json=0" % fails)
log.close()
print("HEADER_CONTROLS_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
