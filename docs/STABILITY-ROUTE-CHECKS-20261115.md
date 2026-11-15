# Stability route: three checks of November 15, 2026

Seat ACER-CLAUDE-FABLE52, at the operator's direction ("do all three steps in that order"). This note stands beside
[`YM_TOPOLOGICAL_STABILITY_PROOF.md`](YM_TOPOLOGICAL_STABILITY_PROOF.md), which is unchanged apart from a pointer to this note. Claims carry MEASURED, DERIVED, READ (taken from the
source of a published paper, with its line) or OPEN.

## 1. The region dictionary for odd sides and rectangles: MEASURED, 0 failures

[`check_bhm_dictionary_general.py`](check_bhm_dictionary_general.py) extends the dictionary of section 3 from even squares to any sides. Each direction is cut into intervals of 2 or 3
cells (an odd side needs one interval of 3), a site is a product of two intervals, and the assignment is one rule per direction: a plaquette goes to the block starting at its own
interval when it sits in the last cell of that interval and to the block before otherwise; a star goes to the block before its interval. On intervals of 2 this is the rule of the
first script.

| Family | Tori | Regions | Failed |
|---|---:|---:|---:|
| Even squares 8 to 40 (regression: the first script counts 38,352) | 17 | 38,352 | 0 |
| Odd squares 9 to 29, the interval of 3 at every x position | 198 | 211,222 | 0 |
| Rectangles, sides 8 to 22, every parity | 210 | 50,610 | 0 |
| Intervals of 3 only, and mixtures with several 3s | 12 | 3,760 | 0 |
| **Total** | 437 | **303,944** | **0** |

Red control: with the plaquette rule changed (`sabotage=first_cell`) all 303,944 regions fail. Rows in [`BHM-DICTIONARY-GENERAL-20261115.hbp`](BHM-DICTIONARY-GENERAL-20261115.hbp). This run was a
check written and run in one sitting; no prediction was frozen before it.

Two consequences for section 6 of the proof document:

- **The site norm grows on odd sides.** A 3 x 3 site holds 18 links, so the one-site perturbation has norm 6 x 18 = 108 lambda (72 lambda for a 2 x 3 site) where the even case has
  48 lambda. In the matching, J = 108 lambda e^mu on tori with an odd side.
- **Rectangles are a statement about the theorem as well.** The dictionary holds on Z_Kx x Z_Ky. Bravyi, Hastings and Michalakis state their theorem on a lattice of one linear size L;
  that their proof carries to Kx != Ky with L read as the shorter side is OPEN here (not read through).

## 2. r0 as a number: not obtainable by reading; the constants are existential

READ in the sources of arXiv:1001.0344 (the long proof) and arXiv:1001.4363 (the short proof), downloaded from arXiv on November 15:

- Theorem 1 of both papers says "there exist constants J0, c1 (and c2) > 0 depending only on mu and the spatial dimension D". Neither paper prints a value.
- In the long proof the constants are built from order-of-magnitude statements: the relative bound of a block-diagonal perturbation is "b = O(w q^2)" (its Lemma on block-diagonal
  stability, source lines 663 to 747); the flow that removes the off-diagonal part is controlled by "there exist constants c1, c2, c3" (lines 1099 to 1190), ending in
  J(n) <= J (J/J0)^(2^n) "for some constant J0 > 0"; the Lieb-Robinson step uses a velocity "bounded by 8 C0(1) K" with further unnamed constants (lines 1622 to 1802).
- The short proof assumes a gap of 1/2 along the path and improves it to 3/4, again with unnamed constants.

So r0 = 48 e^mu / J0 (and the K0 of the finite-size step) cannot be read off. A number needs every lemma of one of the two proofs redone with explicit constants. That is a project of
its own, and the number it yields is expected to be very large (CONJECTURE of the seat: far above every coupling certified in this repository). The statement of the proof document,
"r0 = 9 is not established", stands.

What is explicit and holds for every size today:

| Statement | Source | Growth with the side L |
|---|---|---|
| E9 - E8 >= J_B (2 - 6 L^2 / r), so >= J_B / 2 for r >= 4 L^2 | proof document, section 6 (DERIVED there) | quadratic |
| The two-number bound of `product_bound.py`, positive from r = 5.5, 7.125, 8.375, 9.875, 11.375, 12.875 on L = 3 to 8 | `VECTOR-BOUND.md` (MEASURED per size, exact rationals) | about 1.5 L + 1 |
| The hybrid certificate, per torus and coupling | `VECTOR-BOUND.md`; the batch of November 15 in `independent/hybrid-batch-20261115/` | per point |

The second row has not been proved as a formula in L; a proof that the two-number bound is positive for r >= 1.5 L + c on every L would replace the 4 L^2 of the finite-size step by a
linear law (OPEN, and within reach: the bound is a minimum of a linear form over each lump's constraints).

Why a product-form vector is not expected to give a size-independent r0 (a sketch; Barta gives E1 >= e0, and the size of E1 - e0 growing in proportion to nl is CONJECTURE, in line with the measured growth of the least r with L): with phi = eps^a eta^b positive on every configuration, the local energy at a flat configuration is
e0 = 3 nl (1 - eps^2) and at any other configuration it is e0 plus a positive excess that grows with the number of defects, so E9 >= e0 + gamma with gamma independent of size. But
E8 >= E1 > e0 by an amount proportional to nl, because the product form is not the exact vacuum. The difference of the two extensive quantities is what a stability theorem controls and
a few-number vector does not.

## 3. Terms that are not projectors: the long proof's hypotheses cover them

READ in arXiv:1001.0344, section 2 (source lines 351 to 388): the unperturbed Hamiltonian is H0 = sum over A in S(2) of G_A with the G_A pairwise commuting, positive semidefinite,
frustration free, and with smallest positive eigenvalue at least 1, "equivalent to G_A^2 >= G_A". Projectors P_A (zero space of G_A) and Q_A = I - P_A are then defined from G_A. This
is the form the proof document uses: its block terms have integer spectrum, zero on the local ground space, every other value at least 1.

READ in the proof of the central lemma (lines 670 to 747): the G_A enter through the projectors Q_A (the syndromes and the decomposition R_s) and through one inequality,
G <= H0^2, justified by "creating a defect costs at least a unit of energy". That uses G_A >= Q_A only. No upper bound on G_A is used there.

Scope of this check: the hypotheses, the main theorem and that lemma. The remaining sections of the long proof (the flow equations and the Lieb-Robinson part) were not read line by
line for a hidden use of G_A^2 = G_A; that stays OPEN, as the proof document already lists. The short proof (arXiv:1001.4363) states its H0 as a sum of commuting projectors only, so
the long proof is the one to cite for this model.

## What this leaves

| Item | Status |
|---|---|
| Dictionary on odd sides and rectangles | MEASURED, 303,944 regions, 0 failures |
| The theorem on rectangles (Kx != Ky) | OPEN |
| Non-projector terms | Covered by the stated hypotheses and the central lemma of the long proof; the rest of that proof not audited |
| r0 as a number | Not available without redoing a proof with explicit constants |
| A linear finite-size law | DERIVED later the same day: E9 - E8 > 0 for r >= 3L/2 + 6 on L x L, L >= 4 ([`LINEAR-FINITE-SIZE-LAW-20261115.md`](LINEAR-FINITE-SIZE-LAW-20261115.md)); draft for refutation |
| A reader outside the project | OPEN |
