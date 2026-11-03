# Three-prism orientation CHSH — independent software evidence (2026-10-30)

This public GitHub subset reproduces the **unaltered original** frozen predictions, final Python source and final HBP output. Their SHA-256 digests are checked by SHA256SUMS before a complete byte-exact replay. The full original 12-file HBI -> HBP -> SHA -> SH -> HASH archive, including earlier source/result versions, has its own previously issued seal `ca862c613a81457f55e0865b6a30a369ea22e73e400abd8b4147f8c265045188`. That original seal is **not** claimed to cover this reduced GitHub subset.

Sample: 32768 synthetic trials per setting, 4 settings, per model. 27 shared states representing three curved-prism orientation bits. No physical quantum apparatus or actual three-prism 40-cell propagation is executed.

| Model | S numerator / 32768 | S |
| --- | ---: | ---: |
| Hash-selected locally factorized control | 42246 | 1.28925 |
| Matched classical lookup | 42246 | 1.28925 |
| Centralized quantum-like synthetic parity | 93154 | 2.84235 |
| Centralized PR-box synthetic parity | 131072 | 4.00000 |

All 7 preregistered conditions passed. The hash-selected local model and matched lookup agree in **every one** of their 131072 comparisons. The centralized models explicitly read both measurement settings; they are nonlocal classical *generators*. No result establishes a physical Bell violation, a quantum z mechanism, faster-than-light signalling, or a 3x4 Yang-Mills mass gap. The quantum-like finite sample slightly exceeds 2*sqrt(2); it is not an exact quantum implementation.

**Reproduce:** `sh run.sh` (Python3 and sha256sum only). This is an isolated experiment, no modification to the frozen Yang-Mills pipeline, and no Rust execution claim.

This commit is a **subset publication after the original experiment**. The previously issued full archive remains the authoritative HBI/HBP historical evidence; the published files permit exact replay of its final result. Production HOLD unchanged.
