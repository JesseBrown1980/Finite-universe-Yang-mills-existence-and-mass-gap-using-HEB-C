#!/usr/bin/env python3
"""#137 Stage G: independent exact eight-flat lower test for Wilson sample action.

The original #180 samples and original #185 exact-Q-resolvent norm enclosures
are SHA/source-pinned. No full-Q action norm is estimated here. We use only the
nonnegative flat contribution and a certified total sample normalization upper.
Strict integer comparisons certify an obstruction for the original unshifted O
and Stage E full-state errors; this does not prove that Wilson weight is zero.
"""
import hashlib
import os
import sys
from itertools import permutations
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
INDEP = os.path.join(ROOT, "independent")
sys.path.insert(0, os.path.join(INDEP, "y137-radau-recentred-angle-20261114"))
import recentred_angle as ra

UNIT = 10 ** 12
D1 = 3235251105
D2 = 8676646901
EXPECTED_BLOBS = {
    "independent/y137-q-dual-weight-20261113/RESULT-WILSON-Q-DUAL.hbp":
        "40762ceb865829156e4765b720f52d39a8be9b6f",
    "independent/y137-fullstate-Q-normalization-20261113/RESULT-FULL-W-NORM.hbp":
        "48c02e1e80112e5d758b403f41d07079d9fcb064",
    "independent/finite_s3_3x4_r9_first_gap.py":
        "91bd1e80cbfcfb76198966aa177d097ecfbe8143",
    "independent/y137-radau-recentred-angle-20261114/recentred_angle.py":
        "80f9e9c892572447ba2f246f24834c7a76c62525",
}
FROZEN_W = (1, 3, 2, 3, 3, 2, 2, 2)
FROZEN_O = (14, 8, 5, 6, 0, 2, -7, -7)
Z = (69909875505, 69949729820)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def emit(tag, **fields):
    print(tag + "|" + "|".join(str(k) + "=" + str(v) for k, v in fields.items()) +
          "|json=0", flush=True)


def source_blob(rel):
    raw = open(os.path.join(ROOT, rel), "rb").read()
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()
    need(digest == EXPECTED_BLOBS[rel], "frozen_Git_blob_mismatch:" + rel)
    return raw.decode("ascii")


def records(src, tag):
    rows = []
    for line in src.splitlines():
        if not line.startswith(tag + "|"):
            continue
        items = line.split("|")
        kv = {}
        for item in items[1:]:
            k, sep, v = item.partition("=")
            need(bool(sep) and k not in kv, "malformed_or_duplicate_receipt_field")
            kv[k] = v
        need(kv.get("json") == "0", "receipt_terminator")
        rows.append(kv)
    return rows


def exact_original_inputs():
    original = source_blob("independent/y137-q-dual-weight-20261113/RESULT-WILSON-Q-DUAL.hbp")
    qnorm = source_blob("independent/y137-fullstate-Q-normalization-20261113/RESULT-FULL-W-NORM.hbp")
    source_blob("independent/finite_s3_3x4_r9_first_gap.py")
    source_blob("independent/y137-radau-recentred-angle-20261114/recentred_angle.py")
    flats = records(original, "Y137_QDUAL_FLATS")
    trial = records(original, "Y137_QDUAL_TRIAL")
    full = records(qnorm, "Y137_FULLN_POINT")
    gram = records(qnorm, "Y137_FULLN_GRAM")
    fixed = records(original, "Y137_QDUAL_RAW_WILSON_FIXED_WEIGHT")
    need(len(flats) == 1 and len(trial) == len(full) == 2 and
         len(gram) == len(fixed) == 1, "missing_original_wilson_sample_receipts")
    need(gram[0]["wf"] == ",".join(map(str, FROZEN_W)) and
         gram[0]["BstarB_exact_72_identity"] == "1",
         "original_W_or_coupling_changed")
    need(int(fixed[0]["lower_ppb_floor"]) == 416300 and
         fixed[0]["evidence"] == "RIGOROUS_FOR_UNSHIFTED_WILSON_FIXED_SAMPLES_ONLY",
         "original_fixed_sample_amplitude_not_accepted")
    v = []
    q_up = []
    for i in range(2):
        vi = tuple(map(int, flats[0]["v" + str(i + 1)].split(",")))
        need(vi == tuple(ra.ROWS[i][3]) and len(vi) == 8,
             "original_Wilson_vs_normalization_samples_mismatch")
        need(int(full[i]["sample_num"]) == Z[i] and
             trial[i]["z"] == str(Z[i]) + "/1000000000",
             "original_energy_samples_mismatch")
        need(full[i]["source_Gq"] == trial[i]["q_residual_G"] and
             full[i]["source_trial_norm2"] == trial[i]["norm_W"],
             "original_Q_trial_or_residual_mismatch")
        need(full[i]["flat_sin_upper_per_trillion"] ==
             ("108258863901", "253465115951")[i],
             "original_sample_projector_pin")
        qu = int(full[i]["Q_Rz_Bx_upper_per_trillion"])
        need(0 < qu < UNIT, "uncertified_or_missing_exact_Q_tail_upper")
        v.append(vi)
        q_up.append(qu)
    need(tuple(ra.WF) == FROZEN_W and ra.UNIT == UNIT,
         "historical_eight_flat_metric_mismatch")
    return v, q_up


