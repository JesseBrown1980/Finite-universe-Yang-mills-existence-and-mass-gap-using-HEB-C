# Pre-freeze refutation: PREDICTION-GLOBAL-LOCK-DRAFT-20261110

Refuter: Opus 5.5 second seat for ACER-CLAUDE-FABLE5 (pid 8467a937cba309f7). Read-only on GitHub. No torus spectrum was computed.
Draft sha256 `95f80015...aa79`, flux_cost.py `d9d882d4...c98e`, flux_cost_ladder.py `87059146...4816`. Repo read at origin/main `6a7fc747`.
My script: `refute_lock.py` (integers only, no float, no fractions module). Output: `refute_lock.out.hbp`.

## 1. Lock structure (MEASURED by refute_lock.py, own code)

| G | comm set | kappa | optimal flux sets | flat states (2-torus) | 2 - max tr(nontriv comm) = kappa? |
|---|---|---|---|---|---|
| S3 (chi_std) | 3 = A3 | 3 | one 3-cycle plaquette | 8 | yes |
| 2T | 8 = Q8 | 2 | **tie: one trace-0 plaquette, or two trace-1 plaquettes** | 42 | yes (tie) |
| 2O | 24 = 2T | 1 | one trace-1 plaquette | 56 | yes |
| 2I | 120 (every element a commutator) | 2 - phi | one trace-phi plaquette | 74 | yes |
| Q8 | 2 | 4 | 4 tied sets | 22 | yes (tie) |
| Dic3 (order 12) | 3 | **2** (pair x, x^-1) | two plaquettes | 32 | **no (formula 3)** |
| Dic4 (order 16) | 4 | **4 - 2 sqrt2** | two plaquettes | 46 | **no (formula 2)** |
| Dic6 (order 24) | 6 | **4 - 2 sqrt3** | two plaquettes | 86 | **no (formula 1)** |
| Z6 | 1 | 2 | two plaquettes | 36 | no (no nontrivial commutator) |

- Torus constraint (NAMED, standard): the based, ordered product of all plaquette loops is homotopic to the commutator of the two cycles, so it holds for every raw link configuration. Correct.
- S3: sign([a,b]) = +1, so the number of transposition plaquettes is even; nonflat M >= 3, attained by one 3-cycle plaquette (MEASURED: all commutators even).
- The gauge average of any configuration basis vector is a nonzero vector, so the single 3-cycle flux state is in H_phys on every torus (also Lx, Ly < 3). No charges exist (Gauss law imposed), and M is diagonal, so no superposition goes below kappa.
- Electric term cannot lower the leading coefficient at any order: E >= 0 (spec h_E = {0,3,6}), so H >= J_B M and by min-max **E9 >= 3r J_E exactly**. With E8 <= 3 N_links J_E (flat trial) and E9 <= 3r + 3 N_links (flat + flux trial, block diagonal because one link move changes two plaquettes): **3r - 3N <= E9 - E8 <= 3r + 3N**. (DERIVED here; inputs proved in docs §1.)
- flux_cost_ladder.py reports `plaquettes=1` for 2T because its pair search keeps only strictly cheaper pairs; the tie is hidden. kappa itself is right.

## 2. GL1
(E9-E8)/r -> 3 is right, and E8-E1 <= 3N is o(r). It is a theorem by the sandwich above on every finite torus, so the row cannot fail. 3x3 two-sided values at r = 9, 27, 81, 243 are on file (README point certificates, zero momentum), and 3x4 at r = 243 is already frozen as zgap2 P1, [21.095802, 21.573297] for r(3r - Delta), PENDING.

