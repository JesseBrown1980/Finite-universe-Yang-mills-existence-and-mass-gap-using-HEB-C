#!/usr/bin/env python3
# negctl.py -- verifier seat's own mutations of a copied run directory (floor freeze v2, final-head verification 4).
# usage: python3 -I negctl.py CONTROL RUNDIR [EXTRA...]
# Integers only. Rewrites FLOOR-RUN-RECEIPT.hbp (and its .sha256 when the control says so).
import sys, os, hashlib, shutil, re

NAME = "FLOOR-RUN-RECEIPT.hbp"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(d):
    return open(os.path.join(d, NAME), encoding="utf-8").read().split("\n")


def save(d, L, resign=True):
    p = os.path.join(d, NAME)
    open(p, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    if resign:
        open(p + ".sha256", "w", encoding="utf-8", newline="\n").write("%s  %s\n" % (sha(p), NAME))


def idx(L, prefix):
    return [i for i, x in enumerate(L) if x.startswith(prefix)]


def setf(line, key, val):
    w = line.split("|")
    for i, x in enumerate(w):
        if x.startswith(key + "="):
            w[i] = key + "=" + val
            return "|".join(w)
    raise SystemExit("key %s absent" % key)


def getf(line, key):
    for x in line.split("|"):
        if x.startswith(key + "="):
            return x.split("=", 1)[1]
    return None


def set_both(L, key, val):
    for pfx in ("VERDICT_FIELDS|", "FLOOR_RUN|"):
        for i in idx(L, pfx):
            L[i] = setf(L[i], key, val)


def rechecks(L):
    return idx(L, "RECHECK|")


def certs(d, L):
    return [getf(L[i], "certificate") for i in rechecks(L)]


def main():
    c, d = sys.argv[1], sys.argv[2]
    ex = sys.argv[3:]
    L = load(d)
    R = rechecks(L)
    if c == "missing_cert":
        os.remove(os.path.join(d, certs(d, L)[0]))
    elif c == "subst_bytes":
        open(os.path.join(d, certs(d, L)[0]), "a").write("# appended\n")
    elif c == "subst_rehash":
        p = os.path.join(d, certs(d, L)[0])
        t = open(p).read().split("\n")
        # change the vector entry of the last data row by +1
        for j in range(len(t) - 1, 0, -1):
            if t[j].strip() and not t[j].startswith("#"):
                a = t[j].split()
                a[2] = str(int(a[2]) + 1)
                t[j] = " ".join(a)
                break
        open(p, "w", newline="\n").write("\n".join(t))
        L[R[0]] = setf(L[R[0]], "sha256", sha(p))
        save(d, L)
    elif c == "path_dotdot":
        x = getf(L[R[0]], "certificate")
        L[R[0]] = setf(L[R[0]], "certificate", x.split("/")[0] + "/../" + x)
        save(d, L)
    elif c == "path_abs":
        x = getf(L[R[0]], "certificate")
        L[R[0]] = setf(L[R[0]], "certificate", os.path.join(d, x))
        save(d, L)
    elif c == "symlink_cert":
        x = os.path.join(d, certs(d, L)[0])
        shutil.copy(x, d + ".outside_cert")
        os.remove(x)
        os.symlink(d + ".outside_cert", x)
    elif c == "symlink_rundir":
        rd = os.path.join(d, certs(d, L)[0].split("/")[0])
        shutil.move(rd, d + ".outside_RUN")
        os.symlink(d + ".outside_RUN", rd)
    elif c in ("decision", "gamma", "upper", "upper_vonly", "g0", "certfail", "g0_consistent"):
        if c == "decision":
            set_both(L, "DECISION", "BELOW")
            set_both(L, "PREDICTION", "FALSIFIED")
        elif c == "gamma":
            g = getf(L[idx(L, "VERDICT_FIELDS|")[0]], "GAMMA")
            a, b = g.split("/")
            set_both(L, "GAMMA", "%d/%s" % (int(a) + 1, b))
        elif c == "upper":
            g = getf(L[idx(L, "VERDICT_FIELDS|")[0]], "UPPER_BOUND")
            a, b = g.split("/")
            set_both(L, "UPPER_BOUND", "%d/%s" % (int(a) - 1, b))
        elif c == "upper_vonly":
            i = idx(L, "VERDICT_FIELDS|")[0]
            g = getf(L[i], "UPPER_BOUND_VERIFIER_ONLY")
            a, b = g.split("/")
            L[i] = setf(L[i], "UPPER_BOUND_VERIFIER_ONLY", "%d/%s" % (int(a) - 1, b))
        elif c == "g0":
            i = idx(L, "VERDICT_FIELDS|")[0]
            L[i] = setf(L[i], "g0", ex[0])
        elif c == "g0_consistent":
            i = idx(L, "VERDICT_FIELDS|")[0]
            L[i] = setf(L[i], "g0", ex[0])
            set_both(L, "DECISION", ex[1])
            set_both(L, "PREDICTION", ex[2])
        elif c == "certfail":
            set_both(L, "CERTIFICATE", "FAIL")
        save(d, L)
    elif c in ("ritz_writer", "ritz_verifier"):
        g = getf(L[R[0]], c)
        a, b = g.split("/")
        L[R[0]] = setf(L[R[0]], c, "%d/%s" % (int(a) - 1, b))
        save(d, L)
    elif c == "remove_recheck":
        del L[R[-1]]
        save(d, L)
    elif c == "remove_recheck_and_cert":
        # consistent removal: the RECHECK row, its file, accepted_certificates, and every verdict field set to what is left
        cf = getf(L[R[-1]], "certificate")
        os.remove(os.path.join(d, cf))
        del L[R[-1]]
        i = idx(L, "VERDICT_FIELDS|")[0]
        L[i] = setf(L[i], "accepted_certificates", str(len(R) - 1))
        for k, v in zip(ex[0::2], ex[1::2]):
            if k == "UPPER_BOUND_VERIFIER_ONLY":
                L[i] = setf(L[i], k, v)
            else:
                set_both(L, k, v)
        save(d, L)
    elif c == "dup_recheck":
        L.insert(R[-1] + 1, L[R[-1]])
        save(d, L)
    elif c == "unlisted_extra":
        x = os.path.join(d, certs(d, L)[0])
        shutil.copy(x, os.path.join(os.path.dirname(x), "cert_m7_r14_1_f9.txt"))
    elif c == "edit_no_sidecar":
        i = idx(L, "VERDICT_FIELDS|")[0]
        L[i] = L[i].replace("|json=0", "|note=x|json=0")
        save(d, L, resign=False)
    elif c == "mode_r9":
        i = idx(L, "RECEIPT|")[0]
        L[i] = setf(L[i], "mode", "r9")
        save(d, L)
    elif c == "receipt_r":
        i = idx(L, "RECEIPT|")[0]
        L[i] = setf(L[i], "r", ex[0])
        save(d, L)
    elif c == "recheck_m0":
        L[R[0]] = setf(L[R[0]], "m0", ex[0])
        save(d, L)
    elif c == "no_relative_to":
        L[R[0]] = L[R[0]].replace("|relative_to=RUN_DIRECTORY", "")
        save(d, L)
    elif c == "pred_row":
        i = idx(L, "TOOL|private_copy=PREDICT")[0]
        L[i] = setf(L[i], "sha256", "0" * 64)
        save(d, L)
    elif c == "line_after_final":
        while L and L[-1] == "":
            L.pop()
        L.append("NOTE|after=final|json=0")
        L.append("")
        save(d, L)
    elif c == "dupkey_final":
        # the final line and VERDICT_FIELDS keep their first DECISION/PREDICTION, and carry a second, contrary pair at the end
        for pfx in ("FLOOR_RUN|", "VERDICT_FIELDS|"):
            for i in idx(L, pfx):
                L[i] = L[i].replace("|json=0", "|PREDICTION=%s|DECISION=%s|json=0" % (ex[0], ex[1]))
        save(d, L)
    elif c == "predict_score":
        for i in idx(L, "PREDICT_SCORE|"):
            L[i] = setf(L[i], "outcome", "MET")
        for i in idx(L, "FLOOR_RUN|"):
            L[i] = setf(L[i], "predict_not_met", "none")
        save(d, L)
    elif c == "step_rows":
        for i in idx(L, "STEP|"):
            L[i] = setf(L[i], "resource_limit", "EXCEEDED")
            L[i] = setf(L[i], "writer_peak_kB", "9999999")
        save(d, L)
    elif c == "rename_fword":
        # the certificate file renamed to another f word; the RECHECK row follows the new name
        x = certs(d, L)[0]
        nx = re.sub(r"_f[0-9-]+\.txt$", "_f9-9-9.txt", x)
        os.rename(os.path.join(d, x), os.path.join(d, nx))
        L[R[0]] = setf(L[R[0]], "certificate", nx)
        save(d, L)
    elif c == "minimal":
        # a receipt of only the rows the checker reads, written by hand around the run's certificates
        keep = [x for x in L if x.startswith(("RECEIPT|", "TOOL|private_copy=PREDICT", "RECHECK|", "VERDICT_FIELDS|", "RUN_DIRECTORY|", "FLOOR_RUN|"))]
        fin = [x for x in keep if x.startswith("FLOOR_RUN|")][0]
        short = "|".join(fin.split("|")[:6]) + "|json=0"
        keep = [x for x in keep if not x.startswith("FLOOR_RUN|")] + [short, ""]
        save(d, keep)
    elif c == "splice":
        # ex: DONOR_RUNDIR  -- add every RECHECK row of the donor whose file is not in this run, copy the file in,
        # then set the verdict fields to the values the checker will find (given as k v pairs after the donor)
        donor = ex[0]
        DL = load(donor)
        have = set(certs(d, L))
        add = []
        for i in rechecks(DL):
            cf = getf(DL[i], "certificate")
            if cf not in have:
                shutil.copy(os.path.join(donor, cf), os.path.join(d, cf))
                add.append(DL[i])
        last = rechecks(L)[-1]
        L[last + 1:last + 1] = add
        i = idx(L, "VERDICT_FIELDS|")[0]
        L[i] = setf(L[i], "accepted_certificates", str(len(rechecks(L))))
        kv = ex[1:]
        for k, v in zip(kv[0::2], kv[1::2]):
            if k in ("UPPER_BOUND_VERIFIER_ONLY",):
                L[i] = setf(L[i], k, v)
            else:
                set_both(L, k, v)
        save(d, L)
        print("SPLICE|added=%d|recheck_rows_now=%d" % (len(add), len(rechecks(L))))
    elif c == "fail_to_pass":
        # ex: DONOR_PASS_RECEIPT_DIR -- the run directory is a CERTIFICATE=FAIL run with its certificates on disk.
        # RECHECK rows are taken from a PASS receipt of the same r, m0 and f words (their files are NOT copied: the
        # certificates of this FAIL run are used, and their sha256 must match), the VERDICT_FIELDS and final line from it.
        donor = ex[0]
        DL = load(donor)
        out = [x for x in L if not x.startswith(("VERDICT_FIELDS|", "FLOOR_RUN|", "RUN_DIRECTORY|", "RECHECK|"))]
        while out and out[-1] == "":
            out.pop()
        for i in rechecks(DL):
            cf = getf(DL[i], "certificate")
            if sha(os.path.join(d, cf)) != getf(DL[i], "sha256"):
                raise SystemExit("certificate of the FAIL run differs from the donor row: " + cf)
        out += [x for x in DL if x.startswith("VERDICT_FIELDS|")]
        out += ["RUN_DIRECTORY|path=%s|json=0" % d]
        out += [DL[i] for i in rechecks(DL)]
        out += [x for x in DL if x.startswith("FLOOR_RUN|")] + [""]
        save(d, out)
    else:
        raise SystemExit("unknown control " + c)


main()
