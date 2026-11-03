#!/bin/bash
# The review's reproducers on the Linux build of the pinned source.
R=/mnt/c/tmp/opus55/allpairs-review-20261103
export TMPDIR=$R/diff/tmp
python3 -I -X utf8 "$R/attack/repro.py" "$R/diff/clone-linux/native/ym/target/release/allpairs" "$R/diff/fead9ed/native/ym/results/3x4_stream/perron/allpairs/fixture-controls/fixture-2x2.rooms.gz" "$R/diff/tmp/repro-linux" > "$R/diff/out/repro-linux.hbp" 2>&1
echo "repro_exit=$?"
tail -1 "$R/diff/out/repro-linux.hbp"
