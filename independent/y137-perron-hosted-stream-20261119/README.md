# Independent-machine complete Perron 45,508,080-row physical store replay

## Why this is a separate acceptance gate

The original finite (3×4) (S_3), (r=9) Perron compression certificate provides a certified candidate `λ₁(H'whole) ≥ 94.070673 J_E`, under the exact source/store and symmetry lift premises. The earlier second-seat `fullrebuild.rs` program checked all **45,508,080** physical rows on the original computer in 7,870 seconds and matched the original store with zero mismatches and merkle PASS. A separate hosted Go checker also reproduced the numerical bound from the independently authenticated archive. The remaining engineering evidence is a full, **fresh-host physical row replay** on a second machine.

This lane does exactly that, with the published November 2 independent `second-seat/fullrebuild.rs` pinned to SHA256 `2e9ea99595f29efb53b7a1430e5ea4b7369396e1c70fefc7ab794cdd0b915850`. The prior source and data are unchanged.

## Bounded-disk original-source streaming

The frozen 34-sector room store is published at the original `160726aaaf87386090b2b0b9ecf2815ca2634009` Hugging Face dataset snapshot. Its original **34-file SHA-256 manifest** is pinned by `9213927b3b60cfbeae8ef10730e8c7df2ad52f56159017b048539377886ce3`. The 45,508,080-row `passA.bin` table is pinned by `eefd7752031cf6e1cbfd53dd47128805d1a98bb41de0a9e269222d0e2c6e3cbc`, exactly `728129280=16×45508080` bytes.

The new [Python stream controller](stream_perron.py) downloads, SHA-authenticates and pins the small sector manifest and original passA, creates 34 named pipes, then feeds each immutable original sector into `fullrebuild` in order. **It SHA-256 checks the complete bytes of every sector** while passing the actual logical stream to the reader, and drains any original tail bytes beyond the logical merkle stream without deleting data or silently truncating the original file's SHA. The 34 large files therefore do not need to coexist on the hosted disk.

The original **unmodified** independent fullrebuild Rust code separately rederives canonical gauge keys, global-lattice-symmetry weights, magnetic numbers, all 72 electric moves, actual entry-by-entry sparse matrix rows and full payload merkle from the original `passA` keys. It exits nonzero on any row or merkle disagreement.

## Required hosted acceptance

The workflow `.github/workflows/y137-perron-independent-fullhost.yml` requires all of:

1. Source-free exact-input integrity toy and two altered-manifest controls rejected.
2. Complete unchanged Rust source hash and Rust 1.81 compilation.
3. Exact original 34-sector SHA manifest, passA size/hash and all 34 original room-sector hashes; a different or missing byte fails.
4. **45,508,080 / 45,508,080 physical store rows rebuilt**, zero canonical keys, weights, magnetic or sparse Hamiltonian entry mismatches, and original whole-store merkle PASS.
5. A sealed fresh hosted receipt with the original SHA evidence. Any failed check retains HOLD and preserves the raw logs.

This is an **independent-machine replay of the existing independent physical-row verifier**, not a separately authored new physical rule or a replacement for the previously hosted Go Barta checker. Conditional on matching the original Perron top vector, this additional source acceptance supports the finite `94.070673 J_E` compression-floor proof. It is distinct from the current first-excitation original Wilson `17,074,763/10^12` conditional spectral-weight candidate, whose final source-correlated operator review and independent K3 trial source generation remain open.

All hosted PASS claims are **pending execution**. The four-dimensional continuum Yang–Mills problem remains OPEN. No original Hamiltonian, sector files, vector, or archive receipt is modified.
