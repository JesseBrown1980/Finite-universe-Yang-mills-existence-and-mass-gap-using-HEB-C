# Writes hard/attack_gates.py from the part two script: the nine cases that passed by design there now want exit 2, and the count of exit 0 with a gate short of PASS covers all five gates.
import re
s = open("C:/tmp/opus55/allpairs-review-20261103/diff/attack_gates.py", encoding="utf-8").read().replace("\r\n", "\n")
for name in ["entries_moved_to_the_end", "fields_reversed", "crlf_line_end", "contradiction_after_the_newline", "look_alike_key_unread", "parts_with_no_equals_repeat", "same_sites_other_label", "bad_utf8_in_unread_value", "weights_times_6_label_1x5"]:
    a = 'case("%s", 0,' % name
    assert s.count(a) == 1, name
    s = s.replace(a, 'case("%s", 2,' % name)
a = 'e, c = f.get("header_entries", "-"), f.get("whole_space_count", "-")'
assert s.count(a) == 1
s = s.replace(a, a + '\n            five = [f.get(k, "-") for k in ("header_entries", "whole_space_count", "header_rooms", "padding", "store_identity")]')
a = 'if code == 0 and ("OPEN" in (e, c) or "FAIL" in (e, c)):'
assert s.count(a) == 1
s = s.replace(a, 'if code == 0 and any(x != "PASS" for x in five):')
a = 'rows.append((tool, cap or "default", code, f.get("verdict", "-"), e, c, f.get("rows_read", "-")))'
assert s.count(a) == 1
s = s.replace(a, 'rows.append((tool, cap or "default", code, f.get("verdict", "-"), e, c, f.get("rows_read", "-"), five[2], five[3], five[4]))')
a = "|rows_read=%s|four_runs_agree=%d"
assert s.count(a) == 1
s = s.replace(a, "|rows_read=%s|header_rooms=%s|padding=%s|store_identity=%s|four_runs_agree=%d")
m = re.search(r'% \(name, want, r\[2\], r\[3\], r\[4\], r\[5\], r\[6\], ', s)
assert m
s = s.replace(m.group(0), m.group(0) + "r[7], r[8], r[9], ")
s = s.replace("Tries to reach exit 0 on the corrected allpairs with a count gate at OPEN or FAIL, or with no rows read.", "Tries to reach exit 0 on the hardened allpairs with any of the five gates short of PASS, or with no rows read.")
open("C:/tmp/opus55/allpairs-review-20261103/hard/attack_gates.py", "w", encoding="utf-8", newline="\n").write(s)
