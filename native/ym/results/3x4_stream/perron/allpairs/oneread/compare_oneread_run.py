# Judges a 3x4 run of allpairs with one read of its header block, against the operator's requirements, the original run at 8faadb0 and the text of the hardened run at 9c2c7e6.
# From hardened/compare_hardened_run.py, with R13 of the second seat's review closed: no row may repeat a key, and the text of every row must match, with secs and exe_sha256 blanked. Committed before that run starts.
# Every requirement prints a row, and any that does not hold prints met=0 and exits 1.
#
# usage: compare_oneread_run.py ORIGINAL_OUT NEW_OUT EXIT_CODE STDERR_FILE [--exe EXE]
#   ORIGINAL_OUT  allpairs/ALLPAIRS-3x4.out, refused unless its hash is the one pinned here
#   NEW_OUT       the output of the run being judged
#   EXIT_CODE     its exit code
#   STDERR_FILE   its standard error
#   EXE           when given, the file whose hash the output must name
#
# What this adds beyond the original run: the five gates, the store's two hashes, every payload byte accounted for, each entry answered once.
# Allowed to differ from the original: secs= on each row, and fields the original does not have. What it cannot show: that a run happened, since anyone who can
# write the file can write these rows. A replay shows that. Integer only, json=0.
import hashlib, os, re, sys

ORIGINAL_SHA = "b0b172204fb1cbadeacec6dc58576f6436179225d5f0ea03163ba16227c3f271"
ORIGINAL, NEW, CODE, STDERR = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
PAIRS, ROWS, ENTRIES, ROOMS = 1632625631, 45508080, 3310759342, 3356267422
WINDOWS = [(0, 9065182), (9065182, 19726083), (19726083, 34139976), (34139976, 45508080)]
MERKLE = "ec03c5f8ea5abd37ed8f80e0e9e7f00e37840a753f33a1008fbd090b18072a0b"
HEADER = "65dd63a89d7e1a7cdd3e7876c834c6698a01081ea7a63738e305890bee9e6a21"
# The rows of the hardened run at 9c2c7e6 with offset=0 added, secs and exe_sha256 blanked.
NORMALISED = "b110999535b6dbdd2fdb112dd6cfd7f82af75ea1e05d015af046b7549168b00d"
fails = 0


def read(path):
    return open(path, "rb").read()


def fields(row):
    return dict(x.split("=", 1) for x in row.split("|") if "=" in x)


