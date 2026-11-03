# Can the check of the local rule go red? Each case changes one entry of the rule or one constraint in a copy of local_table.py and runs it with --check against a real store's census.
# A change that drops or alters rows must leave store signatures out of the table, so that copy must exit 1. The clean copy must exit 0.
#
# usage: mutate_local_table.py LOCAL_TABLE_PY LX LY STORE_TABLE OUT_HBP      Integer only, json=0. Exits 1 if any case differs from this.
import os, subprocess, sys, tempfile

SRC, LX, LY, STORE, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
text = open(SRC, encoding="utf-8").read()
CASES = [
    ("clean", None, None, 0),
    ("ee_count", '"ee": ((2, 0, 3),)', '"ee": ((2, 0, 2),)', 1),
    ("ee_change", '"ee": ((2, 0, 3),)', '"ee": ((2, 1, 3),)', 1),
    ("eT_hop_count", '"eT": ((0, 0, 1), (0, 1, 2))', '"eT": ((0, 0, 2), (0, 1, 1))', 1),
    ("eT_change", '"eT": ((0, 0, 1), (0, 1, 2))', '"eT": ((0, 0, 1), (0, 2, 2))', 1),
    ("eC_count", '"eC": ((2, -1, 3),)', '"eC": ((2, -1, 2),)', 1),
    ("eC_change", '"eC": ((2, -1, 3),)', '"eC": ((2, 0, 3),)', 1),
    ("TTs_count", '"TTs": ((-2, 0, 1), (-2, 2, 2))', '"TTs": ((-2, 0, 2), (-2, 2, 1))', 1),
    ("TTs_change", '"TTs": ((-2, 0, 1), (-2, 2, 2))', '"TTs": ((-2, 0, 1), (-2, 1, 2))', 1),
    ("TTd_count", '"TTd": ((-2, 1, 2), (-2, 2, 1))', '"TTd": ((-2, 1, 1), (-2, 2, 2))', 1),
    ("TTd_change", '"TTd": ((-2, 1, 2), (-2, 2, 1))', '"TTd": ((-2, 1, 2), (-2, 1, 1))', 1),
    ("TC_count", '"TC": ((0, -1, 1), (0, 0, 2))', '"TC": ((0, -1, 2), (0, 0, 1))', 1),
    ("TC_change", '"TC": ((0, -1, 1), (0, 0, 2))', '"TC": ((0, 1, 1), (0, 0, 2))', 1),
    ("CC_count", '"CC": ((2, -2, 3),)', '"CC": ((2, -2, 2),)', 1),
    ("CC_change", '"CC": ((2, -2, 3),)', '"CC": ((2, -1, 3),)', 1),
    ("incidence_of_T", "net = 4 * a - 2 * (tts + ttd)", "net = 4 * a - (tts + ttd)", 1),
    ("incidence_of_C", "ec = 4 * b - tc - 2 * cc", "ec = 4 * b - tc - cc", 1),
    ("adjacency_one_too_few_T", "for ttd in range(0, adj_max(a, lx, ly) - tts + 1):", "for ttd in range(0, max(0, adj_max(a, lx, ly) - tts)):", 1),
    ("adjacency_all_at_one", "if inner > adj_max(a + b, lx, ly):", "if inner > 1:", 1),
    ("a_multiple_of_4", "for a in range(0, p + 1, 2)", "for a in range(0, p + 1, 4)", 1),
    ("b_below_2", "for b in range(0, p - a + 1)", "for b in range(0, min(2, p - a + 1))", 1),
]
tmp = tempfile.mkdtemp(prefix="mutate-")
log = open(OUT, "w", encoding="utf-8", newline="\n")
fails = 0
for name, a, b, want in CASES:
    if a is None:
        body = text
    else:
        if text.count(a) != 1:
            raise SystemExit("no single match for " + name)
        body = text.replace(a, b)
    path = os.path.join(tmp, "copy.py")
    open(path, "w", encoding="utf-8", newline="\n").write(body)
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", path, LX, LY, os.path.join(tmp, "table.hbp"), "--check", STORE], capture_output=True, text=True)
    rows = r.stdout.splitlines()
    line = ([x for x in rows if x.startswith("LOCAL_CHECK|")] or [""])[-1]
    missing = line.split("not_in_the_local_table=")[1].split("|")[0] if "not_in_the_local_table=" in line else "-"
    # A copy may also stop on a move that leaves the lumps. That is red as well.
    got = 0 if r.returncode == 0 else 1
    ok = got == want
    fails += 0 if ok else 1
    log.write("MUTATE|case=%s|want_exit=%d|exit=%d|store_signatures_missing=%s|met=%d|json=0\n" % (name, want, r.returncode, missing, 1 if ok else 0))
    log.flush()
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
os.rmdir(tmp)
log.write("MUTATE_DONE|cases=%d|failed=%d|json=0\n" % (len(CASES), fails))
log.close()
print("MUTATE_DONE|cases=%d|failed=%d|json=0" % (len(CASES), fails))
sys.exit(1 if fails else 0)
