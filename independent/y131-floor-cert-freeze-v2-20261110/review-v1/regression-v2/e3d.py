# E3 provenance table: one row per absent path. Reads e3_missing.txt, e3_git_hits.txt, e3_fs_hits.txt, e3_fs_log.txt.
import hashlib, os
W = "/root/floor-v2/"
missing = [l.rstrip("\n").split("\t") for l in open(W + "e3_missing.txt")]
git = {}
for l in open(W + "e3_git_hits.txt"):
    k, blob, path, full = l.rstrip("\n").split("\t"); git[k] = (path, full)
fs = {}
for l in open(W + "e3_fs_hits.txt"):
    full, path = l.rstrip("\n").split("\t", 1); fs.setdefault(full[:16], (path, full))
# files produced by the v2 regression of this seat
reg = {}
for dp, dn, fn in os.walk(W + "reg"):
    for f in fn:
        p = os.path.join(dp, f)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        reg.setdefault(h[:16], (os.path.relpath(p, W), h))
log = open(W + "e3_fs_log.txt").read().split("\n")
out = []
out.append("# E3 provenance of the files= entries of the v1 record (e74d8a46) that are absent from the v1 commit. 2026-11-10, local build seat. HBP, json=0.")
out.append("# provenance=verified: the same bytes (full sha256 starting with the row's fingerprint) are in the repository history, at the path named in where=.")
out.append("# provenance=not_established: no file with that fingerprint was found in the places searched; content_reproduced=1 marks a fingerprint that a 2026-11-10 rerun on this machine reproduced (a rerun output, so the bytes are confirmed and the history of the original file stays open).")
out.append("# No absent file was recreated or back-filled; this table names them.")
nv = nr = nn = 0
for path, h16, rows in missing:
    r = rows.replace(",", "_")
    if h16 in git:
        nv += 1
        out.append("E3|path=%s|sha16=%s|rows=%s|provenance=verified|where=e74d8a46:%s|sha256=%s|json=0" % (path, h16, r, git[h16][0], git[h16][1]))
    elif h16 in reg or h16 in fs:
        nr += 1
        src = ("v2_regression:" + reg[h16][0], reg[h16][1]) if h16 in reg else ("this_machine:" + fs[h16][0], fs[h16][1])
        out.append("E3|path=%s|sha16=%s|rows=%s|provenance=not_established|content_reproduced=1|rerun_file=%s|sha256=%s|json=0" % (path, h16, r, src[0].replace(" ", "_"), src[1]))
    else:
        nn += 1
        out.append("E3|path=%s|sha16=%s|rows=%s|provenance=not_established|content_reproduced=0|json=0" % (path, h16, r))
for d in ("critic2", "verify1_0", "verify1_1", "refix2", "verify2_0", "verify2_1"):
    out.append("E3_FOLDER|path=work/%s|provenance=not_established|found_on_this_machine=0|json=0" % d)
out.append("E3_SEARCH|git=every_blob_reachable_from_170_local_mirror_refs_168_GitHub_branch_heads_and_152_GitHub_pull_heads_(fetched_read-only_2026-11-10)_whose_basename_equals_an_absent_basename_or_whose_path_holds_floor_or_a_seat_folder_name:_122_blobs_hashed|json=0")
for l in log:
    if l.startswith("root=") or l.startswith("hashed="):
        out.append("E3_SEARCH|filesystem=%s|json=0" % l.replace(" ", "_"))
    if l.startswith("SEATDIR"):
        out.append("E3_SEARCH|dir_with_a_seat_folder_name=%s|json=0" % l[8:].replace(" ", "_"))
out.append("E3_END|absent_paths=%d|absent_entries=286|verified=%d|not_established=%d|of_which_content_reproduced=%d|seat_folders_absent=6|json=0" % (len(missing), nv, nr + nn, nr))
open(W + "E3-PROVENANCE.hbp", "w", newline="").write("\n".join(out) + "\n")
print(out[-1])
print("\n".join(o for o in out if o.startswith("E3_SEARCH")))
import collections
print(collections.Counter(o.split("|rerun_file=")[1].split("/")[0] for o in out if "rerun_file=" in o))
