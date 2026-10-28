#!/usr/bin/env python3
"""All-or-nothing verification of downloaded stage B artifacts against a frozen
manifest (reseal_manifest.py), before any count is aggregated.

Phase 1 (no extraction): ZIPDIR must hold exactly one file <artifact_id>.zip for
every manifest entry and nothing else; each file's byte size and raw SHA-256
must equal the manifest. Any failure stops here.

Phase 2a (only if phase 1 passed for all): every ZIP is tested and its member
list checked, still without extracting anything. Phase 2b: each ZIP is extracted
into its own OUT/by-id/<artifact_id>/ directory. It must contain exactly the five
files shards/<shard>/{index.hbi,run.anchor,run.hbp,run.measure,spec} for the
manifest's shard identity, with no absolute or parent paths. The shard
directories are then assembled into OUT/shards/ (a collision is a failure).

Exit 0 only if every artifact passes both phases. Integer-only, json=0.
usage: reseal_verify.py MANIFEST ZIPDIR OUT CELLS MERGES
"""
import hashlib
import os
import shutil
import sys
import zipfile

FILES = ("index.hbi", "run.anchor", "run.hbp", "run.measure", "spec")


def fail(reason, detail="-"):
    print("RESEAL_VERIFY_TOTAL|result=FAIL|reason=%s|detail=%s|json=0" % (reason, detail))
    sys.exit(2)


def read_manifest(path, ncell, nmerge):
    rows, total = [], None
    for line in open(path):
        p = line.rstrip("\n").split("|")
        f = dict(x.split("=", 1) for x in p[1:] if "=" in x)
        if p[0] == "MANIFEST":
            rows.append(f)
        elif p[0] == "MANIFEST_TOTAL":
            total = f
    if total is None or total.get("result") != "PASS":
        fail("manifest_not_pass")
    ids = [r["artifact_id"] for r in rows]
    names = [r["name"] for r in rows]
    shards = [r["shard"] for r in rows]
    if len(set(ids)) != len(ids) or len(set(names)) != len(names) or len(set(shards)) != len(shards):
        fail("manifest_duplicate")
    nc = sum(1 for n in names if n.startswith("cell-"))
    nm = sum(1 for n in names if n.startswith("merge-"))
    if (nc, nm, len(rows)) != (ncell, nmerge, ncell + nmerge) or int(total["artifacts"]) != len(rows):
        fail("manifest_counts", "cells=%d_merges=%d" % (nc, nm))
    return rows


def main():
    man, zdir, out, ncell, nmerge = sys.argv[1:6]
    rows = read_manifest(man, int(ncell), int(nmerge))
    want = {r["artifact_id"] + ".zip": r for r in rows}
    have = sorted(os.listdir(zdir))
    extra = [h for h in have if h not in want]
    missing = [w for w in want if w not in have]
    if extra:
        fail("unexpected_file", extra[0])
    if missing:
        fail("missing_artifact", missing[0])
    # phase 1: size and digest of every raw ZIP, before any extraction
    for fn in sorted(want):
        r = want[fn]
        b = open(os.path.join(zdir, fn), "rb").read()
        if len(b) != int(r["size"]):
            fail("size_mismatch", fn)
        if hashlib.sha256(b).hexdigest() != r["sha256"]:
            fail("digest_mismatch", fn)
    print("RESEAL_VERIFY_PHASE1|artifacts=%d|size_and_digest=all_match|json=0" % len(want))
    # phase 2a: every ZIP tested and its member list checked, still without extracting
    zips = {}
    for fn in sorted(want):
        r = want[fn]
        try:
            z = zipfile.ZipFile(os.path.join(zdir, fn))
            bad = z.testzip()
        except (zipfile.BadZipFile, OSError, EOFError):
            fail("corrupt_zip", fn)
        if bad is not None:
            fail("corrupt_member", fn)
        names = sorted(i.filename for i in z.infolist() if not i.is_dir())
        exp = sorted("shards/%s/%s" % (r["shard"], f) for f in FILES)
        if names != exp:
            fail("contents_mismatch", fn)
        zips[fn] = z
    print("RESEAL_VERIFY_PHASE2A|artifacts=%d|zip_tested=all|members_exact=all|json=0" % len(zips))
    # phase 2b: extraction into a clean root, one directory per artifact id
    if os.path.exists(out):
        fail("out_not_clean", out)
    os.makedirs(os.path.join(out, "by-id"))
    os.makedirs(os.path.join(out, "shards"))
    for fn in sorted(want):
        r = want[fn]
        aid, shard = r["artifact_id"], r["shard"]
        dest = os.path.join(out, "by-id", aid)
        os.makedirs(dest)
        zips[fn].extractall(dest)
        src = os.path.join(dest, "shards", shard)
        tgt = os.path.join(out, "shards", shard)
        if os.path.exists(tgt):
            fail("shard_collision", shard)
        shutil.copytree(src, tgt)
        spec = open(os.path.join(src, "spec")).read().strip()
        if spec.replace("/", "_") != shard:
            fail("spec_identity_mismatch", fn)
    print("RESEAL_VERIFY_PHASE2|artifacts=%d|extracted_exact=all|shards_assembled=%d|json=0"
          % (len(want), len(os.listdir(os.path.join(out, "shards")))))
    print("RESEAL_VERIFY_TOTAL|artifacts=%d|result=PASS|json=0" % len(want))


if __name__ == "__main__":
    main()
