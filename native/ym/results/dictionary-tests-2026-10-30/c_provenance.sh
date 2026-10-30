#!/bin/bash
# Test C: was "f = from" and "m = intelligence" written before the father/mother verses?
# Full-history clone, every commit in order, first match of each, ancestry check. json=0.
set -u
D=$(dirname "$0")/c-repo
[ -e "$D" ] && { echo "C_ABORT|reason=clone_dir_exists|json=0"; exit 2; }
git clone -q -c core.autocrlf=false https://github.com/JesseBrown1980/the-human-based-understanding.git "$D" || { echo "C_ABORT|reason=clone_failed|json=0"; exit 3; }
FX='\bf\b[^\n]{0,40}\bfrom\b'; MX='\bm\b[^\n]{0,40}\bintelligence\b'; FY='father verse'; MY='mother verse'
X=""; Y=""; N=0
for c in $(git -C "$D" rev-list --reverse HEAD); do
  N=$((N+1))
  if [ -z "$X" ] && git -C "$D" grep -qiP "$FX" "$c" -- 2>/dev/null && git -C "$D" grep -qiP "$MX" "$c" -- 2>/dev/null; then X=$c; fi
  if [ -z "$Y" ] && git -C "$D" grep -qiF "$FY" "$c" -- 2>/dev/null && git -C "$D" grep -qiF "$MY" "$c" -- 2>/dev/null; then Y=$c; fi
done
echo "C_HISTORY|commits=$N|head=$(git -C "$D" rev-parse HEAD)|json=0"
for v in X Y; do c=${!v}; [ -n "$c" ] && echo "C_FIRST|which=$v|commit=$c|date=$(git -C "$D" log -1 --format=%cI $c)|subject=$(git -C "$D" log -1 --format=%s $c | tr '|' '/' | cut -c1-120)|json=0"; done
[ -n "$X" ] && echo "C_MATCH|which=X_f|line=$(git -C "$D" grep -hiP "$FX" $X -- | head -1 | tr '|' '/' | cut -c1-160)|json=0"
[ -n "$X" ] && echo "C_MATCH|which=X_m|line=$(git -C "$D" grep -hiP "$MX" $X -- | head -1 | tr '|' '/' | cut -c1-160)|json=0"
[ -n "$Y" ] && echo "C_MATCH|which=Y_father|line=$(git -C "$D" grep -hiF "$FY" $Y -- | head -1 | tr '|' '/' | cut -c1-160)|json=0"
if [ -z "$X" ] || [ -z "$Y" ]; then v="INCONCLUSIVE(missing_X_or_Y)"
elif [ "$X" = "$Y" ]; then v="INCONCLUSIVE(same_commit_cannot_order)"
elif git -C "$D" merge-base --is-ancestor "$X" "$Y"; then v="HOLDS(X_strict_ancestor_of_Y)"
else v="DOES_NOT_HOLD_IN_THIS_REPO"; fi
echo "C_PREDICTION|verdict=$v|scope=written_record_in_this_repo_only|json=0"
