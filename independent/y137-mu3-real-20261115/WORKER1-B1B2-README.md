# Issue #137 — Worker 1 Stage B source recovery (B1/B2)

**Base:** frozen PR #198 prediction commit `fe7bbd3c611d8977b65b6c69f06cbfcee3e20fcf`.
**Independent control:** PR #207 (signed `mu3` pair-vs-row and Q4 sign attacks).
**Stage A:** ACCEPTED at `42bbf383d45ab208434f519b1987adc2564195b2`.

This branch adds a source-reading production gate before the 1,339,058,880-move
enumeration. It checks the **real archived** accepted Q5 target spools from
GitHub Actions run **43615270310** (eight `y137-d11-v1-actual-Q5-groupN`
artifacts) against the immutable `SOURCES-STAGE-B.hbp` frozen on PR #198.
These artifacts were confirmed available on November 16, 2026.

## Exact acceptance

`source_gate.py verify` runs independently for each group using a streaming
reader of `<Q B H H>` records, then `aggregate` accepts only all eight
matching group receipts. The run checks:

- Exact byte count, SHA-256 and target count from each original source receipt.
- Every target in the base-6 13-link address range; an independently constructed six-permutation S3 conjugation table proves that the stored 13-link tuple is the lexicographically least global-conjugation representative and its orbit weight exactly matches the stored 1/2/3/6 field. This source-key audit is performed on every actual row, not a sample.
- Both unsigned 8-channel vector fields are minimally encoded and fit 82 bits
  per channel; a malformed record length or short payload refuses.
- Buckets are exactly `group, group+8, ..., group+56` in increasing order,
  each nonempty. Within every bucket the canonical numeric addresses increase
  strictly.
- All 64 residue classes modulo 64 are accounted for, once each, and all
  18,598,040 records are present. **Distinctness is proved without a 150-MB
  global index:** any address belongs to exactly one residue class modulo 64;
  within that class, strict address ordering rejects duplicates.
- Planted duplicate, bucket-order, out-of-range lane, wrong group, hash, and noncanonical S3 representative corruptions all must be refused before accepting real artifacts.
- The jobs retain per-group source receipts and a final B1/B2 receipt as
  separate GitHub Actions artifacts.

These checks establish **B1/B2**, including actual canonical S3 source keys and their orbit weights, from the preregistered prediction.
They are an exact byte/layout/address-membership audit of Q5 spool records;
full magnetic and 72-move source checks,
raw move/reciprocity, paired-vs-row matrices and exact `mu2` regression belong
to the later B3–B8 implementation.

## Next work for cloud GPT-6

1. Inspect the hosted B1/B2 run and its per-group receipts. If a job fails,
   use the log to repair the reader or identify an authentic source failure;
   never relax frozen source fingerprints.
2. Build a verified global `address -> (orbit weight, two exact 8-vectors)`
   lookup for the accepted 18,598,040 source addresses, using external buckets
   or memory-bounded arrays. Do not binary-search a whole group file.
3. Integrate the Stage A Rust rule for every 72-move row and independent
   index membership. Keep all raw exterior destinations for Stage C; do not
   classify a missing Q5 neighbor as Q6 until K3/Q4 membership is restored.
4. Add a separately checked signed 320-bit arithmetic path and near-boundary
   positive/negative and cancellation controls before numerical accumulation.
5. Produce the two E1/E2 signed Q5-to-Q5 8x8 `mu3_six` matrices, independently
   ordered-row and unordered-edge, with all weighted reverse-pair checks,
   exact equalities and hash receipts. This is a **partial contribution**.
6. Complete signed K3/Q4 source reconstruction (Stage C) and four-moment
   normalized Wilson-weight certification (Stage D).

**Status until subsequent checks:** `real_mu3=NOT_COMPUTED`;
`Wilson_weight=HOLD`; issue #137 OPEN. No previous local work was recovered
after the workstation was lost; this branch starts from the last remote commit.

**Strengthened review:** the initial run 43833313938 proved SHA/size/record and strict radix-64 uniqueness. The second run adds the missing independent S3 canonicality and orbit-weight checks over every archived address. The second run is the full B2 acceptance gate; supersede the initial B2 claim only after its hosted PASS.
