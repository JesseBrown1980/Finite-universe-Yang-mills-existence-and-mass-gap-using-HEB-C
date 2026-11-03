# Judges the attack on the hybrid certificate: every predicted field in HYBRID-ATTACK-PREDICTION.hbp against the rows of the runs.
# usage: compare_attack.py PREDICTION ATTACK_LEDGER UPPER_LEDGER STORE_LEDGER
# Prints one row per field that differs and a count for each group. Exits 1 if a field differs. Integer only, json=0.
# The miss of the first upper ranges is recorded in the prediction file itself, as ATTACK_UPPER_RESULT, and this prints it beside the rest.
import re, sys

PRED, ATTACK, UPPER, STORE = sys.argv[1:5]
TAGS = {
    "tmp/hyb_4x4_r9_m14.hybrid": "m4x4_r9",
    "tmp/hyb_4x4_r6_m14.hybrid": "m4x4_r6",
    "tmp/hyb_4x5_r9_m13.hybrid": "m4x5_r9",
    "tmp/hyb_5x5_r9_m11.hybrid": "m5x5_r9",
    "tmp/hyb_4x4_r9_m8.hybrid": "c4x4_m8",
    "tmp/hyb_4x4_r9_m10.hybrid": "c4x4_m10",
    "tmp/hyb_3x3_r9_m13.hybrid": "c3x3_m13",
    "tmp/hyb_3x4_r9_m14.hybrid": "c3x4_m14",
    "out/hyb_4x4_r9_m12.hybrid": "red_4x4_m12",
    "out/hyb_3x4_m12.hybrid": "red_3x4_m12",
}


def fields(row):
    return dict(x.split("=", 1) for x in row.split("|")[1:] if "=" in x)


def blocks(path):
    """Rows of a ledger per tag: a RUN row names the tag and the rows after it belong to that tag. The later run of a tag wins."""
    out, tag = {}, None
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\r\n")
        m = re.match(r"RUN\|tag=([^|]+)\|exit=(\d+)", line)
        if m:
            tag = m.group(1)
            out[tag] = {"exit": m.group(2)}
            continue
        if tag is not None and "|" in line:
            out[tag][line.split("|")[0]] = fields(line)
    return out


fails, counted = 0, 0


def same(group, name, want, got):
    global fails, counted
    counted += 1
    if str(want) != str(got):
        fails += 1
        print("ATTACK_DIFFERS|group=%s|field=%s|predicted=%s|measured=%s|json=0" % (group, name, want, got))


def within(group, name, low, high, got):
    global fails, counted
    counted += 1
    if not low <= got <= high:
        fails += 1
        print("ATTACK_OUTSIDE|group=%s|field=%s|low=%d|high=%d|measured=%d|json=0" % (group, name, low, high, got))


