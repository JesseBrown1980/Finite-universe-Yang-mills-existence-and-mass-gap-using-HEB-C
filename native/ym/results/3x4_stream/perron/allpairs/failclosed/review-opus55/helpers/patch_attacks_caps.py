# Adds a cap matrix to attacks.py: every named store also runs at caps 0, 1, 2, 3, 7 and 100, and must give the exit, verdict and counters of the default cap.
p = "C:/tmp/opus55/allpairs-review-20261103/attack/attacks.py"
s = open(p, encoding="utf-8").read()
a = """    rcode, rf = reader(path)
    miss = []
"""
b = """    rcode, rf = reader(path)
    caps_differ = []
    for c in CAP_MATRIX:
        cc, ll, ff, _ = tool(RECORDED, path, c)
        if cc != code or strip_varying(ll) != strip_varying(last):
            caps_differ.append("%d:exit=%d" % (c, cc))
    miss = []
"""
assert a in s
s = s.replace(a, b)
a = """    row("RESULT", run="attack_" + name, exit=code, verdict=f.get("verdict"), own_build_same=same, reader_exit=rcode, reader_verdict=rf.get("verdict"), prediction_met=met, miss=";".join(miss) or "-", line=last.replace("|", "~"))
"""
b = """    if CAP_MATRIX and caps_differ:
        miss.append("caps:" + ",".join(caps_differ))
        met = 0
        counts["met"] -= 1
        counts["not_met"] += 1
    row("RESULT", run="attack_" + name, exit=code, verdict=f.get("verdict"), own_build_same=same, reader_exit=rcode, reader_verdict=rf.get("verdict"), caps_tried=len(CAP_MATRIX), caps_same=len(CAP_MATRIX) - len(caps_differ), prediction_met=met, miss=";".join(miss) or "-", line=last.replace("|", "~"))
"""
assert a in s
s = s.replace(a, b)
a = """def attack(name, data, predict, cap=None, reader_verdict="FAIL", keep=False, note=""):"""
b = """CAP_MATRIX = [0, 1, 2, 3, 7, 100] if os.environ.get("ATTACK_CAP_MATRIX") == "1" else []


def strip_varying(s):
    return re.sub(r"\\|secs=\\d+|\\|cap_entries=\\d+|\\|passes=\\d+", "", s)


def attack(name, data, predict, cap=None, reader_verdict="FAIL", keep=False, note=""):"""
assert a in s
s = s.replace(a, b)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
