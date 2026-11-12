D=/mnt/c/tmp/opus55/floor-v2-verify6/pushrepo/independent/y131-floor-cert-freeze-v2-verify6-20261112/raw
mkdir -p $D
sort /root/floor-v6-verify/neg/C.hbp > $D/C-checker-controls.hbp
cp /root/floor-v6-verify/out/B/B.hbp $D/B-launcher-attacks.hbp
cp /root/floor-v6-verify/out/G/runs.hbp $D/G-genuine-runs.hbp
cp /root/floor-v6-verify/neg/X15.chk.txt $D/X15.checker-output.txt
cp /root/floor-v6-verify/neg/X15.mut.txt $D/X15.forge-log.txt
cp /root/floor-v6-verify/out/B/B2.out $D/B2.launcher-output.txt
cp /root/floor-v6-verify/out/B/B5.out $D/B5.launcher-output.txt
cp /root/floor-v6-verify/out/B/FZA.out $D/B8-FZA-output.txt
[ -e /root/floor-v6-verify/out/D13.done ] && { cp /root/floor-v6-verify/out/D13.stdout.txt $D/D13.launcher-output.txt; cp /root/floor-v6-verify/out/D13.recheck.txt $D/D13.checker-output.txt; cp /root/floor-v6-verify/out/D13/FLOOR-RUN-RECEIPT.hbp $D/D13.FLOOR-RUN-RECEIPT.hbp; cp /root/floor-v6-verify/out/D13.sampler $D/D13.host-mount-sampler.txt; }
ls $D
# verification 6 additions: gate A and B text outputs, honest D1 launcher output, reasons
cp /mnt/c/tmp/opus55/floor-v2-verify6/raw/A-integrity.txt $D/A-integrity.txt
cat /root/floor-v6-verify/b_build.out /root/floor-v6-verify/b_clippy.out > $D/A-build-clippy.txt
cp /root/floor-v6-verify/out/B/B7.out $D/B7.launcher-output.txt; cp /root/floor-v6-verify/out/B/B6b.out $D/B6b.launcher-output.txt
cp /root/floor-v6-verify/out/G/D1.out $D/G-D1-honest-launcher-output.txt
bash /mnt/c/tmp/opus55/floor-v2-verify6/scripts/b_reasons.sh > $D/B-reasons.hbp 2>&1
for i in G_D4 G_U2 X15t X15a X02c; do cp /root/floor-v6-verify/neg/$i.chk.txt $D/$i.checker-output.txt; done
ls $D
# D13: the checker pass did not finish (distro restarted 15:07:54 local); copy what exists
cp /root/floor-v6-verify/out/D13.stdout.txt $D/D13.launcher-output.txt; cp /root/floor-v6-verify/out/D13.recheck.txt $D/D13.checker-output-INCOMPLETE.txt; cp /root/floor-v6-verify/out/D13/FLOOR-RUN-RECEIPT.hbp $D/D13.FLOOR-RUN-RECEIPT.hbp; cp /root/floor-v6-verify/out/D13.sampler $D/D13.host-mount-sampler.txt
cat /root/floor-v6-verify/out/D13.start /root/floor-v6-verify/out/D13.exit > $D/D13.launcher-times.txt
{ ps -o pid,lstart,cmd -p 1; journalctl --list-boots --no-pager; } > $D/D13.distro-restart-evidence.txt 2>&1
echo "findmnt_nsfs=[$(findmnt -t nsfs)]" > $D/END-mounts.txt; echo "host_floor_run=$(grep -c floor-run /proc/1/mountinfo)" >> $D/END-mounts.txt
ls $D
