# GPT-6 non-author mathematical review — finite S3 2×2 torus

**Date: 2026-11-03.** Verdict: **PASS for newly reconstructed finite 2×2 S3 algebra**, partial/conditional for the full theorem chain. Not a four-dimensional continuum Yang–Mills existence or mass-gap proof.

Research main first read at 7c44517eb57cb501d894ae8e08b62c63368e4787. The original separate-seat reports are in this directory (PRs #7–#15, #18, consolidated by #91). This review adds a separate implementation instead of merely running the author's Python code.

## Independent reconstruction

Source: [gpt6_2x2_from_permutations.py](gpt6_2x2_from_permutations.py). Expected output: [gpt6_2x2_from_permutations.measure](gpt6_2x2_from_permutations.measure).

The checker independently builds the six permutations of three symbols and their multiplication table. It canonicalizes all **7,776** five-free-link assignments under simultaneous conjugation, reconstructs the exact periodic 2×2 spatial link geometry and spanning-tree gauge fixing, computes each local three-transposition electric update and each plaquette magnetic value, and constructs the full **1,393 × 1,393 sparse operator** without importing the other seat's builders. It checks exact orbit weights, weighted self-adjointness, zero electric row sums, all-pairs graph diameter, and the full operator SHA at the end.

| Property | Fresh independent result |
|---|---|
| Orbit dimension, sum of weights | **1,393; 7,776** |
| Electric nonzero entries | **32,385** |
| Native operator SHA-256 | b6c608f50f81f3bf48fb0203b48e0e3bfc867037dc1d0a96633aa80b962137f3 |
| Flat magnetic orbit count | **8** |
| Flat orbit keys | 0, 7, 21, 1332, 1339, 3996, 4017, 4024 |
| Flat orbit weights | 1, 3, 2, 3, 3, 2, 2, 2 |
| First-order compression PEP | **24 I8** |
| Second-order Schur matrix B | **8/8 rows independently reconstructed** |
| Weighted self-adjointness of B | **PASS** |
| Characteristic polynomial | **(x+6)^4 (x^2+12x+22)(x^2+12x+30)** |
| Graph diameter | **8, exhaustive BFS from all 1,393 vertices** |
| Translation orbits | 319 of length 4; 51 of length 2; 15 of length 1 |
| Z2×Z2 character dimensions | **385, 336, 336, 336** |
| Translation symmetry on all electric entries | **PASS** |

The second-order B entries use only integer sums with denominator 2520 and exact divisibility; no floating point, numerical eigensolver, Fraction, NumPy or SciPy. A deliberately corrupted off-diagonal B coefficient causes weighted self-adjointness failure and a nonzero process exit. The dedicated CI job requires exact output equality and a failing adversarial run, as well as an AST gate banning floating-point and external numerical imports. The source computes the operator before comparing any digest; SHA is a final identity check, not a substitute for calculating H.

## October 25 finite theorem audit

**PR #11, magnetic endpoint: mathematical PASS on this finite model.** The full finite-model reconstruction confirms PEP=24I8 and every entry of B = −P E Q M_Q^(−1) Q E P. Its eigenvalue shifts are −6±sqrt(14), −6±sqrt(6), and −6 fourfold. The second-order gap coefficient is sqrt(14)−sqrt(6). For the conservative domain 0 < s = JE/JB ≤ 1/10000, the original Schur-resolvent proof uses M_Q≥3, M_Q≤12, ||E||≤48, ||QEP||²<120, and a resolvent error ≤120/1249 in units of s². The separate checker verifies the exact rational-square inequalities sqrt(14)>37/10, sqrt(6)<5/2 and 6/5−240/1249>1. Together with the finite-dimensional Feshbach/inertia branch argument, the result is gap(M+sE)>s². This is *pointwise finite-model* behavior, not an infinite-volume uniform bound.

**PR #11, certified coupling rectangles: mathematical PASS conditional on source spectral certificates.** The electric weighted graph Laplacian is PSD, with norm ≤48 by weighted Gershgorin; the magnetic potential satisfies 0≤M≤12. Hence Weyl yields |g(J)−g(J0)|≤96|ΔJE|+24|ΔJB|. The two positive rectangle margins are 3.445801 and 4.540772. The original full-inertia thresholds used to anchor these rectangles were not independently rerun in this audit.

**PR #12, every finite coupling ratio: analytical argument PASS with one named antecedent.** An electric edge has jump rate ≥1, electric diagonal ≤24, magnetic potential ≤12 and graph diameter D=8. For a positive finite-matrix ground vector v, the eigenvalue equation implies v_j≤(24+12r)v_i on each edge, hence v_min/v_max≥(24+12r)^(−8). The exact ground-state transform and weighted Poincaré bound imply gap(E+rM)≥gap(E)(v_min/v_max)^2. Inserting the pre-existing pure-electric gap **gap(E)=6** gives gap(JE E+JB M)≥6JE/(24+12JB/JE)^16 for JE>0 and JB≥0. The new checker verifies a nontrivial pure-electric eigenmode at eigenvalue 6, **but does not independently exclude smaller nonzero eigenvalues**. The exact gap(E)=6 remains an explicit antecedent supplied by earlier native spectral work, not a new independent certificate.

**PR #13, adaptive coupling cells: analytical argument PASS.** Because M≥0, each ordered eigenvalue is monotone. The whole-interval gap lower bound g(r)≥E1(a)−E0(b) for a≤r≤b does not assume gap monotonicity. For r>8, the eight flat trial states yield λ_k≤24 for k<8, and the Q-block inverse bound 1/(3r−24) gives the derivative estimate E'_k(r)≤1440/(3r−24)^2 for k=0,1 wherever differentiable. Integration yields the documented 480-factor bound. The six cells up to r=2 require the previously certified input thresholds; untested large-r anchors stay CONDITIONAL_ONLY.

**PR #14, translation acceleration: structural PASS, full Sturm claims NOT independently replayed here.** The checker translates all eight oriented links before tree gauge fixing and verifies that every translation preserves all electric coefficients and magnetic diagonals. It rederives 385 translation orbits and four character-sector dimensions 385+336+336+336=1393. This establishes the representation dimensions and supports exact block decomposition. It has *not* independently repeated the 385/336-pivot integer Sturm runs or the new two cell thresholds between r=2 and r=3. Given valid anchored counts, the reported 21/20 and 2/5 cell margins follow from homogeneity and operator order.

**PR #15, SHA inference: logic PASS.** A SHA fingerprint identifies bytes; it cannot infer missing spectral information. The example of transporting existing strict energy enclosures from (1,2) and (2,5) to JE=10 and JB from 20 through 25 is algebraically valid if those original intervals are independently certified. The proposed new direct Sturm run at JB=23 is not redone in this source checker.

**PR #18, 3×3 Ritz and ladder: NOT AUDITED by this 2×2 tool.** The 59,246-orbit trial-space data and higher-lattice spectrum require separate verification. This review also does not test the BHM finite-volume stability proof matching, the hybrid store-free Perron lower bound, the physical 4D SU(2) field theory or its continuum mass gap. No such claim is promoted.

## Repository decisions from this review

- **PR #10:** its head a304596c045ade78595e2406416a99fb98dc510b is an ancestor of current main by GitHub's compare relation. Its code is already incorporated; there is nothing useful to merge from that old head. The historical PR may be closed with an already-incorporated explanation while retaining its branch.
- **PR #52:** the old README-only material is superseded by the up-to-date main README and research status register; merging the stale README is not advisable.
- **PR #61:** contains distinct finite S3 Cantor numerical results, but NumPy/SciPy and floating-point time evolution violate the integer-only production policy. **Retain its branch and experimental records, but do not merge into main** without an exact-arithmetic or certified-error rewrite.
- **PR #68:** the formal gap-verdict rule remains HOLD.
- **SU(N) draft #9:** remains open. Arithmetic from its stated 2I conjugacy-class centralizers produces 296 open 2×3 orbits, 29,288 open 2×4 orbits and 74 periodic flat sectors. These are conditional on the class table: no independent new 2I group enumeration, 2I spectral solve or exact-count execution is claimed.

**Merge gate:** merge this audit PR only after its own hosted Python integer reconstruction and deliberate fault-control checks pass. Merge registers independent verification of these limited finite S3 statements; it does not register the withheld gap verdict or certify the open mathematical problems.
