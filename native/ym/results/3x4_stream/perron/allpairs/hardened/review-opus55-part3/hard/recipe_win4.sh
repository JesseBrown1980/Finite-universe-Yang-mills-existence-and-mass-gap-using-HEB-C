#!/bin/bash
# The Windows failing-judge path with the suffix test corrected in a copy, so the judge reaches its last row. Then whether `git clone -c` keeps the setting. Rows only, json=0.
unset MSYS_NO_PATHCONV
R=C:/tmp/opus55/allpairs-review-20261103/hard
C=$R/clones
U=https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C.git
PIN=9c2c7e67e29e0b2450010bd43c3391638e6670eb
A=native/ym/results/3x4_stream/perron/allpairs
H=$A/hardened/reproduce_hardened_run.sh
O=$R/out/recipes
E=$R/tmp/empty-sectors
export CARGO_HOME=$R/tmp/cargo-home-win PATH="/c/Users/acer/.cargo/bin:$PATH"
sed -e "s#^( cd \"\$SECTORS\" && sha256sum -c.*#echo sector_check_replaced#" -e "s#\"seg:341:34:800000000:\$SECTORS/sector-\" 0 470000000#\"D:/ym-3x4-room-run/p0-ball/small/2x2/dev.bin\" 0 470000000#" -e 's#^\[ -e "\$X" \] || X=\$X.exe#[ -f "$X.exe" ] \&\& X=$X.exe#' "$C/lf/$H" > "$R/tmp/recipe-small-lf.sh"
grep -c '\-f "$X.exe"' "$R/tmp/recipe-small-lf.sh"
( cd "$C/lf" && bash "$R/tmp/recipe-small-lf.sh" "$PIN" "$E" "$O/small-lf-3" ) > "$O/small-lf-3.log" 2>&1; c=$?
F=$(grep -a HARDENED_COMPARE_DONE "$O/small-lf-3/HARDENED-COMPARE.hbp" 2>/dev/null | tr -d '\r' | sed -e 's/.*failed=\([0-9]*\).*/\1/')
printf 'RECIPE_WIN4|clone=lf|suffix_test=corrected_in_a_copy|exit=%s|reproduce_done_rows=%s|judge_failed=%s|tool_exit=%s|exe_row=%s|json=0\n' "$c" "$(grep -c REPRODUCE_DONE "$O/small-lf-3.log")" "$F" "$(tr -d '\r\n' < "$O/small-lf-3/exit.txt")" "$(grep -a output_names_this_executable "$O/small-lf-3/HARDENED-COMPARE.hbp" | tr -d '\r' | cut -c22-70 | tr '|' '~')"
rm -f "$R/tmp/recipe-small-lf.sh"
git clone --quiet -c core.autocrlf=false --branch ym-3x4-allpairs-hardened --single-branch "$U" "$C/persist"
git -C "$C/persist" -c advice.detachedHead=false checkout --quiet --detach "$PIN"
F2=native/ym/crates/evolvers/src/bin/allpairs.rs
printf '// edited\n' >> "$C/persist/$F2"
git -C "$C/persist" checkout --quiet -- "$F2"
printf 'RECIPE_WIN4|clone=clone_dash_c_autocrlf_false|autocrlf_in_clone=%s|autocrlf_seen=%s|cr_in_source_after_a_later_checkout=%s|status_lines=%s|json=0\n' "$(git -C "$C/persist" config --local --get core.autocrlf)" "$(git -C "$C/persist" config --get core.autocrlf)" "$(tr -cd '\r' < "$C/persist/$F2" | wc -c)" "$(git -C "$C/persist" status --short | wc -l)"
printf 'RECIPE_WIN4|clone=git_dash_c_autocrlf_false_clone|autocrlf_in_clone=%s|autocrlf_seen=%s|cr_in_source_after_a_later_checkout=%s|json=0\n' "$(git -C "$C/lf" config --local --get core.autocrlf)" "$(git -C "$C/lf" config --get core.autocrlf)" "$(tr -cd '\r' < "$C/lf/$F2" | wc -c)"
rm -rf "$C/persist"
