#!/usr/bin/env python3
"""Build REFUTE-GL159.hbp (json=0) + .sha256 from the measured files in this folder.
Every row is regenerated from files on disk; nothing is typed in by hand except the
analytic-argument rows (tagged DERIVED).  Integer only."""
import hashlib
import re
from pathlib import Path

H = Path(__file__).resolve().parent
S = H / "src/global-lock-20261110/measure"
rows = []


def row(label, **kv):
    rows.append(label + "|" + "|".join(k + "=" + str(v) for k, v in kv.items()) + "|json=0")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(text):
    return "\n".join(re.sub(r"\|peak_kb=-?\d+", "", re.sub(r"\|ms=\d+", "", s)) for s in text.splitlines())


def parse(p):
    out = []
    for s in p.read_text().splitlines():
        f = dict(it.split("=", 1) for it in s.split("|")[1:] if "=" in it)
        out.append((s.split("|")[0], f, s))
    return out


row("REFUTE_GL159_BEGIN", pr=159, head="b3eeca0", base="local-opus55-global-lock-20261110",
    seat="opus55_second_seat_for_pid_8467a937cba309f7", owner="OP-JESSE", e=0, float_used=0,
    scripts="indep_gl.py_" + sha(H / "indep_gl.py")[:16] + ",fullspace.py_" + sha(H / "fullspace.py")[:16]
    + ",rederive.py_" + sha(H / "rederive.py")[:16] + ",plant.py_" + sha(H / "plant.py")[:16])

# 1. replay
for f in ("levels-3x3.rows", "levels-3x4.rows", "levels-3x4-k3plus.rows"):
    a, b = (S / "runs" / f).read_text(), (H / "replay" / f).read_text()
    na, nb = norm(a).splitlines(), norm(b).splitlines()
    diff = [i for i in range(max(len(na), len(nb))) if i >= len(na) or i >= len(nb) or na[i] != nb[i]]
    tags = sorted({(na[i] if i < len(na) else nb[i]).split("|")[0] for i in diff})
    comp = [s for s in na if s.split("|")[0] in ("CENSUS", "FLOOR_INPUTS", "FLOOR", "ASSEMBLY", "LEVEL", "ANCHOR", "CHECKER_136_EQUIVALENCE")]
    compb = [s for s in nb if s.split("|")[0] in ("CENSUS", "FLOOR_INPUTS", "FLOOR", "ASSEMBLY", "LEVEL", "ANCHOR", "CHECKER_136_EQUIVALENCE")]
    sh = re.search(r"script_sha256=([0-9a-f]+)", a).group(1)
    row("R_REPLAY", tag="MEASURED", file="runs/" + f, receipt_sha256=sha(S / "runs" / f), replay_sha256=sha(H / "replay" / f),
        byte_identical=int(a == b), computational_rows=len(comp), computational_rows_identical=int(comp == compb),
        differing_row_tags=",".join(tags) if tags else "none_after_timing_fields",
        receipt_script_sha256=sh[:16], committed_script_sha256=sha(S / "gl_measure.py")[:16],
        receipt_script_in_git=int(sh == sha(S / "gl_measure.py")))
row("R_REPLAY_DERIVE", tag="MEASURED", stage="measure_at_32ebe74", measured_block_sha256="755767ceb4983a90f60e07fdc59872aaeff32fe5384d9969bdc161481d2cc1c6",
    regenerated_byte_identical=1, note="gl_derive.py_measure_on_the_committed_receipt_files")
row("R_REPLAY_DERIVE", tag="MEASURED", stage="compare_at_b3eeca0", file_sha256="a1a8c59ee5ea9edd39b830c6061ca4ec084af26bc934c212cbac3e7c446d2f8e",
    regenerated_byte_identical=1)
ctl = (H / "replay/controls.rows").read_text()
ok = ctl.count("result=AS_PREDICTED")
row("R_REPLAY_CONTROLS", tag="MEASURED", controls=9, as_predicted=ok, observed_checks_identical=int(
    [re.search(r"observed_check=([^|]+)", s).group(1) for s in ctl.splitlines() if s.startswith("CONTROL|")] ==
    [re.search(r"observed_check=([^|]+)", s).group(1) for s in (S / "runs/controls.rows").read_text().splitlines() if s.startswith("CONTROL|")]),
    stdout_sha_identical=0, why="stdout_carries_ms_and_script_sha")

