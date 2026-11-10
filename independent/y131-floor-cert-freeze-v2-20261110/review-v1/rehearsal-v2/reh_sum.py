# Copies each rehearsal's receipt and stdout into review-v1/rehearsal-v2 and writes /root/floor-v2/reh/SUMMARY.txt.
import os, re, shutil, sys
O = "/root/floor-v2/reh/"
D = "/root/floor-v2/repo/independent/y131-floor-cert-freeze-v2-20261110/review-v1/rehearsal-v2/"
T = "/mnt/c/tmp/opus55/floor-v2/"
os.makedirs(D, exist_ok=True)
args = {}
for l in open(T + "reh_all.sh").read().replace("\r", "").split("\n"):
    m = re.match(r"^ (\w+)\) one \w+ (.*);;$", l)
    if m: args[m.group(1)] = m.group(2).replace("'", "").replace(" ", "_")
keep = ("result", "stage", "reason", "comparison", "gamma_cert", "U_all", "steps_run", "steps_ok", "operational_failures", "accepted_certificates", "stop", "rule", "certificate_commands_run")
out = []
for n in sys.argv[1:]:
    txt = open(O + n + ".stdout.txt").read().replace("\r", "")
    open(D + n + ".stdout.txt", "w", newline="\n").write(txt)
    rc = O + n + "/FLOOR-RUN-RECEIPT.hbp"
    if os.path.exists(rc):
        shutil.copyfile(rc, D + n + ".FLOOR-RUN-RECEIPT.hbp")
    fr = [l for l in txt.split("\n") if l.startswith("FLOOR_RUN|")]
    ref = [l for l in txt.split("\n") if l.startswith("REFUSE|") or l.startswith("STOP|")]
    assert len(fr) == 1, (n, len(fr))
    f = dict(x.split("=", 1) for x in fr[0].split("|")[1:] if "=" in x)
    acc = [l for l in (open(rc).read().split("\n") if os.path.exists(rc) else []) if l.startswith("ACCEPTED|")]
    s = n + ":" + args[n] + ":" + ",".join("%s=%s" % (k, f[k]) for k in keep if k in f)
    if acc: s += ",receipt_accepted_per_step=" + "/".join(re.search(r"m0=(\d+)\|count=(\d+)", x).group(1) + ":" + re.search(r"count=(\d+)", x).group(1) for x in acc)
    dec = [l for l in txt.split("\n") if l.startswith("DECISION|")]
    if dec: s += ",decisions=" + "/".join(re.search(r"state=([A-Z_0-9]+)", x).group(1) + ">" + re.search(r"next=(\w+)", x).group(1) for x in dec)
    assert " " not in s and "|" not in s, s
    out.append(s)
for k in ("reh_all.sh", "reh_sum.py", "rev_rows.py", "rev_patch.py", "fe_a.py", "fe_b.py", "fe_c.py", "install.sh"):
    open(D + k, "w", newline="\n").write(open(T + k).read().replace("\r", ""))
open(O + "SUMMARY.txt", "w", newline="\n").write("\n".join(out) + "\n")
print("\n".join(out))
