

# ------------------------------------------------------------------ step: every gate of one m0 step
def peak(ls, bad, what):
    pk = pick(ls, "PEAK_RSS|")
    if len(pk) != 1:
        bad.append("row_011:%s_has_%d_PEAK_RSS_lines" % (what, len(pk)))
        return 0
    f = fld(pk[0])
    if f.get("exit") != "0":
        bad.append("row_011:%s_exit_%s" % (what, f.get("exit")))
    kb = int(f.get("kB", "0")) if f.get("kB", "").isdigit() else LIM_KB
    if kb >= LIM_KB:
        bad.append("row_011:%s_PEAK_RSS_not_under_2GB" % what)
    return kb


def gates(ls, names, bad, what):
    seen = {}
    for x in pick(ls, "GATE|"):
        w = x.split("|")
        if len(w) < 3 or w[2] != "PASS":
            bad.append("%s_gate_%s_is_%s" % (what, w[1] if len(w) > 1 else "?", w[2] if len(w) > 2 else "?"))
        else:
            seen[w[1]] = x
    for x in ls:
        if x.startswith("REFUSE|") or x.startswith("VERDICT|REFUSE"):
            bad.append("%s_prints_refusal" % what)
    for nm in names:
        if nm not in seen:
            bad.append("%s_gate_%s_absent" % (what, nm))
    return seen


def count_is(seen, gate, key, want, bad, row):
    if want is None or gate not in seen:
        return
    got = fld(seen[gate]).get(key)
    if got != str(want):
        bad.append("row_%s:%s_%s_is_%s_pin_%d" % (row, gate, key, got, want))


