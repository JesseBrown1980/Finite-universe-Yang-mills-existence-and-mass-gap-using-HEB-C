set -u
# The single protected r = 9 run. Operator word given 2026-11-12. Runs once; refuses to start a second time.
B=/root/floor-r9; F=$B/repo/independent/y131-floor-cert-freeze-v2-20261110
[ -e $B/LAUNCHED ] && { echo "R9|already launched once, refusing"; exit 9; }
[ "$(git -C $B/repo rev-parse HEAD)" = c8dbcdbf990114292313cbc410a745a14ba0b778 ] || { echo "R9|head differs, refusing"; exit 8; }
[ -z "$(git -C $B/repo status --short)" ] || { echo "R9|checkout not clean, refusing"; exit 8; }
date -u +%FT%TZ > $B/LAUNCHED
cd $F || exit 7
env -i PATH=/usr/bin:/bin HOME=/root bash final/tools/run_floor.sh --launch-r9 > $B/r9.stdout.txt 2>&1
e=$?
echo $e > $B/r9.exit; date -u +%FT%TZ >> $B/r9.exit
echo "R9|exit=$e"; tail -4 $B/r9.stdout.txt
