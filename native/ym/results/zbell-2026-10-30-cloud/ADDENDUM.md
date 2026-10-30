# zbell addendum, written and sealed before any code ran

PREREG.md is internally inconsistent. Its Z-T model text says B = -A everywhere for (a,b) = (1,1),
which gives E(1,1)n = -486, while P4 assumes E(1,1)n = -342. As written, Z-T gives
S*n = 3*342 + 486 = 1512, and 1512^2 = 2,286,144 > 1,889,568 is above the quantum bound.
The original P4 stays as frozen and is run against the model exactly as written; it is expected to FAIL.

Added, not replacing anything:
- Z-T2: as Z-T, but for (1,1) B = -A except on lambda < 72, where B = A, so E(1,1)n = -342.
- P4b: Z-T as written gives S*n = 1512, above the quantum bound, no-signalling exact.
- P4c: Z-T2 gives S*n = 1368, above 972 and within the quantum bound, no-signalling exact.
