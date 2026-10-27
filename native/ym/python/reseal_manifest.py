#!/usr/bin/env python3
"""Freeze the artifact manifest for a seal-only re-run of a stage B run, from
metadata only (no artifact content is downloaded or read).

Inputs
  ARTS_TSV   one line per artifact from the GitHub API, tab-separated:
             id, name, size_in_bytes, digest ("sha256:<hex>"), expired,
             workflow_run.id, workflow_run.head_sha
  WORKFLOW   the original stage B workflow file (its cell and merge matrices
             give the expected shard identity of every artifact)
  RUN HEAD   the source run id and its head commit
  CELLS MERGES  the exact expected numbers of cell and merge artifacts

Output (stdout): one MANIFEST line per artifact, sorted by name, then a
MANIFEST_TOTAL line. Exit 2 (and no MANIFEST_TOTAL|result=PASS) on any
missing, duplicate, expired, extra or wrong-run entry.
usage: reseal_manifest.py ARTS_TSV WORKFLOW RUN HEAD CELLS MERGES   json=0
"""
import re
import sys


def matrix(workflow):
    """name -> expected shard directory, from the original matrices."""
    exp = {}
    for line in open(workflow):
        m = re.search(r'\{id: "([0-9]{3}|m[0-9]{2})", spec: "([^"]+)"\}', line)
        if m:
            i, spec = m.groups()
            name = ("merge-" if i.startswith("m") else "cell-") + i
            if name in exp:
                return None
            exp[name] = spec.replace("/", "_")
    return exp


def main():
    tsv, wf, run, head, ncell, nmerge = sys.argv[1:7]
    ncell, nmerge = int(ncell), int(nmerge)
    exp = matrix(wf)
    problems = []
    if exp is None:
        print("MANIFEST_TOTAL|result=FAIL|reason=duplicate_matrix_id|json=0")
        sys.exit(2)
    rows, seen_id, seen_name = [], set(), set()
    for line in open(tsv):
        if not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        if len(f) != 7:
            problems.append("malformed_line")
            continue
        aid, name, size, digest, expired, wrun, whead = f
        if aid in seen_id:
            problems.append("duplicate_id_%s" % aid)
        if name in seen_name:
            problems.append("duplicate_name_%s" % name)
        seen_id.add(aid)
        seen_name.add(name)
        if expired != "false":
            problems.append("expired_%s" % name)
        if wrun != run or whead != head:
            problems.append("wrong_run_%s" % name)
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            problems.append("bad_digest_%s" % name)
        if name not in exp:
            problems.append("unexpected_%s" % name)
        rows.append((name, aid, int(size), digest[7:], exp.get(name, "-")))
    for name in exp:
        if name not in seen_name:
            problems.append("missing_%s" % name)
    nc = sum(1 for r in rows if r[0].startswith("cell-"))
    nm = sum(1 for r in rows if r[0].startswith("merge-"))
    if (nc, nm, len(exp)) != (ncell, nmerge, ncell + nmerge):
        problems.append("counts_cells=%d_merges=%d_matrix=%d" % (nc, nm, len(exp)))
    for name, aid, size, hexd, shard in sorted(rows):
        print("MANIFEST|name=%s|artifact_id=%s|size=%d|sha256=%s|shard=%s|json=0" % (name, aid, size, hexd, shard))
    ok = not problems
    print("MANIFEST_TOTAL|run=%s|head=%s|artifacts=%d|cells=%d|merges=%d|problems=%d|first_problem=%s|result=%s|json=0"
          % (run, head, len(rows), nc, nm, len(problems), problems[0] if problems else "none", "PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
