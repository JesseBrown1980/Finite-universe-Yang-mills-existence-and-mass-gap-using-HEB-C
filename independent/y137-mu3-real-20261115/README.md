# #137: the real third moment, stage A

Stage A of the build agreed on #137 and #207: an independent Rust enumerator of the raw electric rows, checked
against the frozen 128-row audit of #196 and against the separately written Python rule, with planted faults and an
overflow-safe integer path. `real_mu3=NOT_COMPUTED`; the Wilson weight stays HOLD.

## The enumerator (`rust/src/main.rs`, Rust 1.81, clippy `-D warnings` clean, integers only)

Written from the public definition: S3 as the six permutations of (0,1,2) in lexicographic order, the periodic 3x4
lattice, an 11-link spanning tree, 13 kept links, the six global conjugations. A state is the smallest conjugate of
its 13 kept links; its address is that tuple as a base-6 number, first entry least significant. A raw move
multiplies one of the 24 links on the left by one of the 3 transpositions. It is a third implementation of the
rule, beside the original source and `independent_move_rule.py`.

## What was checked (`RESULT-STAGE-A.hbp`, `sh stage_a.sh GROUP-0.v1 WORKDIR`)

| Check | Result |
|---|---|
| Group 0 Q5 spool of #195: length, 435,324 records, SHA-256 `3f561c26...` | equal to the receipt |
| The 128 audited rows (every 3,000th record of group 0): complete destination-multiplicity maps | 128 of 128 equal to the Python rule |
| Orbit weight of those rows | 128 of 128 equal to the spool |
| Raw moves and genuine self loops in those rows | 9,216 and 0, as #196 recorded |
| 2,000 generated canonical states: complete maps, weight, magnetic number | 2,000 of 2,000 equal |
| Planted faults on a Rust row: a move folded into a self loop with 72 kept; a move omitted; a destination changed; the orbit weight changed | each REFUSED |
| 320-bit accumulator: sum and negated sum of 1,000 products `w a b` (a, b below 2^112, w below 2^40; the sum has 271 bits) | equal to Python integers |

## The integer path

The accumulators are 320-bit two's-complement integers (five 64-bit limbs). The bound comes from the data format:
an amplitude over b is below 2^82, so an amplitude is below 2^112; a product of two is below 2^224; times an orbit
weight (at most 6), a multiplicity (at most 72) and b = 10^9 or a diagonal below 2^40: below 2^273; over at most
2^31 terms: below 2^304. Every partial sum fits with 15 bits to spare. Products of two 128-bit values are formed
limb by limb; no intermediate exceeds its type.

## The benchmark

2,000,000 rows (144,000,000 raw moves) on one thread of the operator's laptop: see the `Y137_STAGE_A_BENCH` row.
The full pass is 1,339,058,880 raw moves.

## What stage A does and does not establish

It establishes that this enumerator reproduces the rule on the frozen audit rows and on generated states, and that
the wide integers are exact. Agreement of the row form and the paired-edge form in stage B will show the
aggregation is consistent; the identity of the signed K3, Q4 and Q5 amplitudes is a separate gate (their own
source hashes and reconstruction), as the second seat set out.