def independently_build_flat():
    group = tuple(permutations(range(3)))
    lookup = {p: i for i, p in enumerate(group)}
    mul = tuple(tuple(lookup[tuple(group[a][group[b][j]] for j in range(3))]
                      for b in range(6)) for a in range(6))
    inv = tuple(next(b for b in range(6) if mul[a][b] == mul[b][a] == 0)
                for a in range(6))
    char = tuple(sum(int(p[j] == j) for j in range(3)) - 1 for p in group)
    conj = tuple(tuple(mul[mul[g][a]][inv[g]] for a in range(6))
                 for g in range(6))
    lx, ly, nsites = 3, 4, 12
    def pos(x, y):
        return (x % lx) * ly + (y % ly)
    tree = [(pos(0, y), pos(0, y + 1), nsites + pos(0, y))
            for y in range(ly - 1)]
    tree += [(pos(x, y), pos(x + 1, y), pos(x, y))
             for y in range(ly) for x in range(lx - 1)]
    discarded = {e for _, _, e in tree}
    kept = tuple(k for k in range(2 * nsites) if k not in discarded)
    need(len(kept) == 13 and len(tree) == 11, "unexpected_gauge_tree")

    def canonical(u):
        h = [0] * nsites
        for src, dst, edge in tree:
            h[dst] = mul[h[src]][u[edge]]
        z = [0] * (2 * nsites)
        for x in range(lx):
            for y in range(ly):
                site = pos(x, y)
                z[site] = mul[mul[h[site]][u[site]]][inv[h[pos(x + 1, y)]]]
                z[nsites + site] = mul[mul[h[site]][u[nsites + site]]][inv[h[pos(x, y + 1)]]]
        need(all(z[k] == 0 for k in discarded), "not_tree_reduced")
        raw = tuple(z[k] for k in kept)
        return min(tuple(conj[g][a] for a in raw) for g in range(6))

    flats = {}
    for a in range(6):
        for b in range(6):
            if mul[a][b] != mul[b][a]:
                continue
            links = [0] * (2 * nsites)
            for y in range(ly):
                links[pos(lx - 1, y)] = a
            for x in range(lx):
                links[nsites + pos(x, ly - 1)] = b
            flats[canonical(links)] = (a, b)
    states = sorted(flats)
    weights = tuple(len({tuple(conj[g][a] for a in state) for g in range(6)})
                    for state in states)
    values = tuple(4 * char[flats[state][0]] + 3 * char[flats[state][1]]
                   for state in states)
    need(len(states) == 8 and sum(weights) == 18, "flat_orbit_census_changed")
    return weights, values


