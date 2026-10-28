#!/usr/bin/env python3
"""Plan control for the certify step (erratum 1): the plan computed with (SPLIT, COLS) must
reproduce the admitted stage B job set exactly, its hash-selected sample must be real
admitted cells, and, without reading any count, every sealed merge's MERGE_INPUT cell list
must equal the plan's cells for that count in order. Integer-only, json=0.

usage: certify_plan_check.py CORES CORES_SHA SPLIT COLS MANIFEST [MANIFEST ...] [--sealed=DIR]
  DIR: the admitted parts/shards directory (only MERGE_INPUT lines are read; no count field).
Exit 0 only if every check holds.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import full_space_certify as fsc  # noqa: E402


def main(a):
    sealed = next((x.split("=", 1)[1] for x in a if x.startswith("--sealed=")), None)
    a = [x for x in a if not x.startswith("--")]
    cores, cores_sha, split, cols, mans = a[0], a[1], int(a[2]), int(a[3]), a[4:]
    entries, sectors, sample, _ = fsc.load_plan(cores, cores_sha, split, cols)
    plan = set()
    for spec, cells, merge in entries:
        if merge:
            plan |= {fsc.sid(c) for c in cells}
            plan.add(fsc.sid(merge))
        else:
            plan.add(fsc.sid(spec))
    admitted, admitted_cells = set(), set()
    for m in mans:
        for line in open(m):
            if line.startswith("CMANIFEST|"):
                f = dict(x.split("=", 1) for x in line.rstrip("\n").split("|")[1:] if "=" in x)
                if f["kind"] in ("cell", "merge"):
                    admitted.add(f["shard"])
                if f["kind"] == "cell":
                    admitted_cells.add(f["shard"])
    plan_eq = plan == admitted
    sample_ok = all(fsc.sid(c) in admitted_cells for c in sample)
    print("PLAN_CHECK|split=%d|cols=%d|plan_specs=%d|admitted_specs=%d|only_in_plan=%d|only_admitted=%d|equal=%d|json=0"
          % (split, cols, len(plan), len(admitted), len(plan - admitted), len(admitted - plan), plan_eq))
    for c in sample:
        print("PLAN_SAMPLE|spec=%s|admitted_cell=%d|json=0" % (c, fsc.sid(c) in admitted_cells))
    part_ok = True
    if sealed:
        n = 0
        for spec, cells, merge in entries:
            if not merge:
                continue
            p = os.path.join(sealed, fsc.sid(merge), "run.hbp")
            got = [re.search(r"\|spec=([^|]+)\|", l).group(1) for l in open(p) if l.startswith("MERGE_INPUT|")]
            ok = got == list(cells)
            part_ok &= ok
            n += 1
            print("PLAN_PARTITION|merge=%s|plan_cells=%d|sealed_merge_inputs=%d|same_list_in_order=%d|json=0"
                  % (fsc.sid(merge), len(cells), len(got), ok))
        print("PLAN_PARTITION_TOTAL|merges=%d|all_equal=%d|counts_read=0|json=0" % (n, part_ok))
    ok = plan_eq and sample_ok and part_ok
    print("PLAN_CHECK_VERDICT|split=%d|cols=%d|%s|json=0" % (split, cols, "PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main(sys.argv[1:])
