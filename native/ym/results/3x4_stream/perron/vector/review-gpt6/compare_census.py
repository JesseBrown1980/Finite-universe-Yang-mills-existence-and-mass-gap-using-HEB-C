# GPT-6's group-convolution census (independent/gpt6_hybrid_census.measure) against the totals this repository's own tools recorded by enumeration.
# Two methods on the same counts. Each row names where the author's number sits. Reads committed files only. Exits 1 on any difference. Integer only, json=0.
# usage: compare_census.py CENSUS_MEASURE VECTOR_DIR
import os
import sys

measure, vector = sys.argv[1:3]
FLAT = 18


def fields(row):
    return dict(x.split("=", 1) for x in row.split("|")[1:] if "=" in x)


def rows(path):
    return open(os.path.join(vector, path), encoding="utf-8", errors="replace").read().split("\n")


enumerated = {}
for line in rows("AUDIT-RUNS.hbp"):
    if line.startswith("AUDIT_ENUMERATE|"):
        f = fields(line)
        enumerated[(f["Lx"], f["Ly"], f["mcut"])] = int(f["configs"])
in_model = set()
for line in rows("attack/ATTACK-RUNS-FINAL-BUILD.hbp"):
    if line.startswith("HYBRIDCHECK_CLASSES|"):
        f = fields(line)
        if f["configs_in_model"] == f["configs_expected"]:
            in_model.add(int(f["configs_in_model"]))
failed, compared = 0, 0
for line in open(measure, encoding="utf-8"):
    if not line.startswith("GPT6_HYBRID_CENSUS|"):
        continue
    f = fields(line)
    nonflat, key = int(f["nonflat"]), (f["Lx"], f["Ly"], f["cut"])
    assert int(f["flat"]) == FLAT
    sources = []
    if enumerated.get(key) == nonflat + FLAT:
        sources.append("AUDIT_ENUMERATE_configs=%d_including_the_flat_18" % (nonflat + FLAT))
    if nonflat in in_model:
        sources.append("HYBRIDCHECK_CLASSES_configs_in_model=%d" % nonflat)
    same = 1 if sources else 0
    failed += 1 - same
    compared += 1
    print("CENSUS_COMPARE|L=%sx%s|cut=%s|gpt6_nonflat=%d|gpt6_flat=%d|same=%d|author_rows=%s|json=0" % (f["Lx"], f["Ly"], f["cut"], nonflat, FLAT, same, "+".join(sources) or "none"))
red = [fields(line) for line in open(measure, encoding="utf-8") if line.startswith("GPT6_HYBRID_RED|")]
bound = open(os.path.join(vector, "VECTOR-BOUND.md"), encoding="utf-8").read()
missing_recorded = "45,144 configurations missing on 4×4 and 3,564 on 3×4" in bound
same_missing = all(r["missing"] == "45144" for r in red) and missing_recorded
failed += 0 if same_missing else 1
print("CENSUS_COMPARE_WITHDRAWN|gpt6_missing_on_4x4_cut12=%s|author_retraction_states=45,144_on_4x4_and_3,564_on_3x4|same=%d|json=0" % (",".join(r["missing"] for r in red), 1 if same_missing else 0))
print("CENSUS_COMPARE_SCOPE|what_this_compares=totals|per_lump_and_row_inequalities=issue_100_open|json=0")
print("CENSUS_COMPARE_DONE|compared=%d|failed=%d|json=0" % (compared, failed))
sys.exit(1 if failed else 0)
