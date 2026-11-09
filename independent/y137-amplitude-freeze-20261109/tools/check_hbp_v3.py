#!/usr/bin/env python3
# check_hbp_v3.py (cloud seat, #137 fix pass 3): successor of check_hbp.py (5555a3ec0262bad7), same audits plus the
# pass-3 sections audit and negctl, the GPT-6 item map, the row-131 partition, the fault verdict rule and the receipt pins.
# Structural audit of the frozen prediction file only; no model arithmetic. Usage: check_hbp_v3.py HBP [YM137_ROOT]
# Format (LF, UTF-8, |json=0 endings, KEY=value fields), tags, ids, cross-references, falsifier reachability, END counts.
import sys
import hashlib

TAGS = {"DERIVED", "CONJECTURE", "OPEN", "REQUIRED"}
SECS = {"model", "floor", "sector", "census", "method", "theorem", "check", "accept", "refuter", "predict_iso",
        "predict_amp", "fault", "map148", "scope", "disclosure", "gate", "audit", "negctl"}
SEC_TAGS = {"theorem": {"DERIVED"}, "check": {"REQUIRED"}, "fault": {"REQUIRED"}, "map148": {"REQUIRED"},
            "accept": {"REQUIRED"}, "refuter": {"REQUIRED"}, "predict_iso": {"CONJECTURE", "OPEN"},
            "predict_amp": {"CONJECTURE", "OPEN"}, "scope": {"REQUIRED"}, "gate": {"REQUIRED"},
            "disclosure": {"REQUIRED"}, "method": {"REQUIRED"}, "audit": {"REQUIRED"}, "negctl": {"REQUIRED"}}
FLOOR = "lambda_min_QHQ_whole_GE_94070673/1000000"