def met(label, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    print("ONEREAD_REQUIREMENT|%s|met=%d|%sjson=0" % (label, 1 if ok else 0, detail + "|" if detail else ""))


raw_original = read(ORIGINAL)
if hashlib.sha256(raw_original).hexdigest() != ORIGINAL_SHA:
    print("ONEREAD_REQUIREMENT|original_run_is_the_pinned_one|met=0|json=0")
    print("ONEREAD_COMPARE_DONE|failed=1|json=0")
    sys.exit(1)
print("ONEREAD_REQUIREMENT|original_run_is_the_pinned_one|met=1|sha256=%s|json=0" % ORIGINAL_SHA)
orig_rows = raw_original.decode().splitlines()
new_text = read(NEW).decode("utf-8", "replace")
new_rows = new_text.splitlines()
last = [r for r in new_rows if r.startswith("ALLPAIRS|")]
passes = [r for r in new_rows if r.startswith("ALLPAIRS_PASS|")]
met("rows_are_four_passes_and_one_final", len(last) == 1 and len(passes) == 4 and len(new_rows) == 5 and new_rows[-1:] == last, "final=%d|pass_rows=%d|all_rows=%d" % (len(last), len(passes), len(new_rows)))
f = fields(last[-1]) if last else {}
pf = [fields(r) for r in passes]


def need(key, want):
    met(key, f.get(key) == str(want), "value=%s" % f.get(key, "-"))


# Every gate, by name.
for key in ("header_entries", "whole_space_count", "header_rooms", "padding", "store_identity", "verdict", "merkle"):
    need(key, "PASS")
need("identity_differs", "-")
# The store, by its two hashes and its own fields.
need("payload_merkle", MERKLE)
need("header_sha256", HEADER)
need("L", "3x4")
need("sector", "Sx+Sy+")
# Every row and every pair of the complete store.
for key, want in (("n", ROWS), ("rows_read", ROWS), ("entries", ENTRIES), ("diag", ROWS), ("pairs", PAIRS), ("sum_w", 13060694016), ("codes", 13060694016), ("passes", 4)):
    need(key, want)
need("flat_w_listed", 7)
# Every payload byte accounted for.
for key, want in (("rooms", ROOMS), ("padding_bytes", 742160), ("padding_nonzero", 0), ("bytes_after_stream", 349114368)):
    need(key, want)
# Zero mismatches and zero unpaired entries, each entry answered once.
for key in ("value_mismatch", "lower_without_upper", "upper_without_lower", "lower_repeated"):
    need(key, 0)
met("no_detail_rows", not any(r.startswith("ALLPAIRS_BAD|") for r in new_rows))
keys_of = lambda row: [x.split("=", 1)[0] for x in row.split("|") if "=" in x]
met("no_row_repeats_a_key", all(len(keys_of(r)) == len(set(keys_of(r))) for r in new_rows))
need("offset", 0)
# All structural checks.
for key in ("columns_not_ascending", "column_out_of_range", "zero_z", "positive_offdiag", "row_sum_nonzero", "zero_weight", "missing_diag"):
    need(key, 0)
# The caps it was asked for and used.
need("cap_requested", 470000000)
need("cap_entries", 470000000)
# Merkle on every pass, windows that cover every row, each upper entry stored, looked up and found once.
met("merkle_each_pass", len(pf) == 4 and all(p.get("merkle") == "PASS" for p in pf))
met("windows", [(p.get("rows_from"), p.get("rows_to")) for p in pf] == [(str(a), str(b)) for a, b in WINDOWS])
digits = lambda v: int(v) if v and v.isdigit() else -1
same_counts = len(pf) == 4 and all(digits(p.get("upper_stored")) == digits(p.get("lookups")) == digits(p.get("found")) >= 0 for p in pf)
met("each_upper_entry_stored_looked_up_and_found_once", same_counts and sum(digits(p.get("found")) for p in pf) == PAIRS and all(p.get("lower_repeated") == "0" for p in pf))
# Against the original run: every field it has, apart from secs. The original's own hash is pinned above.
diffs = []
if len(orig_rows) == len(new_rows):
    for a, b in zip(orig_rows, new_rows):
        fa, fb = fields(a), fields(b)
        if a.split("|")[0] != b.split("|")[0]:
            diffs.append("row")
        diffs += [k for k in fa if k != "secs" and fa[k] != fb.get(k)]
else:
    diffs.append("row_count")
met("every_field_of_the_original_is_the_same_apart_from_secs", not diffs, "differs=%s" % (",".join(sorted(set(diffs))) or "-"))
# The process and the executable.
met("exit_code", CODE == "0", "value=%s" % CODE)
size = os.path.getsize(STDERR)
met("stderr_empty", size == 0, "bytes=%d" % size)
if "--exe" in sys.argv:
    exe = hashlib.sha256(read(sys.argv[sys.argv.index("--exe") + 1])).hexdigest()
    met("output_names_this_executable", f.get("exe_sha256") == exe, "value=%s" % f.get("exe_sha256", "-"))
new_norm = re.sub(r"\|exe_sha256=[0-9a-f]+\|", "|exe_sha256=E|", re.sub(r"\|secs=[0-9]+\|", "|secs=S|", new_text))
met("the_text_of_every_row", hashlib.sha256(new_norm.encode()).hexdigest() == NORMALISED, "normalised_sha256=%s" % hashlib.sha256(new_norm.encode()).hexdigest())
print("ONEREAD_OUTPUT|new_sha256=%s|normalised_sha256=%s|bytes=%d|rows=%d|pass_secs=%s|secs=%s|exe_sha256=%s|json=0" % (hashlib.sha256(read(NEW)).hexdigest(), hashlib.sha256(new_norm.encode()).hexdigest(), len(read(NEW)), len(new_rows), ",".join(p.get("secs", "-") for p in pf), f.get("secs", "-"), f.get("exe_sha256", "-")))
print("ONEREAD_COMPARE_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
