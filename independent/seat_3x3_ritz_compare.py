#!/usr/bin/env python3
"""Compare the outward 3x3 Ritz receipts with the historical receipt, integer only.

Each check below exits 1 with one RITZ-COMPARE|result=FAIL row when it fails.
- The historical receipt, the prediction file and the 10^12 receipt match their pinned
  sha256. The 10^12 pin runs after that receipt's row checks, so a doctored row fails
  first for its own reason.
- Every outward and GPT-6 row carries only the fields its format names.
- Every historical level is the low end of its outward interval at scale 10^6.
- Every level interval has width 1 and the levels ascend, at scale 10^6 and at scale 10^12.
- Every difference field equals the interval difference of its levels.
- Every 10^12 interval lies inside its 10^6 interval.
- GPT-6's rows carry its method label and json=0, and its printed intervals equal the
  seat's, row by row.
- Every doctored copy in the CONTROLS table is rejected for its expected reason.

Also compares the 10^12 trial differences with the third-order law
(9/8)(sqrt14-sqrt6)/r^2, by math.isqrt with outward rounding, and reports each
prediction row as met=1 or met=0. A prediction miss is reported and leaves the exit
code alone. The trial differences are trial-space numbers, full_gap=NOT_CERTIFIED.

usage seat_3x3_ritz_compare.py [--old F] [--new F] [--e12 F] [--gpt6 F] [--prediction F]
"""
from argparse import ArgumentParser
from hashlib import sha256
from math import isqrt
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
HISTORICAL_NAME = "seat_3x3_vacuum_block_ritz.measure"
OUTWARD_NAME = "seat_3x3_vacuum_block_ritz_outward.measure"
E12_NAME = "seat_3x3_vacuum_block_ritz_outward_e12.measure"
REPLAY_NAME = "seat_3x3_ritz_gpt6_replay.measure"
PREDICTION_NAME = "seat_3x3_ritz_outward_PREDICTION.hbp"
HISTORICAL_SHA256 = "8500ef4b3b2f1c67ae410155aca06c9932699509efbfe5307c9521d37ae6708c"
PREDICTION_SHA256 = "a5bb4eab8468c0a5032b1c6f9944ff22b829eb305e5904d96de787f0e59e5ccc"
E12_SHA256 = "fdefb8967b57a6e9935311730d5d5a136364472555057c916618344fb052095c"
MICRO = 1000000
E12 = 1000000000000
GUARD = 10 ** 40
# The ratio column of the original report's scaling table, printed to four decimals, in ppm.
REPORT_RATIO_PPM = {"9": 1096900, "27": 1009200, "81": 1000600}
REPORT_ROUNDING_PPM = 50
ROW_TAG = "HEBC-3X3-BLOCK-RITZ"
REPLAY_TAG = "GPT6_3X3_RITZ"
REPLAY_METHOD = "INTEGER_INTERVAL_LDL"
OUTWARD_KEYS = frozenset(["matrix", "matrix_sha", "states", "JE", "JB", "order", "subspace_dim", "scale", "trial_gap",
                          "upper_trial_gap", "symmetry_diff", "kind", "full_gap", "json"] + ["E%d" % k for k in range(8)])
REPLAY_KEYS = frozenset(["matrix", "states", "JE", "JB", "order", "dim", "ritz_e0_micro", "ritz_e1_micro", "ritz_gap_micro",
                         "full_gap", "method", "json"])
BRACKET = re.compile(r"\[(-?[0-9]+),(-?[0-9]+)\]")
DOTTED = re.compile(r"(-?[0-9]+)\.\.(-?[0-9]+)")


class Fail(Exception):
    """A failed check, with a short reason code for the FAIL row."""

    def __init__(self, reason, detail="none"):
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


