# Judges a 3x4 run of allpairs against the requirements the operator set before it ran, and against the original run at 8faadb0.
# Written before that run ended. Fails closed: every requirement prints a row, and any that does not hold prints met=0 and exits 1.
#
# usage: compare_pin_run.py ORIGINAL_OUT NEW_OUT [EXIT_CODE STDERR_FILE]
#   ORIGINAL_OUT  allpairs/ALLPAIRS-3x4.out, the run at 8faadb0
#   NEW_OUT       the output of the run being judged
#   EXIT_CODE     its exit code, if known
#   STDERR_FILE   its standard error, if kept
# Allowed to differ from the original: secs= on each row. Executable hashes do not appear in these rows. Integer only, json=0.
import hashlib, os, re, sys

ORIGINAL, NEW = sys.argv[1], sys.argv[2]
PAIRS, ROWS, ENTRIES, DIAG, SUM_W = 1632625631, 45508080, 3310759342, 45508080, 13060694016
WINDOWS = [(0, 9065182), (9065182, 19726083), (19726083, 34139976), (34139976, 45508080)]
fails = 0


def read(path):
    return open(path, "rb").read().decode("utf-8", "replace").replace("\r\n", "\n")


def fields(row):
    return dict(x.split("=", 1) for x in row.split("|") if "=" in x)


def met(label, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    print("PIN_REQUIREMENT|%s|met=%d|%sjson=0" % (label, 1 if ok else 0, detail + "|" if detail else ""))


def norm(text):
    return re.sub(r"\|secs=[0-9]+\|", "|secs=S|", text)


orig_text, new_text = read(ORIGINAL), read(NEW)
new_rows = new_text.splitlines()
last = [r for r in new_rows if r.startswith("ALLPAIRS|")]
passes = [fields(r) for r in new_rows if r.startswith("ALLPAIRS_PASS|")]
detail_rows = [r for r in new_rows if r.startswith("ALLPAIRS_BAD|")]
met("one_final_row", len(last) == 1, "final_rows=%d" % len(last))
f = fields(last[-1]) if last else {}
num = lambda k: int(f.get(k, "-1"))

# Required by name.
met("header_entries", f.get("header_entries") == "PASS", "value=%s" % f.get("header_entries", "-"))
met("whole_space_count", f.get("whole_space_count") == "PASS", "value=%s" % f.get("whole_space_count", "-"))
met("verdict", f.get("verdict") == "PASS", "value=%s" % f.get("verdict", "-"))

# The complete store.
for key, want in (("n", ROWS), ("rows_read", ROWS), ("entries", ENTRIES), ("diag", DIAG), ("pairs", PAIRS), ("sum_w", SUM_W), ("codes", SUM_W)):
    met("count_" + key, num(key) == want, "value=%d|want=%d" % (num(key), want))
met("lattice", f.get("L") == "3x4" and f.get("sector") == "Sx+Sy+", "L=%s|sector=%s" % (f.get("L", "-"), f.get("sector", "-")))
met("pairs_arithmetic", PAIRS == (ENTRIES - DIAG) // 2 and (ENTRIES - DIAG) % 2 == 0)

# Zero mismatches, zero unpaired entries.
for key in ("value_mismatch", "lower_without_upper", "upper_without_lower"):
    met("zero_" + key, num(key) == 0, "value=%d" % num(key))
met("no_detail_rows", not detail_rows, "rows=%d" % len(detail_rows))

# All structural checks.
for key in ("columns_not_ascending", "column_out_of_range", "zero_z", "positive_offdiag", "row_sum_nonzero", "zero_weight", "missing_diag"):
    met("zero_" + key, num(key) == 0, "value=%d" % num(key))

# Merkle verification on every pass, and windows that cover every row with nothing left out.
met("pass_count", len(passes) == 4 and num("passes") == 4, "rows=%d|passes=%d" % (len(passes), num("passes")))
met("merkle_each_pass", bool(passes) and all(p.get("merkle") == "PASS" for p in passes) and f.get("merkle") == "PASS", "passes_with_merkle_pass=%d" % sum(p.get("merkle") == "PASS" for p in passes))
met("windows", [(int(p["rows_from"]), int(p["rows_to"])) for p in passes] == WINDOWS)
met("each_upper_entry_stored_looked_up_and_found_once", sum(int(p["upper_stored"]) for p in passes) == sum(int(p["lookups"]) for p in passes) == sum(int(p["found"]) for p in passes) == PAIRS and all(p["upper_stored"] == p["found"] for p in passes), "stored=%d" % sum(int(p["upper_stored"]) for p in passes))

# Against the original run.
same = norm(new_text) == norm(orig_text)
met("every_row_identical_to_the_original_apart_from_secs", same, "original_normalised_sha256=%s|new_normalised_sha256=%s" % (hashlib.sha256(norm(orig_text).encode()).hexdigest(), hashlib.sha256(norm(new_text).encode()).hexdigest()))
if not same:
    o, n = norm(orig_text).splitlines(), norm(new_text).splitlines()
    print("PIN_DIFFERENCE|original_rows=%d|new_rows=%d|differing_rows=%d|json=0" % (len(o), len(n), sum(a != b for a, b in zip(o, n)) + abs(len(o) - len(n))))

# The process, when known.
if len(sys.argv) > 3:
    met("exit_code", sys.argv[3] == "0", "value=%s" % sys.argv[3])
if len(sys.argv) > 4:
    size = os.path.getsize(sys.argv[4])
    met("stderr_empty", size == 0, "bytes=%d" % size)

print("PIN_OUTPUT|new_sha256=%s|bytes=%d|rows=%d|pass_secs=%s|secs=%s|json=0" % (hashlib.sha256(new_text.encode()).hexdigest(), len(new_text.encode()), len(new_rows), ",".join(p.get("secs", "-") for p in passes), f.get("secs", "-")))
print("PIN_COMPARE_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