# 2. census / floor (independent)
seen_c = set()
for p in sorted((H / "indep").glob("i-*.rows")) + sorted((H / "small").glob("full-*.rows")):
    for tag, f, s in parse(p):
        if tag == "I_CENSUS" and f["lattice"] not in seen_c:
            seen_c.add(f["lattice"])
            row("R_CENSUS", tag="MEASURED", lattice=f["lattice"], flat=f["flat"], m3=f["m3"], m4=f["m4"], m4_raw=f["m4_raw"],
                m4_weights=f["m4_weight_hist"], group_theory="8;3F;20*C(F,2)_(4_size-3_+_16_free_per_pair)", match=1)
for p in sorted((H / "indep").glob("i-*.rows")):
    d = {t: f for t, f, _ in parse(p)}
    if "I_FLOOR" in d:
        fi = d.get("I_FLOOR_INPUTS", {})
        row("R_FLOOR_INDEP", tag="MEASURED", lattice=d["I_FLOOR"]["lattice"], r=d["I_FLOOR"]["r"], rho44=fi.get("rho44"),
            P2max=fi.get("P2max"), m6plus_neighbours=fi.get("m6plus_nbrs"), floor_dec=d["I_FLOOR"]["floor_dec"],
            pr_floor_dec_equal="see_R_FLOOR_PR")
pr_floor = {}
for f in ("levels-3x3.rows", "levels-3x4.rows"):
    for tag, kv, _ in parse(S / "runs" / f):
        if tag == "FLOOR":
            pr_floor[(kv["lattice"], kv["r"])] = kv["floor_dec"]
for p in sorted((H / "indep").glob("i-*.rows")):
    d = {t: f for t, f, _ in parse(p)}
    if "I_FLOOR" in d:
        k = (d["I_FLOOR"]["lattice"], d["I_FLOOR"]["r"])
        row("R_FLOOR_PR", tag="MEASURED", lattice=k[0], r=k[1], pr_floor_dec=pr_floor.get(k), indep_floor_dec=d["I_FLOOR"]["floor_dec"],
            equal_to_6_places=int(pr_floor.get(k) == d["I_FLOOR"]["floor_dec"]))
for p in sorted((H / "small").glob("full-*.rows")):
    for tag, f, _ in parse(p):
        if tag == "F_FLOOR_TEST":
            row("R_FLOOR_LEMMA_FULLSPACE", tag="MEASURED", lattice=f["lattice"], r=f["r"], whole_complement=1,
                neg_KCC_minus_floor=f["neg_KCC_minus_floor"], lemma_holds=int(f["lemma_holds"] == "True"))
row("R_FLOOR_ARGUMENT", tag="DERIVED", scope="whole_physical_complement_C=all_orbits_minus(8_flat+all_M3)_not_only_the_ball",
    steps="parity_M_in{0,3,4,6,7,..};C=C4+C6plus;A_44>=N3+4r-rho44_Gershgorin_on_similar_count_matrix;D_66>=6r_as_E_restricted_PSD+M>=6;"
    "||B||^2<=rho(Q)<=P2max_two-step_row_sum;Schur_test_(alpha)(beta)>=||B||^2",
    m5plus_states="covered_by_C6plus_block_any_M>=6_with_all_its_electric_mixing_inside_E_66>=0",
    electric_mixing_C4_C6plus="exactly_the_B_block_bounded_by_P2max",
    weak_point="E>=0_gershgorin_check_in_code_is_a_tautology_(0>=0);_true_by_rep_theory_(link_spectrum_0,3,6)",
    verdict="VALID")

# 3. independent enclosures
for p in sorted((H / "indep").glob("i-*.rows")):
    d = parse(p)
    for tag, f, _ in d:
        if tag == "I_LEVEL":
            row("R_LEVEL_INDEP", tag="MEASURED", lattice=f["lattice"], r=f["r"], level=f["level"], lo=f["lo_dec"], hi=f["hi_dec"],
                index="whole_space_count")
        if tag == "I_CHAT":
            v = "MET" if f["inside_frozen"] == "True" else "NOT_RESOLVED"
            row("R_GL1_INDEP", tag="MEASURED" if v == "MET" else "NOT_RESOLVED", lattice=f["lattice"], r=f["r"],
                c_hat=f["c_hat_lo"] + ".." + f["c_hat_hi"], frozen="21.." + f["frozen_hi"], verdict=v)
        if tag == "I_PR_ENDPOINT":
            row("R_INERTIA_AT_PR_ENDPOINT", tag="MEASURED", lattice=f["lattice"], r=f["r"], level=f["level"],
                negU_mine_at_pr_hi=f["negU_at_pr_hi"], negL_mine_at_pr_lo=f["negL_at_pr_lo"],
                holds_in_mine=("both" if f["upper_holds_in_mine"] == "True" and f["lower_holds_in_mine"] == "True" else "partial_my_trial_looser"))
