#!/usr/bin/env python3
"""Independent, integer-only #137 receipt replay and shell-5 omission control.

This is an acceptance-budget preflight. It does not claim an improved
shell-4/5 source certificate or a positive actual Wilson spectral weight.
"""
import hashlib
from fractions import Fraction
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
U = 10**12
D = 10**9
GAMMA = 94068200000
BUP = 8485281374239
PINS = {
    "center": ("independent/y137-centered-schur-transfer-20261113/RESULT-CENTERED-PROJECTOR.hbp",
               "3a147c8a750dae490882702307f8ec795a3c1f51", "Y137_CENTER_POINT"),
    "ortho": ("independent/y137-Schur-orthogonal-PSD-20261113/RESULT-ORTHOGONAL-SCHUR.hbp",
              "72c97666a8d788aa252085cdfe332102f549377b", "Y137_ORTHO_POINT"),
    "full": ("independent/y137-fullstate-Q-normalization-20261113/RESULT-FULL-W-NORM.hbp",
             "48c02e1e80112e5d758b403f41d07079d9fcb064", "Y137_FULLN_POINT"),
    "combined": ("independent/y137-combined-W-transfer-20261113/RESULT-COMBINED-FULL-W.hbp",
                 "a03d3e6ab5d9340518443e7d1b66c1ca25c2214d", "Y137_COMBINED_POINT"),
    "wilson": ("independent/y137-q-dual-weight-20261113/RESULT-WILSON-Q-DUAL.hbp",
               "40762ceb865829156e4765b720f52d39a8be9b6f",
               "Y137_QDUAL_RAW_WILSON_FIXED_WEIGHT"),
}
SAMPLES = (69909875505, 69949729820)


def require(value, reason):
    if not value:
        raise SystemExit("Y137_INDEP_REFUSE|reason=" + reason + "|json=0")


def ceildiv(n, d):
    require(n >= 0 and d > 0, "invalid_fraction")
    return (n + d - 1) // d


def ceilroot(n):
    require(n >= 0, "invalid_root")
    x = isqrt(n)
    return x + (x*x < n)


def blob_sha(raw):
    pre = ("blob " + str(len(raw)) + "\0").encode("ascii")
    return hashlib.sha1(pre + raw).hexdigest()


def records(key):
    path, pin, tag = PINS[key]
    raw = (ROOT / path).read_bytes()
    require(blob_sha(raw) == pin, "source_pin_" + key)
    result = []
    for line in raw.decode("utf-8").splitlines():
        fields = line.split("|")
        if fields[0] != tag:
            continue
        row = {}
        for fld in fields[1:]:
            require("=" in fld, "malformed_" + key)
            k, val = fld.split("=", 1)
            require(k not in row, "duplicate_" + key)
            row[k] = val
        result.append(row)
    require(len(result) == (1 if key == "wilson" else 2), "record_count_" + key)
    if key != "wilson":
        require(tuple(int(r["sample_num"]) for r in result) == SAMPLES,
                "sample_order_" + key)
    return result


def part(row, field):
    return int(row[field])


def source_rows():
    rows = {key: records(key) for key in PINS}
    fixed = rows["wilson"][0]
    require(fixed["evidence"] ==
            "RIGOROUS_FOR_UNSHIFTED_WILSON_FIXED_SAMPLES_ONLY",
            "raw_wilson_scope")
    require(part(fixed, "lower_ppb_floor") == 416300,
            "raw_wilson_lower_bound")
    require(Fraction(part(fixed, "lower_num"), part(fixed, "lower_den"))
            > Fraction(1, 2500), "raw_wilson_positive_margin")
    for i in range(2):
        old, perp, full, combined = (rows[key][i] for key in
                                      ("center", "ortho", "full", "combined"))
        require(old["U_sha256"] == perp["source_U_sha256"] and
                old["G_sha256"] == perp["source_G_sha256"],
                "different_source_matrix")
        require(part(old, "E_lo_num") == part(full, "true_E_lo_num") ==
                part(combined, "true_E_lo_num") and
                part(old, "E_hi_num") == part(full, "true_E_hi_num") ==
                part(combined, "true_E_hi_num"), "energy_window_changed")
        require(perp["lambda_perp_127_PSD"] == "1" and
                perp["G_all_255_PSD"] == "1" and
                old["mu_strictly_inside_null_gap"] == "1",
                "source_PSD_or_null_gate")
    return rows


