#!/usr/bin/env python3
"""Memory-lean implementation of schur_record_compare.py (comparator v2), for evidence too
large for v2 to hold in RAM (3x3 at t = 90,000,000: 8,643,600 SCOL records per side).

Same rules, same verdicts, same output lines as v2:
  - the shell file is parsed as v2 parses it, but each SCOL record is kept as one canonical
    string `k=v|k=v|...` (fields sorted by name). Field names contain no `=` or `|` and values
    contain no `|`, so two records' strings are equal exactly when v2's field dicts are equal;
  - the room file is streamed line by line against it, with the same malformation checks
    (duplicate summary, duplicate or missing SCOL key, duplicate or missing cols key) in the
    same file order, so the first malformation reported is the one v2 reports;
  - verdict order, diff order (summary fields, SCOL key sets, SCOL records by sorted key,
    cols keys, cols fields) and every printed field are taken from v2's code, reusing v2's
    constants and its evidence function.
With `--v1` it applies the frozen comparator v1 (`9f60d56`) instead: no room-only field
exclusion, no payload_merkle consistency check, and v1's evidence fields.
Equivalence with v2 (and with v1 under `--v1`) is checked on every synthetic control and on real evidence pairs where v2
fits in memory (schur_record_compare_stream_controls.py). Integer-only, json=0.
usage: schur_record_compare_stream.py [--v1] SHELL_T1 ROOM_T1 [SHELL_T2 ROOM_T2 ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schur_record_compare as v2  # noqa: E402


def fields(line):
    p = line.rstrip("\n").split("|")
    return p[0], dict(x.split("=", 1) for x in p[1:] if "=" in x)


def canon(f):
    return "|".join("%s=%s" % (k, f[k]) for k in sorted(f))


def uncanon(s):
    return dict(x.split("=", 1) for x in s.split("|")) if s else {}


def parse_compact(path):
    """v2.parse with each SCOL record held as its canonical string."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    summ, scol, cols = None, {}, {}
    with open(path) as fh:
        for line in fh:
            tag, f = fields(line)
            if tag == "SHELL_SCHUR":
                if summ is not None:
                    return "duplicate_summary"
                summ = f
            elif tag == "SCOL":
                if "cb" not in f or "ca" not in f:
                    return "scol_without_key"
                k = (f["cb"], f["ca"])
                if k in scol:
                    return "duplicate_scol"
                scol[k] = canon(f)
            elif tag == "SHELL_SCHUR_COLS":
                if "cols" not in f:
                    return "cols_line_without_key"
                if f["cols"] in cols:
                    return "duplicate_cols_line"
                cols[f["cols"]] = f
    return summ, scol, cols


def stream_room(path, ca):
    """Stream the room file against the shell records `ca` (consumed as matched).
    Returns a malformation string, or (summary, cols, n_room_scol, room_only, field_diffs)."""
    summ, cols, seen = None, {}, set()
    n_room, room_only, field_diffs = 0, 0, []
    with open(path) as fh:
        for line in fh:
            tag, f = fields(line)
            if tag == "SHELL_SCHUR":
                if summ is not None:
                    return "duplicate_summary"
                summ = f
            elif tag == "SCOL":
                if "cb" not in f or "ca" not in f:
                    return "scol_without_key"
                k = (f["cb"], f["ca"])
                if k in seen:
                    return "duplicate_scol"
                seen.add(k)
                n_room += 1
                s = ca.pop(k, None)
                if s is None:
                    room_only += 1
                elif s != canon(f):
                    a = uncanon(s)
                    for fld in sorted(set(a) | set(f)):
                        if a.get(fld) != f.get(fld):
                            field_diffs.append((k, fld))
                            break
            elif tag == "SHELL_SCHUR_COLS":
                if "cols" not in f:
                    return "cols_line_without_key"
                if f["cols"] in cols:
                    return "duplicate_cols_line"
                cols[f["cols"]] = f
    return summ, cols, n_room, room_only, field_diffs