pred = open(PRED, encoding="utf-8").read().splitlines()
runs = blocks(ATTACK)
fits = blocks(UPPER)
for line in pred:
    kind = line.split("|")[0]
    d = fields(line)
    if kind in ("ATTACK_MAIN", "ATTACK_CONTROL"):
        r = runs[TAGS[d["file"]]]
        group = TAGS[d["file"]]
        cl, ro, ta, top = r["HYBRIDCHECK_CLASSES"], r["HYBRIDCHECK_ROWS"], r["HYBRIDCHECK_TABLE"], r["HYBRIDCHECK"]
        same(group, "reps", d["reps"], r["HYBRIDCHECK_INPUT"]["reps"])
        same(group, "configs", d["configs_at_most_cut"], cl["configs_in_model"])
        same(group, "configs_expected", d["configs_at_most_cut"], cl["configs_expected"])
        same(group, "cert", d["cert_micro"], top["cert_micro"])
        same(group, "min_exact", d["min_exact_micro"], ro["min_exact_micro"])
        same(group, "min_table", d["min_table_micro"], ta["min_table_micro"])
        same(group, "classes_in_one_rep", d["classes_in_one_rep"], cl["classes_in_one_rep"])
        same(group, "lumps_wrong", d["lumps_with_a_wrong_count"], cl["lumps_with_a_wrong_count"])
        same(group, "missing_moves", d["missing_moves"], ro["missing_moves"])
        same(group, "symmetry", d["symmetry_mismatches"], ro["symmetry_mismatches"])
        same(group, "exit", d["exit"], r["exit"])
        if d["rows_past_cut"] != "-":
            same(group, "rows_past_cut", d["rows_past_cut"], ta["rows_past_cut"])
            same(group, "lumps_past_cut", d["lumps_past_cut"], ta["lumps_past_cut"])
    elif kind == "ATTACK_MUST_GO_RED":
        r = runs[TAGS[d["file"]]]
        group = TAGS[d["file"]]
        cl = r["HYBRIDCHECK_CLASSES"]
        same(group, "reps", d["reps"], r["HYBRIDCHECK_INPUT"]["reps"])
        same(group, "configs_missing", d["configs_missing_from_the_model"], cl["configs_missing"])
        same(group, "lumps_wrong", d["lumps_with_a_wrong_count"], cl["lumps_with_a_wrong_count"])
        same(group, "the_lump", d["the_lump"], cl["wrong"].split(":")[0])
        same(group, "exit", d["exit"], r["exit"])
        same(group, "verdict", "FAIL", r["HYBRIDCHECK"]["verdict"])
    elif kind == "ATTACK_TEETH":
        for tag in ("t_claim", "t_lower_one", "t_drop_one", "t_wrong_m", "t_nonzero_flat"):
            same(tag, "exit", 2, runs[tag]["exit"])
            same(tag, "verdict", "FAIL", runs[tag]["HYBRIDCHECK"]["verdict"])
    elif kind == "ATTACK_UPPER_RESULT":
        print(line)
    elif kind == "ATTACK_UPPER2_PREDICTION":
        for tag, key, what in (
            ("m4x4_r9", "4x4_r9_cut14_E9_upper_in", "E9_upper_micro"),
            ("m4x4_r6", "4x4_r6_cut14_E9_upper_in", "E9_upper_micro"),
            ("m4x5_r9", "4x5_r9_cut13_E9_upper_in", "E9_upper_micro"),
            ("m5x5_r9", "5x5_r9_cut11_E9_upper_in", "E9_upper_micro"),
            ("c3x4_m14", "control_3x4_cut14_lambda1_upper_in", "lambda1_upper_micro"),
            ("c3x3_full", "control_3x3_whole_lambda1_upper_in", "lambda1_upper_micro"),
        ):
            low, high = (int(x) for x in d[key].split(".."))
            within("upper_" + tag, what, low, high, int(fits[tag]["HYBRIDCHECK_FIT"][what]))
            same("upper_" + tag, "exit", 0, fits[tag]["exit"])
            same("upper_" + tag, "missing_moves", 0, fits[tag]["HYBRIDCHECK_FIT"]["missing_moves"])
    elif kind == "ATTACK_STORE":
        checks = {}
        for row in open(STORE, encoding="utf-8", errors="replace"):
            row = row.rstrip("\r\n")
            m = re.match(r"STORE_CHECK\|cut=(\d+)\|", row)
            if m:
                checks["3x3_" + m.group(1)] = int(fields(row)["t_cert_milli"])
            elif row.startswith("STORE34_CHECK|"):
                checks["3x4_14"] = int(fields(row)["t_cert_milli"])
        low, high = (int(x) for x in d["3x3_cut13_t_micro_in"].split(".."))
        within("store_3x3_cut13", "t", low, high, checks["3x3_13"])
        within("store_3x3_whole", "t", 76443822, 76448399, checks["3x3_27"])
        if "3x4_14" in checks:
            low, high = (int(x) for x in d["3x4_cut14_t_micro_in"].split(".."))
            within("store_3x4_cut14", "t", low, high, checks["3x4_14"])
        print("ATTACK_STORE_READ|%s|json=0" % "|".join("%s=%d" % kv for kv in sorted(checks.items())))
extra = runs["c3x3_full"]
same("c3x3_full", "cert", 76443824, extra["HYBRIDCHECK"]["cert_micro"])
same("c3x3_full", "configs", 60466158, extra["HYBRIDCHECK_CLASSES"]["configs_in_model"])
same("c3x3_full", "rows_past_cut", 0, extra["HYBRIDCHECK_TABLE"]["rows_past_cut"])
print("ATTACK_COMPARE_DONE|fields=%d|failed=%d|json=0" % (counted, fails))
sys.exit(1 if fails else 0)
