# #137 — independent 8×8 full-Q signed third-moment Dirichlet identity

## Exact alternative to original row and weighted-pair contractions

Let `Q` be the original nonflat physical source support, with canonical gauge
orbits `i`, their physical positive metric weights `W_i=6w_i`, all
`72` raw electric moves `c_ij` per physical row, and weighted reciprocity

```text
W_i c_ij = W_j c_ji.
```

For a given frozen energy numerator `z` and `b=10^9`, the actual
physical reduced operator is `X(z)=D(z)-bC`, with

```text
D_i(z) = b(72+9m_i)-z.
```

For each of the eight original signed source columns `V_i`, define
`V_j=0` outside `Q`. The complete original 8×8 signed third moment
(including its factor six **exactly once** in `W`) obeys the exact
bilinear identity

```text
mu3(z) = Σ_{i∈Q} W_i(b*9m_i-z) V_i^T V_i
       + b Σ_{ {i,j}⊂Q, i<j } W_i c_ij (V_i-V_j)^T (V_i-V_j)
       + b Σ_{i∈Q,j∉Q} W_i c_ij V_i^T V_i.
```

Here each `V_i` is a row of eight signed integer source components, and
`u^T v` denotes their 8×8 outer product. The full outside boundary
includes flat transitions, the exterior of the signed support, and all
true exits. For actual self-loops, `V_i-V_i=0`; their raw counts remain
in the 72-degree identity, so they are handled exactly.

**Proof:** Expand every squared difference on supported unordered
edges. Weighted reciprocity converts the two diagonal supported-edge
contributions to `Σ_i W_i Σ_{j∈Q,j!=i}c_ij V_i^T V_i`,
and the cross terms to
`-b Σ_{i,j∈Q,i!=j}W_i c_ij V_i^T V_j`.
Add the boundary diagonal, and use the **full** 72-move count
`Σ_all_j c_ij=72`. The original diagonal `b72` and the exact
original off-diagonal `-bC` are recovered. Self-loops contribute
`b c_ii` to both original diagonal and subtraction and cancel.
Thus the identity holds on all eight signed lanes for any source and
both original energies, without spectral approximations.

The [new exact-int verifier](dirichlet_identity.py) checks the original
two energy numerators with two 8×8 matrices (128 entries total),
nontrivial reversible weighted edges, explicit exterior-zero boundary,
signs, and eight corruption controls. No float packages or physical
source producing modules are imported. A successful toy demonstrates
the identity implementation; **it is not a whole-Q source acceptance**.

## Required production calculation

1. Construct a separate **full 20,738,636-state signed source index** for
   K3 (155,378), Q4 (1,985,218), and Q5 (18,598,040). Authenticate
   immutable source SHA and exact physical lane normalization. Independently
   reconstruct K3/Q4 source rows (the 864-state challenge in draft #322
   is an accepted preliminary sample); independently regenerate all Q5
   sources from original Q4 boundary (the separate Q5 challenge in draft
   #324 is a preliminary sample).
2. Reenumerate or independently authenticate all `72` raw move
   counts for every supported physical state. Check exact weighted
   reciprocity of all supported pairs, self loops, flat exits and
   exterior exits, with complete source support and no omitted edges.
3. Accumulate independently the three terms above in signed exact
   320-bit or arbitrary-precision integers, with rigorous partial-sum
   bounds, one complete 8×8 matrix at each frozen energy.
   Use separate sharded ordered-row/Dirichlet identities and exact
   boundary counts; do not silently substitute the original B5
   Q5-principal matrix as a precomputed result in the new independent
   calculation.
4. Require byte-identical entries to the original fully archived
   signed-`mu3` matrix [#137 Stage C production](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43894461180),
   exact 64/64 symmetry at each energy, and complete 20M-source provenance.
   Reject source signs, missing crossings, wrong energy, factor-six,
   nonreciprocal flux, omitted 72-move exterior boundaries and
   exact-arithmetic overflow.
5. Only then consider independent Stage C full-source acceptance.
   Stage D exact rational angle/Wilson arithmetic and formal Perron
   full-store verification still require the distinct final review
   gates.

**Present scientific disposition:** original Gate A/B and strengthened
`17074763/10^12` first-Wilson weight source-conditional candidate;
**FORMAL HOLD** until source/graph/operator acceptance. The 4D continuum
Yang–Mills problem remains OPEN. This draft changes no Hamiltonian,
historical source receipt, original first Wilson result or main README.
