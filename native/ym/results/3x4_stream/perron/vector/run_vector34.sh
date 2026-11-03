#!/bin/bash
# The vector test on the 3x4 store, directed by the operator: census of every row, the two fits, each vector written, then the pinned `perroncert check` on every row.
# Read-only on the store. Below normal priority. Rows go to the .out files, start and end to VECTOR-RUN.hbp.
export MSYS_NO_PATHCONV=1
V=/d/ym-3x4-room-run/p0-ball/vector
cd "$V" || exit 9
T=C:/tmp/ym-vector-target/release
DEV=seg:341:34:800000000:D:/ASOLARIA-HOST8-ROOMS-300G/sector-
PASSA=D:/ym-3x4-room-run/passA.bin
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
echo "VECTOR_3x4_START|at=$(now)|prodvec_sha256=$(sha256sum "$T/prodvec.exe" | cut -c1-64)|perroncert_sha256=$(sha256sum "$T/perroncert.exe" | cut -c1-64)|json=0" >> VECTOR-RUN.hbp
"$T/prodvec.exe" census "$DEV" 0 "$PASSA" 3 4 table-3x4.hbp > census-3x4.out 2> census-3x4.err
echo "VECTOR_3x4_CENSUS|at=$(now)|exit=$?|$(cut -c1-300 census-3x4.out)" >> VECTOR-RUN.hbp
for form in product lump; do
  "$T/prodvec.exe" fit table-3x4.hbp 1000 9000 $form g-3x4-$form.hbp > fit-3x4-$form.out 2> fit-3x4-$form.err
  echo "VECTOR_3x4_FIT|at=$(now)|form=$form|exit=$?|$(grep PRODVEC_FIT fit-3x4-$form.out | cut -c1-300)" >> VECTOR-RUN.hbp
  "$T/prodvec.exe" write "$PASSA" 3 4 g-3x4-$form.hbp d-3x4-$form.bin > write-3x4-$form.out 2>&1
  echo "VECTOR_3x4_WRITE|at=$(now)|form=$form|exit=$?|$(cut -c1-200 write-3x4-$form.out)" >> VECTOR-RUN.hbp
  "$T/perroncert.exe" check "$DEV" 0 1000 9000 d-3x4-$form.bin > check-3x4-$form.out 2> check-3x4-$form.err
  echo "VECTOR_3x4_CHECK|at=$(now)|form=$form|exit=$?|$(cut -c1-420 check-3x4-$form.out)" >> VECTOR-RUN.hbp
done
echo "VECTOR_3x4_DONE|at=$(now)|json=0" >> VECTOR-RUN.hbp
