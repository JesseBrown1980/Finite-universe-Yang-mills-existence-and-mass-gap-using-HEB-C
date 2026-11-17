# #137 Stage L — exact original-S3 K5-inclusive physical H^2 Gram

Research draft, November 17, 2026. Stacked on Stage L pilot #259. Original source, exact residuals and previous certification records remain unchanged.

## Mathematical target

Calculate three W-weighted integer moments on the two frozen integer-scaled Stage I residual directions v1,v2:

    S11 = <H v1, H v1>_W
    S12 = <H v1, H v2>_W
    S22 = <H v2, H v2>_W

The two vectors have exactly 633,919 occupied original physical coordinates, source SHA-256 a9c918de7960e7778a918ec0a06a9d22c83b7385d19e3c636f2ea8b942318b4f. Their metric and Htt are previously certified.

For the original orbit weights w, electric multiplicities n(x,y) and magnetic diagonal d_y=72+9M_y:

    F_i(y) = sum_x w_x*n(x,y)*v_i(x)
    (H v_i)(y) = d_y*v_i(y) - F_i(y)/w_y

where the target sum includes all exterior K5 targets. Weighted reverse-edge reciprocity makes the division exact. Consequently

    S_ij = sum_x w_x*d_x^2*v_i(x)*v_j(x)
           - sum_x d_x*[v_i(x)*F_j(x)+v_j(x)*F_i(x)]
           + sum_y F_i(y)*F_j(y)/w_y .

Squaring source-shard-local flux separately is mathematically incorrect. All incoming contributions must be combined by physical target first.

## Implementation

Eight source shards partition all 633,919 active coordinates by original sorted index modulo eight. They evaluate each original 72-move row for a combined 45,642,168 electric moves. Each generates deterministic gzip-compressed binary records of 18 bytes: 13 canonical orbit bytes, four original source-index bytes, one integer multiplicity byte. These compact records avoid repeating giant exact vector coefficients on each physical edge.

There are 128 deterministic target buckets. Eight target owners each handle sixteen buckets, load every original source partition for their targets, reconstruct exact signed physical flux, verify target weights and exact divisibility, then accumulate the three F_i F_j / w moments. Original targets outside the residual-vector support are retained in full.

The final fan-in verifies every source and target owner, all multiplicity records, exact original physical source row count and transition count, two independent global weighted flux sums, full Htt 3/3 regression against the authenticated Stage I receipt, exact H^2 positive semidefiniteness, 468^2 operator ceiling, and the additional Htt inverse-Gram lower bound. Results and SHA-256 source/target manifests are preserved as immutable hosted artifacts. No floats are permitted.

If any runner exceeds storage, memory, or timeout limits, the final verdict remains HOLD. Partial target-bucket results must not be represented as a physical H^2 certificate.

## Scope

Completing this calculation certifies the three exact full-physical H^2 moments for the two Stage I residual directions. Together with previously accepted G, K, C and Htt blocks, they support full-physical residual norms of subsequent rational four-vector Ritz witnesses. They do not by themselves certify the lowest 20,738-dimensional Ritz eigendirections, physical eigenstate normalization, or a positive summed-winding Wilson spectral weight.

Research source is independent/y137-stage-l-h2-k5-20261117/physical_h2_k5.py.
CI is .github/workflows/y137-stage-l-h2-k5-production.yml.
Original Yang-Mills issue #137 remains OPEN / Wilson spectral weight HOLD. Four-dimensional continuum existence and mass gap remain OPEN.
