#!/bin/bash
# Fresh public clone on the Linux lane, then the author's recipe with an empty sectors folder, so the 3x4 store is never read.
R=/mnt/c/tmp/opus55/allpairs-review-20261103/diff
export TMPDIR=$R/tmp CARGO_HOME=$R/tmp/cargo-home
export PATH=/root/.cargo/bin:/usr/bin:/bin
cd "$R" || exit 9
git clone --quiet --branch ym-3x4-allpairs-failclosed --single-branch https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C.git clone-linux 2>&1 | tail -1
cd clone-linux || exit 9
git -c advice.detachedHead=false checkout --quiet --detach fead9ede58cc08d214c396afa70094f0cf2da7a5
git rev-parse HEAD
git status --short | head -3
F=native/ym/results/3x4_stream/perron/allpairs/failclosed
bash "$F/reproduce_pin_run.sh" "$R/tmp/empty-sectors" "$R/out/recipe-linux" > "$R/out/recipe-linux.log" 2>&1
echo "RECIPE_EXIT=$?"
sha256sum native/ym/target/release/allpairs
python3 -I -X utf8 "$F/pe_normal_hash.py" native/ym/target/release/allpairs
echo "pe_exit=$?"
rustc +1.81.0 -V
uname -sr
