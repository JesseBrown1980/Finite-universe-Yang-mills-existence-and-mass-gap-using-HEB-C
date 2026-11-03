# Review 3, verbatim

Relayed by the operator on November 2, 2026. The line breaks inside the formulas come from the copy that reached this seat.

---

Here is an independent second-seat mathematical and methodological review of the PR #79 (3×4 Perron / Barta bound) architecture based on your run records and the four review targets outlined in PERRON-REVIEW.md.

Switching from the 137-column 
LDL 
T
  Schur complement (roomschur) to a principal-compression Barta / Perron–Frobenius certificate (perroncert) on the 300 GB Host-8 store is a major methodological upgrade: it replaces 
O(Nb 
2
 ) fill-in factorization (and the 9 undecided pivots at 90M) with a fill-in-free 
O(nnz) matrix-vector pass (628 s to verify 45,508,080 rows).

Part 1: Audit of the Four Mathematical Links (What Holds vs. Where to Attack)
1. Principal Compression + Cauchy Interlacing + Barta's Inequality (SOUND)
Normally, Barta's inequality (the Collatz–Wielandt lower bound for a Z-matrix) can only lower-bound the ground state 
λ 
1

 , whereas you need a lower bound on the ninth state 
E 
9

  above the 8-state flat-vacuum manifold. Your compression trick bridges this cleanly:

Because the magnetic operator 
M=∑ 
p

 (2−χ(U 
p

 )) is strictly diagonal in the gauge-orbit basis, the 8 flat states (
M=0) are exact coordinate basis vectors.

Deleting the 
k=8 flat coordinate rows and columns produces a principal submatrix 
H 
′
  that remains a Z-matrix (
H 
ij
′

 ≤0 for all 
i

=j, verified by your check that no off-diagonal entry is positive).

By Cauchy's Interlacing Theorem for deleting 
k=8 rows and columns from a symmetric matrix 
H
~
 , the lowest eigenvalue 
μ 
1

 ( 
H
~
  
′
 ) of the compressed matrix satisfies:

λ 
1

 ( 
H
~
 )≤μ 
1

 ( 
H
~
  
′
 )≤λ 
1+8

 ( 
H
~
 )=E 
9

 
Combining Cauchy interlacing (
μ 
1

 ( 
H
~
  
′
 )≤E 
9

 ) with Barta's inequality (
μ 
1

 ( 
H
~
  
′
 )≥min 
h

  
d
~
  
h

 
( 
H
~
  
′
  
d
~
 ) 
h

 

  for any strictly positive vector 
d
~
 >0) chains both inequalities in the same direction:

E 
9

 ≥μ 
1

 ( 
H
~
  
′
 )≥ 
h
min

  
d
~
  
h

 
( 
H
~
  
′
  
d
~
 ) 
h

 

 =t 
cert

 
2. Non-Orthonormal Orbit Weights 
W 
1/2
  Cancellation (SOUND)
Item 2 in your PERRON-REVIEW.md asks whether the non-symmetric 
W-self-adjoint rows (
WH=H 
⊤
 W, where 
W=diag(w 
h

 ) are the u32 orbit weights in passA.bin) distort the principal compression or Barta's ratio. They do not:

Because 
W is strictly positive and diagonal, the coordinate projection 
P onto the 
M≥1 orbits commutes with 
W 
1/2
  (
PW 
1/2
 =W 
1/2
 P). Thus, the principal compression of the physical symmetric operator 
H
~
 =W 
1/2
 HW 
−1/2
  is identically 
H
~
  
′
 =(W 
′
 ) 
1/2
 H 
′
 (W 
′
 ) 
−1/2
 .

Defining the physical test vector as 
d
~
  
h

 = 
w 
h

 


 d 
h

 >0, the irrational 
w 
h

 


  factors cancel out of the Barta quotient on every row 
h:

d
~
  
h

 
( 
H
~
  
′
  
d
~
 ) 
h

 

 = 
w 
h

 


 d 
h

 
w 
h

 


 (H 
′
 d) 
h

 

 = 
d 
h

 
(H 
′
 d) 
h

 

 
This proves that checking 
min 
h

  
d 
h

 
(H 
′
 d) 
h

 

 ≥t 
cert

  directly on the unweighted store 
H 
′
  rigorously certifies the bound for the physical Hilbert-space operator 
H
~
  
′
  without any square-root rounding error.

3. The Whole-Space Lift (45,508,080 Store Rows 
→ 2,177,317,873 Full Orbits) (SOUND IF TWO INVARIANTS HOLD)
Your review guide notes that the lift from the 
S 
x
+

 S 
y
+

  store (45,508,080 rows) to the full gauge-invariant Hilbert space (2,177,317,873 orbits across all momenta and reflections) is the least-tested step. Mathematically, the lift works via group-constant extension, provided two specific invariants are explicitly stated in PERRON-BOUND.md:

How the lift works: Let 
G be the spatial lattice symmetry group (translations and reflections) acting as permutations on the 2,177,317,873 gauge orbits 
O. In a non-zero momentum or odd-reflection sector, the sector-projected matrix has negative/complex characters and is not a Z-matrix. However, every state in every momentum and reflection sector is an eigenvector of the unprojected full-space matrix 
H 
full

  on all 2,177,317,873 orbits.

When you delete all 
M=0 flat orbits from 
H 
full

 , the resulting matrix 
H 
full
′

  on 
O 
′
  is a Z-matrix. Lifting your positive certificate vector 
d 
h

 >0 from the 45,508,080 symmetry classes 
h∈O 
′
 /G to a 
G-constant vector 
D(ω)=d 
[ω]

 >0 on 