## 3. GL2 and delta (MEASURED here, abstract 9x9 open patch, exact)
Vacuum: 3 moves per link at dM = 4, 3/4 per link, no off-diagonal return. Flux: the 4 links of p0 give 12 moves at dM = 1 (diag +9 over vacuum); 4 hop targets, amplitude 3 each (t' t = the right 3-cycle on a shared link), row sum 12; Perron-uniform, so the lowest flux level gets the full sum. **c = 9 + 12 = 21**, delta = 21/r + O(1/r^2) > 0. This equals zgap2's exact c_L = 21 on 3x3, 3x4, 4x4 (on file since 2026-10-30). So the draft's "NAMED, not derived" is wrong: delta's sign and second-order value are on file. Second-order value at r = 9 is 74/3 = 24.667. On file: 3x3 at r = 9 [23.938578, 23.939630]; lower bounds 24.04 (3x4), 23.95 (4x4), 23.62 (4x5), 21.79 (5x5). All lie inside [21, 27], so the lower end cannot fail on any lattice listed; the interval is consistent but too wide to test anything.

## 4. GL3
L moves (pair creation, L-2 hops, annihilation on the L links of one dual cut) give order lambda^L in J_B units, so W ~ r^-(L_min - 1) J_E. The exponent L_min - 1 is right. Of the 8 S3 sectors, 6 leave by transposition moves (L moves) and 2 only by 3-cycle moves (2L moves); W is still set by order L. Problems: 3x3 -> 3x4 keeps L_min = 3, so "W failing to fall with L" fires spuriously; "roughly", "O(1)" and log slopes leave no tolerance and need floats; on-file enclosure widths at r = 243 are about 2e-3 J_E, while W(243) on 3x3 is about C x 1.7e-5 (CONJECTURE), below resolution; no tool on file for 4x4 widths was found by this check (CANNOT_SEE, not FALSE). Sanity: 0.01 < E2-E1 <= W at 3x4, r = 9 needs C >= 0.81 in W ~ C/r^2. That is consistent, at CONJECTURE level only.

## 5. GL5 and the theorem text
- The kappa values are exact (table). They are structure, not predictions. The slope -> kappa(G) is the same sandwich theorem for any finite G with E >= 0, so "a gap slope other than kappa" cannot fail. The level index is E_{n+1} - E_n with n = 8, 42, 56, 74 for S3, 2T, 2O, 2I, not E9 - E8. The electric term for 2T, 2O and 2I is undefined in the draft. 3x3 orbit counts are about 24^9, 48^9 and 120^9, so the named runs are infeasible.
- S3 is not a subgroup of SU(2): it has three involutions, and SU(2)'s only one is -1. The SU(2) ladder is 2T, 2O, 2I and it ends there. No sequence of finite subgroups of SU(2) approaches SU(2) (ADE classification), so "kappa -> 0 as the finite group approaches SU(2)" has no instance. kappa -> 0 does hold for binary dihedral Dic_n, with kappa = 4 - 4cos(pi/n) (pair flux, proved for n >= 3: single commutator classes cost >= 4 - 4cos^2). Those groups approach the normalizer of U(1), not SU(2).
- The general formula "2 - max trace over nontrivial commutators" is REFUTED: Dic3, Dic4, Dic6 and Z6 are counterexamples (MEASURED).
- Joint path theorem: not plausible as stated, because finite subgroups cannot approach SU(2). At large r, finite-group gauge theories sit in the frozen (topological) regime, which is where they stop tracking SU(2) (NAMED: Petcher-Weingarten and Creutz-Okawa freezing transitions). Transfer 1 was not read by this check.
- 3+1D (DERIVED sketch, CONJECTURE): each cube's six faces multiply to e, so nonflat faces form closed dual cycles of length >= 4 (or winding >= L). The cheapest S3 excitation is the 4-face loop around one link with transpositions, **kappa_3D = 8, not 3**. The commutator lock is not binding there. The 3-torus has 21 flat states (MEASURED), not 8. "Direct 3+1D versions" of GL1-GL3 with the same kappa are wrong.

## 6. Hygiene
On file (no re-prediction): 3x3 two-sided at r = 9..243; zgap2 c_L = 21 and its P1 (3x4, r = 243); 3x4 >= 24.04 and #89's bounds (GL2's lower end); the 2xL E2-E1 ~ L/r and the 3x3 E2-E1 third order (GL3, GL4).
Cannot fail: GL1, GL2's lower end, GL2's "lower bounds stop falling", GL4, GL5.
Vague: GL1's "a limit other than 3"; GL2's "delta growing with L"; GL3's "roughly", "O(1)", "W failing to fall", "slope in log r"; GL5's "slope other than kappa".
Wording: "What this establishes" overclaims. The finite runs cover finitely many tori; BHM is matched only for even square tori and r0 is not determined (docs §6). In the background section, "The slope is 3" is the slope of #131's bound, not a measured slope.
Exact repair text: see the return message, mirrored in REFUTE-GLOBAL-LOCK.hbp.
