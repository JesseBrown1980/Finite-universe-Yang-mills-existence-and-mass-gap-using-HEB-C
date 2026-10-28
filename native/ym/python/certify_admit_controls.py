#!/usr/bin/env python3
"""Fail-closed controls for certify_admit.py on synthetic artifacts (no real data is
read). A miniature part with two column cells, one unsplit count, one merge and a
sealed part is built as ZIPs; each mutation must stop admission with its named reason
before anything is extracted for use, and each consumer-copy mutation must fail the
check. The unmutated baseline must pass. Integer-only, json=0.
usage: certify_admit_controls.py
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "certify_admit.py")
FILES = ("index.hbi", "run.anchor", "run.hbp", "run.measure", "spec")
RUN, HEAD = "111", "a" * 40
C1 = "countcols/3/3/1/1/1000/9000/71900000/12/1000/0/100"
C2 = "countcols/3/3/1/1/1000/9000/71900000/12/1000/100/150"
C3 = "count/3/3/-1/-1/1000/9000/52533422/12/1000"
M1 = "countmerge/3/3/1/1/1000/9000/71900000/12/1000"
WF = '''      matrix:
        include:
          - {id: "001", spec: "%s"}
          - {id: "002", spec: "%s"}
          - {id: "003", spec: "%s"}
      matrix:
        include:
          - {id: "m01", spec: "%s"}
''' % (C1, C2, C3, M1)


def shard_files(spec, salt=""):
    i = spec.replace("/", "_")
    return {"shards/%s/%s" % (i, f): ("%s|%s|%s\n" % (f, i, salt)).encode() if f != "spec" else (spec + "\n").encode()
            for f in FILES}


def mkzip(members, corrupt=False):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in sorted(members.items()):
            z.writestr(k, v)
    data = bytearray(b.getvalue())
    if corrupt:
        data[40] ^= 0xFF
    return bytes(data)


def artifacts(mut=""):
    a = {"cell-001": shard_files(C1), "cell-002": shard_files(C2), "cell-003": shard_files(C3),
         "merge-m01": shard_files(M1)}
    part = b"SHARD|x|json=0\nGITRAM_SEAL|name=t|part=1/1|status=%s|json=0\n" % (b"FAIL" if mut == "seal_not_pass" else b"PASS")
    sealed = {"PART-1.hbp": part,
              "PART-1.sha256": ("%s  PART-1.hbp\n" % hashlib.sha256(part if mut != "seal_sha" else b"x").hexdigest()).encode()}
    sealed.update(shard_files(M1))
    sealed.update(shard_files(C3))
    a["sealed-part-1"] = sealed
    if mut == "member_missing":
        del a["cell-001"]["shards/%s/run.measure" % C1.replace("/", "_")]
    if mut == "spec_identity":
        a["cell-002"]["shards/%s/spec" % C2.replace("/", "_")] = (C1 + "\n").encode()
    if mut == "merge_differs":
        a["merge-m01"]["shards/%s/run.hbp" % M1.replace("/", "_")] = b"other\n"
    return a


def build(d, mut="", tsv_mut=""):
    os.makedirs(os.path.join(d, "zips"))
    rows = []
    for k, (name, members) in enumerate(sorted(artifacts(mut).items())):
        data = mkzip(members, corrupt=(mut == "corrupt_zip" and name == "cell-001"))
        aid = str(1000 + k)
        open(os.path.join(d, "zips", aid + ".zip"), "wb").write(data)
        rows.append([aid, name, str(len(data)), "sha256:" + hashlib.sha256(data).hexdigest(), "false", RUN, HEAD])
    if tsv_mut == "expired":
        rows[0][4] = "true"
    if tsv_mut == "wrong_run":
        rows[0][5] = "999"
    if tsv_mut == "duplicate_id":
        rows.append(list(rows[0]))
    if tsv_mut == "unexpected_name":
        rows.append(["5000", "cell-999", "1", "sha256:" + "0" * 64, "false", RUN, HEAD])
    if tsv_mut == "missing_name":
        rows = rows[1:]
    open(os.path.join(d, "wf.yml"), "w").write(WF)
    open(os.path.join(d, "a.tsv"), "w").write("".join("\t".join(r) + "\n" for r in rows))
    r = subprocess.run([sys.executable, TOOL, "manifest", os.path.join(d, "wf.yml"), RUN, HEAD, "1",
                        os.path.join(d, "a.tsv")], capture_output=True, text=True)
    open(os.path.join(d, "m.hbp"), "w").write(r.stdout)
    return r


def admit(d, extra_args=("3", "1", "2")):
    return subprocess.run([sys.executable, TOOL, "admit", os.path.join(d, "out"), *extra_args,
                           os.path.join(d, "m.hbp"), os.path.join(d, "zips")], capture_output=True, text=True)


def last(r):
    s = r.stdout.strip().splitlines()
    return s[-1] if s else ""


def main():
    results = []

    def record(tag, name, ok, got):
        results.append(ok)
        print("%s|case=%s|ok=%d|got=%s|json=0" % (tag, name, ok, got))

    def acase(name, expect, mut="", zipmut=None, args=("3", "1", "2")):
        d = tempfile.mkdtemp(prefix="ca_")
        build(d, mut)
        if zipmut:
            zipmut(d)
        r = admit(d, args)
        used = os.path.isdir(os.path.join(d, "out", "cells")) and not os.path.exists(os.path.join(d, "out", "ADMIT-FILES.sha256"))
        if expect == "PASS":
            ok = r.returncode == 0 and "result=PASS" in last(r)
        else:
            ok = r.returncode != 0 and ("reason=" + expect) in last(r) and not os.path.exists(os.path.join(d, "out", "ADMIT-FILES.sha256"))
        record("CERTIFY_ADMIT_CONTROL", name, ok, last(r).split("|")[2] if last(r).count("|") > 2 else last(r))
        shutil.rmtree(d)
        return used

    def flip(d):
        p = os.path.join(d, "zips", sorted(os.listdir(os.path.join(d, "zips")))[0])
        b = bytearray(open(p, "rb").read()); b[len(b) // 2] ^= 1; open(p, "wb").write(b)

    def shorten(d):
        p = os.path.join(d, "zips", sorted(os.listdir(os.path.join(d, "zips")))[0])
        open(p, "wb").write(open(p, "rb").read()[:-1])

    acase("baseline", "PASS")
    acase("wrong_digest", "digest_mismatch", zipmut=flip)
    acase("wrong_size", "size_mismatch", zipmut=shorten)
    acase("missing_artifact", "missing_artifact", zipmut=lambda d: os.remove(os.path.join(d, "zips", sorted(os.listdir(os.path.join(d, "zips")))[0])))
    acase("unexpected_artifact", "unexpected_file", zipmut=lambda d: open(os.path.join(d, "zips", "77.zip"), "wb").write(b"x"))
    acase("corrupted_zip", "corrupt_", mut="corrupt_zip")
    acase("member_missing", "contents_mismatch", mut="member_missing")
    acase("spec_identity", "spec_identity_mismatch", mut="spec_identity")
    acase("part_sha_mismatch", "part_seal_not_verified", mut="seal_sha")
    acase("part_not_pass", "part_seal_not_verified", mut="seal_not_pass")
    acase("merge_differs_from_sealed", "merge_artifact_differs_from_sealed_shard", mut="merge_differs")
    acase("wrong_totals", "total_cells_3_expected_4", args=("4", "1", "2"))

    # duplicate shard across two parts: the same part admitted twice
    d = tempfile.mkdtemp(prefix="ca_")
    build(d)
    r = subprocess.run([sys.executable, TOOL, "admit", os.path.join(d, "out"), "6", "2", "4",
                        os.path.join(d, "m.hbp"), os.path.join(d, "zips"), os.path.join(d, "m.hbp"), os.path.join(d, "zips")],
                       capture_output=True, text=True)
    record("CERTIFY_ADMIT_CONTROL", "duplicate_across_parts", r.returncode != 0 and "duplicate_shard_across_parts" in last(r), last(r).split("|")[2])
    shutil.rmtree(d)

    for name in ("expired", "wrong_run", "duplicate_id", "unexpected_name", "missing_name"):
        d = tempfile.mkdtemp(prefix="cm_")
        r = build(d, tsv_mut=name)
        fp = [x for x in last(r).split("|") if x.startswith("first_problem=")]
        record("CERTIFY_MANIFEST_CONTROL", name, r.returncode != 0 and bool(fp) and fp[0] != "first_problem=none", fp[0] if fp else last(r))
        shutil.rmtree(d)

    # consumer checks on the admitted copy
    d = tempfile.mkdtemp(prefix="cc_")
    build(d)
    admit(d)
    out = os.path.join(d, "out")
    adm = os.path.join(out, "ADMIT-FILES.sha256")
    grp = "count_3_3_1_1_1000_9000_71900000_12_1000"

    def check(prefix, local, strip=False):
        a = [sys.executable, TOOL, "check", adm, prefix, local] + (["strip"] if strip else [])
        return subprocess.run(a, capture_output=True, text=True)

    def copy(src):
        t = tempfile.mkdtemp(prefix="cl_")
        shutil.rmtree(t)
        shutil.copytree(src, t)
        return t

    t = copy(os.path.join(out, "cells", grp))
    r = check("cells/%s/" % grp, t)
    record("CERTIFY_CHECK_CONTROL", "baseline_group", r.returncode == 0, last(r).split("|")[-2])
    f = os.path.join(t, "shards", C1.replace("/", "_"), "run.hbp")
    open(f, "ab").write(b"x")
    r = check("cells/%s/" % grp, t)
    record("CERTIFY_CHECK_CONTROL", "tampered_file", r.returncode != 0 and "hash_differs" in last(r), last(r).split("|")[2])
    t = copy(os.path.join(out, "cells", grp))
    open(os.path.join(t, "shards", "extra"), "w").write("x")
    r = check("cells/%s/" % grp, t)
    record("CERTIFY_CHECK_CONTROL", "extra_file", r.returncode != 0 and "file_set_differs" in last(r), last(r).split("|")[2])
    t = copy(os.path.join(out, "cells", grp))
    os.remove(os.path.join(t, "shards", C2.replace("/", "_"), "spec"))
    r = check("cells/%s/" % grp, t)
    record("CERTIFY_CHECK_CONTROL", "missing_file", r.returncode != 0 and "file_set_differs" in last(r), last(r).split("|")[2])
    # all groups merged into one directory, as the assemble job downloads them
    t = tempfile.mkdtemp(prefix="cl_")
    for g in os.listdir(os.path.join(out, "cells")):
        shutil.copytree(os.path.join(out, "cells", g), t, dirs_exist_ok=True)
    r = check("cells/", t, strip=True)
    record("CERTIFY_CHECK_CONTROL", "baseline_all_cells_strip", r.returncode == 0, last(r).split("|")[-2])
    t = copy(os.path.join(out, "parts"))
    r = check("parts/", t)
    record("CERTIFY_CHECK_CONTROL", "baseline_parts", r.returncode == 0, last(r).split("|")[-2])
    shutil.rmtree(d)

    n = sum(1 for x in results if x)
    print("CERTIFY_ADMIT_CONTROLS_TOTAL|cases=%d|ok=%d|result=%s|json=0" % (len(results), n, "PASS" if n == len(results) else "FAIL"))
    sys.exit(0 if n == len(results) else 2)


if __name__ == "__main__":
    main()
