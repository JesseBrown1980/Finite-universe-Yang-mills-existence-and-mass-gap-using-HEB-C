# Compares this seat's one pass on the 3x4 store, field by field, with its own prediction row and with the recorded allpairs output.
# usage: compare_3x4.py   Integer only, json=0.
ROOT = "C:/tmp/opus55/allpairs-review-20261103/"
AP = "C:/tmp/opus55/ym-review-wt/native/ym/results/3x4_stream/perron/allpairs/"


def kv(line):
    return dict(x.split("=", 1) for x in line.split("|") if "=" in x)


out = [x for x in open(ROOT + "out/reader-3x4.out", encoding="utf-8").read().splitlines()]
rr = kv([x for x in out if x.startswith("REVIEW_READER|")][0])
win = [kv(x) for x in out if x.startswith("REVIEW_WINDOW|")]
sec = [kv(x) for x in out if x.startswith("REVIEW_SECTOR|")]
pred = kv([x for x in open(ROOT + "REVIEW.hbp", encoding="utf-8").read().splitlines() if x.startswith("PREDICTION|") and "run=reader_3x4_one_pass" in x][0])
fields = "L sector n rows entries diag upper lower not_ascending out_of_range zero_z positive_off row_sum_nonzero zero_weight missing_diag sum_w codes flats flat_w flat_rows flat_off_entries max_cnt max_w min_z max_z max_abs_wz used_rooms trailing_rooms trailing_nonzero_rooms odd_bytes tail_nonzero_bytes stream_read merkle merkle_match sectors_match fingerprint_equal keyed_sum61 buckets_nonzero windows verdict".split()
miss = [k for k in fields if pred.get(k) != rr.get(k)]
print("PREDICTED_AGAINST_READER|fields=%d|differ=%d|which=%s|json=0" % (len(fields), len(miss), ",".join(miss) or "-"))
wr = ",".join("%s..%s" % (w["rows_from"], w["rows_to"]) for w in win)
wu = ",".join(w["upper_stored"] for w in win)
wl = ",".join(w["lower_into_window"] for w in win)
print("PREDICTED_WINDOWS|rows_equal=%d|upper_equal=%d|lower_equal=%d|json=0" % (int(wr == pred["window_rows"]), int(wu == pred["window_upper"]), int(wl == pred["window_lower"])))
rec = open(AP + "ALLPAIRS-3x4.out", encoding="utf-8").read().splitlines()
final = kv([x for x in rec if x.startswith("ALLPAIRS|")][-1])
passes = [kv(x) for x in rec if x.startswith("ALLPAIRS_PASS|")]
pairs = [("L", "L"), ("sector", "sector"), ("n", "n"), ("rows_read", "rows"), ("entries", "entries"), ("diag", "diag"), ("pairs", "upper"), ("pairs", "lower"), ("columns_not_ascending", "not_ascending"), ("column_out_of_range", "out_of_range"), ("zero_z", "zero_z"), ("positive_offdiag", "positive_off"), ("row_sum_nonzero", "row_sum_nonzero"), ("zero_weight", "zero_weight"), ("missing_diag", "missing_diag"), ("flats", "flats"), ("flat_w", "flat_w"), ("sum_w", "sum_w"), ("codes", "codes"), ("passes", "windows")]
d = [a + "!=" + b for a, b in pairs if final.get(a) != rr.get(b)]
print("RECORDED_AGAINST_READER|fields=%d|differ=%d|which=%s|json=0" % (len(pairs), len(d), ",".join(d) or "-"))
same = all(p["rows_from"] == w["rows_from"] and p["rows_to"] == w["rows_to"] and p["upper_stored"] == w["upper_stored"] and p["lookups"] == w["lower_into_window"] for p, w in zip(passes, win)) and len(passes) == len(win)
print("RECORDED_PASSES_AGAINST_READER_WINDOWS|passes=%d|windows=%d|rows_upper_lookups_all_equal=%d|json=0" % (len(passes), len(win), int(same)))
print("SECTORS|hashed=%d|manifest_match=%d|json=0" % (len(sec), sum(1 for s in sec if s["manifest_match"] == "1")))
print("PAIR_COUNT|recorded=%s|reader_upper=%s|reader_lower=%s|fingerprint_upper=%s|fingerprint_lower=%s|keyed_sum61=%s|pairs_touching_flat_rows=%s|pairs_of_H_prime=%d|json=0" % (final["pairs"], rr["upper"], rr["lower"], rr["fingerprint_upper"], rr["fingerprint_lower"], rr["keyed_sum61"], rr["flat_off_entries"], int(rr["upper"]) - int(rr["flat_off_entries"])))
print("PADDING|trailing_rooms=%s|bytes=%d|nonzero_rooms=%s|json=0" % (rr["trailing_rooms"], int(rr["trailing_rooms"]) * 8, rr["trailing_nonzero_rooms"]))
print("BOUND|upper=1632625631|p=2^127-1|false_pass_per_mille_of_a_billionth=see_review|N_over_p_floor_exponent=-29|json=0")
