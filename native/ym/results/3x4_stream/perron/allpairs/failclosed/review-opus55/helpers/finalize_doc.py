# Fills the review's placeholders from the output files, once the bit flip run has ended.
R = "C:/tmp/opus55/allpairs-review-20261103/"
doc = open(R + "ALLPAIRS-REVIEW.md", encoding="utf-8").read()
sweep = [x for x in open(R + "out/sweep-2x2.err", encoding="utf-8").read().splitlines() if x.startswith("SWEEP_DONE")][0]
flip = open(R + "out/bitflip-2x2.err", encoding="utf-8").read().splitlines()
rows = [dict(y.split("=", 1) for y in x.split("|") if "=" in y) for x in flip if x.startswith("BITFLIP|")]
done = [x for x in flip if x.startswith("BITFLIP_DONE")][0]
d = dict(y.split("=", 1) for y in done.split("|") if "=" in y)
total = sum(int(r["flips"]) for r in rows)
exit0 = {r["field"]: int(r["exit0"]) for r in rows}
others = [k for k, v in exit0.items() if v and k != "mag"]
print("flips", total, "exit0", exit0, "panics", d["panics"])
if others:
    one = "Every bit of the 2×2 rows flipped, merkle repaired, %d flips: exit 0 in fields %s. " % (total, ",".join(sorted(exit0)))
else:
    one = "Every bit of the 2×2 rows flipped, merkle repaired, %s flips: only the %s bits of `mag`, which this test leaves unread, exit 0. " % (format(total, ","), format(exit0["mag"], ","))
table = "Every bit of the 2×2 rows, with the merkle repaired each time and the cap rotating through 470,000,000, 100 and 13 (`fuzz bitflip`, output [`out/bitflip-2x2.err`](out/bitflip-2x2.err)), %s flips, %s panics:\n\n" % (format(total, ","), d["panics"])
table += "  | Field | Flips | Exit 0 | Exit 1 | Exit 2 |\n  |---|---|---|---|---|\n"
for r in rows:
    table += "  | `%s` | %s | %s | %s | %s |\n" % (r["field"], format(int(r["flips"]), ","), format(int(r["exit0"]), ","), format(int(r["exit1"]), ","), format(int(r["exit2"]), ","))
table = table.rstrip("\n") + "\n"
for key, val in (("{{BITFLIP_ONE}} ", one), ("{{SWEEP_LINE}}", sweep), ("{{BITFLIP_TEXT}}", table)):
    assert key in doc, key
    doc = doc.replace(key, val)
a = "pass clean, and one changed value past the edge is one mismatch, named ([`out/stars.hbp`](out/stars.hbp), [`out/stars2.hbp`](out/stars2.hbp))."
assert a in doc
doc = doc.replace(a, a + " A sector boundary inside a room, at sector length 4,099, passes clean.")
assert "{{" not in doc
open(R + "ALLPAIRS-REVIEW.md", "w", encoding="utf-8", newline="\n").write(doc)
print("filled")