def fields_of(line, tag, known=None):
    parts = line.split("|")
    if parts[0] != tag:
        raise Fail("MALFORMED", tag + "_row_tag")
    fields = {}
    for part in parts[1:]:
        key, sep, value = part.partition("=")
        if not sep or key in fields:
            raise Fail("MALFORMED", tag + "_field")
        if known is not None and key not in known:
            raise Fail("UNKNOWN_FIELD", key)
        fields[key] = value
    return fields


def rows_of(text, tag, known=None):
    if not text.endswith("\n"):
        raise Fail("MALFORMED", tag + "_no_final_newline")
    return [fields_of(line, tag, known) for line in text[:-1].split("\n")]


def need(row, key):
    if key not in row:
        raise Fail("FIELD_MISSING", key)
    return row[key]


def interval(text, pattern=BRACKET):
    match = pattern.fullmatch(text)
    if match is None:
        raise Fail("MALFORMED", text)
    return int(match.group(1)), int(match.group(2))


def show(pair):
    return "[%d,%d]" % pair


def row_key(row):
    return "matrix=%s|JE=%s|JB=%s|order=%s" % (need(row, "matrix"), need(row, "JE"), need(row, "JB"), need(row, "order"))


def ceil_div(n, d):
    return -((-n) // d)


def levels_of(row, scale):
    """The scale and labels of one outward row, and its 8 width-1 level intervals."""
    if need(row, "scale") != str(scale):
        raise Fail("SCALE", row_key(row))
    labels = (need(row, "kind"), need(row, "full_gap"), need(row, "json"))
    if labels != ("RITZ_TRIAL_GAP_ONLY", "NOT_CERTIFIED", "0"):
        raise Fail("LABEL", row_key(row))
    levels = [interval(need(row, "E%d" % k)) for k in range(8)]
    for k, (low, high) in enumerate(levels):
        if high - low != 1:
            raise Fail("WIDTH", "E%d_%s" % (k, row_key(row)))
    for k in range(7):
        if levels[k][0] > levels[k + 1][0]:
            raise Fail("LEVEL_ORDER", "E%d_%s" % (k, row_key(row)))
    return levels


def differences_of(row, levels):
    """Recomputes the three difference fields from the levels and compares them."""
    e0, e1, e6, e7 = levels[0], levels[1], levels[6], levels[7]
    lower = (e1[0] - e0[1], e1[1] - e0[0])
    upper = (e7[0] - e6[1], e7[1] - e6[0])
    symmetry = (lower[0] - upper[1], lower[1] - upper[0])
    if interval(need(row, "trial_gap")) != lower:
        raise Fail("TRIAL_GAP", row_key(row))
    if interval(need(row, "upper_trial_gap")) != upper:
        raise Fail("UPPER_TRIAL_GAP", row_key(row))
    if interval(need(row, "symmetry_diff")) != symmetry:
        raise Fail("SYMMETRY", row_key(row))
    return lower, upper, symmetry


def check_micro_row(old, new):
    for key in ("matrix", "matrix_sha", "states", "JE", "JB", "order", "subspace_dim"):
        if need(old, key) != need(new, key):
            raise Fail("ROW_KEY", key)
    lows = [int(x) for x in need(old, "all_8_vacua_micro").split(",")]
    gap = interval(need(old, "gap").split("/")[0])
    upper_gap = interval(need(old, "upper_gap").split("/")[0])
    old_symmetry = int(need(old, "symmetry_diff"))
    if len(lows) != 8 or gap[0] != gap[1] or upper_gap[0] != upper_gap[1]:
        raise Fail("MALFORMED", "historical_" + row_key(old))
    if int(need(old, "E0").split("/")[0]) != lows[0] or int(need(old, "E1").split("/")[0]) != lows[1]:
        raise Fail("MALFORMED", "historical_" + row_key(old))
    levels = levels_of(new, MICRO)
    for k, (low, _) in enumerate(levels):
        if low != lows[k]:
            raise Fail("LOW_END", "E%d_%s" % (k, row_key(new)))
    lower, upper, symmetry = differences_of(new, levels)
    if lower != (gap[0] - 1, gap[0] + 1):
        raise Fail("TRIAL_GAP", row_key(new))
    if upper != (upper_gap[0] - 1, upper_gap[0] + 1):
        raise Fail("UPPER_TRIAL_GAP", row_key(new))
    if symmetry != (old_symmetry - 2, old_symmetry + 2):
        raise Fail("SYMMETRY", row_key(new))
    return "RITZ-COMPARE-MICRO|%s|levels=8|low_end_equals_historical=8|width_1=8|trial_gap=%s|historical_gap=%d|" \
           "upper_trial_gap=%s|historical_upper_gap=%d|symmetry_diff=%s|historical_symmetry_diff=%d|result=PASS|json=0" % (
               row_key(new), show(lower), gap[0], show(upper), upper_gap[0], show(symmetry), old_symmetry)


def inside(small, large):
    return large[0] <= small[0] and small[1] <= large[1]


def times(pair, factor):
    return pair[0] * factor, pair[1] * factor


def check_e12_row(micro, row):
    for key in ("matrix", "matrix_sha", "states", "JE", "JB", "order", "subspace_dim"):
        if need(micro, key) != need(row, key):
            raise Fail("ROW_KEY", key)
    factor = E12 // MICRO
    levels = levels_of(row, E12)
    cells = levels_of(micro, MICRO)
    for k in range(8):
        if not inside(levels[k], times(cells[k], factor)):
            raise Fail("E12_OUTSIDE_MICRO", "E%d_%s" % (k, row_key(row)))
    lower, upper, symmetry = differences_of(row, levels)
    for key, value in (("trial_gap", lower), ("upper_trial_gap", upper), ("symmetry_diff", symmetry)):
        if not inside(value, times(interval(need(micro, key)), factor)):
            raise Fail("E12_OUTSIDE_MICRO", "%s_%s" % (key, row_key(row)))
    return "RITZ-COMPARE-E12|%s|levels=8|inside_micro=8|width_1=8|trial_gap=%s|upper_trial_gap=%s|symmetry_diff=%s|" \
           "result=PASS|json=0" % (row_key(row), show(lower), show(upper), show(symmetry))


def law_enclosure():
    """Outward enclosure of (sqrt14 - sqrt6) * GUARD, from math.isqrt."""
    roots = []
    for n in (14, 6):
        root = isqrt(n * GUARD * GUARD)
        if not root * root <= n * GUARD * GUARD < (root + 1) * (root + 1):
            raise Fail("LAW_ENCLOSURE", "sqrt%d" % n)
        roots.append(root)
    return roots[0] - roots[1] - 1, roots[0] - roots[1] + 1


def law_interval(r, scale):
    """Outward integer enclosure of scale * (9/8)(sqrt14 - sqrt6) / r^2."""
    low, high = law_enclosure()
    denominator = 8 * r * r * GUARD
    return 9 * scale * low // denominator, ceil_div(9 * scale * high, denominator)


def ratio_ppm(gap, r, scale):
    """Outward enclosure in ppm of the gap interval, in units of 1/scale, over the law."""
    if gap[0] <= 0:
        raise Fail("SCOPE", "ratio_needs_a_positive_trial_difference")
    low, high = law_enclosure()
    numerator = MICRO * 8 * r * r * GUARD
    denominator = 9 * scale
    return gap[0] * numerator // (denominator * high), ceil_div(gap[1] * numerator, denominator * low)


def law_row(row):
    if need(row, "JE") != "1":
        raise Fail("SCOPE", "law_row_needs_JE_1")
    r = int(need(row, "JB"))
    gap = interval(need(row, "trial_gap"))
    ratio = ratio_ppm(gap, r, E12)
    text = "RITZ-LAW|%s|scale=%d|trial_gap=%s|law_e12=%s|law_micro=%s|ratio_ppm=%s|kind=TRIAL_SPACE_COMPARISON|" \
           "full_gap=NOT_CERTIFIED|json=0" % (
               row_key(row), E12, show(gap), show(law_interval(r, E12)), show(law_interval(r, MICRO)), show(ratio))
    return text, ratio


def report_row(old, ratio):
    """The original report's four-decimal ratio beside the historical gap's ratio and the 10^12 ratio."""
    jb = need(old, "JB")
    gap = interval(need(old, "gap").split("/")[0])
    printed = REPORT_RATIO_PPM[jb]
    rounding = (printed - REPORT_ROUNDING_PPM, printed + REPORT_ROUNDING_PPM)
    return "RITZ-LAW-REPORT|%s|report_ratio_ppm=%d|report_rounding_ppm=%s|historical_gap=%d|historical_gap_ratio_ppm=%s|" \
           "e12_ratio_ppm=%s|report_agrees_with_e12=%d|json=0" % (
               row_key(old), printed, show(rounding), gap[0], show(ratio_ppm(gap, int(jb), MICRO)), show(ratio), inside(ratio, rounding))


def check_replay_row(seat, replay):
    if row_key(seat) != row_key(replay):
        raise Fail("ROW_KEY", row_key(replay))
    if need(replay, "states") != need(seat, "states") or need(replay, "dim") != need(seat, "subspace_dim"):
        raise Fail("GPT6_DISAGREE", "size_" + row_key(replay))
    if need(replay, "full_gap") != "NOT_CERTIFIED":
        raise Fail("GPT6_DISAGREE", "full_gap_" + row_key(replay))
    if (need(replay, "method"), need(replay, "json")) != (REPLAY_METHOD, "0"):
        raise Fail("GPT6_DISAGREE", "label_" + row_key(replay))
    pairs = (("ritz_e0_micro", "E0"), ("ritz_e1_micro", "E1"), ("ritz_gap_micro", "trial_gap"))
    for theirs, ours in pairs:
        if interval(need(replay, theirs), DOTTED) != interval(need(seat, ours)):
            raise Fail("GPT6_DISAGREE", "%s_%s" % (theirs, row_key(replay)))
    return "RITZ-GPT6-REPLAY|%s|states=%s|dim=%s|gpt6_e0=%s|seat_e0=%s|gpt6_e1=%s|seat_e1=%s|gpt6_trial_gap=%s|" \
           "seat_trial_gap=%s|agree=1|full_gap=NOT_CERTIFIED|json=0" % (
               row_key(seat), need(replay, "states"), need(replay, "dim"), need(replay, "ritz_e0_micro"), need(seat, "E0"),
               need(replay, "ritz_e1_micro"), need(seat, "E1"), need(replay, "ritz_gap_micro"), need(seat, "trial_gap"))


def pinned_row(text, pin, name, reason):
    digest = sha256(text.encode("ascii")).hexdigest()
    if digest != pin:
        raise Fail(reason, digest)
    return "RITZ-COMPARE-HASH|file=%s|sha256=%s|pinned=1|json=0" % (name, digest)


def run_checks(bundle):
    """Every fail-closed check. Returns the receipt rows and the parsed tables."""
    rows = [pinned_row(bundle["old"], HISTORICAL_SHA256, HISTORICAL_NAME, "HISTORICAL_SHA"),
            pinned_row(bundle["pred"], PREDICTION_SHA256, PREDICTION_NAME, "PREDICTION_SHA")]
    old_rows = rows_of(bundle["old"], ROW_TAG)
    micro_rows = rows_of(bundle["new"], ROW_TAG, OUTWARD_KEYS)
    e12_rows = rows_of(bundle["e12"], ROW_TAG, OUTWARD_KEYS)
    replay_rows = rows_of(bundle["gpt6"], REPLAY_TAG, REPLAY_KEYS)
    if len(old_rows) != 5 or len(micro_rows) != 5 or len(e12_rows) != 3 or len(replay_rows) != 5:
        raise Fail("ROW_COUNT", "%d,%d,%d,%d" % (len(old_rows), len(micro_rows), len(e12_rows), len(replay_rows)))
    for old, new in zip(old_rows, micro_rows):
        rows.append(check_micro_row(old, new))
    micro_by_key = {row_key(row): row for row in micro_rows}
    if [need(row, "JB") for row in e12_rows] != ["9", "27", "81"]:
        raise Fail("ROW_KEY", "e12_couplings")
    ratios = {}
    for row in e12_rows:
        if row_key(row) not in micro_by_key:
            raise Fail("ROW_KEY", row_key(row))
        rows.append(check_e12_row(micro_by_key[row_key(row)], row))
    rows.append(pinned_row(bundle["e12"], E12_SHA256, E12_NAME, "E12_SHA"))
    rows.append("RITZ-LAW-COEFF|law=(9/8)(sqrt14-sqrt6)/r^2|coefficient_e12=%s|guard_digits=40|json=0" % show(law_interval(1, E12)))
    for row in e12_rows:
        text, ratio = law_row(row)
        rows.append(text)
        ratios[row_key(row)] = ratio
    for old in old_rows:
        if row_key(old) in ratios:
            rows.append(report_row(old, ratios[row_key(old)]))
    for seat, replay in zip(micro_rows, replay_rows):
        rows.append(check_replay_row(seat, replay))
    tables = {"micro": micro_by_key, "e12": {row_key(row): row for row in e12_rows},
              "replay": {row_key(row): row for row in replay_rows}, "ratio": ratios}
    return rows, tables


def doctor(row, key, change):
    """A control that changes one field of one row of a receipt."""
    def apply(text):
        lines = text.split("\n")
        parts = lines[row].split("|")
        for index, part in enumerate(parts):
            if part.startswith(key + "="):
                parts[index] = key + "=" + change(part[len(key) + 1:])
                lines[row] = "|".join(parts)
                return "\n".join(lines)
        raise Fail("CONTROL_SETUP", key)
    return apply


def moved(delta_low, delta_high):
    def change(value):
        for pattern, form in ((BRACKET, "[%d,%d]"), (DOTTED, "%d..%d")):
            match = pattern.fullmatch(value)
            if match is not None:
                return form % (int(match.group(1)) + delta_low, int(match.group(2)) + delta_high)
        raise Fail("CONTROL_SETUP", value)
    return change


def drop_last_row(text):
    return text[:text.rstrip("\n").rfind("\n") + 1]


def extra_field(field):
    """A control that adds one field to the first row of a receipt, before its json field."""
    return lambda text: text.replace("|json=", "|%s|json=" % field, 1)


CONTROLS = (
    ("historical_byte_changed", "old", lambda text: text.replace("53493385", "53493384", 1), "HISTORICAL_SHA"),
    ("prediction_byte_changed", "pred", lambda text: text.replace("issue=99", "issue=98", 1), "PREDICTION_SHA"),
    ("outward_row_dropped", "new", drop_last_row, "ROW_COUNT"),
    ("outward_crlf", "new", lambda text: text.replace("\n", "\r\n"), "LABEL"),
    ("outward_low_end_moved", "new", doctor(3, "E0", moved(-1, -1)), "LOW_END"),
    ("outward_width_2", "new", doctor(3, "E0", moved(0, 1)), "WIDTH"),
    ("outward_floor_both_ends", "new", doctor(3, "E0", moved(0, -1)), "WIDTH"),
    ("outward_trial_gap_narrowed", "new", doctor(3, "trial_gap", moved(1, -1)), "TRIAL_GAP"),
    ("outward_upper_trial_gap_narrowed", "new", doctor(3, "upper_trial_gap", moved(1, -1)), "UPPER_TRIAL_GAP"),
    ("outward_symmetry_narrowed", "new", doctor(3, "symmetry_diff", moved(2, -2)), "SYMMETRY"),
    ("outward_kind_relabelled", "new", doctor(3, "kind", lambda value: "VACUUM_BLOCK_RITZ_UPPER_BOUNDS"), "LABEL"),
    ("outward_full_gap_relabelled", "new", doctor(3, "full_gap", lambda value: "CERTIFIED"), "LABEL"),
    ("e12_moved_out_of_cell", "e12", doctor(1, "E0", moved(MICRO, MICRO)), "E12_OUTSIDE_MICRO"),
    ("e12_width_2", "e12", doctor(1, "E0", moved(0, 1)), "WIDTH"),
    ("e12_trial_gap_narrowed", "e12", doctor(1, "trial_gap", moved(1, -1)), "TRIAL_GAP"),
    ("e12_row_dropped", "e12", drop_last_row, "ROW_COUNT"),
    ("gpt6_interval_moved", "gpt6", doctor(3, "ritz_e0_micro", moved(0, 1)), "GPT6_DISAGREE"),
    ("gpt6_full_gap_relabelled", "gpt6", doctor(3, "full_gap", lambda value: "CERTIFIED"), "GPT6_DISAGREE"),
    ("outward_unknown_field", "new", extra_field("certified_full_gap=[2004,2006]"), "UNKNOWN_FIELD"),
    ("outward_levels_out_of_order", "new", doctor(3, "E2", moved(3, 3)), "LEVEL_ORDER"),
    ("e12_unknown_field", "e12", extra_field("note=full_gap_proved"), "UNKNOWN_FIELD"),
    ("e12_levels_out_of_order", "e12", doctor(1, "E3", moved(MICRO, MICRO)), "LEVEL_ORDER"),
    ("e12_level_moved_inside_its_cell", "e12", doctor(1, "E2", moved(1, 1)), "E12_SHA"),
    ("gpt6_unknown_field", "gpt6", extra_field("note=full_gap_proved"), "UNKNOWN_FIELD"),
    ("gpt6_method_relabelled", "gpt6", doctor(3, "method", lambda value: "FLOATING_POINT"), "GPT6_DISAGREE"),
    ("gpt6_json_relabelled", "gpt6", doctor(3, "json", lambda value: "1"), "GPT6_DISAGREE"),
)


def run_controls(bundle):
    """Each doctored copy must fail run_checks for its expected reason."""
    rows = []
    for name, target, change, expected in CONTROLS:
        copy = dict(bundle)
        copy[target] = change(bundle[target])
        if copy[target] == bundle[target]:
            raise Fail("CONTROL_SETUP", name)
        got = "ACCEPTED"
        try:
            run_checks(copy)
        except Fail as fail:
            got = fail.reason
        if got != expected:
            raise Fail("CONTROL_NOT_REJECTED", "%s_got_%s" % (name, got))
        rows.append("RITZ-COMPARE-CONTROL|case=%s|file=%s|expected=%s|got=%s|result=PASS|json=0" % (name, target, expected, got))
    return rows


def outcome_of(line, tables):
    """One PRED-OUTCOME row and whether it was met, or None for rows measured elsewhere."""
    tag = line.split("|", 1)[0]
    if tag == "PRED-LEVELS":
        predicted = fields_of(line, tag)
        actual = tables["micro"][row_key(predicted)]
        keys = ["E%d" % k for k in range(8)] + ["trial_gap", "upper_trial_gap", "symmetry_diff", "kind", "full_gap"]
        met = all(need(predicted, key) == need(actual, key) for key in keys)
        return "PRED-OUTCOME|row=%s|%s|met=%d|json=0" % (tag, row_key(predicted), met), met
    if tag in ("PRED-REPLAY", "PRED-HOSTED"):
        predicted = fields_of(line, tag)
        actual = tables["replay"][row_key(predicted)]
        keys = ("ritz_e0_micro", "ritz_e1_micro", "ritz_gap_micro")
        met = all(need(predicted, key) == need(actual, key) for key in keys)
        return "PRED-OUTCOME|row=%s|%s|met=%d|json=0" % (tag, row_key(predicted), met), met
    if tag == "PRED-E12-CELL":
        predicted = fields_of(line, tag)
        actual = tables["e12"][row_key(predicted)]
        keys = ["E%d" % k for k in range(8)] + ["trial_gap", "upper_trial_gap", "symmetry_diff"]
        met = all(inside(interval(need(actual, key)), interval(need(predicted, key + "_inside"))) for key in keys)
        gap = interval(need(actual, "trial_gap"))
        symmetry = interval(need(actual, "symmetry_diff"))
        met = met and gap[1] - gap[0] == int(need(predicted, "trial_gap_width_units"))
        met = met and symmetry[1] - symmetry[0] == int(need(predicted, "symmetry_diff_width_units"))
        return "PRED-OUTCOME|row=%s|%s|met=%d|json=0" % (tag, row_key(predicted), met), met
    if tag == "PRED-RATIO":
        predicted = fields_of(line, tag)
        ratio = tables["ratio"][row_key(predicted)]
        limits = interval(need(predicted, "ratio_ppm_inside"))
        met = inside(ratio, limits)
        return "PRED-OUTCOME|row=%s|tag=%s|%s|ratio_ppm_inside=%s|ratio_ppm=%s|met=%d|json=0" % (
            tag, need(predicted, "tag"), row_key(predicted), show(limits), show(ratio), met), met
    if tag == "PRED-CONTROL":
        predicted = fields_of(line, tag)
        control = need(predicted, "control")
        if control in ("doctored_outward_row", "doctored_e12_row", "doctored_historical_file"):
            # run_controls has already failed closed if a doctored copy got through.
            return "PRED-OUTCOME|row=%s|control=%s|compare_exit=1|met=1|json=0" % (tag, control), True
    return None


def main():
    parser = ArgumentParser(description="Compare the outward 3x3 Ritz receipts with the historical receipt")
    parser.add_argument("--old", default=str(HERE.joinpath(HISTORICAL_NAME)))
    parser.add_argument("--new", default=str(HERE.joinpath(OUTWARD_NAME)))
    parser.add_argument("--e12", default=str(HERE.joinpath(E12_NAME)))
    parser.add_argument("--gpt6", default=str(HERE.joinpath(REPLAY_NAME)))
    parser.add_argument("--prediction", default=str(HERE.joinpath(PREDICTION_NAME)))
    args = parser.parse_args()
    try:
        bundle = {}
        sources = (("old", args.old), ("new", args.new), ("e12", args.e12), ("gpt6", args.gpt6), ("pred", args.prediction))
        for key, path in sources:
            try:
                bundle[key] = Path(path).read_bytes().decode("ascii")
            except (OSError, UnicodeDecodeError):
                raise Fail("UNREADABLE", key) from None
        rows, tables = run_checks(bundle)
        controls = run_controls(bundle)
        outcomes = [outcome_of(line, tables) for line in bundle["pred"][:-1].split("\n")]
        outcomes = [item for item in outcomes if item is not None]
    except Fail as fail:
        print("RITZ-COMPARE|result=FAIL|reason=%s|detail=%s|json=0" % (fail.reason, fail.detail.replace("|", ",")))
        sys.exit(1)
    for row in rows + controls + [text for text, _ in outcomes]:
        print(row)
    met = sum(1 for _, ok in outcomes if ok)
    print("RITZ-COMPARE|result=PASS|micro_rows=5|e12_rows=3|replay_rows=5|law_rows=3|controls=%d|predictions_met=%d|"
          "predictions_missed=%d|kind=TRIAL_SPACE_COMPARISON|full_gap=NOT_CERTIFIED|json=0" % (
              len(controls), met, len(outcomes) - met))


if __name__ == "__main__":
    main()
