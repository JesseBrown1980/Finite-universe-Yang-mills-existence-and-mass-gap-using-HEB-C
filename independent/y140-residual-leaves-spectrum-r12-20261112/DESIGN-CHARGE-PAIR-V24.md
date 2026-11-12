# Design note: a static charge pair on the 3x4 S3 lattice (V24)

Date 2026-11-12. Unit ACER-CLAUDE-FABLE52 (pid 61089a99becaa89b), directed by OP-JESSE ("attractor pair";
"you do the design and code reading for the charge pair, which costs no processor time").
Status: DESIGN ONLY. Nothing here has been run. Every derivation below is tagged CONJECTURE until a run or a
second seat checks it. Nothing at r = 9.

## 1. What the writer's Hamiltonian is (read from `floorcert` main.rs, MEASURED as code reading)

- Lattice: periodic 3 x 4, 12 sites, 24 links, 12 plaquettes. Link variable u_e in S3.
- H / J_E = 72 - T + r M on gauge orbits of link configurations.
  - T: the 72 moves "left-multiply one link by one of the three transpositions" (`local_moves`).
  - M: sum over plaquettes of 2 - chi(holonomy), i.e. 0 identity, 2 transposition, 3 three-cycle (`pcost`).
  - Gauge action: u_e -> g_s u_e g_t^-1 (`gauge`). States are functions constant on gauge orbits.
- The floor lane works on Q = non-flat orbits (M >= 1); moves into the 8 flat orbits are counted (`nflat`) and
  projected out. Classes = orbits modulo the 48 lattice symmetries.

## 2. The charge pair (CONJECTURE: derivation by this unit)

Put a static charge in the sign representation at site x and another at site y. Allowed states obey
psi(g.u) = sgn(g_x) sgn(g_y) psi(u).

1. No orbit is lost. A gauge transformation that fixes u has g_x conjugate to g_y (parallel transport), so
   sgn(g_x) sgn(g_y) = 1.
2. Let W(u) = product of sgn(u_e) over the links of a path from x to y. Then W(g.u) = sgn(g_x) W(u) sgn(g_y), so
   psi = W * phi with phi an ordinary gauge-invariant function. The charged sector is the uncharged orbit space
   with the Hamiltonian W H W.
3. M is diagonal, so it is unchanged. A transposition is odd, so a move on a path link flips W. Therefore

       H_charged = 72 + r M - T(links off the path) + T(links on the path).

   The charged problem is the same matrix with the sign of the off-diagonal entries reversed for the moves on the
   path links. Nothing else changes.
4. Two paths between the same sites differ by a closed loop; the two Hamiltonians are conjugate by the diagonal
   +-1 operator "sign of the holonomy of that loop", which is gauge invariant. Same spectrum.

## 3. Checks the build must pass before any number is read

- A. Empty path: the matrix equals today's, row hash included.
- B. Closed path around one plaquette (charges at the same site): spectrum identical to the uncharged one.
  This tests the sign bookkeeping with a known exact answer.
- C. Two different paths between the same two sites give the same lowest level.
- D. Comparison inequality: lowest level (charged) >= lowest level (uncharged) on the same space. (For a symmetric
  matrix, x^T A x >= |x|^T M(A) |x| where M(A) has the off-diagonal entries replaced by -|a_ij|; M(A) is the
  uncharged matrix.) A charged level below the uncharged one means a bug.

## 4. What changes in the machinery

- The floor certificate does NOT carry over. It relies on all off-diagonal entries having one sign (a positive
  vector, Collatz-Wielandt). With a path, signs are mixed. Check D gives a free lower bound (the uncharged floor)
  but no more than that.
- The 48 lattice symmetries reduce to those that map the pair and the path class to themselves (order 2 to 8).
  The class list must be rebuilt at the orbit level or with the reduced group.
- The flat orbits must be kept. The energy of the pair is E0(charged, all orbits) - E0(uncharged, all orbits);
  the floor lane's projection onto non-flat orbits answers a different question.
- Exact quantities available without a new theory: (i) exact rational Rayleigh quotients = upper bounds on the
  charged lowest level on the cutoff space; (ii) exact inertia counts of the cutoff matrix (as in count_v13.py)
  where the size allows; (iii) the comparison lower bound D. The effect of the cutoff on the charged level needs
  its own tail argument; until then results are "at cutoff m0", with the trend in m0 reported.

## 5. Separations that exist

On a periodic 3 x 4 lattice the distinct displacements are (0,1), (0,2), (1,0), (1,1), (1,2): steps 1, 2, 1, 2, 3.
There is no straight separation of 3. CORRECTION beside my earlier statement "separations of 1, 2 and 3 sites":
the three-step separation exists only as the diagonal (1,2).

