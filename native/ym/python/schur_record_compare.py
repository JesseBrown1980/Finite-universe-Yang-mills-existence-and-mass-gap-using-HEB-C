#!/usr/bin/env python3
"""Record-by-record comparison of shellschur and roomschur outputs at the same
thresholds (the P3 gate of results/3x4_stream/MEMORY-PILOT-SPEC.md). Integer-only, json=0.

For each threshold file pair (shellschur output, roomschur output):
  - the SHELL_SCHUR summary line: every field compared exactly, except `matrix=` (the
    input's name differs by construction) and `ms=` (wall-clock runtime metadata);
  - every SCOL line, keyed by (cb, ca): every field compared exactly; the key sets must
    be equal (a column present on one side only is a mismatch);
  - SHELL_SCHUR_COLS lines (split runs), keyed by `cols=`: every field except `ms=` and the
    room-only storage fields (`room_bytes_per_pass=`, `payload_merkle=`, `pass_ms=`, which
    only roomschur writes); the key sets must be equal. All room lines must agree on one
    `payload_merkle`, else INCONCLUSIVE.
Keys are never collapsed: a duplicate SHELL_SCHUR summary, a duplicate SCOL (cb, ca) key,
a duplicate SHELL_SCHUR_COLS `cols=` key, or a SCOL or SHELL_SCHUR_COLS line without its
key makes that file malformed, giving INCONCLUSIVE.
Excluded from equality, and printed as evidence: matrix= (input label) and ms= (wall clock).
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
# Fields only roomschur writes on its SHELL_SCHUR_COLS lines: where the matrix lives and how
# long a pass took, not the arithmetic. Excluded from equality, printed as evidence; every
# room line must carry one and the same payload_merkle, or the evidence is INCONCLUSIVE.
ROOM_ONLY_COLS = {"room_bytes_per_pass", "payload_merkle", "pass_ms"}


def parse(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    summ, scol, cols = None, {}, {}
    for line in open(path):
        p = line.rstrip("\n").split("|")
        f = dict(x.split("=", 1) for x in p[1:] if "=" in x)
        if p[0] == "SHELL_SCHUR":
            if summ is not None:
                return "duplicate_summary"
            summ = f
        elif p[0] == "SCOL":
            if "cb" not in f or "ca" not in f:
                return "scol_without_key"
            k = (f["cb"], f["ca"])
            if k in scol:
                return "duplicate_scol"
            scol[k] = f
        elif p[0] == "SHELL_SCHUR_COLS":
            if "cols" not in f:
                return "cols_line_without_key"
            if f["cols"] in cols:
                return "duplicate_cols_line"
            cols[f["cols"]] = f
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
    merkles = {x.get("payload_merkle") for x in lb.values()}
    if len(merkles) > 1:
        return "INCONCLUSIVE", "room_payload_merkle_inconsistent", 0
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
    if set(la) != set(lb):
        diffs.append("cols_line_keys:%d_only_shell,%d_only_room" % (len(set(la) - set(lb)), len(set(lb) - set(la))))
    for k in sorted(set(la) & set(lb)):
        for f in sorted((set(la[k]) | set(lb[k])) - EXCLUDE_COLS - ROOM_ONLY_COLS):
            if la[k].get(f) != lb[k].get(f):
                diffs.append("cols[%s].%s" % (k, f))
                break
    if diffs:
        return "MISMATCH", diffs[0] + ("|more=%d" % (len(diffs) - 1) if len(diffs) > 1 else "") + ev(sa, sb, lb), len(ca)
    return "AGREE", "result=%s|negative=%s|ambiguous=%s" % (sa.get("result"), sa.get("negative"), sa.get("ambiguous")) + ev(sa, sb, lb), len(ca)


def ev(sa, sb, lb):
    """The excluded fields, kept as evidence (not compared)."""
    room = sorted(lb.values(), key=lambda x: x["cols"])
    rb = ",".join(sorted({x.get("room_bytes_per_pass", "-") for x in room})) or "-"
    mk = ",".join(sorted({x.get("payload_merkle", "-") for x in room})) or "-"
    return ("|excluded_shell_matrix=%s|excluded_room_matrix=%s|excluded_shell_ms=%s|excluded_room_ms=%s"
            "|excluded_room_payload_merkle=%s|excluded_room_bytes_per_pass=%s") % (
        sa.get("matrix", "-"), sb.get("matrix", "-"), sa.get("ms", "-"), sb.get("ms", "-"), mk, rb)


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
