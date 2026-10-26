> Published on `main` as documentation only. Source of truth: branch `http0-sgram-backend-testground` at [`a304596`](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/blob/a304596/SGRAM_CERTIFICATE_CACHE_NOTES.md) (draft PR #10); the backend code is **not** merged.

# SG-RAM notes: certificate caching, matrix jumps and measured timings

For anyone using the HTTP-0 / SG-RAM backend to run HEB-C spectral checks.
Full method, tooling and data: branch `integer-sturm-ladder`,
`independent/ladder/LADDER_METHOD.md`.

## Cache key: what makes two certificates "the same"

A Sturm inertia certificate (count of eigenvalues of H = JE·E + JB·M below
t/1000) is fully determined by its inputs, so it can be stored once and looked
up forever:

    key = sha256(mode | matrix sha(s) | JE | JB | t | scale digits)

- `mode` = `full` (1,393-state matrix, sha `137285e0…`) or `sectors`
  (the four PR #14 translation blocks, shas `fb6dbb3a…`, `9dc22f4b…`,
  `88eb8250…`, `d7dce164…`, counts summed).
- A shard stored under this key is an integrity record. SG-RAM's `/verify`
  already recomputes rather than trusting a shard; keep that for anything
  claimed as proof.

## What SHA can and cannot shortcut

- **Can:** never compute the same certificate twice (lookup by key).
- **Cannot:** produce a new answer. A hash carries no information about an
  uncomputed spectrum: (1, 2, 18.250) and (2, 4, 36.500) have provably equal
  counts, yet their sha-256 values differ in 128 of 256 bits.

## Exact shortcuts that do produce new answers

- **Scaling:** count(k·JE, k·JB, k·t) = count(JE, JB, t). Normalize keys by the
  gcd of (JE, JB, t) to turn whole rays into one cache entry.
- **Monotone cells:** M ⪰ 0, so eigenvalues rise with r = JB/JE; two endpoint
  certificates cover a whole interval: gap/JE ≥ E₁(a) − E₀(b) on [a, b].
- **Translation sectors:** four exact integer blocks; about 12× faster per
  certificate.

## Measured cost per certificate (2 vCPU, scale 10^digits)

| matrix | digits | ms |
|---|---|---|
| full 1,393, Python or Rust | 80 | ~143,000 – 167,000 |
| full 1,393, Rust | 30 | ~78,000 |
| four sectors, Rust | 30 | ~6,300 – 7,500 |

Python and Rust cost the same: the elimination dominates, not the language.

## Fail-closed behaviour to expect

A threshold exactly on an eigenvalue (for example t = 6.000 at JB = 0, where
E₁ = 6) makes a pivot interval contain zero; the verifier refuses to give a
count. Cache only COMPLETE certificates with ambiguous = 0.

Finite S₃ 2×2 torus only; no continuum claim. Integer arithmetic; json=0.
