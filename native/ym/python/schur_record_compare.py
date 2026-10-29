#!/usr/bin/env python3
"""Record-by-record comparison of shellschur and roomschur outputs at the same
thresholds (the P3 gate of results/3x4_stream/MEMORY-PILOT-SPEC.md). Integer-only, json=0.

For each threshold file pair (shellschur output, roomschur output):
  - the SHELL_SCHUR summary line: every field compared exactly, except `matrix=` (the
    input's name differs by construction) and `ms=` (wall-clock runtime metadata);
  - every SCOL line, keyed by (cb, ca): every field compared exactly; the key sets must
    be equal (a column present on one side only is a mismatch);
  - SHELL_SCHUR_COLS lines (split runs): every field except `ms=`.
Outcome per threshold and overall:
  INCONCLUSIVE  a file missing or empty, no SHELL_SCHUR summary line on a side, or a
                summary with result=FAIL (a failed execution, not a completed count);
  MISMATCH      both sides completed and any corresponding field differs;
  AGREE         both sides completed and every corresponding field is equal.
AGREE is implementation agreement only: a threshold whose result is AMBIGUOUS on both
sides agrees as AMBIGUOUS and is not a spectral PASS.
usage: schur_record_compare.py SHELL_T1 ROOM_T1 [SHELL_T2 ROOM_T2 ...]
"""
import os
import sys

EXCLUDE_SUMMARY = {"matrix", "ms"}
EXCLUDE_COLS = {"ms"}


def parse(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    summ, scol, cols = None, {}, []
    for line in open(path):
        p = line.rstrip("\n").split("|")
        f = dict(x.split("=", 1) for x in p[1:] if "=" in x)
        if p[0] == "SHELL_SCHUR":
            if summ is not None:
                return "duplicate_summary"
            summ = f
        elif p[0] == "SCOL":
            k = (f.get("cb"), f.get("ca"))
            if k in scol:
                return "duplicate_scol"
            scol[k] = f
        elif p[0] == "SHELL_SCHUR_COLS":
            cols.append(f)
    return summ, scol, cols


def compare(a_path, b_path):
    a, b = parse(a_path), parse(b_path)
    if a is None or b is None:
        return "INCONCLUSIVE", "missing_or_empty_file", 0
    if isinstance(a, str) or isinstance(b, str):
        return "INCONCLUSIVE", "malformed_" + (a if isinstance(a, str) else b), 0
    (sa, ca, la), (sb, cb, lb) = a, b
    if sa is None or sb is None:
        return "INCONCLUSIVE", "no_summary_line", 0
    if sa.get("result") == "FAIL" or sb.get("result") == "FAIL":
        return "INCONCLUSIVE", "failed_execution", 0
    diffs = []
    for k in sorted((set(sa) | set(sb)) - EXCLUDE_SUMMARY):
        if sa.get(k) != sb.get(k):
            diffs.append("summary.%s:%s!=%s" % (k, sa.get(k), sb.get(k)))
    if set(ca) != set(cb):
        diffs.append("scol_keys:%d_only_shell,%d_only_room" % (len(set(ca) - set(cb)), len(set(cb) - set(ca))))
    for k in sorted(set(ca) & set(cb)):
        for f in sorted(set(ca[k]) | set(cb[k])):
            if ca[k].get(f) != cb[k].get(f):
                diffs.append("scol[%s,%s].%s" % (k[0], k[1], f))
                break
    strip = lambda L: sorted(tuple(sorted((k, v) for k, v in x.items() if k not in EXCLUDE_COLS)) for x in L)
    if strip(la) != strip(lb):
        diffs.append("shell_schur_cols_lines")
    if diffs:
        return "MISMATCH", diffs[0] + ("|more=%d" % (len(diffs) - 1) if len(diffs) > 1 else ""), len(ca)
    return "AGREE", "result=%s|negative=%s|ambiguous=%s" % (sa.get("result"), sa.get("negative"), sa.get("ambiguous")), len(ca)


def main(argv):
    if len(argv) < 2 or len(argv) % 2:
        raise SystemExit("usage: schur_record_compare.py SHELL_T1 ROOM_T1 [SHELL_T2 ROOM_T2 ...]")
    outs = []
    for i in range(0, len(argv), 2):
        v, why, n = compare(argv[i], argv[i + 1])
        outs.append(v)
        print("SCHUR_COMPARE|shell=%s|room=%s|scol_records=%d|verdict=%s|%s|json=0"
              % (os.path.basename(argv[i]), os.path.basename(argv[i + 1]), n, v, why))
    overall = "INCONCLUSIVE" if "INCONCLUSIVE" in outs else ("MISMATCH" if "MISMATCH" in outs else "AGREE")
    print("SCHUR_COMPARE_VERDICT|thresholds=%d|%s|json=0" % (len(outs), overall))
    raise SystemExit(0 if overall == "AGREE" else 2)


if __name__ == "__main__":
    main(sys.argv[1:])
