# T1: universal against non-universal on finite S3 tori (predictions only)

2026-11-09 · lane T1 · written before any measurement on the ten tori. No exact
diagonalization, no Feshbach run and no plaquette curve was computed on any of them.
The only torus computation is a two-move path count on the 2x2 torus (section 7),
which the brief allows as a smallest-case check.

**Tags.** DERIVED: proved in this note. CONJECTURE: not proved here. REPORTED: read in a
source I opened, cited in place. OPEN: not predicted. Nothing here is MEASURED.

**Sources opened (read only).**
[S1] `docs/YM_TOPOLOGICAL_STABILITY_PROOF.md`, finite-universe repo, origin/main `6a7fc747`.
[S2] `independent/FINITE_3X4_S3_FIRST_GAP_LARGE_R_20261108.md` (#143), HEAD `cbd8b70d`.
[S3] `docs/FINITE_S3_FIRST_GAP_AND_TERNARY_SCHUR.md`, origin/main `6a7fc747`.

---

## 0. Results in brief

Write Lmin = min(Lx, Ly), Llong = max(Lx, Ly), m = Lmin, and
kappa_m = binom(2m-2, m-1) / 4^(m-1), so kappa_2 = 1/2, kappa_3 = 3/8, kappa_4 = 5/16.

**(a) Universal, every torus (DERIVED).** There are 8 flat gauge orbits, with weights
(1,3,2,3,3,2,2,2). They span the zero space of M on gauge-invariant states. PTP = 0,
so PHP = 6LxLy·I_8.

**(b) Splitting of the eight lowest levels (DERIVED).** Through order r^-(m-2), the 8x8
effective Hamiltonian is a multiple of I_8. At order r^-(m-1) it is not:

  Sigma = sigma·I_8 + r^-(m-1)·C + O(r^-m),
  C = kappa_m · [ Ly·Gamma_V·[Lx = m] + Lx·Gamma_H·[Ly = m] ].

Gamma_V and Gamma_H are fixed rational 8x8 matrices, listed in section 3.8. Both have
spectrum {3, 1, 0, 0, 0, 0, -1, -3}. Gamma_V + Gamma_H has spectrum
{sqrt14, sqrt6, 0, 0, 0, 0, -sqrt6, -sqrt14}. E_i = 6LxLy - eps_i, and the gaps
eps_i - eps_j equal r^-(m-1)(mu_i - mu_j) + O(r^-m), with mu sorted from the top of C.

| torus | order of first splitting | C | E2 - E1 (leading) |
|---|---|---|---|
| 2x2 | r^-1 | Gamma_V + Gamma_H | (sqrt14 - sqrt6)/r ≈ 1.292168/r |
| 2x3 | r^-1 | (3/2) Gamma_V | 3/r |
| 2x4 | r^-1 | 2 Gamma_V | 4/r |
| 2x5 | r^-1 | (5/2) Gamma_V | 5/r |
| 2x6 | r^-1 | 3 Gamma_V | 6/r |
| 3x3 | r^-2 | (9/8)(Gamma_V + Gamma_H) | (9/8)(sqrt14 - sqrt6)/r^2 ≈ 1.453689/r^2 |
| 3x4 | r^-2 | (3/2) Gamma_V | 3/r^2 (control: equals #143, [S2]) |
| 3x5 | r^-2 | (15/8) Gamma_V | (15/4)/r^2 |
| 4x4 | r^-3 | (5/4)(Gamma_V + Gamma_H) | (5/4)(sqrt14 - sqrt6)/r^3 ≈ 1.615210/r^3 |
| 4x5 | r^-3 | (25/16) Gamma_V | (25/8)/r^3 |

Yes, the order is min(Lx,Ly) - 1. For Lx != Ly the general law is
E2 - E1 = 2·Llong·kappa_Lmin·r^-(Lmin-1), and for Lx = Ly = L it is
L·kappa_L·(sqrt14 - sqrt6)·r^-(L-1).
The 2xL family splits at order 1/r for every L, with E2 - E1 = L/r, which grows linearly
in L. The mechanism is the same in every case. What is special about 2xL is that its
short side never grows. Every family with a fixed short side behaves the same way at
its own fixed order.

**(c) The gap above the band (DERIVED).** E9 - E8 = 3r + O(1/r) on all ten tori. The
leading term is uniform in torus size. The next term is also uniform once Lmin >= 3,
and it is not uniform on the thin tori:

| tori | E9 - E8 |
|---|---|
| 3x3, 3x4, 3x5, 4x4, 4x5 | 3r - 21/r + O(r^-2) |
| 2xL, L = 3..6 | 3r - (4L+57)/(2r) + O(r^-2): -69/2, -73/2, -77/2, -81/2 |
| 2x2 | 3r - (21 + 17·sqrt2/2 + sqrt14)/r ≈ 3r - 36.762473/r |

The universal content consists of the eight orbits and their weights, the normalized
spectrum of C (one shape for rectangles, one for squares), the gap 3r, and the number
21 for Lmin >= 3. The non-universal content consists of the order Lmin - 1, the
prefactor Llong·kappa_Lmin, and the thin-torus 1/r coefficients.

---

## 1. Model and conventions

- Periodic Lx x Ly torus with Lx, Ly >= 2. It has V = LxLy vertices, n = 2LxLy links
  and LxLy plaquettes. Link h(x,y) runs (x,y)->(x+1,y) and link v(x,y) runs
  (x,y)->(x,y+1). The plaquette holonomy is
  g_p(x,y) = h(x,y)·v(x+1,y)·h(x,y+1)^-1·v(x,y)^-1, with the product taken in path
  order. Every plaquette has four distinct links, and every link borders two distinct
  plaquettes. Both facts need Lx, Ly >= 2.
- T = {(12),(13),(23)}. A move (l,t) is L_t^l: g_l -> t·g_l. The operator T_op is the
  sum over all l and t of L_t^l, and H/J_E = 3n·I - T_op + r·M = 6LxLy·I - T_op + r·M.
  The "72" in the brief is 6LxLy on 3x4 (and on 2x6). On the other tori the constant is
  6LxLy. Every prediction is a difference, or is stated relative to 6LxLy, so the
  constant never matters.
- m_p = 2 - chi_std(g_p) = 3 - #fix(g_p), which takes the value 0, 2 or 3 on e, a
  transposition or a 3-cycle.
- Gauge action: g_l -> k_s(l)·g_l·k_t(l)^-1. The relation
  k·(t g)·k'^-1 = (k t k^-1)·(k g k'^-1) shows that a gauge transformation maps the move
  (l,t) to (l, k_s t k_s^-1). Since T is a conjugacy class, T_op commutes with gauge
  transformations, and so does M.
- Holonomy pair at a vertex (x,y): a is the holonomy around row y (horizontal links)
  starting at (x,y), and b is the holonomy around column x (vertical links).
- The eight flat classes, in the brief's weight order, are:
  F1 (e,e), F2 (e,T), F3 (e,C), F4 (T,e), F5 (T,T), F6 (C,e), F7 (c,c), F8 (c,c^-1).
  T means a transposition and C a 3-cycle. This is the "compatible eight-class order" of
  [S2]: its CA block is F1-F3, its CB block is F4-F5, and its zero block is F6-F8.
- Count form: A(i->j) is the sum of walk amplitudes from one representative
  configuration of orbit i into orbit j. In the orthonormal orbit basis the operator is
  W^(1/2)·A·W^(-1/2), with W = diag(weights). It has the same spectrum.

## 2. Part (a): the universal flat sector

**A1 (DERIVED).** M >= 0 and M is diagonal in configurations, with m_p = 0 iff g_p = e.
So the zero space of M on gauge-invariant functions is spanned by the indicator
functions of gauge orbits of flat configurations, one orbit state per orbit.

**A2 (DERIVED).** Gauge-fix a spanning tree to e. A flat configuration is then fixed by
its based holonomy pair (a,b). The pair commutes, and every commuting pair occurs (the
standard flat connection to Hom(pi_1, G) correspondence). The residual gauge freedom is
global conjugation. S3 has 18 commuting pairs (= |G|·#classes = 6·3), which fall into 8
conjugation orbits. The orbit of (a,b) has size w = 6/|C(a,b)|, where C(a,b) is the
joint centralizer:

  (e,e): w = 1. (e,T), (T,e), (T,T): w = 3. (e,C), (C,e), (c,c), (c,c^-1): w = 2.

So the weights are (1,3,2,3,3,2,2,2) in the order F1..F8. The full gauge orbit sizes
are 6^(V-1)·w. None of this depends on Lx or Ly. The eight states are the D(S3) ground
space, the common zero space of the quantum-double terms ([S1] section 2, REPORTED: there
it is checked exactly by `flatcomp` on 2x2, 2x3, 2x4, 2x5 and 3x3).

**A3 (DERIVED).** One move changes the two plaquettes of its link, which are distinct,
from e to a transposition. So every single-move neighbour of a flat state has M = 4.
There are 3n = 6LxLy such moves. Hence P·T_op·P = 0 and P·H·P = 6LxLy·I_8.

**A4 (DERIVED).** Every nonflat configuration has M >= 3. The argument follows [S2]. Under
sign: S3 -> {±1}, the product of all plaquette signs is +1, so transposition plaquettes
come in even numbers and cost >= 4. One 3-cycle plaquette costs 3. M = 3 is attained, as
section 4.1 shows.

## 3. Part (b): where the eight-fold degeneracy first breaks

### 3.1 The Schur equation and its walk expansion

Put lambda = 6LxLy - eps and D = r·M_Q (M_Q >= 3 on Q = I - P). The Feshbach/Schur
equation on P is

  eps·psi = Sigma(eps)·psi,  Sigma(eps) = P T Q (D - T_Q + eps)^-1 Q T P,
  with T_Q = Q T_op Q,

which expands as the convergent series
Sigma(eps) = sum_k P T [D^-1 (T_Q - eps)]^k D^-1 T P for r large on a fixed torus.
Multiply out the products. Each term is (-eps)^i times a sum over walks of j = k - i + 2
moves from P to P, with every intermediate state nonflat. The weight of a walk is a
product of factors 1/(r·M(state)), with one extra factor for each eps insertion, so it is
a function of the sequence of intermediate magnetic energies alone. A walk of j moves
contributes at order r^-(j-1), and every eps insertion adds an order of
eps/r = O(r^-2).

Since dSigma/deps = -P T Q R^2 Q T P <= 0, with R = (D - T_Q + eps)^-1 > 0, Sigma(eps)
is non-increasing in eps. Each of its eight eigenvalue branches nu_i(eps) therefore
meets the line nu = eps exactly once. Those eight roots are the eight lowest physical
levels: QHQ >= 3n - ||T_Q|| + 3r >= 3r, so Cauchy interlacing gives E9 >= 3r, while
min-max with PHP = 3n gives E8 <= 3n. The band is isolated once r > 2LxLy, as in [S2].

### 3.2 Short flat-to-flat walks

A row is the cycle of horizontal links h(·,y), and a column is the cycle of vertical
links v(x,·). A *straight line* is a full column of horizontal links {h(x,y): y} (Ly links,
which needs Ly = Lmin) or a full row of vertical links {v(x,y): x} (Lx links, which needs
Lx = Lmin).

**B1 (DERIVED).** Let W be a walk of k <= Lmin moves from a flat f to a flat f'', and let
S' be the set of links whose net factor is not e. Then exactly one of the following holds.

- (i) Some row and some column avoid S'. Then the holonomy pair based where they cross
  is unchanged, so [f''] = [f].
- (ii) k = Lmin, and W moves each link of a straight line exactly once. Then [f''] !=
  [f].

*Proof.* At most s'_h rows and at most s'_v columns meet S', with s'_h + s'_v <= k <= Lmin.
If (i) fails then, say, s'_h >= Ly. That forces s'_h = Ly = Lmin = k and s'_v = 0, so
there is one horizontal link per row, each moved once. Plaquette (x_y, y) has its bottom
link moved, its sides unmoved, and its top link moved only if x_(y+1) = x_y. Flatness
then forces a single column. For the class change in (ii), every row crosses the column
once, so sgn(a) flips. Conjugation preserves the sign, so the class changes. The case of
a row of vertical links is the same with sgn(b). ∎

### 3.3 Locality: only walks that wrap the torus can see the class

For a link set S, the incidence multigraph I(S) has vertex set S and one edge
{l, l'; p} for every plaquette p that contains both l and l'. A closed walk in I(S)
defines a closed torus path: join the source vertices s(l_i) -> s(l_(i+1)) along ∂p_i.

**B2 (DERIVED).** Suppose every closed walk of I(S) gives a contractible torus path. Then
for every flat f there is a bijection of label sequences, t_i -> k_(l_i)·t_i·k_(l_i)^-1,
with the following property. After every prefix of moves, the plaquette holonomy classes
reached from f equal those reached from the trivial configuration e by the relabelled
sequence. In particular, all magnetic energies agree.

*Proof.* Let u_i be the transport along ∂p, in f, from the base point of p to s(l_i). This
is well defined because p is flat. Write tau_l for the product of the labels applied to l
so far. Then the holonomy of p after the moves is the product, in boundary order, of
u_i·tau_(l_i)^(±1)·u_i^-1. For a link traversed backwards, the prefix ends at s(l), so the
same formula holds. Its class depends only on the relative transports
P_p(s(l) -> s(l')) = u_l^-1·u_l'. Treat these as a connection on I(S). Every cycle of I(S)
then carries the holonomy of f around a contractible torus path, which is e, so frames
k_l exist with P_p(s(l) -> s(l')) = k_l^-1·k_l' on every edge. Substituting gives the
class of the product of k_l·tau_l^(±1)·k_l^-1, which is the trivial configuration's
value under the relabelling. The relabelling is a bijection of T on each move, and it is
consistent on repeated moves of one link. ∎

**B3 (DERIVED).** If some closed walk of I(S) gives a non-contractible path, then
|S| >= Lmin. If |S| = Lmin, then S is a straight line.

*Proof.* The four links of plaquette (x,y) have sources (x,y), (x+1,y), (x,y+1) and (x,y).
A step between two links of one plaquette therefore moves the source by one of
0, ±(1,0), ±(0,1), ±(1,-1). Lift to Z^2. A non-contractible closed walk returns displaced
by (wx·Lx, wy·Ly) != 0. Since |dx|, |dy| <= 1 per step, it has >= Lmin steps. Splitting at
repeated vertices leaves a simple non-contractible cycle, so |S| >= Lmin.

Now take the equality case with Lx < Ly. The winding is (±1, 0), and every step has
dx = +1, say. Such steps are (1,0), from h(x,y) or v(x,y) to v(x+1,y), and (1,-1), from
h(x,y+1) to v(x+1,y). Both end on a vertical link, so every vertex of the cycle is
vertical. From v(x,y), the only dx = +1 step goes to v(x+1,y). So S is a row of
vertical links.

For Lx = Ly, a diagonal winding would need every step to be (1,-1) (or every step
(-1,1)). But (1,-1) steps only go horizontal to vertical, and no (1,-1) step leaves a
vertical link. Diagonal windings are therefore impossible. ∎

### 3.4 The theorem

**B4 (DERIVED).** Let m = Lmin. In the orbit basis,

  Sigma(eps) = sigma(eps, r)·I_8 + r^-(m-1)·C + O(r^-m)

uniformly for 0 <= eps <= 1. Here sigma is scalar, and C collects the straight-line walks
of exactly m moves, with no eps insertion. For m >= 3, sigma = (3LxLy/2)/r + O(r^-2). For
m = 2 the scalar part at order 1/r is the same, 3n/4 = 3LxLy/2.

*Proof.* Take a link sequence of k <= m moves with link set S. If I(S) has no
non-contractible cycle, B2 maps its walks from f, bijectively and with equal energies,
onto walks from e. By B1(i), applied to both, flat-to-flat walks of this kind keep the
class, so they contribute delta_([f],[f'']) times a number that does not depend on f.
If I(S) has a non-contractible cycle, then by B3 we have |S| = m = k: a straight line,
each link moved once. These are the walks of B1(ii). They only change the class (zero
diagonal), and they enter at order r^-(m-1). With an eps insertion they enter at order
r^-(m+1) or later. Walks of more than m moves are O(r^-m). At order 1/r, every one of
the 3n first moves returns by its own inverse with M = 4, which gives 3n/4. ∎

**Corollary (DERIVED).** Let mu_1 >= ... >= mu_8 be the eigenvalues of C. Put
g(eps) = eps - sigma(eps), so g' = 1 + O(r^-2). By Weyl's inequality,
eps_i = sigma(eps_i) + r^-(m-1)·mu_i + O(r^-m). Hence

  E_j - E_i = eps_i - eps_j = r^-(m-1)·(mu_i - mu_j) + O(r^-m),

and in particular E2 - E1 = (mu_1 - mu_2)·r^-(m-1) + O(r^-m). C is nonzero and has zero
diagonal, so the effective 8x8 Hamiltonian stops being scalar exactly at order
r^-(m-1) = r^-(min(Lx,Ly)-1).

### 3.5 The straight-line amplitude

**B5 (DERIVED).** Let Lambda = (l_0, ..., l_(m-1)) be a straight line, with chain
plaquettes p_i between l_i and l_(i+1) (indices mod m). For m = 2 the two links share both
plaquettes.

- *Labels.* A walk ends flat iff, for each i, the label on l_(i+1) is the transport of the
  label on l_i through p_i. For a row of vertical links, plaquette (x,y) is flat after the
  moves iff t_(x+1) = h(x,y)^-1·t_x·h(x,y). Around the line, this requires t_0 to commute
  with the holonomy h_Lambda of the cycle through the sources. That holonomy is a_y for a
  row of vertical links and b_x for a column of horizontal links. So there are
  |T ∩ C(h_Lambda)| flat-ending label sequences, one for each such t_0.
- *Energies.* Suppose the subset A of the line has been moved, with matching labels. A
  chain plaquette has trivial holonomy when both or neither of its links have moved, and
  a transposition holonomy when exactly one has. So M(A) = 2·|∂A| = 4·arcs(A), where
  arcs counts the runs of A on the cycle C_m.
- *Orderings.* The amplitude per valid t_0 is
  sum over the m! orderings of prod_(j=1)^(m-1) 1/(4r·arcs(A_j)), which equals
  N_m·(4r)^-(m-1).
- **N_m = binom(2m-2, m-1)** (the closed form, which gives kappa_m = N_m/4^(m-1)).
  By rotation, N_m = m·S_(m-1). Here S_n is the same sum for a path of n links in which
  the links are *removed* one at a time; it uses arcs(A) = runs(A^c) on a cycle. The
  product runs over the n nonempty sets, from the full path down to a single link.
  Removing first the link at position k splits the path into two independent paths of
  k-1 and n-k links, and their run counts add. The *shuffle identity*
  F(i,j) = [F(i+1,j) + F(i,j+1)]/(x_i + y_j), with F = X_i·Y_j and terminal energies 0,
  shows that summing over interleavings factorizes. So S_n = sum_k S_(k-1)·S_(n-k), with
  S_0 = 1, which is the Catalan recursion. Hence N_m = m·Cat(m-1) = binom(2m-2, m-1).
  The values are N_2..N_8 = 2, 6, 20, 70, 252, 924, 3432. Pre-freeze check P2 confirms
  these exactly, and P3 confirms N_2 = 2 on 2x2. ∎

### 3.6 The class action

**B6 (DERIVED).** A row of vertical links at height y changes the pair based at (0,y) by
(a,b) -> (a, t·b), with t in T ∩ C(a). There are Ly such rows when Lx = m. A column of
horizontal links changes the pair by (a,b) -> (t·a, b), with t in T ∩ C(b). There are
Lx such columns when Ly = m. Counting targets class by class gives Gamma_V and Gamma_H.
So

  C = kappa_m·[Ly·Gamma_V·[Lx = m] + Lx·Gamma_H·[Ly = m]].

On 3x4 this is (3/2)·Gamma_V. It reproduces [S2] entry for entry: CA = ((0,9/2,0),
(3/2,0,3), (0,9/2,0)), CB = ((0,3/2),(3/2,0)), and zero on F6..F8. That is the control.

### 3.7 Spectra

**B7 (DERIVED; check P1).** Gamma_V has characteristic polynomial x^4(x^2-1)(x^2-9),
with the blocks [[0,√3,0],[√3,0,√6],[0,√6,0]] → 0, ±3 on F1..F3, then ±1 on F4, F5, and 0
on F6..F8. Gamma_H is the same up to the swap a <-> b. Gamma_V + Gamma_H has characteristic
polynomial x^4(x^4 - 20x^2 + 84) = x^4(x^2-6)(x^2-14). Split it under a <-> b.

- The swap-even part is a star centred on (F2+F4)/√2, with edges √6 to F1, √6 to
  (F3+F6)/√2 and √2 to F5, giving eigenvalues ±√14, 0, 0. F7 and F8 contribute two
  more zeros.
- The swap-odd part is [[0,√6],[√6,0]], on (F2-F4)/√2 and (F3-F6)/√2.

Every spectrum is symmetric about 0. Gamma_V flips sgn(b) and Gamma_H flips sgn(a), so C
is bipartite with respect to sgn(a)·sgn(b).

### 3.8 The matrices (count form, row = source, column = target, order F1..F8)

  Gamma_V: F1>F2 3, F2>F1 1, F2>F3 2, F3>F2 3, F4>F5 1, F5>F4 1, all other entries 0.
  Gamma_H: F1>F4 3, F4>F1 1, F4>F6 2, F6>F4 3, F2>F5 1, F5>F2 1, all other entries 0.

Both satisfy detailed balance with the weights: w_i·A_ij = w_j·A_ji.

### 3.9 Consequences

- Rectangular tori (Lx != Ly). Let s = Llong·kappa_Lmin. Then the leading pattern is
  E1..E8 = Ebar - s·(3, 1, 0, 0, 0, 0, -1, -3)·r^-(Lmin-1). So E2 - E1 = 2s, E3 - E2 = s,
  E3 = E4 = E5 = E6, E8 - E1 = 6s, and (E3-E2)/(E2-E1) = 1/2.
- Square tori (L x L). Let s = L·kappa_L. The pattern is
  s·(√14, √6, 0^4, -√6, -√14). So E2 - E1 = s(√14 - √6),
  (E3-E2)/(E2-E1) = (√21+3)/4 ≈ 1.895644, and E8 - E1 = 2√14·s.
- Ebar, the mean of E1..E8, is 6LxLy - (3LxLy/2)/r + O(r^-2) on every torus, because C is
  traceless. For Lmin >= 3, all eight levels individually equal
  6LxLy - (3LxLy/2)/r + O(r^-2).
- Symmetry sectors. On square tori the E2 eigenvector is odd under the diagonal
  reflection x <-> y. A computation restricted to the swap-even sector would therefore
  report a second level at mu = 0, with E2_even - E1 = s·√14: √14/r on 2x2,
  (9/8)√14/r^2 on 3x3, (5/4)√14/r^3 on 4x4. Under x -> -x, F7 and F8 trade places
  ((c,c) -> (c^-1,c), which is conjugate to (c,c^-1)). So the odd state F7 - F8 sits at
  mu = 0, and a reflection-even sector holds only 7 of the 8 band states. All eight
  states have zero momentum.

### 3.10 Thin tori

2xL splits at order 1/r for every L, with C = (L/2)·Gamma_V and E2 - E1 = L/r. The band
width E8 - E1 is 3L/r. The order is fixed and the coefficient is extensive in the long
direction. This is the thin-torus behaviour that [S1] section 6 cautions about (REPORTED
there via Klich, arXiv:0912.0945, which I did not open). The derivation above is my own
and makes no use of that caution.

The same holds for every fixed short side. 3xL splits at r^-2 with E2 - E1 = (3L/4)/r^2,
for L >= 4. Exponential suppression, about Llong·(4r)^-(Lmin-1)·binom(2Lmin-2,Lmin-1),
appears only when both sides grow. In the owner's frame, the eight-fold "continuous"
degeneracy is exact up to resolution r^-(Lmin-2) and breaks at the computable order
r^-(Lmin-1), with a computable coefficient. The shape of the break is universal and its
scale is not.

## 4. Part (c): the gap above the band

### 4.1 The M = 3 manifold (DERIVED)

M = 3 means exactly one plaquette p0 carries a 3-cycle and every other plaquette is flat.
Remove p0 and the surface is a punctured torus. The configurations are flat connections
on it with boundary holonomy [A,B]. Flat connections mod gauge correspond to pairs (A,B)
in G^2 mod conjugation, and [A,B] is a 3-cycle iff A and B do not commute. There are 18
such pairs, and the conjugation action on them is free. That gives 3 orbits for each p0,
labelled TT = (sgnA, sgnB) = (-,-), TC = (-,+) and CT = (+,-). The sign field is flat
because sgn(3-cycle) = +, so these labels are global invariants. In total the M = 3
manifold has dimension 3LxLy. Check P1 confirms the orbit count and the labels, and P3
confirms them on 2x2.

### 4.2 First order vanishes (DERIVED)

A move on a link of ∂p0 takes p0 to a transposition and creates one transposition next
door, so M = 4. A move elsewhere creates two transpositions, so M = 7. So P3·T·P3 = 0,
and the first-order energy is 3r + 6LxLy. The flat band's first-order energy is 6LxLy, so
E9 - E8 = 3r + O(1/r) on every torus, uniformly.

### 4.3 Second order for Lmin >= 3 (DERIVED)

Here E = 3r + 6LxLy - K/r + O(r^-2), with K = P3 T Q (M-3)^-1 Q T P3.

- *Returns.* The 12 moves on ∂p0 have denominator 1 and the other 3n - 12 have
  denominator 4. That gives D0 = 12 + (3n-12)/4 = 3LxLy/2 + 9.
- *Hops.* Take the first move (l,t) on a link l in ∂p0. The second move on l must undo
  p0, and exactly one label does so: it is c^-1·t in the frame of p0. The net effect is
  that a 3-cycle multiplies l and the flux moves across l. That gives 3 hops per link,
  each of weight 1, and every hop keeps (sgnA, sgnB).
- No other two-move process returns to M = 3. The second move must repair both nonflat
  plaquettes, and when Lmin >= 3 only the first move's own link touches both.

So K = (3LxLy/2 + 9)·I + 3·A_plaq ⊗ I_3, where A_plaq is the adjacency of the Lx x Ly
plaquette torus. This gives

  E(k, s) = 3r + 6LxLy - [3LxLy/2 + 9 + 6cos(2πkx/Lx) + 6cos(2πky/Ly)]/r + O(r^-2).

The lowest level is threefold, one state per s, at k = 0:
E9 = E10 = E11 = 3r + 6LxLy - (3LxLy/2 + 21)/r. Therefore

  **E9 - E8 = 3r - 21/r + O(r^-2)** on 3x3, 3x4, 3x5, 4x4 and 4x5.

The next level is E12 - E9 = 6(1 - cos(2π/Llong))/r. That is 9/r on 3x3, 6/r on 3x4 and
4x4, and (15 - 3√5)/2/r ≈ 4.145898/r on 3x5 and 4x5.

### 4.4 2xL, L >= 3 (DERIVED)

The two vertical links of every row share both plaquettes of that row. That adds three
kinds of process. They are written for the gauge h(0,y0) = h(0,y0+1) = v(0,y0) = e, in
which p0 = u = [A,B]. Check P1 confirms the counts at group level.

- (alpha) Moves on both vertical links of p0. The flux stays and sgnB flips. It is valid
  iff [A, sB] != e. There are 2 valid s for TT and TC and 0 for CT. Each has 2 orderings
  through M = 4.
- (beta) The same pair of links, but the flux hops to the other plaquette of its row and
  sgnB flips. It is valid iff A s A^-1 s != u. There are 2, 2 and 0 valid s.
- (ii) Partner-pair moves in each of the L-1 other rows. The internal state flips
  TT <-> TC. There is one valid t iff A is a transposition, and each process has 2
  orderings through M = 7, so weight 1/2.

TT and TC then have equal row sums D0 + 12 + 8 + (L-1)/2, and CT has D0 + 12. The
operator is nonnegative and symmetric, and the TT/TC block is connected. So its Perron
value is that row sum, with D0 = 3L + 9:

  E9 = 3r + 12L - ((7L+57)/2)/r, E8 = 12L - (3L/2)/r, so
  **E9 - E8 = 3r - (4L+57)/(2r)**,

which is -69/2, -73/2, -77/2 and -81/2 for L = 3..6. E9 is simple at this order. The 1/r
coefficient grows like 2L. The flux state has an extensive deficit against E1: it gains
1/(2r) per row where the ground state gains 3/(2r).

### 4.5 2x2 (DERIVED; check P3)

Both partner directions are present, so both (alpha, beta, ii) families occur. In
units of 1/r, the zero-momentum reduction on (TT, TC, CT) is
27·I + (17/2)·[[0,1,1],[1,0,0],[1,0,0]], whose Perron value is 27 + 17√2/2. P3 confirms
all 12 rows of the 12x12 second-order matrix exactly. So

  E9 = 3r + 24 - (27 + 17√2/2)/r and E8 = 24 - (6 - √14)/r, giving
  **E9 - E8 = 3r - (21 + 17√2/2 + √14)/r ≈ 3r - 36.762473/r.**

### 4.6 Uniformity

The leading term 3r = 3J_B/J_E is the same on all ten tori. For Lmin >= 3 the 1/r
coefficient -21 is also volume-independent, which fits the target theorem of [S1]. On 2xL
the 1/r coefficient is -(2L + 57/2), so at any fixed r the gap shrinks linearly in L.

## 5. Universal against non-universal

| content | universal (the same on all ten tori) | non-universal |
|---|---|---|
| flat sector | 8 orbits; weights (1,3,2,3,3,2,2,2); PTP = 0 | the constant 6LxLy |
| first shell | M = 4 for every single move; min nonflat M = 3 | the number of moves, 6LxLy |
| splitting | shape of spec C: (3,1,0^4,-1,-3) (rectangle) or (√14,√6,0^4,-√6,-√14) (square); ratio 1/2 or (√21+3)/4; symmetric spectrum | order Lmin - 1; prefactor Llong·binom(2Lmin-2,Lmin-1)/4^(Lmin-1) |
| gap | 3r; for Lmin >= 3, -21/r; threefold E9 | thin-torus 1/r coefficients; E12 - E9 |

## 6. Conjectures and open items

- **CJ1 (CONJECTURE).** Gamma_V is the closed-loop operator of the D(S3) anyon D
  (transposition flux, trivial charge) along the short cycle. Its spectrum equals
  {S_Dβ/S_Aβ} = (3,-3,0,1,-1,0,0,0). I checked only that the multisets agree and that
  Tr(W_x·W_y) = 0, from a D(S3) S-matrix I wrote from memory, not from an opened source.
- **CJ2 (CONJECTURE).** On Lmin >= 3, the triplet E9, E10, E11 first splits at order
  r^-(Lmin-1), through transposition-flux lines in the presence of the 3-cycle flux, and
  at leading order it is equally spaced: (E11-E10)/(E10-E9) -> 1.
- **CJ3 (CONJECTURE).** On 2xL at fixed r, the "eight lowest levels = flat band" picture
  fails beyond L* = (6r^2 - 57)/4 + O(r), where E9 - E8 changes sign. This is the
  computable break point of the thin family.
- **OPEN.** Every value at finite r, including r = 9, and every coefficient beyond those
  stated.

## 7. Pre-freeze computations (integers only, python3 -I -B; all light)

| id | script | sha256 (first 16 hex) | output sha256-16 | content |
|---|---|---|---|---|
| P1 | s3_gamma.py | 575fc383e31edaad | bf45f5047301df10 | S3 only: 18 commuting pairs, 8 orbits, weights; Gamma_V, Gamma_H and their sum with characteristic polynomials; [S2] block check; M3 internal orbits with the (alpha, beta, ii) counts; integer-sqrt decimals |
| P2 | cycle_orderings.py | 7fb2f6306ea736ae | b4a5bc2b2f8fb81f | N_m for m = 2..8 on the cycle C_m, equal to binom(2m-2, m-1) |
| P3 | torus2x2_second_order.py | 52613e3e3f4cee5e | 19fe91c186250ef7 | 2x2 only: tree-gauge census (18 flat, 72 M3 in tree gauge, giving 8 and 12 orbits); two-move path sums: flat sector = 6I + Gamma_V + Gamma_H, M3 12x12 as in section 4.5 |

No torus other than 2x2 was built. No eigenvalue of any Hamiltonian was computed.

## 8. Verdict protocol (used by every row)

Let D(r) be the measured quantity times the stated power of r. A row is MET in either of
two cases: an exact large-r series (an exact Schur/Feshbach expansion) gives exactly the
predicted coefficient, or certified values at r in {10^4, 10^5} give |D/PRED - 1| <= 5e-3
at 10^5 with the deviation shrinking like 1/r. A row is NOT_MET if the order differs,
meaning D(r) -> 0 or -> infinity, or if the limit differs beyond that tolerance.
Counting rows are MET only on exact equality.