O 
′
  yields:

D 
ω

 
(H 
full
′

 D) 
ω

 

 = 
d 
[ω]

 
1

  
h 
′
 ∈O 
′
 /G
∑

 ( 
ω 
′
 ∈h 
′
 
∑

 (H 
full
′

 ) 
ω,ω 
′
 

 )d 
h 
′
 

 = 
d 
[ω]

 
(H 
′
 d) 
[ω]

 

 ≥t 
cert

 
The two invariants you must verify in PERRON-BOUND.md:

Complete 
M=0 Removal: Deleting the 
M=0 rows in the 
S 
x
+

 S 
y
+

  store removes the 
G-orbits of all 8 flat states of 
D(S 
3

 ) (since 
M is 
G-invariant, no 
M=0 flat state can hide in a non-trivial momentum/reflection sector outside those 
G-orbits).

No High-
M Truncation in the Store: The 45,508,080 rows in the store must span the entire 
S 
x
+

 S 
y
+

  orbit space up to the maximum magnetic energy 
M 
max

 =3×12=36, with no truncated boundary shell where electric flips are silently dropped.

4. Monotone Extension to All 
r≥9 (SOUND)
Because 
M is diagonal with 
M 
h

 ≥3 on every non-flat gauge-invariant row (confirming why your tightest row landed at 
M=3), keeping the exact same vector 
d>0 at any 
r≥9 gives:

d 
h

 
(H 
′
 (r)d) 
h

 

 = 
d 
h

 
(E 
′
 d) 
h

 

 +9M 
h

 +(r−9)M 
h

 ≥t 
cert

 (9)+3(r−9)
Combined with the coupling-independent flat-subspace bound 
E 
8

 (r)≤3×24=72J 
E

 , the bound 
E 
9

 (r)−E 
8

 (r)≥21.061051J 
E

 +3(r−9)J 
E

  holds for all 
r≥9.

Part 2: Four Specific Questions to Resolve Before Merging PR #79
Before you merge PR #79 into main, check these four items (these are the exact points an external referee will scrutinize):

Does 
E 
8

 ≤70.031J 
E

  at 
r=9 Bound All 8 Flat States or Only the 
(+,+) Flat States?

For all 
r≥9, using 
E 
8

 ≤72J 
E

  is unconditional because every vector in the 8-dimensional 
M=0 flat subspace satisfies 
⟨v,H(r)v⟩≤72J 
E

 ∥v∥ 
2
 .

For your tighter 
r=9 claim (
E 
9

 −E 
8

 ≥23.030J 
E

  via 
E 
8

 ≤70.031J 
E

 , rising to 
∼23.68J 
E

  after the 93.7 warm start), Courant–Fischer / Rayleigh–Ritz requires an 8-dimensional trial subspace 
V 
8

  whose maximum eigenvalue (the 8th Rayleigh–Ritz root, not the 1st) is at most 
70.031J 
E

 .

Check whether your ball upper bound 
70.031J 
E

  is the largest of the 8 dressed flat-cluster upper bounds across all flat sectors, or only the lowest symmetric flat state 
E 
1

 (+,+). If 
70.031J 
E

  is only 
E 
1

 (+,+) while the highest of the 8 dressed flat states sits closer to 
70.1–70.5J 
E

 , you must subtract the 8th dressed flat upper bound (not the 1st) when quoting 
E 
9

 −E 
8

 .

Exact Integer vs. Floating-Point Rounding in perroncert check and check_d_stream.py:

How are the entries of d93000000.bin (364 MB, 8 bytes per row across 45,508,080 rows) stored—as positive u64/i64 fixed-point integers or f64 floats?

If d is integer (u64/i64), verify that perroncert check and check_d_stream.py test the inequality in exact 128-bit integer arithmetic without floating-point division:

10 
6
 ⋅(H 
′
 d) 
h

 ≥⌊10 
6
 ⋅t 
cert

 ⌋⋅d 
h

 
If d is stored as f64, then IEEE-754 round-to-nearest in 
(H 
′
 d) 
h

 /d 
h

  can jitter by a few ULPs (
∼10 
−14
 ), and the checker must use directed downward rounding (fesetround(FE_DOWNWARD) or interval arithmetic) to be a strict mathematical certificate.

Independent Verification of passA.bin Against 
H (Item 1 of PERRON-REVIEW.md):

Uploading passA.bin (728 MB, 16 bytes per row: u64 base-6 gauge-fixed link key, u32 orbit weight, u32 magnetic number) to Hugging Face Jessedbrown/ym-3x4-room-store is the right move.

To close Item 1 in PERRON-REVIEW.md, include a small standalone Python script (verify_sample_rows.py) in PR #79 that takes random rows (plus the tightest row at 
M=3), decodes the u64 base-6 key into the 24 link elements of 
S 
3

 , applies all 
24×3=72 electric transpositions and 12 plaquette characters directly from the group multiplication table of 
S 
3

 , folds each target into its canonical 
G×S 
3
12

 -orbit key, and verifies that the resulting row matches the store row byte-for-byte.

Operational Gate on the 08:53 Check-In and 93.7 Warm Start:

Keeping PR #78 merged (ebfdd2f) and leaving PR #79 open while check_d_stream.py finishes and the 93.7 J_E warm start runs (WARM34.hbp, keeping d93000000.bin untouched) is clean release discipline.

If you paste the text of PERRON-BOUND.md (and the output of check_d_stream.py once your check-in fires), I will audit the exact equations and the 
E 
8

 ≤70.031J 
E

  ball derivation line by line so you have a complete second-seat sign-off before merging PR #79.
