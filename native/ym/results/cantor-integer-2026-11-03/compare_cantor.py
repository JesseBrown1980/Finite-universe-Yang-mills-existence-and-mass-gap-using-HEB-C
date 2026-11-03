# Judges the integer Cantor drive against its prediction, beside the floating-point run it repeats.
# usage: compare_cantor.py FLOAT_DIR RESULT_R9 RESULT_R243 SECOND_PATH TEETH   Exits 1 if anything differs from the prediction. Integers only, json=0.
import re, sys

FLOAT_DIR, R9, R243, SECOND, TEETH = sys.argv[1:6]
ONE_E_MINUS_9 = 10 ** 21  # at scale 10^30
fails = 0


def fld(row):
    return dict(x.split("=", 1) for x in row.split("|")[1:] if "=" in x)


def dec_e30(text):
    # A printed decimal with no exponent, as an integer at scale 10^30, keeping its own exact digits.
    if "e" in text or "E" in text:
        raise SystemExit("an exponent in " + text)
    whole, _, frac = text.partition(".")
    return int(whole) * 10 ** 30 + int((frac + "0" * 30)[:30])


def met(label, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    print("CANTOR_REQUIREMENT|%s|met=%d|%sjson=0" % (label, 1 if ok else 0, detail + "|" if detail else ""))


def load(path):
    runs, cmp_row, verdict, head, bound = {}, None, None, None, None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\r\n")
        if line.startswith("RUN|"):
            f = fld(line)
            runs[f["control"]] = f
        elif line.startswith("COMPARE|"):
            cmp_row = fld(line)
        elif line.startswith("CANTOR_INT_VERDICT|"):
            verdict = fld(line)
        elif line.startswith("CANTOR_INT|"):
            head = fld(line)
        elif line.startswith("CANTOR_INT_BOUND|"):
            bound = fld(line)
    return runs, cmp_row, verdict, head, bound


def load_float(path):
    runs, fid = {}, None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\r\n")
        if line.startswith("RUN|"):
            f = fld(line)
            runs[f["control"]] = f
        elif line.startswith("COMPARE|"):
            fid = fld(line)["driven_vs_zero_fidelity"]
    return runs, fid


worst = {}
for r, path, fname, K, RS, order in (
    (9, R9, "s22_r9.hbp", "76", "2118", ["inverted", "zero", "rotated_one", "cantor"]),
    (243, R243, "s22_r243.hbp", "278", "40026", ["inverted", "zero", "cantor", "rotated_one"]),
):
    runs, cmp_row, verdict, head, bound = load(path)
    fruns, ffid = load_float(FLOAT_DIR + "/" + fname)
    met("r%d_verdict" % r, verdict is not None and verdict["result"] == "PASS")
    met("r%d_inputs" % r, head["matrix_sha256"].startswith("902a8a01d527") and head["signal_sha256"].startswith("1f48fa508323") and head["states"] == "211" and head["nnz"] == "2607" and (head["positive"], head["negative"], head["zero"]) == ("32", "32", "665"))
    met("r%d_sizes" % r, head["K"] == K and head["R"] == RS, "K=%s|R=%s" % (head["K"], head["R"]))
    met("r%d_bound" % r, bound["remainder_at_most_one_unit"] == "1" and bound["delta_below_2^-110"] == "1" and bound["weighted_self_adjoint"] == "PASS", "delta_bits=%s" % bound["delta_units_bits"])
    for control in ("cantor", "zero", "inverted", "rotated_one"):
        f, g = runs[control], fruns[control]
        met("r%d_%s_norm_and_way_back" % (r, control), f["norm_within_bound"] == "1" and f["inverse_within_bound"] == "1", "norm_dev_bits=%s|inverse_dev2_bits=%s" % (f["norm_dev_bits"], f["inverse_dev2_bits"]))
        for what in ("magnetic_expectation", "return_probability"):
            lo, hi = int(f[what + "_lo_e30"]), int(f[what + "_hi_e30"])
            printed = dec_e30(g[what])
            dist = 0 if lo <= printed <= hi else min(abs(printed - lo), abs(printed - hi))
            worst[r] = max(worst.get(r, 0), dist)
            met("r%d_%s_%s" % (r, control, what), hi - lo <= 10 and dist <= ONE_E_MINUS_9, "integer_lo_e30=%d|integer_hi_e30=%d|float_printed=%s|float_distance_e30=%d" % (lo, hi, g[what], dist))
    lo, hi = int(cmp_row["driven_vs_zero_fidelity_lo_e30"]), int(cmp_row["driven_vs_zero_fidelity_hi_e30"])
    printed = dec_e30(ffid)
    dist = 0 if lo <= printed <= hi else min(abs(printed - lo), abs(printed - hi))
    worst[r] = max(worst.get(r, 0), dist)
    met("r%d_fidelity" % r, hi - lo <= 10 and dist <= ONE_E_MINUS_9, "integer_lo_e30=%d|integer_hi_e30=%d|float_printed=%s|float_distance_e30=%d" % (lo, hi, ffid, dist))
    values = [int(runs[c]["magnetic_expectation_lo_e30"]) for c in order]
    met("r%d_ordering_of_the_magnetic_expectation" % r, all(a < b for a, b in zip(values, values[1:])), "order=%s" % ",".join(order))
print("CANTOR_FLOAT_DISTANCE|r9_worst_e30=%d|r243_worst_e30=%d|json=0" % (worst[9], worst[243]))

# The second path overlaps, control by control.
runs9 = load(R9)[0]
seen = 0
for line in open(SECOND, encoding="utf-8"):
    if not line.startswith("SECOND_PATH|"):
        continue
    f = fld(line.rstrip("\r\n"))
    c = runs9[f["control"]]
    for what in ("magnetic_expectation", "return_probability"):
        a0, a1 = int(c[what + "_lo_e30"]), int(c[what + "_hi_e30"])
        b0, b1 = int(f[what + "_lo_e30"]), int(f[what + "_hi_e30"])
        met("second_path_%s_%s" % (f["control"], what), max(a0, b0) <= min(a1, b1), "second_lo_e30=%d|second_hi_e30=%d" % (b0, b1))
    seen += 1
met("second_path_has_all_four_controls", seen == 4)

# The sabotages.
teeth = {}
for line in open(TEETH, encoding="utf-8"):
    m = re.match(r"TOOTH\|name=([a-z_]+)\|exit=(\d+)", line)
    if m:
        teeth[m.group(1)] = int(m.group(2))
for name in ("short_taylor", "low_precision", "break_symmetry"):
    met("tooth_%s_exits_2" % name, teeth.get(name) == 2)
wrong = load(sys.argv[6])[0] if len(sys.argv) > 6 else None
if wrong:
    fr = load_float(FLOAT_DIR + "/s22_r9.hbp")[0]["cantor"]
    moved = abs(int(wrong["cantor"]["magnetic_expectation_lo_e30"]) - dec_e30(fr["magnetic_expectation"]))
    met("tooth_wrong_pulse_moves_past_1e-9", moved > ONE_E_MINUS_9, "distance_e30=%d" % moved)
print("CANTOR_COMPARE_DONE|failed=%d|json=0" % fails)
sys.exit(1 if fails else 0)
