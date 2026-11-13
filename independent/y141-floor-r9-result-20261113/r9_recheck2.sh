set -u
# Second attempt of the recheck. The first (r9_recheck.sh) omitted commit=C, so the checker stopped with
# certificates_rechecked=0; its output is kept as recheck.txt. This one runs in a fresh git clone at the freeze commit.
B=/root/floor-r9; C=c8dbcdbf990114292313cbc410a745a14ba0b778
PUB=79e6c40a20b7972c70e68f69cb580d261e540f29336464cd54836ac06961daa1
[ -e $B/recheck2.exit ] && { echo "RECHECK2|already ran, refusing"; exit 9; }
[ -e $B/chk ] || git clone -q --branch local-opus55-floor-cert-freeze-v2-20261110 https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C.git $B/chk || exit 6
[ "$(git -C $B/chk rev-parse HEAD)" = $C ] || { echo "RECHECK2|clone head differs"; exit 8; }
[ -z "$(git -C $B/chk status --short)" ] || { echo "RECHECK2|clone not clean"; exit 8; }
echo "$PUB  $B/second/run9/FLOOR-RUN-RECEIPT.hbp" | sha256sum -c - || exit 8
cd $B/chk/independent/y131-floor-cert-freeze-v2-20261110 || exit 7
date -u +%FT%TZ > $B/recheck2.start
python3 -I -B final/tools/recheck_floor.py receipt=$B/second/run9/FLOOR-RUN-RECEIPT.hbp commit=$C receipt_sha256=$PUB out=$B/recheck2.out > $B/recheck2.txt 2>&1
e=$?
echo $e > $B/recheck2.exit; date -u +%FT%TZ >> $B/recheck2.exit
echo "RECHECK2|exit=$e"; tail -5 $B/recheck2.txt
