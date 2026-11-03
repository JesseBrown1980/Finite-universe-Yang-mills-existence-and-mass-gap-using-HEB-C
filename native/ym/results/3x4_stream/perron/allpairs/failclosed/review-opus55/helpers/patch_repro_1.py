# Adds the four-row store and the unclamped cap label to repro.py, so each defect row in the review has its reproducer there.
p = "C:/tmp/opus55/allpairs-review-20261103/attack/repro.py"
s = open(p, encoding="utf-8").read()
a = """case("C5_cap_one", store(P), {"exit": 0, "cap_entries": 1, "passes": 188}, cap=1)
"""
b = """case("C5_cap_one", store(P), {"exit": 0, "cap_entries": 1, "passes": 188}, cap=1)
case("D5_cap_max_label", store(P), {"exit": 0, "cap_entries": 18446744073709551615, "passes": 1}, cap=18446744073709551615)
"""
assert a in s
s = s.replace(a, b)
a = """# D7: a doubled lower entry"""
b = """w4 = 13060694016 // 4
four = [[w4, 3, [(0, 2), (1, -1), (3, -1)]], [w4, 3, [(0, -1), (1, 2), (2, -1)]], [w4, 3, [(1, -1), (2, 2), (3, -1)]], [w4, 3, [(0, -1), (2, -1), (3, 2)]]]
fp = b"".join(struct.pack("<IHH", w_, m_, len(e_)) + b"".join(struct.pack("<Ii", j_, z_) for j_, z_ in e_) for w_, m_, e_ in four)
fl = "YMROOMHDR|L=3x4|sector=Sx+Sy+|n=4|nl=24|rooms=16|entries=12|payload_bytes=%d|payload_merkle=%s|w_self_adjoint=PASS|json=0\\n" % (len(fp), merkle(fp))
case("D6_four_row_store_labelled_3x4", fl.encode().ljust(4096, b"\\0") + fp, {"exit": 0, "verdict": "PASS", "L": "3x4", "n": 4, "pairs": 4, "sum_w": 13060694016, "whole_space_count": "PASS", "header_entries": "PASS", "merkle": "PASS"})
# D7: a doubled lower entry"""
assert a in s
s = s.replace(a, b)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
