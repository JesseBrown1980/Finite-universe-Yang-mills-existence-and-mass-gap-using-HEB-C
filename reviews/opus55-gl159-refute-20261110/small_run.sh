O=/mnt/c/tmp/opus55/gl159-refute/small
mkdir -p $O
cd /root/gl159/plant
for L in 1x3 3x1; do
  python3 -I gl_measure.py $L 9,27,81 kf=2 k3=1 > $O/pr-$L.rows 2>&1; echo "pr $L exit=$?" >> $O/exits
  python3 -I /mnt/c/tmp/opus55/gl159-refute/fullspace.py $L 9,27,81 $O/pr-$L.rows > $O/full-$L.rows 2>&1; echo "full $L exit=$?" >> $O/exits
done
echo DONE >> $O/exits
