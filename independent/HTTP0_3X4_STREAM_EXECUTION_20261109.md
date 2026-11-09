# HTTP-0 3×4 streamed input freeze — independent execution

The [GitHub Actions input-freeze workflow](../.github/workflows/gpt6-http0-3x4-input-freeze.yml) downloads the original public sector key table and final positive Perron vector, verifies their pinned SHA-256 values, and reads **every one of the 45,508,080 aligned records**. The 771 leaves each cover at most `3^10 = 59,049` rows. A frozen leaf holds content hashes, row ranges, local orbit-weight sum, magnetic-flat count, and a chained SHA-256 seal. The final receipt carries the full input census and root seal. All output is plain `HBP`, `json=0`.

## Public source inputs

| Input | Bytes | Pinned SHA-256 |
|---|---:|---|
| `perron/passA.bin` | 728,129,280 | `eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc` |
| `perron/top/x3-c.bin` | 364,064,640 | `f5c5428db1fc5d91d2ab891689f0dac7263dc26c8f9b60a2db82728f6ea0dcd1` |

Both inputs are published in [the original room-store Hugging Face dataset](https://huggingface.co/datasets/Jessedbrown/ym-3x4-room-store). The independent hash targets were extracted from the original source's `HF-UPLOAD.hbp`. The workflow reads these exact files and preserves their bytes.

## Exact verifier gates

- Read ordered 16-byte `key u64, orbit_weight u32, magnetic_cost u32` rows and 8-byte signed comparison-vector entries, strictly position aligned.
- Require ascending orbit keys, weight 1..288, magnetic cost 0..36; require the 7 flat-sector rows to carry `d=0`, and every remaining comparison-vector entry to be strictly positive.
- Independently accumulate the full `6^13` orbit-weight sum, 18 flat weights, `M_min_nonflat=3`, `M_max=36`, `d_min=9,610,602` and `d_max=13,054,544,824,728,578`.
- Hash both entire inputs while streaming and check against the frozen source hashes; reject any truncation, trailing bytes, duplicate key, or mutation.
- Emit exactly 771 ordered 59,049-row freeze checkpoints and a final SHA-256 chain root. The last checkpoint has 40,350 rows.
- Execute seven corruption tests on a separately generated 8-record input pair, each requiring a failing exit.

## Reproduction

```bash
python3 -I independent/gpt6_http0_stream_inputs.py --selftest
python3 -I independent/gpt6_http0_stream_inputs.py /path/to/passA.bin /path/to/x3-c.bin > 3x4-input-freeze.hbp
```

## Follow-on streaming rows

The row-reconstruction stage consumes the ordered key table, positive vector and original `sector-341.rooms` through `sector-374.rooms` files. It rebuilds each electric transition using the S₃ permutation law and symmetry canonicalization, validates the weighted reverse transition, computes the exact Perron ratio over every nonflat row, and freezes the 771 rowwise receipts against the already verified input-leaf seal. The existing [full-rebuild source](../native/ym/results/3x4_stream/perron/second-seat/fullrebuild.rs) and original [all-pairs checks](../native/ym/results/3x4_stream/perron/allpairs/) supply separate reference implementations for cross-checking.

The Pascal-pyramid identity governs the ternary checkpoint addressing and integrity chain; any operator-level jump in the Hamiltonian remains subject to direct equivalence testing against the underlying 72 electric moves per row.

## Measured first and final complete leaves

[Hosted run 42618356849](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/42618356849) independently reconstructed 59,049 rows in the first leaf and 40,350 in the final leaf, for **99,399 rows and 7,156,728 electric moves**, passing exact orbit keys, weights, magnetic costs, all 72 electric transitions per row, positive-vector ratios, and sampled weighted reverse-pairs. The first leaf's minimum is `94,070,896` micro-`J_E`; the final leaf finds the registered global minimum `94,070,673` at row `45,507,968`. Source and measured fields are pinned in [the leaf receipt](GPT6_HTTP0_TWO_FULL_LEAVES_MEASURED_20261109.hbp).

## Whole 771-leaf execution

The [27-shard hosted workflow](../.github/workflows/gpt6-http0-3x4-full-replay.yml) partitions 771 ternary leaves into 27 contiguous sections of up to 29 leaves. Every shard reads and authenticates both original input files, constructs each complete electric row directly from the S₃ permutation rules, validates every magnetic cost and group-orbit weight, and checks its exact Perron ratio. The independent [HBI/HBP aggregator](gpt6_http0_aggregate_leaves.py) checks all 771 ordered partitions, total `45,508,080` rows, `3,276,581,760` electric moves, full orbit-weight census, the eight-vacuum first-excitation separation's Perron minimum, source pins, and produces one chained SHA-256 root.
