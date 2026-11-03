#!/bin/bash
# Fresh public clones on the Windows lane, then both recipes with an empty sectors folder, so the 3x4 store is never read and no build runs. Rows only, json=0.
R=C:/tmp/opus55/allpairs-review-20261103/hard
C=$R/clones
U=https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C.git
PIN=9c2c7e67e29e0b2450010bd43c3391638e6670eb
OLD=0fd24d31e3abad7c2745a2c3ffa917663418621a
H=native/ym/results/3x4_stream/perron/allpairs/hardened/reproduce_hardened_run.sh
P=native/ym/results/3x4_stream/perron/allpairs/failclosed/reproduce_pin_run.sh
E=$R/tmp/empty-sectors
O=$R/out/recipes
mkdir -p "$C" "$E" "$O"
emit() { printf 'RECIPE|%s|json=0\n' "$*"; }
tailrow() { tail -1 "$1" | tr -d '\r' | cut -c1-120 | tr '|' '~'; }

# Default clone: this machine's system git config holds core.autocrlf=true.
git clone --quiet --branch ym-3x4-allpairs-hardened --single-branch "$U" "$C/default"
git -C "$C/default" -c advice.detachedHead=false checkout --quiet --detach "$PIN"
emit "clone=default|head=$(git -C "$C/default" rev-parse HEAD)|manifest_sha256=$(sha256sum "$C/default/native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256" | cut -c1-64)|cr_in_manifest=$(tr -cd '\r' < "$C/default/native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256" | wc -c)"
( cd "$C/default" && bash "$H" "$PIN" "$E" "$O/default-hardened" ) > "$O/default-hardened.log" 2>&1; c=$?
emit "clone=default|recipe=hardened|exit=$c|last=$(tailrow "$O/default-hardened.log")"
( cd "$C/default" && bash "$P" "$E" "$O/default-pin" ) > "$O/default-pin.log" 2>&1; c=$?
emit "clone=default|recipe=pin|exit=$c|last=$(tailrow "$O/default-pin.log")"

# The header's advice.
git -c core.autocrlf=false clone --quiet --branch ym-3x4-allpairs-hardened --single-branch "$U" "$C/lf"
git -C "$C/lf" -c advice.detachedHead=false checkout --quiet --detach "$PIN"
emit "clone=c_autocrlf_false|head=$(git -C "$C/lf" rev-parse HEAD)|manifest_sha256=$(sha256sum "$C/lf/native/ym/results/3x4_room_backed/receipts/hf-store/SECTORS-341-374.sha256" | cut -c1-64)|autocrlf_in_clone=$(git -C "$C/lf" config --local --get core.autocrlf)|autocrlf_seen=$(git -C "$C/lf" config --get core.autocrlf)|status_lines=$(git -C "$C/lf" status --short | wc -l)"
( cd "$C/lf" && bash "$H" "$PIN" "$E" "$O/lf-hardened" ) > "$O/lf-hardened.log" 2>&1; c=$?
emit "clone=c_autocrlf_false|recipe=hardened|exit=$c|source_at_pin=$(cut -c1-64 "$O/lf-hardened/source-at-pin.sha256" 2>/dev/null)|sectors_failed_rows=$(grep -c FAILED "$O/lf-hardened/sectors-check.txt" 2>/dev/null)|last=$(tailrow "$O/lf-hardened.log")"
( cd "$C/lf" && bash "$P" "$E" "$O/lf-pin" ) > "$O/lf-pin.log" 2>&1; c=$?
emit "clone=c_autocrlf_false|recipe=pin|exit=$c|sectors_failed_rows=$(grep -c FAILED "$O/lf-pin/sectors-check.txt" 2>/dev/null)|last=$(tailrow "$O/lf-pin.log")"

# A PIN the recipe has never heard of: this commit's recipe, in a checkout of the earlier commit, with that commit as PIN. No constant in the recipe names the source.
git -C "$C/lf" worktree add --quiet --detach "$C/lf-old" "$OLD"
cp "$C/lf/$H" "$R/tmp/recipe-copy.sh"
( cd "$C/lf-old" && bash "$R/tmp/recipe-copy.sh" "$OLD" "$E" "$O/old-pin" ) > "$O/old-pin.log" 2>&1; c=$?
emit "clone=c_autocrlf_false_at_0fd24d3|recipe=hardened_with_PIN_0fd24d3|exit=$c|source_at_pin=$(cut -c1-64 "$O/old-pin/source-at-pin.sha256" 2>/dev/null)|reached_the_sector_check=$(grep -c FAILED "$O/old-pin/sectors-check.txt" 2>/dev/null)|last=$(tailrow "$O/old-pin.log")"
git -C "$C/lf" worktree remove --force "$C/lf-old"
rm -f "$R/tmp/recipe-copy.sh"

# A source edit the recipe's first check must see, and a config it may not.
( cd "$C/lf" && printf '// edited\n' >> native/ym/crates/evolvers/src/bin/allpairs.rs && bash "$H" "$PIN" "$E" "$O/edited" ) > "$O/edited.log" 2>&1; c=$?
emit "clone=c_autocrlf_false|edit=allpairs_rs_one_line|exit=$c|last=$(tailrow "$O/edited.log")"
git -C "$C/lf" checkout --quiet -- native/ym/crates/evolvers/src/bin/allpairs.rs
mkdir -p "$C/lf/native/.cargo"
printf '[build]\nrustflags = ["-C", "opt-level=1"]\n' > "$C/lf/native/.cargo/config.toml"
( cd "$C/lf" && bash "$H" "$PIN" "$E" "$O/parent-config" ) > "$O/parent-config.log" 2>&1; c=$?
emit "clone=c_autocrlf_false|edit=untracked_native_dot_cargo_config_toml|exit=$c|reached_the_sector_check=$(grep -c FAILED "$O/parent-config/sectors-check.txt" 2>/dev/null)|status=$(git -C "$C/lf" status --short | tr -d '\r' | tr '\n' ' ' | cut -c1-60)|last=$(tailrow "$O/parent-config.log")"
rm -rf "$C/lf/native/.cargo"
mkdir -p "$C/lf/native/ym/crates/evolvers/.cargo"
printf '[build]\nrustflags = ["-C", "opt-level=1"]\n' > "$C/lf/native/ym/crates/evolvers/.cargo/config.toml"
( cd "$C/lf" && bash "$H" "$PIN" "$E" "$O/untracked-inside" ) > "$O/untracked-inside.log" 2>&1; c=$?
emit "clone=c_autocrlf_false|edit=untracked_file_inside_the_pathspec|exit=$c|reached_the_sector_check=$(grep -c FAILED "$O/untracked-inside/sectors-check.txt" 2>/dev/null)|last=$(tailrow "$O/untracked-inside.log")"
rm -rf "$C/lf/native/ym/crates/evolvers/.cargo"
emit "done=1"
