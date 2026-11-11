#!/usr/bin/env bash
# Review evidence for PR #159: verifies every filed refuter file against REFUTER-MANIFEST.hbp (path, byte count, full sha256),
# checks the manifest's own sha256 against the value recorded in the PR body (argument 1), and that the folder, searched through
# every subfolder, holds only the manifest's files and the filing extras (REFUTER-MANIFEST.hbp, README.md, FILED.hbp).
# The evidence files are never edited.  json=0.
# usage: verify_refuter_manifest.sh MANIFEST_SHA256 [FOLDER]
set -euo pipefail
want="$1"
d="${2:-reviews/opus55-gl159-refute-20261110}"
m="$d/REFUTER-MANIFEST.hbp"
got=$(sha256sum "$m" | cut -c1-64)
if [ "$got" != "$want" ]; then echo "FAILED|check=manifest_sha256|got=$got|want=$want|json=0"; exit 1; fi
n=0
list=$(mktemp)
printf '%s\n' REFUTER-MANIFEST.hbp README.md FILED.hbp > "$list"
while IFS='|' read -r tag path bytes sha _; do
  [ "$tag" = REFUTER_FILE ] || continue
  p=${path#path=}; b=${bytes#bytes=}; h=${sha#sha256=}
  f="$d/$p"
  if [ ! -f "$f" ] || [ -L "$f" ]; then echo "FAILED|check=missing|path=$p|json=0"; exit 1; fi
  if [ "$(wc -c < "$f")" -ne "$b" ]; then echo "FAILED|check=bytes|path=$p|json=0"; exit 1; fi
  if [ "$(sha256sum "$f" | cut -c1-64)" != "$h" ]; then echo "FAILED|check=sha256|path=$p|json=0"; exit 1; fi
  printf '%s\n' "$p" >> "$list"
  n=$((n + 1))
done < "$m"
grep -qx "REFUTER_MANIFEST_END|files=$n|json=0" "$m" || { echo "FAILED|check=manifest_count|files=$n|json=0"; exit 1; }
seen=0
while IFS= read -r f; do
  rel=${f#"$d"/}
  grep -qxF -- "$rel" "$list" || { echo "FAILED|check=unlisted|path=$rel|json=0"; exit 1; }
  seen=$((seen + 1))
done < <(find "$d" -mindepth 1 ! -type d | LC_ALL=C sort)
rm -f "$list"
echo "REFUTER_MANIFEST_CHECK|manifest_sha256=$got|files=$n|path_bytes_sha256_all_match=1|folder_entries=$seen|unlisted=0|json=0"
