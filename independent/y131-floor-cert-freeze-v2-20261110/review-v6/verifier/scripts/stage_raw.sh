D=/mnt/c/tmp/opus55/floor-v2-verify5/pushrepo/independent/y131-floor-cert-freeze-v2-verify5-20261111/raw
mkdir -p $D
sort /root/floor-v5-verify/neg/C.hbp > $D/C-checker-controls.hbp
cp /root/floor-v5-verify/out/B/B.hbp $D/B-launcher-attacks.hbp
cp /root/floor-v5-verify/out/G/runs.hbp $D/G-genuine-runs.hbp
cp /root/floor-v5-verify/neg/X15.chk.txt $D/X15.checker-output.txt
cp /root/floor-v5-verify/neg/X15.mut.txt $D/X15.forge-log.txt
cp /root/floor-v5-verify/out/B/B2.out $D/B2.launcher-output.txt
cp /root/floor-v5-verify/out/B/B5.out $D/B5.launcher-output.txt
cp /root/floor-v5-verify/out/B/FZA.out $D/B8-FZA-output.txt
[ -e /root/floor-v5-verify/out/D13.done ] && { cp /root/floor-v5-verify/out/D13.stdout.txt $D/D13.launcher-output.txt; cp /root/floor-v5-verify/out/D13.recheck.txt $D/D13.checker-output.txt; cp /root/floor-v5-verify/out/D13/FLOOR-RUN-RECEIPT.hbp $D/D13.FLOOR-RUN-RECEIPT.hbp; cp /root/floor-v5-verify/out/D13.sampler $D/D13.host-mount-sampler.txt; }
ls $D
