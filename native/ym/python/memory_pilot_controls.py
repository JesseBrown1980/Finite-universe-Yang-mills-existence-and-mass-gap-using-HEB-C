#!/usr/bin/env python3
"""Synthetic controls for memory_pilot_derive.py (MEMORY-PILOT-SPEC.md section 7). No real
measurement is used. Integer-only, json=0.
usage: memory_pilot_controls.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_pilot_derive as d  # noqa: E402

N = 45508080
MIB = 1 << 20


def run_line(k, rss_kib, anon=0, peak=0, oom=0, kill=0, exit_=0, adm=1, sha="a" * 64):
    return ("PILOT_RUN|K=%d|ru_maxrss_kib=%d|anon_max=%d|memory_peak=%d|oom=%d|oom_kill=%d|exit=%d|admitted=%d|scol_col0_sha256=%s|json=0"
            % (k, rss_kib, anon, peak, oom, kill, exit_, adm, sha))


def clean(col=16 * N, res=41 * N + 3 * 64 * MIB):
    return ["PILOT_N|n=%d|json=0" % N] + [run_line(k, -(-(res + k * col) // 1024)) for k in (1, 2, 4)]


def outcome(lines):
    o = d.derive(lines)
    last = o[-1].split("|")
    der = [l for l in o if l.startswith("PILOT_DERIVED|")]
    return last[1], last[2], der[0] if der else ""


def main():
    res_ok = []

    def case(name, lines, want, check=None):
        got, reason, der = outcome(lines)
        ok = got == want and (check is None or check(der))
        res_ok.append(ok)
        print("PILOT_CONTROL|case=%s|want=%s|got=%s|%s|ok=%d|json=0" % (name, want, got, reason, ok))

    base = clean()
    exp_cap = (12 * (1 << 30) - (-(-(41 * N + 3 * 64 * MIB) // MIB) * MIB)) // (-(-(16 * N) // MIB) * MIB)
    case("clean_set", base, "PILOT_PASS", lambda s: ("|CAP=%d|" % exp_cap) in s)
    case("missing_ru_maxrss", [base[0], base[1].replace("ru_maxrss_kib=", "ru_maxrss_kib=-").replace("=-", "=-", 1).split("|ru_maxrss")[0] + "|json=0", base[2], base[3]], "INCONCLUSIVE")
    case("missing_K4", base[:3], "INCONCLUSIVE")
    case("recorded_failure", base + ["PILOT_FAIL|reason=upload_failed|json=0"], "INCONCLUSIVE")
    case("oom_kill", base[:3] + [run_line(4, 9000000, kill=1, exit_=137)], "NOT_ADMISSIBLE")
    case("peak_over_budget", base[:3] + [run_line(4, (13 << 30) // 1024)], "NOT_ADMISSIBLE")
    case("reserve_over_budget", clean(res=13 << 30), "NOT_ADMISSIBLE",
         lambda s: "|CAP=0|" in s)
    case("column0_differs", base[:3] + [base[3].replace("a" * 64, "b" * 64)], "INCONCLUSIVE")
    small = clean(col=1 << 20, res=1 << 20)
    case("below_declared_lifted", small, "PILOT_PASS",
         lambda s: ("|COL_BYTES=%d|" % (-(-(16 * N) // MIB) * MIB)) in s and ("|RESERVE=%d|" % (-(-(41 * N + 3 * 64 * MIB) // MIB) * MIB)) in s)
    big = clean(col=1500 * MIB, res=3000 * MIB)
    case("measured_above_declared_used", big, "PILOT_PASS",
         lambda s: "|COL_BYTES=%d|" % (1500 * MIB) in s and "|CAP=%d|" % ((12 * 1024 - 3000) // 1500) in s)
    case("duplicate_K", base + [base[1]], "INCONCLUSIVE")
    case("not_admitted_line", base[:3] + [base[3].replace("admitted=1", "admitted=0")], "INCONCLUSIVE")
    n = sum(1 for x in res_ok if x)
    print("PILOT_CONTROLS_TOTAL|cases=%d|ok=%d|result=%s|json=0" % (len(res_ok), n, "PASS" if n == len(res_ok) else "FAIL"))
    sys.exit(0 if n == len(res_ok) else 2)


if __name__ == "__main__":
    main()
