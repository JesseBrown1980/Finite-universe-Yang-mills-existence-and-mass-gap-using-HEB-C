#!/bin/bash
# The recipe, in both Windows clones, patched to the 2x2 store with the sector check replaced: what a default clone reaches, and what the build gives on each. Rows only, json=0.
R=C:/tmp/opus55/allpairs-review-20261103/hard
C=$R/clones
PIN=9c2c7e67e29e0b2450010bd43c3391638e6670eb
A=native/ym/results/3x4_stream/perron/allpairs
H=$A/hardened/reproduce_hardened_run.sh
O=$R/out/recipes
E=$R/tmp/empty-sectors
export CARGO_HOME=$R/tmp/cargo-home-win PATH="/c/Users/acer/.cargo/bin:$PATH"
for name in default lf; do
  sed -e "s#^( cd \"\$SECTORS\" && sha256sum -c.*#echo sector_check_replaced#" -e "s#\"seg:341:34:800000000:\$SECTORS/sector-\" 0 470000000#\"D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin\" 0 470000000#" "$C/$name/$H" > "$R/tmp/recipe-small-$name.sh"
  ( cd "$C/$name" && bash "$R/tmp/recipe-small-$name.sh" "$PIN" "$E" "$O/small-$name" ) > "$O/small-$name.log" 2>&1; c=$?
  X=$C/$name/native/ym/target/release/allpairs.exe
  N=$(python3 -I -X utf8 "$C/lf/$A/failclosed/pe_normal_hash.py" "$X" 2>&1 | tr -d '\r' | tr '|' '~' | cut -c1-200)
  F=$(grep -a HARDENED_COMPARE_DONE "$O/small-$name/HARDENED-COMPARE.hbp" 2>/dev/null | tr -d '\r' | sed -e 's/.*failed=\([0-9]*\).*/\1/')
  P=$(grep -a original_run_is_the_pinned_one "$O/small-$name/HARDENED-COMPARE.hbp" 2>/dev/null | tr -d '\r' | cut -c1-70 | tr '|' '~')
  printf 'RECIPE_WIN2|clone=%s|exit=%s|reproduce_done_rows=%s|judge_failed=%s|first_judge_row=%s|file_sha256=%s|cr_in_source=%s|normal=%s|json=0\n' "$name" "$c" "$(grep -c REPRODUCE_DONE "$O/small-$name.log")" "$F" "$P" "$(sha256sum "$X" | cut -c1-64)" "$(tr -cd '\r' < "$C/$name/native/ym/crates/evolvers/src/bin/allpairs.rs" | wc -c)" "$N"
  rm -f "$R/tmp/recipe-small-$name.sh"
done
