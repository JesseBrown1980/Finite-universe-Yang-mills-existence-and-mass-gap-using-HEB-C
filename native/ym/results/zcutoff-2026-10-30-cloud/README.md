# zcutoff: a collapsing vortex in the finite fluid, at three resolutions (2026-10-30)

A swirl driven toward zero core radius on the same physical schedule at grid sizes 24³, 48³ and 96³,
in the D3Q27 lattice gas with trits 0–2 and the 288 involutive gates of `GATES.lut`. A control arm pushes
the same cells with scrambled directions. Rust 1.81, std only, integer only, clippy `-D warnings` exit 0,
HBI → HBP → SHA → SH → HASH, json=0.

The question is where OpenAI's September 2026 construction shrinks a vortex core to zero volume
(core volume ~ τ^(3/2−h), speed ~ τ^(−1/2−h)): what does a finite fluid do?

## Result (`RESULT.hbp`)

| Grid | Peak axis vorticity, drive | Control | Drive ÷ control | Peak cell momentum (cap 364) | Core edge at end |
|---|---|---|---|---|---|
| 24³ | 681 | 167 | 4.1× | 276 | 3 cells (1/8 of box) |
| 48³ | 2,011 | 226 | 8.9× | 334 | 6 cells (1/8) |
| 96³ | 4,078 | 358 | 11.4× | 364, the cap | 12 cells (1/8) |

- The vortex concentrates as resolution rises: axis vorticity grows about ×3, then ×2.
- The core does not follow the collapse. The drive radius goes to zero; the core ends at 1/8 of the box
  at every resolution, the same physical size. At 96³ it narrowed from 15 cells to 8 and spread back to 12.
- At 96³ the peak cell momentum reaches the occupancy cap exactly. Once the inner cells are full, further
  pushes cannot concentrate the swirl: the finite-capacity cutoff.
- The cell maximum of |curl j|² is the same in drive and control: fine-scale vorticity is lattice noise.
- With ν ≈ 0.43 (`../*calib*`), the viscous length √(νT) is 4.5, 6.4 and 9.1 cells; the core tracks the
  box, set by the momentum cap and drive geometry.

| check | result |
|---|---|
| C1 conservation, occupancy | PASS |
| C2 every value under the computed caps (JCAP 364, WCAP 15,552) | PASS |
| C3 physical peak vorticity rises with resolution | PASS |
| C4 core never below one cell; physical core volume falls with resolution | PASS |
| A1 drive more than 10× control at every grid | FAIL (4.1×, 8.9×, 11.4×) |
| A2 axis vorticity rises with resolution | PASS |
| A3 cell maximum is noise | PASS |

`PREREG.md` (`441a404f…`) was frozen before any code; `ADDENDUM.md` (`a58eae93…`) added the control arm and
axis measures before run 2. `RESULT.run1.hbp` is run 1; `RESULT.interrupted.hbp` is an interrupted first
attempt, reproduced byte for byte by run 1. `run.sh` rebuilds with Rust 1.81 and checks byte identity.
