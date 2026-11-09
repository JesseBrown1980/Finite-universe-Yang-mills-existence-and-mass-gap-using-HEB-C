# #137: the reflection-sector isolation of E₂, gate-clean integer certificate

**Status:** DRAFT. Second-seat review is pending. The cloud seat refutes this certificate under the #137 lane split.

**Model:** the periodic 3×4 finite-S₃ gauge-invariant Hamiltonian H = J_E(E + rM) at r = 9 (the merged #136 setting).

**Certified here** (receipt [`Y137-K3-SECTOR-ISOLATION.hbp`](Y137-K3-SECTOR-ISOLATION.hbp), sha256 `cf91b9e4…`):

- At z₀ = 699567503/10⁷, the reflection-even sector has **exactly 2** levels below z₀, and the reflection-odd sector has **none**. The lower and upper one-sided counts agree: even 2 and 2, odd 0 and 0.
- **E₃_even ≥ 699686993/10⁷ J_E** (69.9686993). At that threshold the even counts are 2 and 2 and the odd counts 0 and 0.
- **E_odd ≥ 699689591/10⁷ J_E** (69.9689591). At that threshold the even counts are 3 and 2 and the odd counts 0 and 0.
- **Scope:** the lower-side counts are CONDITIONAL on #131's floor λ_min(QHQ_whole) ≥ 94.070673 J_E. #152 rebuilt that floor's sector rows independently; the stored-row comparison and the all-pairs census stay on the original run. The upper-side counts come from min–max and are unconditional. The split into even and odd sectors uses the lattice reflection's commutation with H, which is measured exactly on the whole support of the matrices: the K3 ball and its shell-4 exterior.

**Method** ([`y137_k3_sector_isolation.py`](y137_k3_sector_isolation.py), integer only, no arguments):

- **Reuse.** The script imports the merged checker [`finite_s3_3x4_r9_first_gap.py`](finite_s3_3x4_r9_first_gap.py) (git blob `91bd1e80`) by file name and reuses its primitives.
- **Equivalence test.** A copy of the checker's threshold computation takes the denominator b, the number of Jacobi steps and the trial ball (K2 or K3) as parameters. At b = 100, 4 steps and K2, it reproduces the checker's own outcome on its four frozen levels. Both inertias and all three witness hashes (U, G, L) match byte for byte.
- **K3 trial.** The trial ball holds the orbits within three electric moves of the flats: 155,378 states and 1,356,528 nonzeros, with the complete shell-4 exterior of 1,985,218 targets and 9,690,600 edges. The run uses 12 integer Jacobi steps at scale 10¹². These sizes equal the original chain's logged census.
- **Sectors.** The 8×8 lower and upper matrices are split by integer congruence into the reflection-even block (the six fixed flats and flat₆ + flat₇) and the odd block (flat₆ − flat₇). The decoupling is checked exactly.
- **Controls.** Five controls must fail, and each does: a broken reflection, an odd-vector sign flip, an odd upper-form sign flip, 3 Jacobi steps in place of 4, and a dropped shell-4 edge.
- **Reproducibility.** A second run in a fresh directory, holding only the script and the checker, writes the receipt byte for byte. Peak memory is about 700 MB.

**Agreement with the original, non-gate-clean chain.** The original is kept verbatim in [`y137-evidence-20261109/`](y137-evidence-20261109/) and pinned as an evidence folder.

- **K2 at z = 69956/1000:** byte-identical, including the witness hashes.
- **K3 at the three thresholds:** count for count. The original logged counts only. The port uses the checker's rounding direction, and three ROUNDING_VARIANT rows rerun it with the original's rounding: the same counts, different witnesses, both valid.

**Second seat (local refuter) verdict: CONFIRMED_WITH_NOTES.**

- **Confirmed by measurement:** the rerun, the gate and a line-by-line comparison of the threshold copy against the checker.
- **Not run, so open (CANNOT_SEE):** its independent recount of the sector inertia by a different exact method, and its two planted faults.
- **Its notes, carried here:**
  - the even/odd split rests on the reflection commuting with H, which is measured on the matrices' support;
  - the docstring's Schur-route wording for the upper side should defer to the min–max route;
  - a full-coverage guard against a dropped symmetric shell-4 edge is currently the census equality, and a 72-move conservation check would add an independent one;
  - shell-4 detailed balance on unsampled targets follows from the moves being involutions (NAMED).

**Beyond this certificate.** The strictly positive Wilson-sum weight that #137 asks for is the cloud seat's amplitude lane and is OPEN. Nothing here bears on the continuum.