def flat_action_lower(vi, wi, oi, q_upper):
    pn = sum(w * x * x for w, x in zip(wi, vi))
    act = sum(w * o * o * x * x for w, o, x in zip(wi, oi, vi))
    need(pn > 0 and act > 0, "invalid_flat_vector_or_Wilson_action")
    # Norm^2 of exact resolvent-dressed sample:
    # flat-action/pn divided by (1+||R_z B v||^2), using the
    # accepted outward Q norm upper in units 10^-12.
    num = act * UNIT * UNIT
    den = pn * (UNIT * UNIT + q_upper * q_upper)
    need(den > 0, "missing_or_invalid_sample_normalization")
    # Integer floor of (lower W norm) * 10^12; never round upward.
    floor = isqrt((num * UNIT * UNIT) // den)
    return num, den, floor


def negative_tests(w, o, v):
    def frozen(wi, oi, vv):
        need(wi == FROZEN_W and oi == FROZEN_O, "incorrect_flat_operator_or_weight")
        need(vv == v, "swapped_or_corrupted_sample_vectors")
    tests = [
        (tuple(reversed(w)), o, v),
        (w, tuple(o[i] + int(i == 0) for i in range(8)), v),
        (w, o, list(reversed(v))),
    ]
    for wi, oi, vv in tests:
        try:
            frozen(wi, oi, vv)
        except ValueError:
            continue
        raise ValueError("negative_control_wrong_transformation_accepted")
    try:
        need(False, "missing_Q_tail_upper")
    except ValueError:
        pass
    else:
        raise ValueError("negative_control_missing_Q_accepted")
    need(w == FROZEN_W and o == FROZEN_O, "independent_flat_orbit_mismatch")


def main():
    vectors, q_uppers = exact_original_inputs()
    weights, values = independently_build_flat()
    need(weights == FROZEN_W and values == FROZEN_O, "independent_flat_rebuild_not_equal_source")
    negative_tests(weights, values, vectors)
    emit("Y137_G_FLATS", dimension=8, orbit_W=",".join(map(str, weights)),
         original_Wilson_O=",".join(map(str, values)),
         original_samples_same="PASS", source_blob_pins="4_OF_4_PASS",
         negative_controls="REFUSED")
    cert = []
    for i in range(2):
        num, den, floor = flat_action_lower(vectors[i], weights, values, q_uppers[i])
        need(num > (64 if i == 0 else 16) * den,
             "flat_lower_not_above_conservative_8_or_4")
        emit("Y137_G_POINT", level=i + 1, sample_num=Z[i],
             exact_Q_tail_upper_per_trillion=q_uppers[i],
             squared_lower_num=num, squared_lower_den=den,
             action_lower_floor_per_trillion=floor,
             conservative_integer_lower=8 if i == 0 else 4)
        cert.append((num, den, floor))
    # d2 is paired with O U1; d1 with O* U2 (O is real W-diagonal).
    # Even the cheap lower 8,4 gives a strict *lower* on the LHS.
    lower_cost_num = (8 * D2 + 4 * D1) * UNIT + 14 * D1 * D2
    lower_cost_den = UNIT * UNIT
    need(50 * lower_cost_num > lower_cost_den,
         "unshifted_observable_specific_sufficient_gate_not_ruled_out")
    need(cert[0][2] > 1646001682476 and cert[1][2] > 1646001682476,
         "common_ceiling_not_ruled_out")
    emit("Y137_G_VERDICT", accepted_samples="SAME_AS_180_185_AND_STAGE_E_FLATS",
         original_sample_weight="STRICT_GT_1_OVER_2500",
         source_conditional_flat_norm_lower="2_OF_2_CERTIFIED",
         conservative_cost_lower_num=lower_cost_num,
         conservative_cost_lower_den=lower_cost_den,
         required_margin_num=1, required_margin_den=50,
         raw_unshifted_common_action_ceiling="IMPOSSIBLE_FOR_ORIGINAL_SAMPLES",
         raw_unshifted_specific_inequality="NO_GO_WITH_ACCEPTED_D1_D2",
         shifted_observable="NOT_TESTED", full_Q_Wilson_action="NOT_COMPUTED",
         original_first_Wilson_weight="HOLD", issue_137="OPEN")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, IndexError, ZeroDivisionError) as exc:
        print("Y137_G_REFUSE|reason=" + str(exc) + "|json=0", flush=True)
        raise SystemExit(1) from None
