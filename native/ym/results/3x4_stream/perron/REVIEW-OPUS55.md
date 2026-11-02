# Second-seat refutation of the two-sided Perron claims

Written by a separate seat (Claude Opus 5.5) on November 2, 2026, at the operator's word, with the 3×4 store off limits while certifying passes ran.
The text below is its final report, unchanged. Its scripts and its own solvers are in [`second-seat/`](second-seat/). What the author did about each finding is in
[`PERRON-TWO-SIDED.md`](PERRON-TWO-SIDED.md), section 6.

---

RESULT: every printed bound I could test holds. The defects are in wording, labels, provenance and out-of-range input. Worst first:

D1. **94.064904 has only the tool's own number behind it.** The doc says values come from the exact check. 93.718415, 94.002305 and 94.064904 come from perronritz only, and certify went to x3-b.bin. The new best is 94.065384: `CERTIFY_ROW|tool=perroncert_check|t_cert_milli=94065384|matches_grid=1`. check_d_strict was still running, with certify-strict.out empty at 14:43 local. The doc table is one row stale.

D2. **Broken links.** TWO-SIDED-SMALL.hbp and TWO-SIDED-3x4.hbp are absent next to the doc. The 3x4 file exists nowhere under p0-ball; SMALL is only in jump34/small.

D3. **`E_self_adjoint=PASS` prints with no comparison when k=1.** On a mutated real 2x2 store (row 1 column 2 z-1, diag+1, merkle fixed):
- one vector: exit 0, PASS
- two or three stored vectors: refused
- two vectors built proportional at that pair: PASS
- `check_d_strict --self-adjoint`: refuses
- `check_d_strict` without that flag, and `perroncert check`: exit 0
The stored vectors have 0 blind pairs among 1,178. The all-rows form carries this weight.

D4. **Section 2's "Products are checked and fail closed" holds for the W-weighted products only.** All three cases below exit 0:
- JB=340282366920938463463374607431768212 (1000*JB wraps to 544) on real 2x2: prints upper_milli=14736010; perroncert check wraps too.
- JE=10^32: LOWER and perroncert check both print -1757393161294822841211590954851; the exact value is -5258767442854788153626900616317121065.
- Crafted store (9000 repeats of z=-2^31, d=2^63-1): both print 10000000; the exact value is -1.78e38. check_d_strict refuses it.
Reach is under D4 in DERIVED below.

D5. **Section 6.1 "leaves the side from below untouched" holds for the Perron root of the store's matrix.** The step to E9 is interlacing, which needs symmetry, so both sides rest on the all-rows form.

D6. **Row and M labels can differ at a tie; the value stays equal.** Real 2x2, vector tie-d.bin (sha 316e36a6...), JB=8463, value 44220887 from both: `pass` gives row 54, M=4; `perroncert check` gives row 41, M=7. Natural ties in 544 tested pairs: 0.

D7. **"Least integer theta" fails for theta_1 < 0.** The tool prints 0: 1,109 fuzz rows, negative-diagonal stores only. Sound, since 0 >= theta_1.

D8. **Row support and provenance.**
- "Seven vectors": the receipt has 5 pairs (2 small, 3 on 3x3).
- "77 s" has no row.
- 76.409643 (M=20) and 76.448118 are absent from the rows; my rerun reproduces both.
- The JB=6000 and 4000 label match is on one vector.
- pass1.out came from perronritz.exe (cdddf4f2, source jump34/perronritz.rs.at-pin, sha 0fc0769b), but the doc links the later source (8aac0eff). pass, upper_side, forms_at, lower_side, Acc and run_pass are text-identical, and old and new outputs matched on 215 fuzz cases and 13 small passes.
- `jump`, which made x-93-937.bin, exists only in the pinned source.

