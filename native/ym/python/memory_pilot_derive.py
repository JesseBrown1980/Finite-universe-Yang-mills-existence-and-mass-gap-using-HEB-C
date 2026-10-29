#!/usr/bin/env python3
"""Derive COL_BYTES, RESERVE, CAP and the outcome of the 3x4 memory pilot from its raw
measurement lines (MEMORY-PILOT-SPEC.md sections 4-5). Integer-only, json=0.

Input lines (one file):
  PILOT_N|n=<states>|json=0
  PILOT_RUN|K=<k>|ru_maxrss_kib=<int>|anon_max=<bytes>|memory_peak=<bytes>|oom=<int>|oom_kill=<int>
           |exit=<int>|admitted=<0|1>|scol_col0_sha256=<hex>|json=0        (K = 1, 2, 4)
  PILOT_FAIL|reason=<text>|json=0       (any infrastructure failure recorded by the workflow)
usage: memory_pilot_derive.py RAW.hbp
"""
import sys

MIB = 1 << 20
BUDGET = 12 * (1 << 30)
KS = (1, 2, 4)


def up_mib(x):
    return -(-x // MIB) * MIB


def fields(line):
    return dict(p.split("=", 1) for p in line.strip().split("|")[1:] if "=" in p)


def derive(lines):
    out = []

    def done(outcome, reason):
        out.append("PILOT_OUTCOME|%s|reason=%s|json=0" % (outcome, reason))
        return out

    fails = [fields(l) for l in lines if l.startswith("PILOT_FAIL|")]
    if fails:
        return done("INCONCLUSIVE", "recorded_failure:" + fails[0].get("reason", "-"))
    ns = [fields(l) for l in lines if l.startswith("PILOT_N|")]
    runs = {}
    for l in lines:
        if l.startswith("PILOT_RUN|"):
            f = fields(l)
            k = int(f.get("K", "0"))
            if k in runs:
                return done("INCONCLUSIVE", "duplicate_K_%d" % k)
            runs[k] = f
    need = ("ru_maxrss_kib", "anon_max", "memory_peak", "oom", "oom_kill", "exit", "admitted", "scol_col0_sha256")
    if len(ns) != 1 or sorted(runs) != list(KS) or any(any(x not in runs[k] or runs[k][x] in ("", "-") for x in need) for k in KS):
        return done("INCONCLUSIVE", "missing_or_incomplete_measurement")
    try:
        n = int(ns[0]["n"])
        P = {k: max(int(runs[k]["ru_maxrss_kib"]) * 1024, int(runs[k]["anon_max"])) for k in KS}
        exits = [int(runs[k]["exit"]) for k in KS]
        ooms = sum(int(runs[k]["oom"]) + int(runs[k]["oom_kill"]) for k in KS)
        admitted = [runs[k]["admitted"] for k in KS]
    except (KeyError, ValueError):
        return done("INCONCLUSIVE", "malformed_measurement")
    col_decl, res_decl = 16 * n, 41 * n + 3 * 64 * MIB
    col_meas = up_mib(max(P[2] - P[1], -(-(P[4] - P[2]) // 2), 0))
    res_meas = up_mib(max(max(P[k] - k * col_meas for k in KS), 0))
    col = max(col_meas, up_mib(col_decl))
    res = max(res_meas, up_mib(res_decl))
    cap = (BUDGET - res) // col if res < BUDGET else 0
    for k in KS:
        out.append("PILOT_PEAK|K=%d|P=%d|bound=%d|within=%d|json=0" % (k, P[k], k * col + res, P[k] <= k * col + res))
    out.append("PILOT_DERIVED|n=%d|COL_BYTES_meas=%d|RESERVE_meas=%d|COL_BYTES_decl=%d|RESERVE_decl=%d|COL_BYTES=%d|RESERVE=%d|BUDGET=%d|CAP=%d|json=0"
               % (n, col_meas, res_meas, col_decl, res_decl, col, res, BUDGET, cap))
    if len({runs[k]["scol_col0_sha256"] for k in KS}) != 1:
        return done("INCONCLUSIVE", "column0_differs_across_K")
    if any(e != 0 for e in exits) and ooms == 0:
        return done("INCONCLUSIVE", "nonzero_exit_without_oom")
    if ooms > 0:
        return done("NOT_ADMISSIBLE", "oom_event")
    if any(P[k] > BUDGET for k in KS):
        return done("NOT_ADMISSIBLE", "peak_over_budget")
    if cap < 1:
        return done("NOT_ADMISSIBLE", "cap_below_1")
    if admitted != ["1", "1", "1"]:
        return done("INCONCLUSIVE", "admission_line_not_admitted")
    return done("PILOT_PASS", "all_gates")


def main():
    for line in derive(open(sys.argv[1]).read().splitlines()):
        print(line)


if __name__ == "__main__":
    main()
