set -u
V=/root/floor-v4-verify; N=$V/neg; mkdir -p $N; S=/mnt/c/tmp/opus55/floor-v2-verify4/negctl.py
CK=$V/exp0/independent/y131-floor-cert-freeze-v2-20261110
BASE=$V/second/D1
ctl() { # id control [extra...] ; env CKDIR overrides the checkout, ARGX extra checker arguments
  local id=$1 c=$2; shift 2
  rm -rf $N/$id $N/$id.outside_cert $N/$id.outside_RUN; cp -a ${SRCBASE:-$BASE} $N/$id
  [ "$c" = none ] || python3 -I $S $c $N/$id "$@" > $N/$id.mut.txt 2>&1 || { echo "CONTROL|id=$id|mutation_failed=$(tail -1 $N/$id.mut.txt)|json=0"; return; }
  ( cd ${CKDIR:-$CK} && python3 -I -B final/tools/recheck_floor.py receipt=${RCPT:-$N/$id/FLOOR-RUN-RECEIPT.hbp} ${ARGX:-} > $N/$id.chk.txt 2>&1; echo "CONTROL|id=$id|control=$c|exit=$?|$(tail -1 $N/$id.chk.txt | cut -d'|' -f2-4)|reasons=$(tail -1 $N/$id.chk.txt | grep -o 'reasons=[^|]*' | cut -c1-330)|json=0" )
}
