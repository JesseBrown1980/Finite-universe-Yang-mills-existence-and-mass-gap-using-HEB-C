cd /root/gl159/plant
O=/mnt/c/tmp/opus55/gl159-refute/plant
mkdir -p $O
python3 -I gl_measure.py 3x3 243 kf=1 k3=1 > $O/clean_3x3_r243.rows 2>&1; echo "clean exit=$?" >> $O/exits
for k in floor105 p2_95 drop_edge e8_as_e7 e9_as_e10; do
  python3 -I gl_measure_$k.py 3x3 243 kf=1 k3=1 > $O/${k}_3x3_r243.rows 2>&1; echo "$k 3x3_r243 exit=$?" >> $O/exits
done
python3 -I gl_measure.py 3x3 729 kf=1 k3=1 > $O/clean_3x3_r729.rows 2>&1; echo "clean 3x3_r729 exit=$?" >> $O/exits
for k in e8_as_e7 e9_as_e10; do
  python3 -I gl_measure_$k.py 3x3 729 kf=1 k3=1 > $O/${k}_3x3_r729.rows 2>&1; echo "$k 3x3_r729 exit=$?" >> $O/exits
done
echo DONE >> $O/exits
