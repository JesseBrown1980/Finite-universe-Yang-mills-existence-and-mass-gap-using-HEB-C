p = "C:/tmp/opus55/allpairs-review-20261103/ALLPAIRS-REVIEW.md"
s = open(p, encoding="utf-8").read()
a = "Claims carry MEASURED, NAMED or CONJECTURE. Every run has its prediction beside its outcome in [`REVIEW.hbp`](REVIEW.hbp), with timestamps this seat wrote."
b = "Claims carry MEASURED, NAMED or CONJECTURE. Each tool run has its prediction beside its outcome in [`REVIEW.hbp`](REVIEW.hbp), with timestamps this seat wrote, and a `NOTE` row names the read-only lookups."
assert a in s
s = s.replace(a, b)
a = "- **Every bit.** Every bit of the 2×2 rows, with the merkle repaired"
b = "- **Every bit.** Each bit of the 2×2 rows, with the merkle repaired"
assert a in s
s = s.replace(a, b)
a = "Every bit of the 2×2 rows flipped, merkle repaired, 180,352 flips: only the 3,376 bits of `mag`, which this test leaves unread, exit 0."
b = "All 180,352 bits of the 2×2 rows flipped, merkle repaired: only the 3,376 bits of `mag`, which this test leaves unread and `fullrebuild` reads, exit 0."
assert a in s
s = s.replace(a, b)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
