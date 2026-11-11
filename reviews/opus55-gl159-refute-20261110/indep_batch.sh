cd /mnt/c/tmp/opus55/gl159-refute
CK=/mnt/c/tmp/opus55/gl159-refute/src/global-lock-20261110/measure/runs
for r in 27 81 243; do
  python3 -I indep_gl.py 3x3 $r check=$CK/levels-3x3.rows > indep/i-3x3-r$r.rows 2> indep/i-3x3-r$r.err &
done
wait
python3 -I indep_gl.py 3x4 243 check=$CK/levels-3x4.rows > indep/i-3x4-r243.rows 2> indep/i-3x4-r243.err &
python3 -I indep_gl.py 3x4 27 check=$CK/levels-3x4-k3plus.rows > indep/i-3x4-r27.rows 2> indep/i-3x4-r27.err &
wait
python3 -I indep_gl.py 3x4 729 check=$CK/levels-3x4.rows > indep/i-3x4-r729.rows 2> indep/i-3x4-r729.err
echo DONE > indep/BATCH_DONE
