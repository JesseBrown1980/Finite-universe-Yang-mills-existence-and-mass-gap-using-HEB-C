#!/bin/bash
# The patched recipe in the LF clone again, with MSYS_NO_PATHCONV unset as a plain Git Bash has it, so the judge can read its paths. Rows only, json=0.
unset MSYS_NO_PATHCONV
R=C:/tmp/opus55/allpairs-review-20261103/hard
C=$R/clones
PIN=9c2c7e67e29e0b2450010bd43c3391638e6670eb
A=native/ym/results/3x4_stream/perron/allpairs
H=$A/hardened/reproduce_hardened_run.sh
O=$R/out/recipes
E=$R/tmp/empty-sectors
export CARGO_HOME=$R/tmp/cargo-home-win PATH="/c/Users/acer/.cargo/bin:$PATH"
sed -e "s#^( cd \"\$SECTORS\" && sha256sum -c.*#echo sector_check_replaced#" -e "s#\"seg:341:34:800000000:\$SECTORS/sector-\" 0 470000000#\"D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin\" 0 470000000#" "$C/lf/$H" > "$R/tmp/recipe-small-lf.sh"
( cd "$C/lf" && bash "$R/tmp/recipe-small-lf.sh" "$PIN" "$E" "$O/small-lf-2" ) > "$O/small-lf-2.log" 2>&1; c=$?
F=$(grep -a HARDENED_COMPARE_DONE "$O/small-lf-2/HARDENED-COMPARE.hbp" 2>/dev/null | tr -d '\r' | sed -e 's/.*failed=\([0-9]*\).*/\1/')
printf 'RECIPE_WIN3|clone=lf|exit=%s|reproduce_done_rows=%s|judge_failed=%s|tool_exit=%s|exe_row=%s|json=0\n' "$c" "$(grep -c REPRODUCE_DONE "$O/small-lf-2.log")" "$F" "$(tr -d '\r\n' < "$O/small-lf-2/exit.txt")" "$(grep -a output_names_this_executable "$O/small-lf-2/HARDENED-COMPARE.hbp" | tr -d '\r' | cut -c22-70 | tr '|' '~')"
rm -f "$R/tmp/recipe-small-lf.sh"