CLAIM|id=C1|verdict=SURVIVED|attack=own reader, own exact inertia, Barta and Rayleigh; 3x4 from receipts and files only|evidence=2x2 exact inertia of W(H'-theta), n=204: theta 46467673 gives 0 negative, 46467674 gives 1, 46466823 gives 0, so ceil(lambda1)=46467674=printed upper. 2x3 lambda1 in [58443132,58443133], printed 58441733 and 58443134. 3x3 lambda1 in [76448397,76448398], perroncert check on my vector 76448397, printed 76448116 and 76448399. 2x2 at 17 couplings: bad=0|json=0
CLAIM|id=C2|verdict=SURVIVED|attack=1,500 synthetic stores through the pinned binaries against exact forms and a Sturm chain; 250 cases with sums past 2^128|evidence=16,829 UPPER rows: mismatch 0, unsound 0. 2,545 OPEN rows correct, 5,898 LOWER correct, 11 fail-closed refusals. 815 form rows past 2^127 and 2^128: mismatch 0. Wrap paths are D4|json=0
CLAIM|id=C3|verdict=SURVIVED|attack=section 3 line by line; exact rationals on 1,500 random Z-matrices (general, reducible, W-symmetric), every threshold order|evidence=57,968 steps, 11,060 with t_k>=mu: failures of identity, equation, positivity, monotonicity and value<=level all 0. The proof needs only t_k<lambda1|json=0
CLAIM|id=C4|verdict=SURVIVED|attack=every gamma rewritten as a vector and run through perroncert check, plus own Barta on 2x2 and 2x3|evidence=1,117 value rows and 322 OPEN rows: mismatch 0 in value, row or M; 611 negative values; perroncert refused all OPEN. x is the named divided difference exactly in all sets. 3x4 x3-b: grid = check = 94065384|json=0
CLAIM|id=C5|verdict=SURVIVED|attack=544 (JB,vector) pairs on 2x2, 2x3 and 3x3, including 79 envelope breaks|evidence=value mismatch 0, LOWER row mismatch 0, own mismatch 0. Label difference only at the crafted tie, D6|json=0
CLAIM|id=C6|verdict=SURVIVED|attack=own whole-space build on 2x2 and 2x3, lift at r0 != 9, direct level counts|evidence=see MEASURED|json=0
CLAIM|id=C7|verdict=SURVIVED|attack=exact recomputation from receipts; store-free pass over passA.bin and 7 vector files|evidence=see MEASURED. Row-support flags are D1, D2, D8|json=0
CLAIM|id=C8|verdict=SURVIVED|attack=any-d test with own and random vectors; mutated stores; hostile reading|evidence=any d>0 survives; objections below; 94.071171 rests on store=H plus the all-rows form|json=0

MEASURED
- **C6, whole space, own code.** 2x2 has 1,393 orbits, 2x3 has 47,449. Both have exactly 8 flats, diagonal 3nl, 0 flat-flat couplings, M>=3, and W-symmetry on all pairs. All 211 and 2,646 sector rows match the store exactly, and every class member gives the same row.
- **C6, lift.** Whole-space and sector ratios are exactly equal at every orbit, and the bound holds, at 84 (r0,r) pairs on 2x2 (r0 from 0.5 to 9) and 54 on 2x3.
- **C6, direct count (supporting: 200-bit fixed-point integer elimination, no interlacing).** Own 2x2 whole-space H at (r0,r)=(4,27),(5,12),(6,6),(9,9): exactly 8 levels below theta and 8 below 24+1e-6.
- **C7, receipts.** 120 UPPER and 32 LOWER rows recomputed: mismatch 0. 32 M values (3..36 without 5, 35), rows sum to 45,508,073 and equal PASSA_M_HIST. The r table is exact at 102061051, 93061051, 87122453, 79745170, 75745170, 71321650.
- **C7, crossing of 72.** Exact 1093567/180000=6.075372: value 71.99665 at r=6.075, 72.00565 at r=6.076.
- **C7, arithmetic.** s/d_max=5575.8155, floor gives 93955575. 24.033904 and 22.064904 are right; they appear only in your request, not in the doc, and 70.031 applies at r=9 only.
- **3x4, store-free.** Key table and vector files reproduce all 10 G and M forms of pass1.out exactly. Argmax row is 44742735 for all 7 vectors.
- **3x4, vector identity.** x3-a=(5d0-19d1+14d2)*8192+316 d2 and x3-b=(5d0-19d1+14conv)*8192 on all rows. Vector-only prediction gives 94064904 and 94065384 at that row, each also the minimum over all rows.
- **3x4, Ritz with no room read.** G plus the sum of w d gives 94071180 on the first three vectors (printed 94071176), and 94081866, 94073074, 94071775 for the pairs (printed 94081864, 94073069, 94071770). With the converged vector: 94071173.
- **Stores.** Own rebuild of all 288,645 rows of 3x3 from the definition: key, weight, M, entries mismatch 0. Exact W-symmetry on 15,408,669 entries: 0 bad. `fullrebuild` repeats this with 0 mismatches on 2x2, 2x3 and 3x3, and two negative controls exit 2.
- **3x3 couplings, own exact brackets, `perroncert check` printing the lower end.**
| r | lambda1 range | doc's lower bound | short by (J_E) |
|---|---|---|---|
| 4 | [53689314, 53689315] | | |
| 4.06 | [54114091, 54114092] | | |
| 5 | [59771910, 59771911] | 59.028025 | 0.744 |
| 6 | [64601090, 64601091] | 64.504251 | 0.097 |
  The route with E8<=54 ends between r=4 and r=4.06: no d can reach 54 at r=4. A vector solved at 4.06 extends the doc's "every r>=5" to r>=4.06. r=4 stays open for the gap and needs a lower E8 bound.
- **Reach of a better vector.** Own Chebyshev filter from uniform on 3x3: certified 76448396 at 400 matvecs, 76448397 at 800. On 3x4 each matvec is a store pass.

DERIVED
- **D4 reach.** At JE=1000 and modest JB, rows with check_d_strict's structure give sum|z|<=2^32, so every term stays under 2^116 for any i64 vector. The vectors behind the printed 3x4 numbers (d<=2^54) stay under 2^122 for any i32/u16 row content.
- **M>=3 on any torus.** Each link lies in 2 plaquettes, so the count a of odd plaquettes is even and M=2a+3b. That excludes M=1, 2 and 5, and excludes 35 with 12 plaquettes. Matches missing=[5,35].
- **Flat count.** Flat orbits are conjugacy classes of commuting pairs in S3: 3+2+3=8 on every periodic lattice. Row sums are unchanged by the lift at any r because the coupling enters only on the diagonal.

CONJECTURE
- lambda1(3x4) is about 94.0711 to 94.0712. On 3x3, vectors at comparable distance (75, 76, 76.3) overshoot ceil(lambda1) by 9 units, and the store-free span gives 94071173.

Hostile first objections
1. The upper side bounds lambda1(H'); E9 has a lower bound only. On 2x2, lambda1=46.467674 while 8 levels lie below 46.576171 and 9 below 46.578124 (own count).
2. store=H on 3x4 rests on samples (5,556 and 4,264 rows) plus row sums and the random form. A full rebuild is affordable, see below.
3. All of this is one finite lattice, as the doc says.
On "any d>0": the Barta proof is independent of provenance, and my own and random vectors all land at or below the level.
On "E_ab=E_ba plus the form": the form covers all rows, so it is enough at its stated false-pass chance. The chosen-vector test alone is what D3 shows.

NOT RUN (the store is off limits; commands ready, not executed)
- `D:/ym-3x4-room-run/p0-ball/perroncert.exe check seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector- 0 1000 9000 D:/ym-3x4-room-run/p0-ball/jump34/x3-a.bin` expects 94064904.
- Same tool, JB=7000, p34/d93000000.bin: expects 79745170, row 44743136, M=8.
- `C:/tmp/opus55/ym-two-sided/fullrebuild.exe 341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector- D:/ym-3x4-room-run/passA.bin 3 4 3` expects 45,508,080 rows and 0 mismatches, merkle PASS. Scaled from the 3x3 rate, about 3.7 hours at 3 threads. Any nonzero mismatch falsifies store=H.
Also not done:
- Bareiss on 2x3 and whole-space 2x2: too costly here. Exact Barta and Rayleigh decide instead.
- Exact all-pairs symmetry on 3x4: only the random form covers it.
- check_d_strict on x3-b: the author's run, still in progress.
New during this pass, outside these claims: JUMP.hbp has OUTSIDE_GO_RESULT and MY_ERROR rows on padding inside the payload, and PERRON-REVIEW.md was edited by the author.

Worktree and D:/ym-3x4-room-run untouched by me. Scripts and vectors are in C:/tmp/opus55/ym-two-sided/: c1_small.py, c1_inertia.py, c1_couplings.py, c2_fuzz.py, c2_wrap.py, c2_acc.py, c3_random.py, c4_grid.py, c4b_open.py, c5_coupling.py, c5b_tie.py, c6_lattice.py, c6_lift.py, c6_count.py, c7_receipts.py, c8_asym.py, own33.rs, own33_rebuild.rs, own34.rs, own34_post.py, fullrebuild.rs, tie-d.bin, own33-c2-i64.bin, own33-r406-i64.bin
