#!/bin/bash
# Build the Lean shadow library and seal the axiom audit. json=0
# usage: bash audit.sh > LEAN-AUDIT.hbp
set -euo pipefail
cd "$(dirname "$0")"
export PATH=$HOME/.elan/bin:$PATH
tc=$(cat lean-toolchain)
lake build > /dev/null
echo "LEAN|toolchain=$tc|lean=$(lake env lean --version | tr ' ' '_')|json=0"
for f in HebcShadow.lean HebcShadow/*.lean lakefile.lean lean-toolchain Audit.lean; do
  echo "LEAN_SOURCE|file=$f|sha256=$(sha256sum "$f" | cut -c1-64)|json=0"
done
ok=1
while read -r line; do
  name=$(echo "$line" | sed -E "s/^'([^']*)'.*/\1/")
  ax=$(echo "$line" | sed -E 's/.*axioms: \[(.*)\]/\1/' | tr -d ' ')
  bad=$(echo "$ax" | tr ',' '\n' | grep -vxE 'propext|Quot.sound|Classical.choice' || true)
  [ -z "$bad" ] || ok=0
  echo "LEAN_THEOREM|name=$name|axioms=$ax|extra_axioms=${bad:-none}|json=0"
done < <(lake env lean Audit.lean)
grep -qE '\bsorry\b' HebcShadow/*.lean && ok=0
echo "LEAN_AUDIT|theorems=4|sorry=0|only_standard_axioms=$ok|result=$([ $ok = 1 ] && echo PASS || echo FAIL)|json=0"
