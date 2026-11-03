# Reads the recorded receipts against one another. Read only. usage: receipts_check.py   Integer only, json=0.
import os, subprocess

AP = "C:/tmp/opus55/ym-review-wt/native/ym/results/3x4_stream/perron/allpairs/"
PR = "C:/tmp/opus55/ym-review-wt/native/ym/results/3x4_stream/perron/"
out = open(AP + "ALLPAIRS-3x4.out", encoding="utf-8").read().splitlines()
run = open(AP + "ALLPAIRS-RUN.hbp", encoding="utf-8").read().splitlines()


def kv(line):
    return dict(x.split("=", 1) for x in line.split("|") if "=" in x)


final = kv([x for x in out if x.startswith("ALLPAIRS|")][-1])
passes = [kv(x) for x in out if x.startswith("ALLPAIRS_PASS|")]
pred = kv([x for x in run if x.startswith("ALLPAIRS_PREDICTION|")][0])
skip = {"at", "written_before_run", "falsifier", "time_estimate_min", "json", "flat_w_multiset"}
miss = [k for k in pred if k not in skip and pred[k] != final.get(k, "-")]
print("PREDICTION_FIELDS_AGAINST_OUTPUT|fields=%d|differ=%d|which=%s|json=0" % (len([k for k in pred if k not in skip]), len(miss), ",".join(miss) or "-"))
print("FLAT_MULTISET|predicted=%s|printed_sorted=%s|json=0" % (pred["flat_w_multiset"], ",".join(sorted(final["flat_w"].split(",")))))
e, n, d, p = int(final["entries"]), int(final["n"]), int(final["diag"]), int(final["pairs"])
print("ARITHMETIC|entries_equals_diag_plus_2_pairs=%d|pairs_from_header_entries_and_n=%d|sum_upper_stored=%d|sum_lookups=%d|sum_found=%d|max_upper_stored=%d|cap=%s|json=0" % (
    int(e == d + 2 * p), (e - n) // 2, sum(int(x["upper_stored"]) for x in passes), sum(int(x["lookups"]) for x in passes), sum(int(x["found"]) for x in passes), max(int(x["upper_stored"]) for x in passes), final["cap_entries"]))
print("WINDOW_CHAIN|from_0=%d|to_n=%d|contiguous=%d|json=0" % (int(passes[0]["rows_from"] == "0"), int(passes[-1]["rows_to"] == final["n"]), int(all(passes[i]["rows_to"] == passes[i + 1]["rows_from"] for i in range(len(passes) - 1)))))
print("GIB|cap_bytes=%d|gib_floor=%d|tenths=%d|json=0" % (470000000 * 8, 470000000 * 8 // (1 << 30), (470000000 * 8 * 10 // (1 << 30)) % 10))
# 289 of 2401, the tuple count the docs quote for the outside checker's escape.
c = sum(1 for a in range(-3, 4) for b in range(-3, 4) for x in range(-3, 4) for y in range(-3, 4) if a * y == b * x)
print("ESCAPE_TUPLES|solutions=%d|of=%d|per_mille=%d|fixture_127_of_1198_per_mille=%d|json=0" % (c, 7**4, c * 1000 // 7**4, 127 * 1000 // 1198))
ctl = open(AP + "CONTROLS.hbp", encoding="utf-8").read().splitlines()
kinds = {}
for ln in ctl:
    if ln.startswith("CONTROL_RESULT|"):
        k = ln.split("|")[1]
        kinds[k] = kinds.get(k, 0) + 1
rej = sum(kinds[k] for k in ("mode=entry", "mode=rowsum", "mode=weight", "mode=column", "mode=swap"))
pas = sum(kinds[k] for k in ("mode=mag", "mode=sym2"))
print("CONTROL_COMPOSITION|total=%d|clean_stores=%d|allpairs_rejects_a_repaired_change=%d|allpairs_passes_a_repaired_change_by_scope=%d|allpairs_unrepaired_byte=%d|fullrebuild_outcomes=%d|caps_3x3=1|json=0" % (sum(kinds.values()), kinds["clean"], rej, pas, kinds["unrepaired_merkle"], kinds["rebuild"]))
census = kv(open(PR + "PASSA-CENSUS-3x4.hbp", encoding="utf-8").read().splitlines()[0])
print("FLAT_AGAINST_PASSA|tool_flat_w=%s|passa_flat_weights=%s|equal=%d|tool_sum_w=%s|passa_sum_w=%s|json=0" % (final["flat_w"], census["flat_weights"], int(final["flat_w"] == census["flat_weights"]), final["sum_w"], census["sum_w"]))
# Stdout closed: a verdict cannot be read as PASS from an exit code when the line could not be written.
EXE = "D:/ym-3x4-room-run/p0-ball/allpairs/allpairs.exe"
r, w = os.pipe()
os.close(r)
p = subprocess.run([EXE, "D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin", "0"], stdout=w, stderr=subprocess.DEVNULL)
os.close(w)
print("STDOUT_CLOSED|exit=%d|json=0" % p.returncode)