## 6. What to expect (CONJECTURE; this corrects my earlier "energy rises with separation")

- In the electric-dominated regime (small r) the link energies of 72 - T are 0 (no flux), 3 (two-dimensional
  flux), 6 (sign flux). A sign-charge pair needs sign flux across every cut between the charges: cost about 6 per
  step, linear in separation (confinement).
- At large r the magnetic term dominates. Finite-group gauge theories in two space dimensions have a deconfined
  phase there: the pair energy should level off with separation.
- r = 12 is on the magnetic side (the non-flat floor is near 72 + 12 * 2.7). So at r = 12 the more likely outcome
  is a pair energy that depends weakly on separation. Which side r = 12 and r = 9 fall on for this Hamiltonian is
  not known to me; the run measures it.
- The sharp test is the comparison of a small r with a large r. Small r is outside the floor lane's whitelist
  (r in {21/2, 12, 14} or r >= 20). The whitelist exists to protect the r = 9 prediction; using r < 8 for this
  separate test is the operator's decision.

## 7. Open choices for the operator

1. Charge type. Sign charge (this note): scalar problem, one sign flip rule, cheapest. Two-dimensional charge:
   the "fundamental" one with the cheaper string (3 per step), but the states carry 4 components and the build is
   several times larger. Recommendation: sign charge first.
2. Couplings: r = 12 and r = 20 (allowed now); add r = 1 or 2 if the operator permits small r for this test.
3. Cutoffs 5, 6, 7 first (small), then 8, 9 if the trend needs it.

## 8. Runs that would measure each conclusion

| Claim | Run |
|---|---|
| 2.3 sign-flip rule | checks A, B, C |
| comparison inequality | check D at every cutoff |
| pair energy vs separation | lowest level at the five displacements, cutoffs 5-7, r = 12 and 20 |
| confinement at small r | same at r = 1 or 2 (needs the operator's word) |

Predictions are to be sealed in SPEC-CHARGE-V24.hbp before the first run. Review of sections 2 and 3 by a second
seat (opus55 or GPT-6) is requested before building.

## 9. Review by the verifier seat (opus55), 2026-11-12, reading only, no computation (CONJECTURE until run)

Kept beside the text above; nothing above is rewritten.

- 2.1 no orbit excluded: HOLDS.
- 2.2-2.3 sign-flip rule: HOLDS with four conditions for the build:
  (a) "on the path" means links used an odd number of times;
  (b) moves that land back in the same orbit sit on the diagonal and take the on/off sign too;
  (c) the writer's `canon()` (48 symmetries x 6 conjugations) is not valid here; reduce by the gauge orbit only,
      and record for every move, including two-step tail moves and flat moves, whether its link is on the path;
  (d) the lattice symmetry is reduced to the stabilizer of the pair, which acts with sign factors; the charged
      matrix has mixed signs, so there is no argument placing the lowest state in the invariant sector: every
      one-dimensional sector of that group must be computed, or no reduction used.
- 2.4 path independence: HOLDS, loops around the torus included.
- 3.D comparison: HOLDS; wording corrected: with on-path self-moves the comparison matrix is not literally the
  uncharged matrix, but the inequality still holds. Compare like with like (all sectors on the same orbit set).
- 4: the note UNDER-claimed. The tail lower bound carries over through |x|, and the Schur step holds with signed
  couplings, so an exact inertia count of the signed core matrix gives a rigorous lower bound with the tail
  included. The Collatz-Wielandt step on the core does not carry over, as stated. Keeping the flats is correct.
- 6 expectation: OVERSIMPLIFIED, with a blocking point. Link costs 0 / 3 / 6 are right and the pair energy at
  r = 0 is exactly 6 x (graph distance). But at small r the ground state is spread over all magnetic numbers
  (mean about 24 of 36), so the low-cutoff spaces (cutoffs 5 to 9) CANNOT measure confinement. The small-r test
  needs the electric basis, perturbation theory, or the exact r = 0 check. At large r the leading effect is local
  and small, roughly 0.001 J_E at r = 12 (rough count), so a positive pair-energy claim needs enclosures narrower
  than that, formed as lower(charged) - upper(uncharged) and upper(charged) - lower(uncharged). A difference of
  two upper bounds bounds nothing.

Consequences for the plan: build at the gauge-orbit level with per-move path flags; no small-r run in the
magnetic cutoff basis; at r = 12 and r = 20 the target is a two-sided enclosure of a small pair energy.
