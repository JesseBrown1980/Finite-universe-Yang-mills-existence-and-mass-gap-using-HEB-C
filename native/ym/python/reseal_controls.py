#!/usr/bin/env python3
"""Fail-closed controls for the seal-only re-run, on disposable copies.

Uses two real artifacts (one cell, one merge) already downloaded into PREDIR as
<artifact_id>.zip, a mini manifest built from the frozen manifest's lines for
them, and synthetic mutations. Every mutation must stop reseal_verify.py with a
non-zero exit and the named reason, before phase 2b (no shard is assembled);
the unmutated baseline must pass. reseal_manifest.py is checked the same way
on mutated metadata. Integer-only, json=0.
usage: reseal_controls.py FROZEN_MANIFEST PREDIR ID_CELL ID_MERGE WORKFLOW
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "reseal_verify.py")
MANIFEST = os.path.join(HERE, "reseal_manifest.py")


def run_verify(man_lines, zips, tag):
    d = tempfile.mkdtemp(prefix="rc_")
    zd = os.path.join(d, "zips")
    os.makedirs(zd)
    for name, data in zips.items():
        open(os.path.join(zd, name), "wb").write(data)
    open(os.path.join(d, "m.hbp"), "w").write("".join(man_lines))
    out = os.path.join(d, "out")
    r = subprocess.run([sys.executable, VERIFY, os.path.join(d, "m.hbp"), zd, out, "1", "1"],
                       capture_output=True, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    assembled = os.path.isdir(os.path.join(out, "shards")) and len(os.listdir(os.path.join(out, "shards")))
    shutil.rmtree(d)
    return r.returncode, last, assembled


def main():
    frozen, predir, idc, idm, wf = sys.argv[1:6]
    lines = [l for l in open(frozen) if l.startswith("MANIFEST|") and
             ("artifact_id=%s|" % idc in l or "artifact_id=%s|" % idm in l)]
    assert len(lines) == 2
    total = "MANIFEST_TOTAL|run=mini|head=mini|artifacts=2|cells=1|merges=1|problems=0|first_problem=none|result=PASS|json=0\n"
    base = {idc + ".zip": open(os.path.join(predir, idc + ".zip"), "rb").read(),
            idm + ".zip": open(os.path.join(predir, idm + ".zip"), "rb").read()}
    results = []

    def case(name, man, zips, expect):
        rc, last, assembled = run_verify(man, zips, name)
        if expect == "PASS":
            ok = rc == 0 and "result=PASS" in last and assembled == 2
        else:
            ok = rc != 0 and ("reason=%s" % expect) in last and not assembled
        results.append(ok)
        print("RESEAL_CONTROL|case=%s|expect=%s|rc=%d|assembled=%d|got=%s|ok=%d|json=0"
              % (name, expect, rc, int(assembled or 0), last.split("|")[2] if last.count("|") > 2 else last, ok))

    case("baseline", lines + [total], base, "PASS")
    flipped = dict(base)
    b = bytearray(flipped[idc + ".zip"]); b[len(b) // 2] ^= 1; flipped[idc + ".zip"] = bytes(b)
    case("wrong_digest", lines + [total], flipped, "digest_mismatch")
    short = dict(base); short[idm + ".zip"] = base[idm + ".zip"][:-1]
    case("wrong_size", lines + [total], short, "size_mismatch")
    miss = dict(base); del miss[idm + ".zip"]
    case("missing_artifact", lines + [total], miss, "missing_artifact")
    extra = dict(base); extra["99999999999.zip"] = base[idc + ".zip"]
    case("unexpected_artifact", lines + [total], extra, "unexpected_file")
    case("duplicate_id", lines + [lines[0], total], base, "manifest_duplicate")
    # corrupted ZIP whose manifest size and digest are made to match: must be caught in phase 2a
    import hashlib
    bad = bytearray(base[idc + ".zip"])
    for i in range(30, 60):
        bad[i] ^= 0xFF
    bad = bytes(bad)
    ml = [l.replace("size=%d|" % len(base[idc + ".zip"]), "size=%d|" % len(bad))
           .replace(hashlib.sha256(base[idc + ".zip"]).hexdigest(), hashlib.sha256(bad).hexdigest())
          if "artifact_id=%s|" % idc in l else l for l in lines]
    cz = dict(base); cz[idc + ".zip"] = bad
    case("corrupted_zip", ml + [total], cz, "corrupt_")  # corrupt_zip or corrupt_member (CRC)
    case("manifest_not_pass", lines + [total.replace("result=PASS", "result=FAIL")], base, "manifest_not_pass")

    # manifest builder on mutated metadata
    rows = []
    for l in lines:
        f = dict(x.split("=", 1) for x in l.strip().split("|")[1:] if "=" in x)
        rows.append([f["artifact_id"], f["name"], f["size"], "sha256:" + f["sha256"], "false", "40353983355",
                     "50d6539575b078c23a6402069d27c82ddd523f7a"])

    def mcase(name, rs, expect):
        d = tempfile.mkdtemp(prefix="rm_")
        t = os.path.join(d, "a.tsv")
        open(t, "w").write("".join("\t".join(r) + "\n" for r in rs))
        r = subprocess.run([sys.executable, MANIFEST, t, wf, "40353983355",
                            "50d6539575b078c23a6402069d27c82ddd523f7a", "128", "4"], capture_output=True, text=True)
        last = r.stdout.strip().splitlines()[-1]
        ok = r.returncode != 0 and expect in last
        results.append(ok)
        print("RESEAL_MANIFEST_CONTROL|case=%s|rc=%d|first_problem=%s|ok=%d|json=0"
              % (name, r.returncode, [x for x in last.split("|") if x.startswith("first_problem=")][0][14:], ok))
        shutil.rmtree(d)

    # the two real rows alone are an incomplete grid: 130 missing
    mcase("incomplete_grid", rows, "first_problem=missing_")
    mcase("expired", [rows[0][:4] + ["true"] + rows[0][5:], rows[1]], "expired_")
    mcase("wrong_run", [rows[0][:5] + ["1"] + rows[0][6:], rows[1]], "wrong_run_")
    mcase("duplicate_id", [rows[0], rows[0], rows[1]], "duplicate_id_")
    mcase("extra_name", rows + [["1", "cell-999", "1", "sha256:" + "0" * 64, "false", "40353983355",
                                  "50d6539575b078c23a6402069d27c82ddd523f7a"]], "unexpected_cell-999")
    n_ok = sum(1 for x in results if x)
    print("RESEAL_CONTROLS_TOTAL|cases=%d|ok=%d|result=%s|json=0" % (len(results), n_ok,
                                                                       "PASS" if n_ok == len(results) else "FAIL"))
    sys.exit(0 if n_ok == len(results) else 2)


if __name__ == "__main__":
    main()
