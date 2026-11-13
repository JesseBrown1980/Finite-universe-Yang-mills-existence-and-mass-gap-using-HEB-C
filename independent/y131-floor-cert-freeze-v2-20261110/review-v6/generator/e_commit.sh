#!/bin/bash
# fifth correction round: the local commit, after e_final.sh has staged the file set.
set -eu
R=/root/floor-v2/repo
cd $R
[ "$(git rev-parse HEAD)" = 3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0 ]
[ "$(git rev-parse --abbrev-ref HEAD)" = local-opus55-floor-cert-freeze-v2-20261110 ]
REC=$(sha256sum independent/y131-floor-cert-freeze-v2-20261110/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp | cut -d' ' -f1)
git commit -q -F - <<EOF
Floor certificate freeze v2: fifth correction round (UNRESOLVED never accepted; namespace references; workspace manifest; freeze HEAD)

The fifth final-head verification of 3c41ea2d returned FAIL (review-v6/verifier/):
one high finding on the checker (X15), two medium findings on the launcher
(B2, B5/B7). This commit answers them. Record rows 142-146 are new; rows 114
and 131 are revised; the 16 PREDICT rows, main.rs, the gate, the verifier
scripts and the evaluator are byte-identical.

- recheck_floor.py: ACCEPT=YES is given to ABOVE and BELOW only; an UNRESOLVED
  result is never accepted (row 143). Smaller: a PREDICT_SCORE row without a
  row key, the r9 PROTOCOL row's repeated-field flag, commit= against HEAD.
- run_floor.sh: mount tables and open descriptors are read at the three points
  of row 139 and a reference to the namespace that is no member process, or a
  mount namespace without a member process, stops the run; a Cargo.toml naming
  a workspace above the Rust folder stops the run; with a frozen build HEAD
  must equal the freeze commit and the index may hide no file (row 144).
- Rehearsals at excluded couplings (review-v6/rehearsal-v2f/), including one
  full-size run to m0=13 and its checker pass.

Record sha256 $REC, 146 rows.
Nothing was computed at r = 9 or within 1 of it. The r = 9 run stays on HOLD
until an independent verification of this commit passes.

Co-Authored-By: Claude <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_015mpUd96o4PQc3pNCRh44Cm
EOF
git rev-parse HEAD
git status --short | grep -v '^?? ' | head -5
git push origin local-opus55-floor-cert-freeze-v2-20261110 2>&1 | tail -2
