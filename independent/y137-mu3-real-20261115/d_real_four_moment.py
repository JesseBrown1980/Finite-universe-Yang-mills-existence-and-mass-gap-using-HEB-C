#!/usr/bin/env python3
"""Issue #137 Cloud GPT-6: real four-moment Schur acceptance from the exact Stage C mu3.

Uses ONLY the original frozen rational/integer window and bracket code in
y137-mu3-acceptance-20261115, plus original pinned mu0, mu1, mu2 source files.
Input mu3_six was produced by four separately hosted full-Q Rust matrix jobs.
This executable computes the actual (not scenario-point) four-moment bracket.

Scientific gates kept distinct: actual Wilson first-excitation weight = HOLD.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "y137-mu3-acceptance-20261115"))
import mu3_acceptance as test
mr = test.mr

MU3_FILE = os.path.join(HERE, "RESULT-WORKER1-C-FULL-SIGNED-MU3-TWO-ENERGY-20261116.hbp")
FROZEN = (69909875505, 69949729820)
EXPECTED_MU3_SIX_SHA = {
    69909875505: "62787ba280050e598323eddcc67e0cd6234b8e2cfcb7b7bc65e6275fdfae4763",
    69949729820: "481f2c6b96cb7a7b756e15e96eb8734538a2b74fcb309ac2103a3e8f0284644d",
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def fields(line, tag):
    chunks = line.split("|")
    need(chunks[0] == tag, "wrong_source_record")
    row = {}
    for chunk in chunks[1:]:
        k, sep, v = chunk.partition("=")
        need(bool(sep) and k not in row, "duplicate_or_malformed_field")
        row[k] = v
    need(row.get("json") == "0", "invalid_receipt_terminator")
    return row


def parse_pinned_mu3(source):
    matrix_rows = [fields(line, "Y137_C_MU3_ACCEPT_MATRIX")
                   for line in source.splitlines()
                   if line.startswith("Y137_C_MU3_ACCEPT_MATRIX|")]
    verdicts = [fields(line, "Y137_C_MU3_ACCEPT_VERDICT")
                for line in source.splitlines()
                if line.startswith("Y137_C_MU3_ACCEPT_VERDICT|")]
    need(len(matrix_rows) == 2 and len(verdicts) == 1, "missing_or_duplicate_matrix_or_verdict")
    verdict = verdicts[0]
    need(verdict.get("two_frozen_energies") == "69909875505,69949729820"
         and verdict.get("whole_space_mu3_two_energy_matrices") == "CALCULATED"
         and verdict.get("row_vs_pair_exact_entries") == "128"
         and verdict.get("strict_signed_320bit_absolute_partial_sum_below_2pow294") == "PASS",
         "unaccepted_original_mu3_provenance")
    out = {}
    for item in matrix_rows:
        z = int(item["sample_num"])
        need(z in FROZEN and z not in out, "wrong_or_duplicate_energy")
        s = item["full_whole_Q_mu3_six"]
        digest = hashlib.sha256(s.encode("ascii")).hexdigest()
        need(digest == item["matrix_sha256"] == EXPECTED_MU3_SIX_SHA[z],
             "mu3_six_numeric_matrix_changed")
        need(item.get("all_64_exact_row_pair_entries") == "PASS"
             and item.get("original_B5_Q5_principal") == "ONCE",
             "missing_full_operator_acceptance")
        rows = mr.matrix(s)
        need(all(x % 6 == 0 for row in rows for x in row),
             "mu3_six_not_exactly_divisible_by_six")
        m3 = [[x // 6 for x in row] for row in rows]
        need(mr.symmetric(m3), "mu3_exact_symmetry_failure")
        out[z] = m3
    return out


def accepted_old_moments(index):
    sample = mr.read(mr.CACHE, "source", "Y137_CACHE_POINT")[index]
    one = mr.read(mr.MU1, "mu1", "Y137_MU1_COMPLETE_POINT")[index]
    two = mr.read(mr.MU2, "mu2", "Y137_D11_MU2_POINT")[index]
    z = FROZEN[index]
    need(all(int(record["sample_num"]) == z for record in (sample, one, two)),
         "historical_sample_order")
    U0i, G0 = mr.matrix(sample["U0"]), mr.matrix(sample["G0"])
    need(mr.sha(U0i) == sample["U_sha256"]
         and mr.sha(G0) == sample["G_sha256"]
         and all(x % 6 == 0 for row in G0 for x in row),
         "original_U0_G0_hash_or_weight")
    M0 = [[x // 6 for x in row] for row in G0]
    M1, M2 = mr.matrix(one["exact_mu1_8x8"]), mr.matrix(two["actual_K3_mu2_8x8"])
    need(mr.sha(M0) == one["wholeQ_mu0_sha256"] == two["actual_K3_mu0_sha256"]
         and mr.sha(M1) == one["wholeQ_mu1_sha256"] == two["actual_K3_mu1_sha256"]
         and mr.sha(M2) == two["actual_K3_mu2_sha256"],
         "original_mu0_mu1_mu2_SHA_regression")
    return test.F(U0i), test.F(M0), test.F(M1), test.F(M2)


def calculate():
    with open(MU3_FILE, encoding="ascii") as f:
        mu3 = parse_pinned_mu3(f.read())
    accepted = 0
    for index, z in enumerate(FROZEN):
        U0, m0, m1, m2 = accepted_old_moments(index)
        m3 = test.F(mu3[z])
        g, h = 94068200000 - z, 468000000000 - z
        need(0 < g < h, "invalid_frozen_spectral_range")
        L, U = test.window(m0, m1, m2, g, h)
        ok, reason = test.accept(mu3[z], L, U)
        need(ok, "real_mu3_outside_frozen_Loewner_window:" + reason)
        accepted += 1
        lo3, hi3 = test.bracket3(U0, m0, m1, m2, g, h)
        lo4, hi4 = test.bracket4(U0, m0, m1, m2, m3, g, h)
        nested = test.le(lo3, lo4) and test.le(hi4, hi3) and test.le(lo4, hi4)
        three_width = test.trace(test.sub(hi3, lo3))
        four_width = test.trace(test.sub(hi4, lo4))
        ratio_ppm = test.ppm(four_width, three_width)
        old_width = test.trace(test.scale(m0, test.Ratio(1, g)))
        old_ratio_ppm = test.ppm(four_width, old_width)
        negative_upper = mr.inertia(test.to_int(hi4))
        negative_lower = mr.inertia(test.to_int(lo4))
        target = index + 1
        low_den, low_sha = test.fingerprint(lo4)
        high_den, high_sha = test.fingerprint(hi4)
        print("Y137_D_REAL_FOUR_MOMENT|sample_num={}|mu3_window=PASS"
              "|four_moment_inside_three_moment={}"
              "|four_width_per_million_of_three={}"
              "|four_width_per_million_of_original={}"
              "|lower_negative_inertia={}|upper_negative_inertia={}"
              "|required_negative_inertia={}"
              "|lower_den={}|lower_exact_sha256={}"
              "|upper_den={}|upper_exact_sha256={}"
              "|source_mu3_six_sha256={}|Wilson_weight=HOLD|json=0".format(
                 z, "PASS" if nested else "HOLD", ratio_ppm, old_ratio_ppm,
                 negative_lower, negative_upper, target,
                 low_den, low_sha, high_den, high_sha, EXPECTED_MU3_SIX_SHA[z]),
              flush=True)
        need(nested, "real_four_moment_not_nested_in_three_moment")
        need(negative_lower == negative_upper == target,
             "actual_four_moment_inertia_disagreement")
    need(accepted == 2, "missing_real_energy")
    print("Y137_D_REAL_FOUR_MOMENT_VERDICT|real_mu3_windows=2_OF_2_PASS"
          "|real_four_moment_brackets=2_OF_2_EXACT"
          "|both_original_inertia_targets=PASS"
          "|first_Wilson_spectral_weight=HOLD"
          "|remaining=FULL_STATE_NORMALIZATION_ERROR_BELOW_1_OVER_700"
          "|json=0", flush=True)


def toy():
    with open(MU3_FILE, encoding="ascii") as f:
        raw = f.read()
    m = parse_pinned_mu3(raw)
    need(set(m) == set(FROZEN), "missing_frozen_matrices")
    original = EXPECTED_MU3_SIX_SHA[FROZEN[0]]
    bad = raw.replace(original, "0" * 64, 1)
    try:
        parse_pinned_mu3(bad)
    except ValueError:
        pass
    else:
        raise ValueError("forged_SHA_accepted")
    bad = raw.replace("69909875505", "69949729820", 1)
    try:
        parse_pinned_mu3(bad)
    except ValueError:
        pass
    else:
        raise ValueError("energy_swap_accepted")
    print("Y137_D_FOUR_MOMENT_TOY|two_pinned_full_matrices=PASS"
          "|forged_SHA=REFUSED|energy_swap=REFUSED"
          "|source_only_integer_arithmetic=PASS|real_brackets=NOT_COMPUTED|json=0")


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["real"]:
            calculate()
        elif sys.argv[1:] == ["toy"]:
            toy()
        else:
            raise ValueError("usage: d_real_four_moment.py real|toy")
    except (ValueError, KeyError, OSError, ZeroDivisionError) as exc:
        print("Y137_D_REAL_FOUR_MOMENT_REFUSE|reason={}|json=0".format(exc), flush=True)
        raise SystemExit(1) from None