def ev_v1(sa, sb):
    """v1's evidence fields (frozen comparator 9f60d56)."""
    return "|excluded_shell_matrix=%s|excluded_room_matrix=%s|excluded_shell_ms=%s|excluded_room_ms=%s" % (
        sa.get("matrix", "-"), sb.get("matrix", "-"), sa.get("ms", "-"), sb.get("ms", "-"))


def compare(a_path, b_path, v1=False):
    if not os.path.exists(b_path) or os.path.getsize(b_path) == 0:
        b_missing = True
    else:
        b_missing = False
    a = parse_compact(a_path)
    if a is None or b_missing:
        return "INCONCLUSIVE", "missing_or_empty_file", 0
    if isinstance(a, str):
        return "INCONCLUSIVE", "malformed_" + a, 0
    sa, ca, la = a
    n_shell = len(ca)
    b = stream_room(b_path, ca)
    if isinstance(b, str):
        return "INCONCLUSIVE", "malformed_" + b, 0
    sb, lb, n_room, room_only, field_diffs = b
    shell_only = len(ca)  # shell keys never matched by a room record
    if sa is None or sb is None:
        return "INCONCLUSIVE", "no_summary_line", 0
    if sa.get("result") == "FAIL" or sb.get("result") == "FAIL":
        return "INCONCLUSIVE", "failed_execution", 0
    if not v1:
        merkles = {x.get("payload_merkle") for x in lb.values()}
        if len(merkles) > 1:
            return "INCONCLUSIVE", "room_payload_merkle_inconsistent", 0
    cols_excl = v2.EXCLUDE_COLS if v1 else v2.EXCLUDE_COLS | v2.ROOM_ONLY_COLS
    evid = ev_v1(sa, sb) if v1 else v2.ev(sa, sb, lb)
    diffs = []
    for k in sorted((set(sa) | set(sb)) - v2.EXCLUDE_SUMMARY):
        if sa.get(k) != sb.get(k):
            diffs.append("summary.%s:%s!=%s" % (k, sa.get(k), sb.get(k)))
    if shell_only or room_only:
        diffs.append("scol_keys:%d_only_shell,%d_only_room" % (shell_only, room_only))
    for k, fld in sorted(field_diffs):
        diffs.append("scol[%s,%s].%s" % (k[0], k[1], fld))
    if set(la) != set(lb):
        diffs.append("cols_line_keys:%d_only_shell,%d_only_room" % (len(set(la) - set(lb)), len(set(lb) - set(la))))
    for k in sorted(set(la) & set(lb)):
        for f in sorted((set(la[k]) | set(lb[k])) - cols_excl):
            if la[k].get(f) != lb[k].get(f):
                diffs.append("cols[%s].%s" % (k, f))
                break
    if diffs:
        return "MISMATCH", diffs[0] + ("|more=%d" % (len(diffs) - 1) if len(diffs) > 1 else "") + evid, n_shell
    return "AGREE", "result=%s|negative=%s|ambiguous=%s" % (sa.get("result"), sa.get("negative"), sa.get("ambiguous")) + evid, n_shell


def main(argv):
    v1 = bool(argv) and argv[0] == "--v1"
    if v1:
        argv = argv[1:]
    if len(argv) < 2 or len(argv) % 2:
        raise SystemExit("usage: schur_record_compare_stream.py SHELL_T1 ROOM_T1 [SHELL_T2 ROOM_T2 ...]")
    outs = []
    for i in range(0, len(argv), 2):
        v, why, n = compare(argv[i], argv[i + 1], v1)
        outs.append(v)
        print("SCHUR_COMPARE|shell=%s|room=%s|scol_records=%d|verdict=%s|%s|json=0"
              % (os.path.basename(argv[i]), os.path.basename(argv[i + 1]), n, v, why))
        sys.stdout.flush()
    overall = "INCONCLUSIVE" if "INCONCLUSIVE" in outs else ("MISMATCH" if "MISMATCH" in outs else "AGREE")
    print("SCHUR_COMPARE_VERDICT|thresholds=%d|%s|json=0" % (len(outs), overall))
    raise SystemExit(0 if overall == "AGREE" else 2)


if __name__ == "__main__":
    main(sys.argv[1:])
