# Y137 independent exact whole-cross operator ceiling

Scientific review draft (November 16, 2026), stacked on accepted-source draft PR #254. Retains the original Stage I and complete 20,736×2 cross-block source and production run unchanged.

The [hosted original-source eight-shard run #43997180450](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/actions/runs/43997180450) accepted 41,472 signed integer cross entries from 28,634 physical rows, 2,061,648 original electric moves, and all four exact frozen residual Gram bilinear identities. Its final integer matrix SHA256 is \`fafdd16b524af6e0f8aea96fcda5699fb89968c498e406792a1ed576a0226b7f\`. The complete result receipt is frozen alongside the independent checker.

## Exact global norm acceptance

Let B be the original 20,736 basis, V the two residual vectors, W the original positive physical orbit metric, and H the source-authenticated finite 3×4 S3 Hamiltonian. The whole H has the exact operator bound 0 ≤ H ≤ 468 I. Write G_old=BᵀWB, G_new=VᵀWV=dE and C=BᵀWHV. The W-orthogonal projection P_old gives:

    Cᵀ G_old⁻¹ C = (P_old H V)ᵀ W (P_old H V)
                 ≼ (H V)ᵀ W (H V)
                 ≼ 468² G_new.

Compute all three independent entries of Cᵀ G_old⁻¹ C exactly via the 4×4 Schur core remaining after eliminating eight flat, 132 selected K2 and 20,592 selected K3 indicator columns. Two independent integer routes must agree: direct 4×4 adjugate reconstruction, and the original independent 5×5 bordered Bareiss determinant. Then certify exact 2×2 PSD of 468² G_new − Cᵀ G_old⁻¹ C. This check contracts **all 41,472 cross entries**, rather than just the two frozen trial vectors' four projections.

The original production artifact is downloaded read-only from its immutable run and its SHA256 is checked before parsing. This is a second mathematical source-consistency control of C. The complete 20,738-dimensional generalized Ritz inertia/root brackets are the next spectral gate, followed by full-physical residual and summed-winding Wilson spectral-weight verification. Issue #137 OPEN / Wilson HOLD.

Workflow: \`.github/workflows/y137-cross-global-norm-accept.yml\`.
