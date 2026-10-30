# zteleport, cloud seat: the iterated-teleportation hierarchy T_N for the zbell models.
Pre-registration, frozen before any code.

Reference: Dmello, Xu, Renou, Gross, "An operational characterization of finite-dimensional quantum
theory", arXiv 2610.03694. Thm 18: a theory satisfying their Condition 1 (correlations preserved
under iterated teleportation) that violates CHSH at all reaches 2*sqrt(2); Cor 20: it reaches exactly
2*sqrt(2). This package tests the teleportation-hierarchy part (CHSH across T_N), not the paper's
full group-generator experiment. Baselines: zbell in PR #44 (seal 83b49c9a…), unchanged.

Rust 1.81, std only, integer and exact-rational arithmetic, json=0. 2*sqrt(2) is never computed:
quantum checks compare S^2 with 8 exactly.

## Hierarchy T_N
N + 1 bipartite resources in a chain. Endpoint L holds the left half of resource 1, endpoint R the
right half of resource N+1, station k (k = 1..N) the right half of resource k and the left half of
resource k+1. Each station returns one of four outcomes mu_k. Endpoints have CHSH settings s, t in {0,1}.
For each outcome string mu: p(mu), the conditional correlators E(s,t|mu), and S_mu = the maximum of
|+-E00 +-E01 +-E10 +-E11| with an odd number of minus signs. Reported: S_N = sum over mu of
p(mu) * S_mu, as an exact rational.

## Models
- Q (quantum reference, locally composed): each resource is |Phi+>, each station makes a Bell-state
  measurement. Integer statevectors (unnormalised, Bell vectors of norm^2 2), N = 0..4 (up to 10
  qubits). For each mu: the endpoint 2-qubit state, its 3x3 correlation matrix T_mu (exact rational)
  and its marginals.
- PRW (PR boxes composed by local wirings, the only operations available for boxes): each resource
  is a PR box (a XOR b = x*y, outputs uniform). A station inputs x0 into its first half, reads b1,
  inputs f(b1) into its second half, reads a2, and outputs mu = g(b1, a2). Every deterministic wiring
  is enumerated: x0 in {0,1}, f one of 4 maps, g one of 256 maps (2,048 per station). N = 1 and
  N = 2 exhaustively (2,048^2 station pairs at N = 2).
- ZPR (z as a global controller that sees s and t, the zbell S = 4 model): mu uniform over 4^N;
  endpoint a uniform; b = a XOR s*t XOR (parity of mu's low bits). N = 0..4.
- ZT (z global, tuned, the zbell Z-T2 model): per mu, the Z-T2 counts (E*n = +-342 of n = 486). N = 0..4.
- LH (local, hash-selected): endpoint outputs from an integer hash of (side, setting, lambda), station
  outcomes from an integer hash of (station, lambda), lambda = 0..485. N = 0..4.

## Predictions (exact equality)
- H1 Q: for every N and mu, p(mu) = 4^-N; T_mu is diagonal with entries +-1 and equals D * T_0 with
  T_0 = diag(1,-1,1) and D a signed diagonal of determinant +1 (a Pauli frame), so the residual
  T_mu - D T_0 is exactly 0; S_mu^2 = 8; endpoint marginals are 0. Q satisfies the hierarchy.
- H2 PRW: S_0 = 4, and the best wiring gives S_1 = 2 exactly and S_2 = 2 exactly. Derivation, frozen
  here: given mu, a_L XOR b_R = const XOR s*x0 XOR f(b1)*t has no s*t term, so each conditional
  correlation is local. PR correlations do not survive one teleportation step.
- H3 ZPR: S_N = 4 and p(mu) = 4^-N for N = 0..4, no-signalling exact. A global z preserves any
  correlation through the hierarchy by construction, so the hierarchy alone does not constrain it.
- H4 ZT: S_N * 486 = 1368 for N = 0..4.
- H5 LH: S_mu <= 2 for every mu and N, so S_N <= 2.
- H6 measured, not predicted: for each model, the first N and the condition (probability,
  correlation identity, CHSH) at which it departs from the quantum reference.
Any build failure or missing row is INCONCLUSIVE.
