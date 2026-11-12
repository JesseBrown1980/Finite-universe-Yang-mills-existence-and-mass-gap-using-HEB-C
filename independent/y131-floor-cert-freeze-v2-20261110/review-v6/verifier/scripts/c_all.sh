# c_all.sh -- verifier seat (opus55), verification 5, gate C driver: copies the genuine run directories (receipt,
# sidecar, RUN folders, logs; no tmp, no target) to $V/second and runs every control, three at a time.
set -u
V=/root/floor-v5-verify; mkdir -p $V/second $V/neg
for r in D1 D2 D3 D4 U2 L1 H1; do rm -rf $V/second/$r; cp -a $V/out/G/$r $V/second/$r; rm -rf $V/second/$r/tmp $V/second/$r/target; done
IDS="G_D1 G_D2 G_D3 G_D4 G_U2 G_H1 G_D1_pub G_D2_pub N01 N02 N03 N04 N05 N06 N07 N08 N09 N10 N11 N12 N13 N14 N15 N16 N17 N18 N20 N21 N23 N24 N25 N26 N27 X01 X01s X01r X01p X01e X02 X02b X02c X03 X04 X04b X04c X05 X06 X06b X06c X06d X07 X07b X08 X08p X09 X10 X11 X11b X12 X12b X12c X13 X13b X14 X15 X15t X15a"
echo $IDS | tr ' ' '\n' | xargs -P 3 -I{} bash /mnt/c/tmp/opus55/floor-v2-verify5/scripts/c_one.sh {} > $V/neg/C.hbp 2>&1
touch $V/neg/C.done
