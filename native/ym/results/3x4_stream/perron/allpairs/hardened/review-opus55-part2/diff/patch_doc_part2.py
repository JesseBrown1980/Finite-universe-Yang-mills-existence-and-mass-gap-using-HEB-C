p = "C:/tmp/opus55/allpairs-review-20261103/ALLPAIRS-REVIEW-DIFF.md"
s = open(p, encoding="utf-8").read()
def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b)
rep("Recipe: three findings below |", "Recipe: R1 to R3 below |")
rep("- `d78f263f…` and `cdb22218…` differ by 24 bytes, as recorded. The third build, `9bc0675a…`, is off this machine's run folders I read, so its 20 bytes are NAMED.", "- `d78f263f…` and `cdb22218…` differ by 24 bytes, as recorded ([`diff/out/build-bytes.hbp`](diff/out/build-bytes.hbp)). The third build, `9bc0675a…`, stayed out of reach under `D:/ym-3x4-room-run/p0-ball`, so its 20 bytes are NAMED.")
rep("**What the judge and the recipe cannot show.** MEASURED by passing cases:", "**What the judge and the recipe cannot show.** MEASURED in the same file:")
rep("| R6 | `PERRON-TWO-SIDED.md`, \"A replay compares the source hash and that normal hash\" |", "| R6 | `PERRON-TWO-SIDED.md:259`, \"A replay compares the source hash and that normal hash\" |")
rep("| R7 | The \"Corrected\" row of the table in `PERRON-TWO-SIDED.md` section 5, and the row above it |", "| R7 | `PERRON-TWO-SIDED.md:238-239` |")
rep("| R8 | `compare_pin_run.py:2`, `PERRON-TWO-SIDED.md` \"written while the run was going\" |", "| R8 | `compare_pin_run.py:2`, `PERRON-TWO-SIDED.md:268`, \"written while the run was going\" |")
rep("Same fix as the prediction rows: push before the run. Its soundness does not rest on the order, since the row-identity test was predicted first |", "Same fix as the prediction rows: push before the run. Its soundness is measured above and needs no order |")
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
