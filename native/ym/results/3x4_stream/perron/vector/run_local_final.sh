#!/bin/bash
# The store-free results as one record: each table's hash, then check_local_bound.py on each result, with the two fits' values. Below normal priority.
export MSYS_NO_PATHCONV=1
V=/d/ym-3x4-room-run/p0-ball/vector
cd "$V" || exit 9
R=C:/Users/acer/ym-vector-wt/native/ym/results/3x4_stream/perron/vector
OUT=LOCAL-RUNS.hbp
: > "$OUT"
chk() { # label lx ly form t samples seed
  L=$2x$3
  G=g-local-$L-$4.hbp
  [ -n "${8:-}" ] && G=$8
  echo "LOCAL_RESULT|L=$L|form=$4|JE=1000|JB=$1|t_milli=$5|flat_bound=$(( 6 * $2 * $3 ))|gap_milli=$(( $5 - 6 * $2 * $3 * 1000000 ))|table_sha256=$(sha256sum local-$L.hbp | cut -c1-64)|g_sha256=$(sha256sum "$G" | cut -c1-64)|json=0" >> "$OUT"
  python3 -I -X utf8 "$R/check_local_bound.py" local-$L.hbp "$G" 1000 "$1" "$5" "$2" "$3" "$6" "$7" | sed "s/^/$L|$4|/" >> "$OUT"
}
chk 9000 3 3 lump 73106758 6000 1
chk 9000 3 4 lump 89291147 6000 11
chk 9000 4 4 lump 112252744 30000 12
chk 9000 4 5 lump 134017195 6000 13
chk 9000 3 3 product 69939027 2000 21
chk 9000 3 4 product 85120864 2000 22
chk 9000 4 4 product 106126509 2000 23
chk 9000 4 5 product 127118270 2000 24
chk 9000 5 5 product 154016734 2000 25
chk 6000 4 4 lump 96472613 6000 31 scan/g-4x4-6000.hbp
echo "LOCAL_RUNS_DONE|at=$(date -u +%Y-%m-%dT%H:%M:%SZ)|json=0" >> "$OUT"
