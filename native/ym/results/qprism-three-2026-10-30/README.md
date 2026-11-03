# Three prisms × 3 — hash-selected curved j and predicted particle branches

Isolated **software** test, 2026-10-30. Three serial 3-way prisms, 27 final branches and signed ternary GF(3) amplitudes. This is a conceptual test motivated by the user's Q-PRISM work, **not** a run of the Q-PRISM simulator or hardware. No physical FTL signal, quantum transport, or Yang–Mills mass gap is established.

At logical t=0 a 40-leaf Merkle root over source and untouched future-stage sites is computed. A separate protocol z token includes this physical root, the selected laser destination, and the signal. For each prism, SHA-256 of the token and prism index selects either curved j+ = I+R−R² or j− = I−R+R², which are transposes. The 3 digits of the selected destination select columns. The controller forecasts all 27 signed final branches before propagation; local source-to-prism-to-output movement remains one edge per tick, arriving at t=3.

Across **54 cases** (27 destinations × ±1 laser polarity), all **eight registered software checks PASS**. Occupied branch counts by tick are 1,3,9,27; the independently coded closed-form forecast matches actual three-stage propagation; 8 distinct j schedules occur. A destination change changes the *protocol* root immediately, while the physical t=0 Merkle root remains unchanged if the source is unchanged. In-flight trajectories do not retroactively change. Invalid and stale tokens are rejected. A deliberately exposed global token leaks early information: the expected negative control is **LEAK**, not PASS for physical no-signaling.

The pre-registration SHA-256 is `f880459cef7c5f00c194f19691429347d499545e2c232732be42bba92434780c`. The expected exact generated `RESULT.hbp` SHA-256 is `5875929926f4fdfdb1b8577839e675a87aed51cf157bb82851dbe816ffd7dc5c`. These are independent local measurements; CI must replay the exact committed source to verify the latter.

Source revisions after the initial local run were retained in the separate evidence archive: V1 used the same function for forecast and propagation; V2 changed forecast to a closed-form independent oracle; V3 replaced the physical source digest with a real 40-leaf Merkle root. Pre-registration remained fixed. Revisions are **not** a single pristine preregistered run.

The global destination-aware token is deliberately part of the algorithm. Therefore this experiment does **not** establish that a physical laser needs instantaneous destination information to travel, and it does not pick one physically correct curve. Keeping local observers unable to access the token is essential for causality. The result is separate from the existing production HOLD and frozen P2/P3/P4 runs.

Run: `python3 q3_test.py`, then `echo "5875929926f4fdfdb1b8577839e675a87aed51cf157bb82851dbe816ffd7dc5c  RESULT.hbp" | sha256sum -c`. Exact-head CI runs that procedure.
