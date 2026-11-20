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

Every trial lane and the intermediate K3 signed residual `R` is newly constructed from the independent lattice rule using exact integers. The historical `SIGNED-K3.v1` [Stage C archive in run #43867088509](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43867088509) actually contains `V1=X R`, **not** `R`. The new checker therefore uses that immutable, SHA-authenticated archive to verify the full 155,378-state canonical key and orbit-weight census without conflating the two different vectors. For numerical acceptance of the trial, it independently constructs the complete exact `8×8` original K3 Schur trial upper matrix `U0` at both original energies and compares **128/128 exact entries** against the historical immutable `RESULT-MAGNETIC-CACHE.hbp`. It also independently enumerates every one of the **1,985,218 Q4 exterior canonical states** reached by the new K3 electric boundary, derives each reverse coupling from the exact gauge-orbit weighted balance relation, and regenerates both complete **K3 interior and Q4 exterior signed residuals**. A separately reused tested signed 320-bit integer accumulator recomputes the full original `G0=6R*WR` matrices, requiring **another 128/128 exact archived G0 entries** to match. The complete signed Stage C `V1=X R` physical source comparison remains a distinct later gate.

The Rust toy checks group orbit structure, full 72-move electric enumeration, and that flooring instead of the source's upward Jacobi rounding is a detectable faulty alternate.

## Dispositions and next independent gate

The hosted workflow `.github/workflows/y137-independent-k3-trial.yml` first requires strict compiler/toy and no-floating controls, then the exhaustive original K3 support audit and two-energy 128-entry K3 trial-matrix comparison. **Do not mark first-principles K3 source PASS before the actual full hosted job succeeds.**

Current production aims to verify the complete **1,985,218-state Q4 exterior residual**, generated independently from the new K3 trial by `R4=-b Σ c_(Q4,K3)Y(K3)`, through both original exact 8×8 Gram matrices. Individual archived Q4 Stage C rows store `V1` rather than `R`; a full source-by-source `V1` reconstruction from the new residual remains a subsequent acceptance obligation. The previously accepted Q5 physical boundary uses the Q4 residual premise.

The 45,508,080-row Perron whole-store original-source replication, final original Wilson-action mathematical review and full four-dimensional continuum Yang–Mills proof remain separate obligations. The improved finite original first-Wilson squared-weight candidate `17,074,763/10^12` stays **SOURCE-CONDITIONAL / FORMAL HOLD** until these are accepted. This PR edits neither original Hamiltonian nor source files or main README.