def cmd_step(a):
    m = int(a["m0"])
    r = rat(a["r"])
    out = a["out"]
    lg = out + "/log"
    run = out + "/RUN%d" % m
    mode = a["mode"]
    R = rows(a["pred"])
    need(R)
    C = CENSUS.get(m, {}) if mode == "r9" or a.get("census") == "1" else {}
    bad = []
    crows = []
    fwords = a["fspec"].split(";")
    rh = lines(lg + "/m%d_rowhash.txt" % m)
    ce = lines(lg + "/m%d_cert.txt" % m)
    pk_r = peak(rh, bad, "rowhash")
    pk_c = peak(ce, bad, "cert")
    seen = gates(rh, [], bad, "rowhash")
    seen2 = gates(ce, [], bad, "cert")
    both = dict(seen)
    both.update(seen2)
    for nm in WGATES:
        if nm not in both:
            bad.append("row_055:writer_gate_%s_absent" % nm)
    for s in (seen, seen2):
        count_is(s, "class_detailed_balance", "edges", C.get("edges"), bad, "047")
        count_is(s, "symmetry_image_rows", "rows_rebuilt", C.get("rebuilt"), bad, "051")
        count_is(s, "symmetry_image_rows", "classes", C.get("classes"), bad, "051")
        count_is(s, "local_delta_vs_full_M", "moves_checked", C.get("moves"), bad, "055")
        count_is(s, "link_multiset_table", "configurations_checked", C.get("conf"), bad, "055")
    ro = pick(rh, "ROWHASH_ONLY|")
    rowhash = keyshash = ""
    if len(ro) != 1:
        bad.append("rowhash_step_line_absent")
    else:
        f = fld(ro[0])
        rowhash = f.get("sha256", "")
        keyshash = f.get("keyshash", "")
        if f.get("m0") != str(m) or len(rowhash) != 64 or len(keyshash) != 64:
            bad.append("rowhash_step_line_malformed")
    rh_pin = R[C["rh"]][1]["value"] if "rh" in C else None
    kh_pin = R[C["kh"]][1]["value"] if "kh" in C else None
    if rh_pin and rowhash != rh_pin:
        bad.append("row_%s:rowhash_differs_from_pin" % C["rh"])
    if kh_pin and keyshash != kh_pin:
        bad.append("row_%s:keyshash_differs_from_pin" % C["kh"])
    kf = run + "/core_keys_m%d.bin" % m
    if not os.path.isfile(kf) or sha(kf) != keyshash:
        bad.append("keys_file_sha256_differs_from_KEYSHASH")
    for x in pick(ce, "ROWHASH|"):
        if fld(x).get("sha256") != rowhash:
            bad.append("cert_command_rowhash_differs_from_rowhash_step")
    for x in pick(ce, "KEYSHASH|"):
        if fld(x).get("sha256") != keyshash:
            bad.append("cert_command_keyshash_differs_from_rowhash_step")
    if not pick(ce, "ROWHASH|") or not pick(ce, "KEYSHASH|") or not pick(ce, "KEYS|loaded="):
        bad.append("cert_command_did_not_reuse_the_rowhash_directory")
    for x in pick(ce, "TAIL|"):
        if fld(x).get("gate_observed_ge_layer") != "PASS":
            bad.append("row_050:tail_gate_not_PASS")
    fbsha = a.get("fbsha", "")
    if mode == "r9":
        fz = pick(ce, "FREEZE|")
        if not fz:
            bad.append("row_009:writer_FREEZE_line_absent")
        for x in fz:
            f = fld(x)
            if f.get("commit") != a["commit"] or f.get("prediction_sha256") != a["psha"] or f.get("binary_sha256") != fbsha:
                bad.append("row_018:writer_FREEZE_line_differs")
    # directory content: rowhash files plus the certificates the writer lists (row 001)
    before = set(x for x in lines(lg + "/m%d_dir_after_rowhash.txt" % m) if x)
    wrote = {}
    for x in pick(ce, "WROTE|"):
        w = x.split("|")
        wrote[os.path.basename(w[1])] = fld(x).get("sha256", "")
    now = set(os.listdir(run)) if os.path.isdir(run) else set()
    extra = sorted(now - before - set(wrote))
    if extra:
        bad.append("row_001:directory_holds_%d_files_not_listed_by_WROTE" % len(extra))
    cl = pick(ce, "CERT|")
    if len(cl) != len(fwords) or len(wrote) != len(fwords):
        bad.append("row_002:%d_CERT_lines_%d_WROTE_lines_for_%d_f_words" % (len(cl), len(wrote), len(fwords)))
    vsha_pin = R["019"][1]["value"]
    mem_max = 0
    for i, x in enumerate(cl):
        cb = []
        f = fld(x)
        fw = f.get("f", "")
        if i < len(fwords) and fw != fwords[i]:
            cb.append("row_002:f_word_order")
        base = "cert_m%d_r%d_%d_f%s.txt" % (m, r[0], r[1], fw.replace(",", "-"))
        path = run + "/" + base
        gm = re.match(r"^([0-9]+)/([0-9]+)=", f.get("gamma", ""))
        g_w = (int(gm.group(1)), int(gm.group(2))) if gm else None
        row = {"f": fw, "file": base, "sha": "ABSENT", "gamma": None, "rw": None, "rv": None,
               "cap": f.get("tail_cap", ""), "next": f.get("next_t_refused", ""), "gate": "MISSING"}
        if g_w is None or f.get("row_check") != "PASS" or not f.get("next_t_refused", "").startswith("gate="):
            cb.append("row_046:writer_CERT_line")
        if f.get("r") != "%d/%d" % r or f.get("m0") != str(m) or f.get("rowhash") != rowhash:
            cb.append("writer_CERT_line_r_m0_rowhash")
        if base not in wrote or not os.path.isfile(path):
            cb.append("certificate_file_absent")
        else:
            row["sha"] = sha(path)
            if row["sha"] != wrote[base]:
                cb.append("certificate_sha256_differs_from_WROTE")
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                head = fh.readline().rstrip("\n")
            hd = {}
            for w in head.split(" "):
                if "=" in w:
                    k, v = w.split("=", 1)
                    hd[k] = v
            if hd.get("m0") != str(m) or hd.get("r") != "%d/%d" % r or hd.get("f") != fw:
                cb.append("header_m0_r_f")
            if hd.get("rowhash") != rowhash or hd.get("keyshash") != keyshash:
                cb.append("header_rowhash_keyshash")
            if mode == "r9" and (hd.get("freeze") != a["commit"] or hd.get("pred") != a["psha"]):
                cb.append("row_009:header_freeze_pred")
            g = lines(lg + "/m%d_gate_%s.txt" % (m, base))
            vs = gates(g, VGATES, cb, "verifier")
            gr = pick(g, "GATE_REQUIRED|")
            vd = pick(g, "VERDICT|PASS|")
            if len(gr) != 1 or not gr[0].startswith("GATE_REQUIRED|PASS|") or len(vd) != 1:
                cb.append("row_053:GATE_REQUIRED_not_PASS")
                row["gate"] = "REFUSE" if gr else "MISSING"
            else:
                row["gate"] = "PASS"
                gf = fld(gr[0])
                if gf.get("cert_sha256") != row["sha"] or gf.get("rowhash") != rowhash or gf.get("verifier_sha256") != vsha_pin:
                    cb.append("row_053:GATE_REQUIRED_fields")
                vm = re.match(r"^VERDICT\|PASS\|lambda_min\(QHQ\) >= ([0-9]+)/([0-9]+) at r = ([0-9]+)/([0-9]+) \(m0 = ([0-9]+)\)\|", vd[0])
                if not vm:
                    cb.append("VERDICT_line_unreadable")
                else:
                    g_v = (int(vm.group(1)), int(vm.group(2)))
                    if not eq((int(vm.group(3)), int(vm.group(4))), r) or int(vm.group(5)) != m:
                        cb.append("VERDICT_r_m0")
                    g_h = rat(hd["t"]) if re.match(r"^[0-9]+/[0-9]+$", hd.get("t", "")) else None
                    if g_h is None or g_w is None or not eq(g_v, g_h) or not eq(g_v, g_w):
                        cb.append("row_005:gamma_three_way_mismatch")
                    else:
                        row["gamma"] = g_v
                    if fld(vd[0]).get("min_slack") != f.get("min_slack") or fld(vs.get("row_check", "")).get("min_slack") != f.get("min_slack"):
                        cb.append("row_054:min_slack_differs")
                rz = pick(g, "RITZ_CLASS_VECTOR|")
                if len(rz) == 1 and re.match(r"^[0-9]+\.[0-9]{6}$", rz[0].split("|")[1]) and re.match(r"^[0-9]+\.[0-9]{6}$", f.get("ritz_upper", "")):
                    row["rv"] = rat(rz[0].split("|")[1])
                    row["rw"] = rat(f["ritz_upper"])
                    if row["gamma"] is not None and not le(row["gamma"], add(rmin([row["rv"], row["rw"]]), (1, MIL))):
                        cb.append("row_052:gamma_above_Ritz_upper")
                else:
                    cb.append("row_052:Ritz_lines")
                mems = pick(g, "MEM|")
                if not mems:
                    cb.append("row_011:verifier_MEM_absent")
                for y in mems:
                    mm = re.match(r"^MEM\|([0-9]+)kB", y)
                    kb = int(mm.group(1)) if mm else LIM_KB
                    mem_max = max(mem_max, kb)
                    if kb >= LIM_KB:
                        cb.append("row_011:verifier_MEM_not_under_2GB")
                for y in pick(g, "KEYSHASH|"):
                    if fld(y).get("sha256") != keyshash:
                        cb.append("row_056:verifier_keyshash")
                en = pick(g, "ENUM|")
                if "orbits" in C:
                    ef = fld(en[0]) if en else {}
                    if ef.get("orbits") != str(C["orbits"]) or ef.get("classes") != str(C["classes"]) or ef.get("weight") != str(C["weight"]):
                        cb.append("row_043_044:verifier_ENUM_differs_from_pin")
                if mode == "r9":
                    vf = pick(g, "FREEZE|")
                    ff = fld(vf[0]) if vf else {}
                    if ff.get("commit") != a["commit"] or ff.get("prediction_sha256") != a["psha"] or ff.get("verifier_sha256") != vsha_pin:
                        cb.append("row_009:verifier_FREEZE_line")
        row["bad"] = cb
        bad.extend("f_%s:%s" % (fw.replace(",", "-"), y) for y in cb)
        crows.append(row)
    ok = not bad
    acc = [c for c in crows if ok]
    G = rmax([c["gamma"] for c in acc])
    U = rmin([add(rmin([c["rv"], c["rw"]]), (1, MIL)) for c in acc])
    Uv = rmin([add(c["rv"], (1, MIL)) for c in acc])
    o = ["STEP|m0=%d|status=%s|accepted=%d|certificates=%d|G=%s|U=%s|U_verifier_only=%s|writer_peak_kB=%d|verifier_mem_max_kB=%d|rowhash=%s|keyshash=%s|rowhash_pin=%s|bad=%s|json=0"
         % (m, "OK" if ok else "FAIL", len(acc), len(crows), rs(G), rs(U), rs(Uv), max(pk_r, pk_c), mem_max,
            rowhash or "NONE", keyshash or "NONE", ("row_" + C["rh"]) if "rh" in C else "three_way_equality_only", ";".join(bad) or "none")]
    for c in crows:
        o.append("CERTROW|m0=%d|f=%s|file=%s|sha256=%s|accepted=%d|gate=%s|gamma=%s|ritz_writer=%s|ritz_verifier=%s|tail_cap=%s|next_t_refused=%s|bad=%s|json=0"
                 % (m, c["f"], c["file"], c["sha"], 1 if ok else 0, c["gate"], rs(c["gamma"]), rs(c["rw"]), rs(c["rv"]), c["cap"], c["next"], ";".join(c["bad"]) or "none"))
    for e in extra:
        g = lines(lg + "/m%d_gate_%s.txt" % (m, e))
        gr = pick(g, "GATE_REQUIRED|")
        o.append("CERTROW|m0=%d|f=UNLISTED|file=%s|sha256=%s|accepted=0|gate=%s|gamma=NONE|bad=not_listed_by_WROTE|json=0"
                 % (m, e, sha(run + "/" + e), gr[0].split("|")[1] if gr else "NOT_A_CERTIFICATE"))
    with open(lg + "/m%d_step.hbp" % m, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o) + "\n")
    print("\n".join(o))
    sys.exit(0 if ok else 1)
