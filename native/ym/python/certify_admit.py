#!/usr/bin/env python3
"""Input admission for the full-space certify step: every artifact of every sealed
stage B part is checked, all-or-nothing, before anything is aggregated.
Integer-only, json=0.

  manifest PART_WORKFLOW RUN HEAD PART ARTS_TSV
      Freeze one part's artifact manifest from API metadata only (no content read).
      ARTS_TSV lines: id, name, size_in_bytes, digest, expired, workflow_run.id,
      workflow_run.head_sha. Expected identities come from the part workflow's
      matrices: cell-NNN -> its cell shard, merge-mNN -> its merge shard,
      sealed-part-PART -> PART-PART.hbp/.sha256 plus the final shard of every count
      of that part (merged counts and unsplit counts). Exit 2 on any missing,
      duplicate, expired, extra or wrong-run entry.

  admit OUT CELLS MERGES FINALS MANIFEST ZIPDIR [MANIFEST ZIPDIR ...]
      Phase 1 (no extraction): each ZIPDIR holds exactly <artifact_id>.zip for its
      manifest; every size and raw SHA-256 matches. Phase 2a (no extraction): every
      ZIP passes testzip and has exactly its expected members; shard identities are
      unique across all parts; totals equal CELLS, MERGES and FINALS. Phase 2b:
      extraction into OUT (clean): cells to OUT/cells/<count id or _unsplit>/shards/,
      sealed parts to OUT/parts/; each spec file must name its shard; each
      PART-n.sha256 must verify and end in GITRAM_SEAL status=PASS; each merge
      artifact must equal, byte for byte, the sealed shard of the same id. Writes
      OUT/ADMIT-FILES.sha256 (every extracted file, path relative to OUT).

  check ADMIT_FILES PREFIX LOCALDIR [strip]
      A consumer's downloaded copy must hold exactly the admitted files under PREFIX
      (with the next path component dropped if `strip`), each with its admitted hash.
"""
import hashlib
import os
import re
import shutil
import sys
import zipfile

FILES = ("index.hbi", "run.anchor", "run.hbp", "run.measure", "spec")


def h(b):
    return hashlib.sha256(b).hexdigest()


def sid(spec):
    return spec.replace("/", "_")


def group_of(spec):
    kind, rest = spec.split("/", 1)
    if kind.endswith("countcols"):
        return sid(kind[: -len("cols")] + "/" + "/".join(rest.split("/")[:-2]))
    return "_unsplit"


def matrix(wf):
    cells, merges = {}, {}
    for line in open(wf):
        m = re.search(r'\{id: "([0-9]{3}|m[0-9]{2})", spec: "([^"]+)"\}', line)
        if m:
            i, spec = m.groups()
            d = merges if i.startswith("m") else cells
            if i in d:
                return None, None
            d[i] = spec
    return cells, merges


def die(tag, reason, detail="-"):
    print("%s|result=FAIL|reason=%s|detail=%s|json=0" % (tag, reason, detail))
    sys.exit(2)


