# #137 — independent first-principles reconstruction of accepted 3×4 S₃ K3 trial

## Source-generation acceptance goal

The previous full-state signed `μ₃` recalculation [hosted run #44581486671](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/44581486671) independently reproduced both complete 20,738,636-state electric operators and all 128 signed-moment matrix entries, but used authenticated original signed physical source vectors.

This draft attacks the **upstream source-generation premise itself**.

The new standalone Rust 1.81 [reconstructor](k3_reconstruct.rs) rebuilds the finite 3×4 periodic, 24-oriented-link (S_3) model from the six explicit permutations, 11-link tree gauge and thirteen retained links. It derives the eight commuting flat orbits, three successive complete breadth-first shells (8, 264, 7,770, 147,344), **155,378 nonflat K3 states**, each row's complete 72 electric moves, magnetic cost, orbit weight, self-loop correction, flat couplings, and nonflat graph adjacency. It imports **no historical K3 trial generator** or accepted residual builder.

For each original frozen energy numerator `z ∈ {69909875505,69949729820}` with `b=10^9`, it independently runs the original **twenty** integer Jacobi sweeps with `scale=10^12` and **outward/upward** rounding, starting at zero:

```text
d_i = b(72+9*m_i-c_ii) - z
Y_i^(0) = 0
Y_i^(t+1) = ceil[ b*(scale*C_i + sum_{j nonflat, j ≠ i} c_ij Y_j^(t))/d_i ]
R_i = d_i Y_i^(20) - b*(scale*C_i + sum_{j nonflat, j ≠ i} c_ij Y_j^(20)).
```

Every trial lane and the intermediate K3 signed residual `R` is newly constructed from the independent lattice rule using exact integers. The historical `SIGNED-K3.v1` [Stage C archive in run #43867088509](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43867088509) actually contains `V1=X R`, **not** `R`. The new checker therefore uses that immutable, SHA-authenticated archive to verify the full 155,378-state canonical key and orbit-weight census without conflating the two different vectors. For numerical acceptance of the trial, it independently constructs the complete exact `8×8` original K3 Schur trial upper matrix `U0` at both original energies and compares **128/128 exact entries** against the historical immutable `RESULT-MAGNETIC-CACHE.hbp`. The complete signed `V1` source remains a separate acceptance gate requiring the Q4 residual.

The Rust toy checks group orbit structure, full 72-move electric enumeration, and that flooring instead of the source's upward Jacobi rounding is a detectable faulty alternate.

## Dispositions and next independent gate

The hosted workflow `.github/workflows/y137-independent-k3-trial.yml` first requires strict compiler/toy and no-floating controls, then the exhaustive original K3 support audit and two-energy 128-entry K3 trial-matrix comparison. **Do not mark first-principles K3 source PASS before the actual full hosted job succeeds.**

Once K3 source generation is independently accepted, independently regenerate the entire **1,985,218-state Q4 exterior residual** from the same new K3 trial via `R4=-b Σ c_(Q4,K3) Y(K3)`, checking its original signed source files across both energies. This completes the first-principles `K3/Q4` signed-source chain that fed full-Q `μ₃`. The previously independently verified Q5 boundary source is generated from this Q4 residual via exact electric moves.

The 45,508,080-row Perron whole-store original-source replication, final original Wilson-action mathematical review and full four-dimensional continuum Yang–Mills proof remain separate obligations. The improved finite original first-Wilson squared-weight candidate `17,074,763/10^12` stays **SOURCE-CONDITIONAL / FORMAL HOLD** until these are accepted. This PR edits neither original Hamiltonian nor source files or main README.