def bound_for(rows, i, source_factor=1, energy_factor=1, fixed_mu=True):
    """Independent reassembly. Factors describe hypotheticals, not certificates."""
    old, perp, full, c = (rows[key][i] for key in
                          ("center", "ortho", "full", "combined"))
    z = SAMPLES[i]
    hi = part(old, "E_hi_num")
    require(hi == z and GAMMA > hi, "frozen_sample_and_floor")
    g = GAMMA - hi
    old_delta = part(full, "energy_variation_num")
    delta = ceildiv(old_delta, energy_factor) if energy_factor else 0
    action = ceildiv(part(perp, "selected_source_action_upper_per_trillion"),
                     source_factor) if source_factor else 0
    qup = part(full, "Q_Rz_Bx_upper_per_trillion")
    qlo = part(full, "Q_Rz_Bx_lower_per_trillion")
    extra = ceildiv(delta * BUP * qup, U * g)
    previous_extra = part(perp, "energy_directional_extra_upper_per_trillion")
    mu = (part(perp, "Rayleigh_mu_upper_per_trillion") -
          previous_extra + extra)
    if not fixed_mu:
        mu -= part(old, "energy_scalar_drift_upper_per_trillion")
        mu += ceildiv(delta * U, D)
    else:
        mu = part(c, "Rayleigh_mu_refined_upper_per_trillion")
    gap = part(perp, "Schur_null_gap_lower_per_trillion")
    require(0 < mu < gap, "Rayleigh_branch")
    center = (part(perp, "centered_variational_U_upper_per_trillion") +
              action + extra)
    sine = ceildiv(center * U, gap - mu)
    require(sine < U, "vacuous_flat_angle")
    flat = ceilroot(2 * U * (U - isqrt(U*U - sine*sine)))
    qr = ceildiv(BUP * flat * D, U * g)
    qe = ceildiv(delta * qup, g)
    qdiff = qr + qe
    unnormalized = ceilroot(flat*flat + qdiff*qdiff)
    nz = isqrt(U*U + qlo*qlo)
    nt = isqrt(U*U + max(0, qlo-qdiff)**2)
    norm = isqrt(nz*nt)
    error = ceildiv(unnormalized * U, norm)
    return {"sine": sine, "error": error, "mu": mu,
            "energy_extra": extra, "source_action": action}


def source_replay(rows):
    errs = []
    for i in range(2):
        c = rows["combined"][i]
        r = bound_for(rows, i)
        require(r["sine"] == part(c, "refined_flat_sin_upper_per_trillion"),
                "flat_sin_mismatch")
        require(r["error"] ==
                part(c, "full_normalized_state_error_upper_per_trillion"),
                "full_W_norm_mismatch")
        errs.append(r["error"])
    total = sum(errs)
    require(total == 144090460519, "accepted_combined_ceiling")
    require(700*total >= U, "incorrect_success_label")
    return total


def hypotheticals(rows):
    cases = (
        ("source_action_zero", 0, 1, True, 13162197722),
        ("energy_variation_zero", 1, 0, True, 130824656179),
        ("both_100_fixed_rayleigh", 100, 100, True, 1435396879),
        ("both_101_fixed_rayleigh", 101, 101, True, 1421178505),
        ("both_100_recomputed_rayleigh", 100, 100, False, 1318722908),
    )
    for name, fa, fe, keep_mu, want in cases:
        total = sum(bound_for(rows, i, fa, fe, keep_mu)["error"]
                    for i in range(2))
        require(total == want, "sensitivity_" + name)
        # The final column is a planning calculation; no source certificate exists.
        print("Y137_INDEP_SENSITIVITY|case=" + name +
              "|combined_upper_per_trillion=" + str(total) +
              "|would_pass_numeric_gate=" + str(int(700*total < U)) +
              "|verified_source_improvement=0|json=0")


def krylov_lemma_and_faults():
    """Exact toy shell4->shell5 residual. The last component must be counted."""
    # A = [[10,-1],[-1,5]] >= 4 I by row diagonal dominance.
    # Starting residual R=[10,0] is entirely on shell4.
    # Corrector V=[1,0] leaves E=R-AV=[0,1] on shell5.
    # A^-1 = [[5,1],[1,10]] / 49, so X=R^T A^-1 R.
    lower = Fraction(10)
    exact = Fraction(500, 49)
    upper = lower + Fraction(1, 4)
    require(lower <= exact <= upper, "Krylov_sandwich")
    require(exact > lower, "shell5_omission_not_detected")
    # A corrupted pinned receipt must fail the independently computed Git blob.
    example = b"Y137_DATA|abc=1|json=0\n"
    require(blob_sha(example) != blob_sha(example + b"tamper"),
            "sha_negative_control")
    print("Y137_INDEP_KRYLOV|toy_shell4_residual=10,0"
          "|toy_shell5_correction_residual=0,1"
          "|exact_resolvent_num=500|exact_resolvent_den=49"
          "|lower=10|upper=41/4|omitted_shell5_rejected=1"
          "|tampered_receipt_rejected=1|source_model=TOY_ONLY|json=0")


def main():
    rows = source_rows()
    total = source_replay(rows)
    print("Y137_INDEP_BASELINE|source_pins=5|samples=2"
          "|accepted_combined_error_per_trillion=" + str(total) +
          "|true_first_Wilson_weight=HOLD|json=0")
    krylov_lemma_and_faults()
    hypotheticals(rows)
    print("Y137_INDEP_VERDICT|integer_replay=PASS"
          "|next_real_shell4_certificate=NOT_PRESENT"
          "|next_real_energy_brackets=NOT_PRESENT"
          "|actual_E1_E2_Wilson_spectral_weight=HOLD|json=0")


if __name__ == "__main__":
    main()
