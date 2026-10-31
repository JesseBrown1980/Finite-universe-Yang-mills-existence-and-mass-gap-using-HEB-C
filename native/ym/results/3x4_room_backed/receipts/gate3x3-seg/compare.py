# READ-ONLY record comparator, one threshold.  Side A / side B = comma-separated file lists
# (e.g. shellschur split run: SCOL file + merge file).  Rules (operator 2026-10-29):
#  - SCOL records canonicalised by key (cb, ca); every field of the line compared.
#  - Duplicate key on a side, FAIL line, missing SHELL_SCHUR, unreadable file -> INCONCLUSIVE.
#  - Missing keys or differing fields between completed runs -> MISMATCH.
#  - Same keyed set in a different order -> AGREE, order difference reported separately.
#  - SHELL_SCHUR: all fields compared except matrix= (input label) and ms= (wall time);
#    both ms values are printed as raw evidence.  Unpaired progress lines are diagnostics.
import sys, hashlib
def fld(line, k):
    for kv in line.split("|"):
        if kv.startswith(k): return kv[len(k):]
    return None
def side(paths):
    ss, ssraw, diag, fail, scol_lines = None, None, {}, [], 0
    slots = seen = None; m = None; seq = hashlib.sha256(); dup = None
    for p in paths.split(","):
        with open(p, "rb") as f:
            for raw in f:
                line = raw.rstrip(b"\r\n").decode()
                tag = line.split("|", 1)[0]
                if tag == "SCOL":
                    if m is None:
                        m = int(fld(line, "core=")); slots = bytearray(16 * m * m); seen = bytearray(m * m)
                    cb, ca = int(fld(line, "cb=")), int(fld(line, "ca="))
                    if not (0 <= cb < m and 0 <= ca < m): fail.append(f"key_out_of_range:{cb},{ca}"); continue
                    k = ca * m + cb
                    if seen[k]: dup = dup or (cb, ca)
                    seen[k] = 1; slots[16*k:16*k+16] = hashlib.sha256(raw.rstrip(b"\r\n")).digest()[:16]
                    seq.update(raw.rstrip(b"\r\n") + b"\n"); scol_lines += 1
                elif tag == "SHELL_SCHUR":
                    if fld(line, "result=") == "FAIL": fail.append(line)
                    ssraw = line
                    ss = "|".join(x for x in line.split("|") if not x.startswith(("matrix=", "ms=")))
                else:
                    diag[tag] = diag.get(tag, 0) + 1
    return dict(ss=ss, ssraw=ssraw, diag=diag, fail=fail, n=scol_lines, m=m, slots=slots, seen=seen, seq=seq.hexdigest(), dup=dup)
def line_for(paths, key):
    for p in paths.split(","):
        for raw in open(p, "rb"):
            l = raw.rstrip(b"\r\n").decode()
            if l.startswith("SCOL|") and (int(fld(l, "cb=")), int(fld(l, "ca="))) == key: return l
    return "<absent>"
pa, pb, t = sys.argv[1], sys.argv[2], sys.argv[3]
def out(o, why=""):
    print(f"COMPARE|t={t}|outcome={o}{'|reason='+why if why else ''}|json=0"); sys.exit({"AGREE": 0, "MISMATCH": 2}.get(o, 3))
try:
    A, B = side(pa), side(pb)
except Exception as e:
    out("INCONCLUSIVE", f"unreadable_or_malformed:{e}")
for nm, S in (("A", A), ("B", B)):
    print(f"COMPARE_SIDE|side={nm}|scol={S['n']}|core={S['m']}|keys_seen={sum(S['seen']) if S['seen'] else 0}|dup={S['dup']}|fail={len(S['fail'])}|seq_sha256={S['seq']}|unpaired={S['diag']}|ms={fld(S['ssraw'] or '', 'ms=')}|json=0")
    if S["fail"]: out("INCONCLUSIVE", f"side_{nm}_failed:{S['fail'][0][:120]}")
    if S["ss"] is None: out("INCONCLUSIVE", f"side_{nm}_missing_SHELL_SCHUR")
    if S["n"] == 0: out("INCONCLUSIVE", f"side_{nm}_no_SCOL_records")
    if S["dup"] is not None: out("INCONCLUSIVE", f"side_{nm}_duplicate_key:{S['dup']}")
sum_eq = A["ss"] == B["ss"]
print(f"COMPARE_SUMMARY|t={t}|equal={int(sum_eq)}|excluded=matrix=,ms=|json=0")
if not sum_eq:
    print("COMPARE_SUMMARY_A|" + A["ss"]); print("COMPARE_SUMMARY_B|" + B["ss"])
if A["m"] != B["m"]:
    out("MISMATCH", f"core_size_{A['m']}_vs_{B['m']}")
first = None
if A["slots"] != B["slots"] or A["seen"] != B["seen"]:
    m = A["m"]
    for k in range(m * m):
        if A["seen"][k] != B["seen"][k] or A["slots"][16*k:16*k+16] != B["slots"][16*k:16*k+16]:
            first = (k % m, k // m); break
if first is not None:
    print(f"COMPARE_DIFF|key=cb{first[0]},ca{first[1]}|json=0")
    print("COMPARE_DIFF_A|" + line_for(pa, first)); print("COMPARE_DIFF_B|" + line_for(pb, first))
print(f"COMPARE_SCOL|t={t}|keyed_equal={int(first is None)}|order_equal={int(A['seq']==B['seq'])}|json=0")
out("AGREE" if (first is None and sum_eq) else "MISMATCH")