def main():
    path = sys.argv[1]
    raw = open(path, "rb").read()
    errs = []

    def err(m):
        errs.append(m)

    text = raw.decode("utf-8")
    if b"\r" in raw:
        err("CR found")
    if b"\t" in raw:
        err("TAB found")
    if not text.endswith("\n"):
        err("no final LF")
    lines = text.split("\n")[:-1]
    rows, end = [], None
    seen_record = False
    for ln, line in enumerate(lines, 1):
        if line.startswith("#"):
            if seen_record:
                err("comment after first record at line %d" % ln)
            continue
        seen_record = True
        if not line.endswith("|json=0"):
            err("line %d does not end with |json=0" % ln)
        parts = line.split("|")
        kind = parts[0]
        kv = {}
        for f in parts[1:]:
            if "=" not in f:
                err("line %d field without '=': %s" % (ln, f))
                continue
            k, v = f.split("=", 1)
            if not k or not v:
                err("line %d empty key or value: %s" % (ln, f))
            if "=" in v:
                err("line %d value contains '=': %s" % (ln, f))
            if any(c.isspace() for c in f):
                err("line %d whitespace in field: %s" % (ln, f))
            if k in kv:
                err("line %d duplicate key %s" % (ln, k))
            kv[k] = v
        if kind == "PREDICT":
            rows.append((ln, kv))
        elif kind == "PREDICTION_END":
            if end is not None:
                err("two END rows")
            end = (ln, kv)
            if ln != len(lines):
                err("END row is not last")
        else:
            err("line %d unknown record type %s" % (ln, kind))
    # ids, sec, tags
    for i, (ln, kv) in enumerate(rows, 1):
        if kv.get("id") != "%03d" % i:
            err("line %d id %s expected %03d" % (ln, kv.get("id"), i))
        sec, tag = kv.get("sec"), kv.get("tag")
        if sec not in SECS:
            err("line %d bad sec %s" % (ln, sec))
        if tag not in TAGS:
            err("line %d bad tag %s" % (ln, tag))
        if sec in SEC_TAGS and tag not in SEC_TAGS[sec]:
            err("line %d sec %s with tag %s" % (ln, sec, tag))
        if kv.get("json") != "0":
            err("line %d json field" % ln)
        if "cond" in kv and kv["cond"] != "accepted_source_assumption":
            err("line %d cond value" % ln)
        b = kv.get("basis", "")
        if "MEASURED" in b and not ("excluded_r" in b or "r_independent" in b):
            err("line %d MEASURED basis without excluded_r or r_independent: %s" % (ln, b))
        if tag == "CONJECTURE" and "falsified_if" not in kv:
            err("line %d CONJECTURE row without falsified_if" % ln)
    by = lambda s: [kv for _, kv in rows if kv.get("sec") == s]
    floor_rows = [kv for kv in by("floor") if kv.get("accepted_source_assumption") == FLOOR]
    if len(floor_rows) != 1:
        err("floor row with the exact name: %d" % len(floor_rows))
    checks = {}
    for kv in by("check"):
        c = kv.get("check")
        if c in checks:
            err("duplicate check %s" % c)
        for k in ("statement", "executes", "on_fail"):
            if k not in kv:
                err("check %s missing %s" % (c, k))
        if kv.get("on_fail") not in ("REFUSE", "HOLD"):
            err("check %s on_fail %s" % (c, kv.get("on_fail")))
        if "never" in kv.get("executes", "") or kv.get("executes") == "none":
            err("check %s not executable" % c)
        checks[c] = kv
    refd = {c: [] for c in checks}

    def need_checks(lst, who):
        for t in lst.split(","):
            if t not in checks:
                err("%s references undefined check %s" % (who, t))
            else:
                refd[t].append(who)

    faults = {}
    for j, kv in enumerate(by("fault"), 1):
        f = kv.get("fault", "")
        code = f.split("_")[0]
        if code != "PF%02d" % j:
            err("fault code %s expected PF%02d" % (code, j))
        for k in ("how", "refused_by", "run_at", "verdict", "falsifier", "maps"):
            if k not in kv:
                err("fault %s missing %s" % (code, k))
        if "," in kv.get("refused_by", ""):
            err("fault %s refused_by must name one check" % code)
        need_checks(kv.get("refused_by", ""), code + ".refused_by")
        if "also" in kv:
            need_checks(kv["also"], code + ".also")
        if "r9" not in kv.get("run_at", ""):
            err("fault %s not run at r9" % code)
        faults[code] = kv
    must = ["wrong_character", "dropped_exterior_edge", "wrong_weight", "floor_raised_to_a_Ritz", "sign_flipped",
            "adjoint_term_dropped", "odd_sector_ignored", "E2_multiplicity_assumed"]
    for m in must:
        if not any(m in kv["fault"] for kv in faults.values()):
            err("required planted fault missing: %s" % m)
    mapped = {}
    for kv in by("map148"):
        keys = [k for k in kv if k.startswith("PR148_F")]
        if len(keys) != 1:
            err("map148 row keys %s" % keys)
            continue
        k = keys[0]
        if k in mapped:
            err("duplicate map %s" % k)
        need_checks(kv[k], k)
        mapped[k] = kv
        targets = set(kv[k].split(","))
        for pf in kv.get("planted", "").split(","):
            if pf not in faults:
                err("%s planted %s undefined" % (k, pf))
                continue
            fk = faults[pf]
            hit = {fk["refused_by"]} | set(fk.get("also", "").split(","))
            if not (hit & targets):
                err("%s: planted %s is refused by none of the mapped checks" % (k, pf))
            if k.replace("PR148_", "") not in fk.get("maps", ""):
                err("%s: planted %s does not list %s in maps" % (k, pf, k))
    for i in range(1, 13):
        if "PR148_F%d" % i not in mapped:
            err("PR148_F%d unmapped" % i)
    items = {}
    for kv in by("accept"):
        it = kv.get("owner_item", "").split("_")[0]
        items[it] = kv
        for k in ("requirement", "checks", "verdict", "falsifier"):
            if k not in kv:
                err("accept %s missing %s" % (it, k))
        need_checks(kv.get("checks", ""), "accept" + it)
    if sorted(items) != ["1", "2", "3", "4"]:
        err("owner items %s" % sorted(items))
    tests = {}
    for kv in by("refuter"):
        t = kv.get("refuter_test", "").split("_")[0]
        tests[t] = kv
        need_checks(kv.get("answered_by", ""), "refuter" + t)
    if sorted(tests) != ["1", "2", "3", "4", "5", "6"]:
        err("refuter tests %s" % sorted(tests))
    # ---- pass 3 audits ----
    ids = {kv.get("id") for _, kv in rows}
    if not any("6747959074" in l for l in lines if l.startswith("#")):
        err("no header line cites comment 6747959074")
    items6 = {}
    for kv in by("audit"):
        it = kv.get("gpt6_item", "").split("_")[0]
        if it in items6:
            err("duplicate gpt6 item %s" % it)
        items6[it] = kv
        if "6747959074" not in kv.get("cites", ""):
            err("audit item %s does not cite comment 6747959074" % it)
        for rid in kv.get("answered_by_rows", "").split(","):
            if rid not in ids:
                err("audit item %s references undefined row %s" % (it, rid))
        if "answered_by_checks" not in kv:
            err("audit item %s names no check" % it)
        else:
            need_checks(kv["answered_by_checks"], "audit" + it)
    if sorted(items6) != ["1", "2", "3", "4", "5", "6"]:
        err("gpt6 items %s" % sorted(items6))
    import os
    root = sys.argv[2] if len(sys.argv) > 2 else None
    for kv in by("negctl"):
        for k in ("script", "output"):
            v = kv.get(k, "")
            p, _, h = v.rpartition("_")
            if len(h) != 16 or any(c not in "0123456789abcdef" for c in h):
                err("negctl %s field %s has no 16-hex fingerprint" % (kv.get("negctl"), k))
            elif root is not None:
                fp = os.path.join(root, p)
                if not os.path.exists(fp):
                    err("negctl %s file missing: %s" % (kv.get("negctl"), p))
                elif hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16] != h:
                    err("negctl %s fingerprint mismatch: %s" % (kv.get("negctl"), p))
                else:
                    print("PIN_OK|negctl=%s|%s=%s|sha256_16=%s" % (kv.get("negctl"), k, p, h))
    gate131 = [kv for kv in by("gate") if "run_integrity_checks" in kv]
    if len(gate131) != 1:
        err("row 131 not found")
    else:
        ri = gate131[0]["run_integrity_checks"].split(",")
        rc = gate131[0]["route_certificate_checks"].split(",")
        allc = ri + rc
        if sorted(allc) != sorted(checks) or len(set(allc)) != len(allc):
            err("row 131 does not partition the checks: missing %s extra %s"
                % (sorted(set(checks) - set(allc)), sorted(set(allc) - set(checks))))
        print("ROW131|run_integrity=%d|route_certificate=%d|checks=%d" % (len(ri), len(rc), len(checks)))
        for c in ri:
            if checks.get(c, {}).get("on_fail") != "REFUSE":
                err("run-integrity check %s is not on_fail REFUSE" % c)
    for code, kv in faults.items():
        v = kv.get("verdict", "")
        if not ("executed_and_FAIL" in v or "reported_missing" in v):
            err("fault %s verdict does not follow header line 10: %s" % (code, v))
        if "FAIL_or_be_reported_missing" in v:
            err("fault %s keeps the old 'or missing' verdict" % code)
    # tag counts and END row
    cnt = {t: 0 for t in TAGS}
    for _, kv in rows:
        cnt[kv["tag"]] = cnt.get(kv["tag"], 0) + 1
    want = {"rows": len(rows), "checks": len(checks), "faults": len(faults), "map148": len(mapped),
            "accept": len(items), "refuter": len(tests), "audit": len(items6), "negctl": len(by("negctl"))}
    want.update(cnt)
    if end is None:
        err("no END row")
    else:
        for k, v in want.items():
            if end[1].get(k) != str(v):
                err("END %s=%s expected %s" % (k, end[1].get(k), v))
    unref = sorted(c for c, w in refd.items() if not w)
    print("FILE|path=%s|sha256=%s|bytes=%d|lines=%d" % (path.split("/")[-1], hashlib.sha256(raw).hexdigest(),
                                                       len(raw), len(lines)))
    print("COUNTS|" + "|".join("%s=%d" % (k, v) for k, v in sorted(want.items())))
    print("SECS|" + "|".join("%s=%d" % (s, len(by(s))) for s in sorted(SECS)))
    print("CHECKS_UNREFERENCED_BY_FAULT_ACCEPT_REFUTER_OR_MAP|" + (",".join(unref) if unref else "none"))
    for code, kv in faults.items():
        print("REACH|%s|refused_by=%s|executes=%s|on_fail=%s" % (code, kv["refused_by"],
                                                               checks.get(kv["refused_by"], {}).get("executes"),
                                                               checks.get(kv["refused_by"], {}).get("on_fail")))
    print("ERRORS|%d" % len(errs))
    for e in errs:
        print("ERR|" + e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
