# Row-by-row comparison of the prediction record at the first version 2 commit cfc57bef and in the working tree
# (correction round). Writes review-v2/ROW-COMPARE-CFC57BEF.hbp.
import hashlib, re, subprocess
C1 = "cfc57befadcb61fb36b992af841941adaecd3fd0"
V = "independent/y131-floor-cert-freeze-v2-20261110/"
NAME = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
REPO = "/root/floor-v2/repo/"
def old(rel):
    return subprocess.run(["git", "-C", REPO, "show", C1 + ":" + V + rel], stdout=subprocess.PIPE, check=True).stdout
a = old(NAME)
b = open(REPO + V + NAME, "rb").read()
def rows(x):
    d = {}; order = []
    for l in x.decode("utf-8").split("\n"):
        m = re.match(r"^([A-Z_]+)\|id=(\d{3})\|", l)
        if m: d[m.group(2)] = (m.group(1), l); order.append(m.group(2))
    return d, order
A, oa = rows(a); B, ob = rows(b)
h = lambda x: hashlib.sha256(x).hexdigest()
out = ["# Row-by-row comparison of the prediction record at commit %s (sha256 %s) and after the correction round (sha256 %s). Made by compare2.py from the two files. HBP, json=0." % (C1, h(a), h(b))]
same = 0; changed = []; npred = 0; psame = 0
for i in oa:
    ta, la = A[i]; tb, lb = B[i]
    assert ta == tb
    sb = 1 if la == lb else 0
    same += sb
    row = "ROWCMP|id=%s|type=%s|same_bytes=%d|sha16_cfc57bef=%s|sha16_now=%s" % (i, ta, sb, h(la.encode())[:16], h(lb.encode())[:16])
    if not sb:
        fa = [tuple(f.split("=", 1)) for f in la.split("|")[1:]]; fb = [tuple(f.split("=", 1)) for f in lb.split("|")[1:]]
        da, db = dict(fa), dict(fb)
        ch = [k for k, v in fa if k in db and db[k] != v] + ["+" + k for k, v in fb if k not in da] + ["-" + k for k, v in fa if k not in db]
        row += "|changed_fields=" + ",".join(ch)
        changed.append(i)
    if ta == "PREDICT":
        npred += 1; psame += sb
    out.append(row + "|json=0")
new = [i for i in ob if i not in A]
for i in new:
    out.append("ROWNEW|id=%s|type=%s|sha16_now=%s|json=0" % (i, B[i][0], h(B[i][1].encode())[:16]))
ha = [l for l in a.decode().split("\n") if l.startswith("#")]; hb = [l for l in b.decode().split("\n") if l.startswith("#")]
fixed = {}
for rel in ("work/design/rs/src/main.rs", "work/design/rs/Cargo.toml", "work/design/rs/Cargo.lock", "work/design/gate_required.sh", "work/design/py/cert_gate.py", "work/design/py/indep_verify.py", "work/design/peak_rss.py", "final/tools/lint_hbp.py"):
    fixed[rel] = 1 if h(old(rel)) == h(open(REPO + V + rel, "rb").read()) else 0
assert all(fixed.values()), fixed
assert npred == 16 and psame == 16, (npred, psame)
out.append("FILECMP|same_bytes_as_cfc57bef=" + ",".join(sorted(fixed)) + "|json=0")
out.append("ROWCMP_END|cfc57bef_rows=%d|same_bytes=%d|changed=%d|changed_ids=%s|new_rows=%d|new_ids=%s|predict_rows=%d|predict_same_bytes=%d|header_lines_cfc57bef=%d|header_lines_now=%d|header_lines_same=%d|json=0"
           % (len(oa), same, len(changed), "_".join(changed), len(new), "_".join(new), npred, psame, len(ha), len(hb), sum(1 for l in ha if l in hb)))
open(REPO + V + "review-v2/ROW-COMPARE-CFC57BEF.hbp", "w", newline="\n").write("\n".join(out) + "\n")
print(out[-1])
