# Row-by-row comparison of the v1 and v2 prediction records. Writes review-v1/ROW-COMPARE-V1-V2.hbp.
import hashlib, re, sys
R = "/root/floor-v2/repo/independent/"
NAME = "final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp"
a = open(R + "y131-floor-cert-freeze-20261110/" + NAME, "rb").read()
b = open(R + "y131-floor-cert-freeze-v2-20261110/" + NAME, "rb").read()
def rows(x):
    d = {}; order = []
    for l in x.decode("utf-8").split("\n"):
        m = re.match(r"^[A-Z_]+\|id=(\d{3})\|", l)
        if m: d[m.group(1)] = l; order.append(m.group(1))
    return d, order
def fields(l):
    p = l.split("|"); return p[0], [tuple(f.split("=", 1)) for f in p[1:]]
A, oa = rows(a); B, ob = rows(b)
out = ["# Row-by-row comparison of the prediction record of version 1 (commit e74d8a46, sha256 %s) and version 2 (sha256 %s). Made by compare.py from the two files. HBP, json=0." % (hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())]
same = 0; changed = []; pred_same = 0; pred_core_same = 0; npred = 0
for i in oa:
    ta, fa = fields(A[i]); tb, fb = fields(B[i]); da = dict(fa); db = dict(fb)
    sb = 1 if A[i] == B[i] else 0
    same += sb
    ch = [k for k, v in fb if k not in da] ; add = ["+" + k for k in ch]
    mod = [k for k, v in fa if k in db and db[k] != v]; rem = ["-" + k for k, v in fa if k not in db]
    core = all(da.get(k) == db.get(k) for k in ("value", "met_if", "not_met_if", "falsifier"))
    row = "ROWCMP|id=%s|type=%s|tag=%s|same_bytes=%d|sha16_v1=%s|sha16_v2=%s" % (i, ta, da["tag"], sb, hashlib.sha256(A[i].encode()).hexdigest()[:16], hashlib.sha256(B[i].encode()).hexdigest()[:16])
    if not sb:
        row += "|changed_fields=%s|value_met_if_not_met_if_falsifier_same=%d" % (",".join(mod + add + rem) or "NONE", 1 if core else 0)
        changed.append((i, ta, mod + add + rem, core))
    if ta == "PREDICT":
        npred += 1; pred_same += sb; pred_core_same += 1 if core else 0
    assert ta == tb
    out.append(row + "|json=0")
new = [i for i in ob if i not in A]
for i in new:
    tb, fb = fields(B[i])
    out.append("ROWNEW|id=%s|type=%s|tag=%s|sha16_v2=%s|json=0" % (i, tb, dict(fb)["tag"], hashlib.sha256(B[i].encode()).hexdigest()[:16]))
out.append("ROWCMP_END|v1_rows=%d|same_bytes=%d|changed=%d|changed_ids=%s|new_rows=%d|new_ids=%s|predict_rows=%d|predict_same_bytes=%d|predict_value_met_if_not_met_if_falsifier_same=%d|json=0" % (len(oa), same, len(changed), "_".join(c[0] for c in changed), len(new), "_".join(new), npred, pred_same, pred_core_same))
open(R + "y131-floor-cert-freeze-v2-20261110/review-v1/ROW-COMPARE-V1-V2.hbp", "w", newline="").write("\n".join(out) + "\n")
print(out[-1])
for c in changed: print(c)
# header diff
ha = [l for l in a.decode().split("\n") if l.startswith("#")]; hb = [l for l in b.decode().split("\n") if l.startswith("#")]
print("header lines", len(ha), len(hb), "same", sum(1 for l in ha if l in hb))