def cmd_manifest(a):
    wf, run, head, part, tsv = a
    cells, merges = matrix(wf)
    if cells is None:
        die("CMANIFEST_TOTAL", "duplicate_matrix_id")
    finals = sorted([sid(s) for s in merges.values()] +
                    [sid(s) for s in cells.values() if not s.split("/", 1)[0].endswith("countcols")])
    exp = {"cell-" + i: ("cell", sid(s), group_of(s)) for i, s in cells.items()}
    exp.update({"merge-" + i: ("merge", sid(s), "-") for i, s in merges.items()})
    exp["sealed-part-" + part] = ("sealed", "PART-" + part, "-")
    problems, rows, seen_id, seen_name = [], [], set(), set()
    for line in open(tsv):
        if not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        if len(f) != 7:
            problems.append("malformed_line")
            continue
        aid, name, size, dig, expired, wrun, whead = f
        if aid in seen_id:
            problems.append("duplicate_id_" + aid)
        if name in seen_name:
            problems.append("duplicate_name_" + name)
        seen_id.add(aid)
        seen_name.add(name)
        if expired != "false":
            problems.append("expired_" + name)
        if wrun != run or whead != head:
            problems.append("wrong_run_" + name)
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", dig):
            problems.append("bad_digest_" + name)
        if name not in exp:
            problems.append("unexpected_" + name)
            continue
        kind, shard, grp = exp[name]
        rows.append((name, aid, int(size), dig[7:], kind, shard, grp))
    for name in exp:
        if name not in seen_name:
            problems.append("missing_" + name)
    for r in sorted(rows):
        print("CMANIFEST|part=%s|name=%s|artifact_id=%s|size=%d|sha256=%s|kind=%s|shard=%s|group=%s|json=0"
              % ((part,) + r))
    for s in finals:
        print("CMANIFEST_FINAL|part=%s|shard=%s|json=0" % (part, s))
    ok = not problems
    print("CMANIFEST_TOTAL|part=%s|run=%s|head=%s|artifacts=%d|cells=%d|merges=%d|finals=%d|problems=%d|first_problem=%s|result=%s|json=0"
          % (part, run, head, len(rows), len(cells), len(merges), len(finals), len(problems),
             problems[0] if problems else "none", "PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 2)


def read_manifest(path):
    rows, finals, total = [], [], None
    for line in open(path):
        p = line.rstrip("\n").split("|")
        f = dict(x.split("=", 1) for x in p[1:] if "=" in x)
        if p[0] == "CMANIFEST":
            rows.append(f)
        elif p[0] == "CMANIFEST_FINAL":
            finals.append(f["shard"])
        elif p[0] == "CMANIFEST_TOTAL":
            total = f
    if total is None or total.get("result") != "PASS" or int(total["artifacts"]) != len(rows):
        die("ADMIT_TOTAL", "manifest_not_pass", path)
    return total, rows, finals


def cmd_admit(a):
    out, ncell, nmerge, nfinal = a[0], int(a[1]), int(a[2]), int(a[3])
    pairs = [(a[i], a[i + 1]) for i in range(4, len(a), 2)]
    parts = []
    for man, zdir in pairs:
        total, rows, finals = read_manifest(man)
        parts.append((total["part"], rows, finals, zdir))
    # phase 1: exact file sets, sizes, digests
    n = 0
    for part, rows, finals, zdir in parts:
        want = {r["artifact_id"] + ".zip": r for r in rows}
        have = sorted(os.listdir(zdir))
        extra = [x for x in have if x not in want]
        missing = [x for x in want if x not in have]
        if extra:
            die("ADMIT_TOTAL", "unexpected_file", "part%s_%s" % (part, extra[0]))
        if missing:
            die("ADMIT_TOTAL", "missing_artifact", "part%s_%s" % (part, missing[0]))
        for fn, r in sorted(want.items()):
            b = open(os.path.join(zdir, fn), "rb").read()
            if len(b) != int(r["size"]):
                die("ADMIT_TOTAL", "size_mismatch", "part%s_%s" % (part, fn))
            if h(b) != r["sha256"]:
                die("ADMIT_TOTAL", "digest_mismatch", "part%s_%s" % (part, fn))
            n += 1
    print("ADMIT_PHASE1|artifacts=%d|size_and_digest=all_match|json=0" % n)
    # phase 2a: CRC, exact members, global uniqueness and totals
    zips, cell_ids, merge_ids, final_ids = [], [], [], []
    for part, rows, finals, zdir in parts:
        for r in rows:
            fn = os.path.join(zdir, r["artifact_id"] + ".zip")
            try:
                z = zipfile.ZipFile(fn)
                bad = z.testzip()
            except (zipfile.BadZipFile, OSError, EOFError):
                die("ADMIT_TOTAL", "corrupt_zip", "part%s_%s" % (part, r["name"]))
            if bad is not None:
                die("ADMIT_TOTAL", "corrupt_member", "part%s_%s" % (part, r["name"]))
            names = sorted(i.filename for i in z.infolist() if not i.is_dir())
            if r["kind"] == "sealed":
                exp = ["PART-%s.hbp" % part, "PART-%s.sha256" % part] + \
                      ["shards/%s/%s" % (s, f) for s in finals for f in FILES]
                final_ids += finals
            else:
                exp = ["shards/%s/%s" % (r["shard"], f) for f in FILES]
                (cell_ids if r["kind"] == "cell" else merge_ids).append(r["shard"])
            if names != sorted(exp):
                die("ADMIT_TOTAL", "contents_mismatch", "part%s_%s" % (part, r["name"]))
            zips.append((part, r, z, finals))
    for label, ids, want in (("cells", cell_ids, ncell), ("merges", merge_ids, nmerge), ("finals", final_ids, nfinal)):
        if len(set(ids)) != len(ids):
            die("ADMIT_TOTAL", "duplicate_shard_across_parts", label)
        if len(ids) != want:
            die("ADMIT_TOTAL", "total_%s_%d_expected_%d" % (label, len(ids), want))
    print("ADMIT_PHASE2A|artifacts=%d|zip_tested=all|members_exact=all|cells=%d|merges=%d|finals=%d|unique=1|json=0"
          % (len(zips), len(cell_ids), len(merge_ids), len(final_ids)))
    # phase 2b: extraction into a clean root
    if os.path.exists(out):
        die("ADMIT_TOTAL", "out_not_clean", out)
    tmp = os.path.join(out, ".x")
    os.makedirs(os.path.join(out, "parts", "shards"))
    merges_seen = {}
    for part, r, z, finals in zips:
        d = os.path.join(tmp, part, r["artifact_id"])
        os.makedirs(d)
        z.extractall(d)
        if r["kind"] == "sealed":
            hb = open(os.path.join(d, "PART-%s.hbp" % part), "rb").read()
            side = open(os.path.join(d, "PART-%s.sha256" % part)).read().split()
            last = hb.decode().splitlines()[-1]
            if side[:1] != [h(hb)] or not (last.startswith("GITRAM_SEAL|") and "|status=PASS|" in last):
                die("ADMIT_TOTAL", "part_seal_not_verified", "part" + part)
            for f in ("PART-%s.hbp" % part, "PART-%s.sha256" % part):
                shutil.copy2(os.path.join(d, f), os.path.join(out, "parts", f))
            for s in finals:
                if open(os.path.join(d, "shards", s, "spec")).read().strip().replace("/", "_") != s:
                    die("ADMIT_TOTAL", "spec_identity_mismatch", s)
                shutil.copytree(os.path.join(d, "shards", s), os.path.join(out, "parts", "shards", s))
        else:
            s = r["shard"]
            if open(os.path.join(d, "shards", s, "spec")).read().strip().replace("/", "_") != s:
                die("ADMIT_TOTAL", "spec_identity_mismatch", s)
            if r["kind"] == "cell":
                shutil.copytree(os.path.join(d, "shards", s), os.path.join(out, "cells", r["group"], "shards", s))
            else:
                merges_seen[s] = os.path.join(d, "shards", s)
    for s, src in sorted(merges_seen.items()):
        sealed = os.path.join(out, "parts", "shards", s)
        for f in FILES:
            if not os.path.exists(os.path.join(sealed, f)) or \
               open(os.path.join(src, f), "rb").read() != open(os.path.join(sealed, f), "rb").read():
                die("ADMIT_TOTAL", "merge_artifact_differs_from_sealed_shard", s)
    shutil.rmtree(tmp)
    lines = []
    for dp, dn, fn in os.walk(out):
        for f in fn:
            p = os.path.join(dp, f)
            lines.append("%s  %s" % (h(open(p, "rb").read()), os.path.relpath(p, out)))
    lines.sort(key=lambda l: l.split("  ", 1)[1])
    open(os.path.join(out, "ADMIT-FILES.sha256"), "w").write("\n".join(lines) + "\n")
    groups = sorted(os.listdir(os.path.join(out, "cells")))
    print("ADMIT_PHASE2B|files=%d|cell_groups=%d|merge_artifacts_equal_sealed=%d|seals_verified=%d|json=0"
          % (len(lines), len(groups), len(merges_seen), sum(1 for p in parts)))
    print("ADMIT_GROUPS|%s|json=0" % ",".join(groups))
    print("ADMIT_TOTAL|artifacts=%d|files_sha256=%s|result=PASS|json=0"
          % (len(zips), h(open(os.path.join(out, "ADMIT-FILES.sha256"), "rb").read())))


def cmd_check(a):
    admit, prefix, local = a[0], a[1], a[2]
    strip = len(a) > 3 and a[3] == "strip"
    exp = {}
    for line in open(admit):
        dig, p = line.rstrip("\n").split("  ", 1)
        if not p.startswith(prefix):
            continue
        q = p[len(prefix):]
        if strip:
            q = q.split("/", 1)[1]
        if q in exp:
            die("ADMIT_CHECK", "ambiguous_after_strip", q)
        exp[q] = dig
    have = {}
    for dp, dn, fn in os.walk(local):
        for f in fn:
            p = os.path.join(dp, f)
            have[os.path.relpath(p, local)] = h(open(p, "rb").read())
    if not exp:
        die("ADMIT_CHECK", "nothing_admitted_under_prefix", prefix)
    if set(have) != set(exp):
        extra = sorted(set(have) - set(exp))
        miss = sorted(set(exp) - set(have))
        die("ADMIT_CHECK", "file_set_differs", (extra or ["-"])[0] + "/" + (miss or ["-"])[0])
    bad = [k for k in exp if exp[k] != have[k]]
    if bad:
        die("ADMIT_CHECK", "hash_differs", bad[0])
    print("ADMIT_CHECK|prefix=%s|local=%s|files=%d|result=PASS|json=0" % (prefix, local, len(exp)))


if __name__ == "__main__":
    {"manifest": cmd_manifest, "admit": cmd_admit, "check": cmd_check}[sys.argv[1]](sys.argv[2:])
