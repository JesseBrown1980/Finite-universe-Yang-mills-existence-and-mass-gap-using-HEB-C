# #137 Worker 1 — real B3 operator-row census

Stacked on draft PR #208 and its hosted, independently accepted source-identity gates B1/B2. Base source prediction is frozen in draft PR #198 at commit `fe7bbd3c611d8977b65b6c69f06cbfcee3e20fcf`.

**Scope of this step:** use the Stage A independently written Rust 1.81 S3 move generator on all 18,598,040 authenticated archived Q5 keys; count exactly 1,339,058,880 raw 72-move transitions and independently verify canonicality, orbit weights and magnetic numbers. Build the complete Q5 address lookup across all eight groups before classifying on-Q5 and outside-Q5 directed moves. Preserve all group-wise counts, 64 bucket boundary counts and deterministic boundary fingerprints.

The `rust/src/bin/b3_census.rs` uses the publicly defined group of six permutations, 11-link gauge tree, 13 kept links, 24 edges and three transpositions independently of the original Python move implementation. It streams each `GROUP-g.v1` twice: once to build a global `address -> orbit weight` membership hash map, once to generate the complete 72-transition row. Header, weight, address-range, radix bucket sequence and source-size/target-count assertions are applied at both passes. The hosted workflow additionally reruns *all eight source SHA-256 checks* against `SOURCES-STAGE-B.hbp` before applying the electric operator.

For each supported Q5 source:
- reconstruct the exact raw 72 generator outcomes and aggregate identical destinations into counts;
- recompute the canonical address, orbit size and 12 plaquette magnetic number;
- count supported Q5 and exterior destinations/multiplicities separately;
- distinguish genuine self loops, store per-Q5-target-group move totals and per-64-residue exterior move totals;
- fingerprint exterior `(source,target,multiplicity)` transitions in reproducible source order.

**Boundary semantics:** every destination missing from the global Q5 map is labeled `outside_Q5`, rather than guessed to be Q6. Stage C will identify Q4/K3 and all cross-support terms from the pinned parent source. The deterministic B3 runner can regenerate the exterior edge stream from frozen inputs; the present census records counts/digest but is not a full boundary-edge archive.

**Controls:** Rust 1.81 clippy `-D warnings`, repository no-float audit, exact zero-state 72-move toy and wrong orbit-weight refusal, and all eight source SHA-256 checks. Hosted `B3=PASS` is permitted only after every row and all cross-group support lookups have actually been processed, with actual source rows = 18,598,040 and moves = 1,339,058,880. Release output includes group receipts, final verdict, source/executable SHA-256 and toolchain.

**Next:** independent reciprocal weighted edge gate B4, runtime-checked signed 320-bit arithmetic B7, two exact 8x8 row/pair Q5 principal moment matrices B5, all 16 Q5 mu2 frozen fingerprints B6, planted semantic controls B8; then Stage C signed Q4/K3 and Stage D full-state normalization.

**Scientific status:** Q5-only source census, not yet actual whole-space mu3. First-excitation Wilson weight HOLD, issue #137 OPEN.
