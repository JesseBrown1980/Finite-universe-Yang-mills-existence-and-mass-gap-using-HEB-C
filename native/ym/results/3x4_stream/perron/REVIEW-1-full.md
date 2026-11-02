# Independent mathematical and source review of Yang–Mills PR #79

**Review date:** 2026-11-02  
**Repository:** `JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C`  
**PR:** https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/pull/79  
**Inspected head:** `155acddd66d2ab061cdfb7716bc24e58a48ae476`  
**Verdict:** Mathematical argument ACCEPTED WITH PRECONDITIONS; **3×4 numerical certificate NOT independently verified**. Scientific result merge HOLD; experimental-tools merge can be considered with explicit non-certification labeling.

## 1. What was independently checked

Let `H` be a finite-dimensional real, symmetrizable, self-adjoint Hamiltonian with nonpositive off-diagonal entries. Let `F` be a set of `k` basis states and let `H'` be the principal submatrix excluding them. For any strictly positive vector `d` on the remaining states,

`lambda_{k+1}(H) >= lambda_min(H') >= min_i (H'd)_i/d_i`.

The first inequality follows by Cauchy interlacing applied to the similar symmetric matrix `W^{1/2} H W^{-1/2}` for a positive diagonal weight `W`. Removing whole orbit basis vectors remains a principal compression because the similarity is diagonal. For the second inequality, choose `s` large enough that `N = sI-H'` is entrywise nonnegative; its row-sum bound `rho(N) <= max_i (Nd)_i/d_i` gives the stated result.

The sector-to-whole-space lift is justified if a finite symmetry group acts by permutations of the original gauge-orbit basis, preserves `H` and `F`, and the `(+, +)` sector matrix is the actual restriction to functions constant on symmetry orbits. A positive sector `d` then lifts to a positive function on every non-flat original orbit. Its individual row ratios equal the sector row ratios. The whole-space bound follows with `k=8` whole-space flat states even though the sector has seven flat rows.

The claimed `r >= 9` extension does **not** assume monotonicity of the gap. It uses separately: `M >= 0`, hence `lambda_9(H(r)) >= lambda_9(H(9))`, and the trial-space bound `lambda_8(H(r)) <= 72 J_E` for all `r`. Thus if the 3×4 certificate and matrix identity are sound, `E9(r)-E8(r) >= t_cert-72 J_E` for all `r >= 9`, on this finite lattice only.

### Independent control

I constructed a six-state symmetric real `H` invariant under exchanging three state pairs, with two flat basis states; the orbit-constant sector has three states. Eigenvalues:

- `lambda_3(H) = 8.32732731`
- `lambda_min(H'_whole) = 7.43844719`
- `lambda_min(H'_sector) = 7.43844719`
- a test vector `d=(1,1)` gives `min_i(H'_sector d)_i/d_i = 7`.

The expected ordering holds. This validates an independent finite-dimensional control for the argument, **not** the 3×4 store or its reported numerical bound.

## 2. Reviewed implementation

Read `PERRON-BOUND.md`, `PERRON-RULE-DRAFT.md`, `PERRON-RESULT.hbp`, `perroncert.rs`, `roomball.rs`, `roomio.rs`, `ymroom.rs` and `check_d_stream.py` from PR #79.

- `perroncert.check()` uses exact signed integer arithmetic for the row ratio with positive `d`, zero flat entries, a nonpositive-off-diagonal requirement and a full payload-merkle check.
- Integer floor is appropriate: it makes `t_cert` conservative.
- `roomball` forms principal submatrices. Its Ritz levels are upper bounds on corresponding full-sector levels, not lower bounds; the source correctly states this.
- The sector-to-whole-space proof depends on correct symmetry action, weighted self-adjointness and faithful Hamiltonian rows. The implementation's `w_self_adjoint=PASS` header and payload-merkle match confirm internal construction/identity, but do not substitute for an independently constructed Hamiltonian-row comparison. The builder's 64-bit aggregate symmetry checksum does not constitute an exhaustive pairwise exact proof by itself.
- `check_d_stream.py` reports `bad_d` and `positive_offdiag` rather than raising an error if either is nonzero. The receiving gate **must** require both zero, or preferably the script should itself fail closed. It also uses `assert` for essential checks, which are disabled by Python `-O`; use explicit exceptions for a release-grade independent verifier.

## 3. Numerical status at inspected head

The PR has passed CI at `155acddd...`, but its title and `PERRON-RESULT.hbp` still state `perron_3x4_run=NOT_RUN`, `second_seat_review=NOT_DONE`, `gap_verdict=NONE`.

A separate operator-provided transcript reports a 3×4 `perroncert` value `t_cert = 93.061051 J_E`, with 12 full passes, and a matching `perroncert check`. The same transcript says the separately written Python 3×4 check was still running, and that the 364 MB `d93000000.bin` and 728 MB `passA.bin` had not yet been uploaded. Those later observations cannot be marked independently reproduced from PR #79's inspected public contents.

If all required evidence is ultimately verified, the arithmetic consequences are:

- for `r >= 9`, `E9-E8 >= 93.061051-72 = 21.061051 J_E`;
- at `r=9` with independently certified `E8 <= 70.031`, `E9-E8 >= 23.030051 J_E`.

These are **conditional in this review**, not a signed numerical certificate.

## 4. Required before scientific-result merge

1. Publish immutable `d93000000.bin` with file size and SHA-256; publish `passA.bin` and the exact pinned 34-sector store revision with SHA-256/Merkle identity.
2. Seal the actual solve log, `perroncert check` result, and independently written `check_d_stream.py` result on the same `d`, store and `(JE,JB)` inputs. Both `bad_d` and `positive_offdiag` must be zero; rows/minimum and checksum should match.
3. Independently rebuild and compare a preregistered sample of 3×4 Hamiltonian rows from `passA.bin` against the mathematical S3 gauge theory definition, including diagonal, transitions, orbit weights, signs and magnetic terms. Check exact weighted symmetry `w_i H_ij = w_j H_ji` on sampled pairs and preferably all pairs through a sorted edge pass.
4. Confirm the whole-space eight-flat trial-space bound and the rigorous `E8 <= 70.031` ball count; avoid claiming the stronger bound unless its exact inertia count is sealed and reproducible.
5. Replace all stale `NOT_RUN`, `draft`, `not reviewed` language in any **result** document with versioned, source-pinned receipts while retaining the original preregistration and failures unchanged. The preregistered rule still requires separate operator approval and registration; PR #79 must not silently amend the 60M-only production rule.
6. Test exact-head CI and run a deliberate wrong-Merkle, swapped-`d`, and mutated-row negative-control suite. Do not equate passing compiler/Clippy jobs with scientific replication.

## 5. Merge recommendation

- **APPROVE the derivation as a conditional mathematical statement.** It is a valid finite-matrix theorem if the indicated Hamiltonian and symmetry representation are correct.
- **HOLD merger of PR #79 as a certified 3×4 numerical result** until the public vector, separate check, source identity, and row-link evidence exist and are validated.
- It is reasonable to merge PR #79 earlier **only as experimental tooling and draft methodology**, with `3x4_result=NOT_INDEPENDENTLY_VERIFIED`, no registered gap verdict and no production/threshold authorization. Any such merge must be explicitly described as a software merge, not scientific certification.

**Scope:** one finite 3×4 lattice, not arbitrary volume or an infinite-volume Yang–Mills mass-gap theorem.
