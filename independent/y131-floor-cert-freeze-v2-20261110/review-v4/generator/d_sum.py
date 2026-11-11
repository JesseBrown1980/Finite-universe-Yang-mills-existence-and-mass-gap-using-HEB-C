# Third correction round: one summary token per rehearsal, and the copies under review-v4/rehearsal-v2d.
# Prints one line per entry and a list of entries whose exit code differs from the expected one.
import os, re, shutil, sys
O = "/root/floor-v3/rehd/"
D = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/review-v4/rehearsal-v2d/"
ST1 = open(O + "STAGE1.sha256").read().split()[0]
LAUNCH = ["NS0", "NS1", "NS2", "NS3", "XNS", "K", "PQ", "FB5", "FB1", "FB2", "FB3", "A1", "A2", "A3", "D13"]
OTHER = ["FZA"]
CHECK = ["RK", "RA1", "RA2", "RA3", "RFB1", "RD13", "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10", "N11", "N12", "N13", "N14", "N15", "N16", "N17", "N18", "N19", "N20", "N21"]
WANT = {"NS0": 0, "NS1": 4, "NS2": 4, "NS3": 4, "K": 0, "PQ": 1, "FB5": 4, "FB1": 0, "FB2": 1, "FB3": 1, "A1": 2, "A2": 0, "A3": 3,
        "FZA": 0, "RK": 0, "RA1": 0, "RA2": 0, "RA3": 0, "RFB1": 0, "RD13": 0}
for n in CHECK:
    WANT.setdefault(n, 1)


def clean(t):
    t = re.sub(r"[;|\s]", "+", t)
    assert all(32 < ord(c) < 127 for c in t), t[:60]
    return t


def fld(line):
    d = {}
    for w in line.split("|"):
        if "=" in w:
            k, v = w.split("=", 1)
            d.setdefault(k, v)
    return d


os.makedirs(D, exist_ok=True)
summ = []
odd = []
for n in LAUNCH + OTHER + CHECK:
    so = O + n + ".stdout"
    if not os.path.isfile(so) or not os.path.isfile(O + n + ".exit"):
        odd.append(n + ":NOT_RUN")
        continue
    ex = int(open(O + n + ".exit").read().split()[0])
    last = [l for l in open(so, encoding="utf-8", errors="replace").read().split("\n") if l][-1]
    f = fld(last)
    if n in OTHER:
        tok = "%s:exit_%d:%s" % (n, ex, last.replace("|json=0", "").replace("|", ","))
    elif n in LAUNCH:
        if not last.startswith("FLOOR_RUN|"):
            odd.append(n + ":last_line_is_not_FLOOR_RUN")
        tok = "%s:exit_%d:CERTIFICATE=%s,PREDICTION=%s,DECISION=%s,certificate_reason=%s" % (n, ex, f.get("CERTIFICATE"), f.get("PREDICTION"), f.get("DECISION"), f.get("certificate_reason"))
        if "reason" in f:
            tok += ",stage=%s,reason=%s" % (f.get("stage"), f.get("reason"))
        if f.get("CERTIFICATE") == "PASS":
            tok += ",GAMMA=%s,UPPER_BOUND=%s,steps_ok=%s,accepted_certificates=%s" % (f.get("GAMMA"), f.get("UPPER_BOUND"), f.get("steps_ok"), f.get("accepted_certificates"))
        rc = O + n + "/FLOOR-RUN-RECEIPT.hbp"
        if os.path.isfile(rc):
            shutil.copyfile(rc, D + n + ".FLOOR-RUN-RECEIPT.hbp")
            if n != "XNS" and ST1 not in open(rc).read():
                odd.append(n + ":receipt_lacks_the_stage-1_record_hash")
        nt = O + n + ".note.txt"
        if os.path.isfile(nt):
            shutil.copyfile(nt, D + n + ".note.txt")
            tok += "," + clean(open(nt).read().strip().replace("|json=0", "").replace("|", ","))
    else:
        if not last.startswith("RECHECK_VERDICT|"):
            odd.append(n + ":last_line_is_not_RECHECK_VERDICT")
        tok = "%s:exit_%d:ACCEPT=%s" % (n, ex, f.get("ACCEPT"))
        if "DECISION" in f:
            tok += ",DECISION=%s,GAMMA=%s,UPPER_BOUND_VERIFIER_ONLY=%s,certificates_rechecked=%s" % (f.get("DECISION"), f.get("GAMMA"), f.get("UPPER_BOUND_VERIFIER_ONLY"), f.get("certificates_rechecked"))
        tok += ",reasons=" + (f.get("reasons") or f.get("not_started") or "none")[:260]
    shutil.copyfile(so, D + n + ".stdout.txt")
    if n in WANT and WANT[n] != ex:
        odd.append("%s:exit_%d_expected_%d" % (n, ex, WANT[n]))
    summ.append(clean(tok))
    print(summ[-1][:300])
open(O + "SUMMARY.txt", "w", newline="\n").write("\n".join(summ) + "\n")
print("ENTRIES", len(summ), "ODD", odd)
sys.exit(1 if odd else 0)