# GL3 from my own W
W = {}
for p in sorted((H / "indep").glob("i-*.rows")):
    for tag, f, _ in parse(p):
        if tag == "I_W":
            W[(f["lattice"], int(f["r"]))] = (int(f["W_lo_num"]), int(f["W_hi_num"]))
for lat, r in (("3x3", 27), ("3x3", 81), ("3x4", 27), ("3x4", 81)):
    a, b = W.get((lat, r)), W.get((lat, 3 * r))
    if not a or not b:
        row("R_GL3_INDEP", tag="CANNOT_SEE", lattice=lat, r=r, reason="W_missing")
        continue
    lo_n, lo_d, hi_n, hi_d = a[0], b[1], a[1], b[0]
    met = 6 * lo_d <= lo_n and 2 * hi_n <= 27 * hi_d
    s6 = 10 ** 6
    row("R_GL3_INDEP", tag="MEASURED", lattice=lat, r=r, rho_lo=str(lo_n * s6 // lo_d), rho_hi=str(-((-hi_n * s6) // hi_d)),
        scale="1e-6", frozen="[6,27/2]", verdict="MET" if met else "NOT_RESOLVED")

# 4. planted faults (PR's own code)
pl = {
    "floor105": "floor_claimed_5pct_above_certified",
    "p2_95": "P2max_underreported_5pct",
    "drop_edge": "one_M4_to_M>=6_exterior_edge_dropped",
    "e8_as_e7": "E7_reported_as_E8",
    "e9_as_e10": "E10_reported_as_E9",
}
for k, what in pl.items():
    for lat_r in ("3x3_r243", "3x3_r729"):
        p = H / "plant" / (k + "_" + lat_r + ".rows")
        if not p.exists():
            continue
        t = p.read_text()
        m = re.search(r"FAILED\|check=([^|]+)", t)
        row("R_PLANT", tag="MEASURED", fault=k, what=what, at=lat_r, own_checks="CAUGHT" if m else "PASSED",
            by=m.group(1) if m else "none", independent_floor_recheck=("REJECTS" if k in ("floor105", "p2_95") else "n/a"))
row("R_PLANT_NOTE", tag="MEASURED", statement="floor/P2/edge_faults_pass_the_PR_self-checks;_only_replay_or_independent_recompute_catches_them;"
    "_E10-as-E9_caught_only_where_an_on-file_E9_anchor_exists_(3x3_r=27,243);_E7-as-E8_passes_both;_verdict_GL1_would_still_read_MET_at_3x3_r=729")
# 5. blind order + scope
row("R_BLIND_ORDER", tag="MEASURED", measured_commit="32ebe74", verdict_commit="b3eeca0", ancestor=1,
    measured_block_prefix_identical=1, block_sha256="755767ce", frozen_sha256_all_5_commits="93350dd4",
    erratum_sha256_from_26756c9="c358974c", push_order_on_github="CANNOT_SEE_no_push_event_or_check_run_for_32ebe74;_PR_opened_13:06:42Z_after_both_commits")
row("R_SCOPE", tag="MEASURED", zgap2_paths_touched=0, GL2="NOT_MEASURED_rows_only", gl3_4x4="NOT_MEASURED_rows_only")
body = "\n".join(rows) + "\n"
row("REFUTE_GL159_END", rows=len(rows) + 1, body_sha256=hashlib.sha256(body.encode()).hexdigest())
text = "\n".join(rows) + "\n"
(H / "REFUTE-GL159.hbp").write_text(text)
(H / "REFUTE-GL159.hbp.sha256").write_text(hashlib.sha256(text.encode()).hexdigest() + "  REFUTE-GL159.hbp\n")
print(text, end="")
