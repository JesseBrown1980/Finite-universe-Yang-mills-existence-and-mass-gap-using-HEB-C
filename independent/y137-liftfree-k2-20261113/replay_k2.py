#!/usr/bin/env python3
"""Issue #137: audit substitution of the new lift-free floor into old K2 Schur test.

The historical K2 evaluator is imported verbatim by its original git blob SHA.
No trial weights, graph edges, thresholds, Jacobi steps or source are modified.
Exact integer arithmetic only. New floor is a separate #173 certificate.
"""
from hashlib import sha1, sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD_FILE = ROOT / "independent/finite_s3_3x4_r9_first_gap.py"
RESULT = ROOT / "independent/y142-floor-word-search-20261113/RESULT-WORD-SEARCH.hbp"
GATE = ROOT / "independent/y142-floor-word-search-20261113/m13/run_m13_gate.txt"
OLD_SHA = "91bd1e80cbfcfb76198966aa177d097ecfbe8143"
RESULT_SHA = "57de51858e6a44dadd51c6e8419a549343145038"
GATE_SHA = "de97069e9fcc82fe2695fa922c4a3ab45d9143e8"
CERT_SHA = "7ad6e19977796ba4ecd321fdd028156fe57ee7ff782a6aef0aedb0a686c4a6b6"
OLD_G = 94070673
NEW_G = 94068200
ORIGINAL = ((0, 0), (1, 1), (1, 1), (6, 2))


def check(ok, label):
    if not ok:
        print("LIFT_FREE_K2_REFUSE|gate=" + label + "|json=0", flush=True)
        raise SystemExit(1)


def blob_pin(path, expected):
    raw = path.read_bytes()
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    got = sha1(header + raw).hexdigest()
    check(got == expected, "git_blob_" + path.name)
    return raw


def source_gate():
    result = blob_pin(RESULT, RESULT_SHA).decode("utf-8")
    gate = blob_pin(GATE, GATE_SHA).decode("utf-8")
    check("gamma=940682/10000|" in result, "new_floor_exact_gamma")
    check("pinned_verifier=GATE_REQUIRED_PASS|" in result, "new_result_pass")
    check("outcome=IMPROVED_BELOW_THRESHOLD|" in result, "new_decision_record")
    check("GATE_REQUIRED|PASS|" in gate, "new_cert_verifier_pass")
    check("cert_sha256=" + CERT_SHA in gate, "new_cert_sha256")
    check("t=940682/10000|" in gate, "new_cert_value")
    check(NEW_G < OLD_G, "new_floor_weaker_than_old")
    return sha256(result.encode()).hexdigest(), sha256(gate.encode()).hexdigest()


def main():
    result_hash, gate_hash = source_gate()
    blob_pin(OLD_FILE, OLD_SHA)
    spec = spec_from_file_location("historical_k2_unchanged", OLD_FILE)
    check(spec is not None and spec.loader is not None, "module_loader")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    name, source_num = module.source_floor()
    check(name == "PINNED_CONDITIONAL_WHOLE_ORBIT_LIFT", "original_source_label")
    check(source_num == OLD_G, "original_pinned_source_value")
    check(module.PERRON_SCALE == 1000000 and module.STEPS == 4,
          "old_precision_and_steps")
    check(tuple(x[0] for x in module.LEVELS) == (6989, 6992, 6993, 6996),
          "old_four_thresholds")
    check(tuple(x[1:] for x in module.LEVELS) == ORIGINAL,
          "old_frozen_inertias")

    print("LIFT_FREE_K2_BEGIN|historical_module_blob=" + OLD_SHA
          + "|liftfree_result_sha256=" + result_hash
          + "|liftfree_gate_sha256=" + gate_hash
          + "|source=PR173_certified_floor_at_r9"
          + "|checker_K2_graph=UNCHANGED|json=0", flush=True)

    w, m, adj, qflat, outer = module.graph()
    results = []
    for (a, lo, hi) in module.LEVELS:
        old = module.threshold(a, w, m, adj, qflat, outer, OLD_G)
        new = module.threshold(a, w, m, adj, qflat, outer, NEW_G)
        check(old[:2] == (lo, hi), "historical_K2_inertia_" + str(a))
        check(new[2] == old[2] and new[3] == old[3],
              "same_exact_U_and_G_" + str(a))
        check(new[0] >= old[0] and new[1] == old[1],
              "monotone_weaker_sandwich_" + str(a))
        results.append(new[:2])
        print("LIFT_FREE_K2_THRESHOLD|z=" + str(a) + "/100"
              + "|old_floor=" + str(OLD_G) + "/1000000"
              + "|new_floor=" + str(NEW_G) + "/1000000"
              + "|old_lower_inertia=" + str(old[0])
              + "|new_lower_inertia=" + str(new[0])
              + "|upper_inertia=" + str(new[1])
              + "|U_sha256=" + new[2]
              + "|G_sha256=" + new[3]
              + "|L_new_sha256=" + new[4]
              + "|json=0", flush=True)

    # One-sided inertia conditions suffice for E1/E2 windows;
    # the z=69.96 lower inertia need not be exactly 6.
    windows = (results[0] == (0, 0) and results[1] == (1, 1)
               and results[2] == (1, 1) and results[3][1] >= 2
               and results[3][0] >= results[3][1])
    label = ("WINDOWS_PRESERVED" if windows else "WINDOWS_NOT_ESTABLISHED")
    print("LIFT_FREE_K2_VERDICT|status=" + label
          + "|E1=(69.89,69.92)_if_preserved"
          + "|E2=(69.93,69.96)_if_preserved"
          + "|E3_separation=OPEN|Wilson_first_weight=OPEN"
          + "|original_#131_preserved=YES"
          + "|original_checker_source_modified=NO|json=0", flush=True)
    print("LIFT_FREE_K2_COMPLETE|thresholds=4|source_pins=PASS"
          + "|same_U_and_G=PASS|old_count_replay=PASS"
          + "|monotonicity=PASS|json=0", flush=True)


if __name__ == "__main__":
    main()
