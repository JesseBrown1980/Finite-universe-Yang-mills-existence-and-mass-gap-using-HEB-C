# c_one.sh ID -- verifier seat (opus55), verification 5, gate C: one checker control on a copied run directory.
# The checker always runs from the clean export of 3c41ea2d ($V/exp0), never from a tree that launched a run.
set -u
V=/root/floor-v5-verify; G=$V/second; N=$V/neg; mkdir -p $N
S=/mnt/c/tmp/opus55/floor-v2-verify5/scripts
CK=$V/exp0/independent/y131-floor-cert-freeze-v2-20261110
id=$1
pub() { grep -o "^RUN|id=$1|.*publish=[0-9a-f]*" $V/out/G/runs.hbp | grep -o 'publish=[0-9a-f]*' | cut -d= -f2; }
base() { rm -rf $N/$id $N/$id.outside_cert $N/$id.outside_RUN; cp -a $G/$1 $N/$id; }
mut() { python3 -I $S/negctl5.py "$1" $N/$id "${@:2}" >> $N/$id.mut.txt 2>&1 || { echo "CONTROL|id=$id|mutation_failed=$(tail -1 $N/$id.mut.txt | tr '|' ':')|json=0"; exit 0; }; }
forge() { python3 -I $S/forge.py $N/$id $CK "$@" >> $N/$id.mut.txt 2>&1; }
weak() { python3 -I $S/weaken.py "$@" >> $N/$id.mut.txt 2>&1; }
ARGS=""
case $id in
  G_D1) base D1;; G_D2) base D2;; G_D3) base D3;; G_D4) base D4;; G_U2) base U2;; G_H1) base H1;;
  G_D1_pub) base D1; ARGS="receipt_sha256=$(pub D1)";;
  G_D2_pub) base D2; ARGS="receipt_sha256=$(pub D2)";;
  N01) base D1; mut missing_cert;;
  N02) base D1; mut subst_bytes;;
  N03) base D1; mut subst_rehash;;
  N04) base D1; mut path_dotdot;;
  N05) base D1; mut path_abs;;
  N06) base D1; mut symlink_cert;;
  N07) base D1; mut symlink_rundir;;
  N08) base D1; mut decision;;
  N09) base D1; mut gamma;;
  N10) base D1; mut upper;;
  N11) base D1; mut upper_vonly;;
  N12) base D1; mut ritz_writer;;
  N13) base D1; mut ritz_verifier;;
  N14) base D1; mut g0 112/1;;
  N15) base D1; mut remove_recheck;;
  N16) base D1; mut dup_recheck;;
  N17) base D1; mut unlisted_extra;;
  N18) base D1; mut edit_no_sidecar;;
  N20) base D1; mut certfail;;
  N21) base D1; ARGS="commit=3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0";;
  N23) base D1; mut receipt_r 21/2;;
  N24) base D1; mut recheck_m0 8;;
  N25) base D1; mut no_relative_to;;
  N26) base D1; mut pred_row;;
  N27) base D1; mut line_after_final;;
  X01) base D3; mut dupkey_final CONFIRMED ABOVE;;
  X01s) base D1; mut dupfield "STEP|" G 1/1;;
  X01r) base D1; mut dupfield "RECHECK|" gamma 1/1;;
  X01p) base D1; mut dupfield "PROTOCOL|" m0_steps 7;;
  X01e) base D1; mut dupfield "RECEIPT|" mode r9;;
  X02) base D1; mut predict_score;;
  X02b) base D1; mut score_set 068 MET 070 NOT_MET;;
  X02c) base D1; mut drop_key "PREDICT_SCORE|row=058" row;;
  X03) base D1; mut step_rows;;
  X04) base D1; mut minimal;;
  X04b) base D1; mut handwritten;;
  X04c) base D1; mut handwritten; ARGS="receipt_sha256=$(pub D1)";;
  X05) base D1; mut rename_fword;;
  X06) base D2; mut remove_recheck_and_cert; mut remove_recheck_and_cert; forge;;
  X06b) base D2; mut drop_step 8; forge;;
  X06c) base D2; mut opfail_step 8; forge;;
  X06d) base D2; mut drop_step 8; mut protocol_set m0_steps 7; forge;;
  X07) base D4; mut splice $G/D1; forge;;
  X07b) base D4; mut splice $G/D1; mut protocol_set f "1;4,3,2,1"; forge;;
  X08) base L1; mut replace_receipt $G/D1;;
  X08p) base L1; mut replace_receipt $G/D1; ARGS="receipt_sha256=$(pub L1)";;
  X09) base D1; mut add_step $G/D2 8; forge;;
  X10) base U2; mut drop_step 8; forge;;
  X11) base D1; mut protocol_set g0 2/1;;
  X11b) base D1; mut verdict_g0_both 100/1; forge;;
  X12) base D1; mut as_r9; forge; ARGS="commit=3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0 receipt_sha256=$(sha256sum $N/$id/FLOOR-RUN-RECEIPT.hbp | cut -d' ' -f1)";;
  X12b) base D1; mut as_r9; ARGS="receipt_sha256=$(sha256sum $N/$id/FLOOR-RUN-RECEIPT.hbp | cut -d' ' -f1)";;
  X12c) base D1; mut as_r9; ARGS="commit=3c41ea2d9dd01de0ffcd547a7e7d417baa2ca6c0";;
  X13) base D1; ARGS="receipt_sha256=0000000000000000000000000000000000000000000000000000000000000000";;
  X13b) base D1; ARGS="receipt_sha256=XYZ";;
  X14) base D1; mut swap_recheck;;
  X15) base D3; weak $N/$id/RUN7/cert_m7_r14_1_f4-3-2-1.txt vfrom $N/$id/RUN7/cert_m7_r14_1_f1.txt 1022056/10000; forge;;
  X15t) base D3; weak $N/$id/RUN7/cert_m7_r14_1_f4-3-2-1.txt vfrom $N/$id/RUN7/cert_m7_r14_1_f1.txt 100/1; forge;;
  X15a) base D1; weak $N/$id/RUN7/cert_m7_r14_1_f4-3-2-1.txt t 1/2; weak $N/$id/RUN7/cert_m7_r14_1_f1.txt t 1/2; forge;;
  *) echo "CONTROL|id=$id|unknown|json=0"; exit 0;;
esac
( cd $CK && python3 -I -B final/tools/recheck_floor.py receipt=$N/$id/FLOOR-RUN-RECEIPT.hbp $ARGS out=$N/$id.chk.out > $N/$id.chk.txt 2>&1; e=$?
  T=$(tail -1 $N/$id.chk.txt)
  echo "CONTROL|id=$id|exit=$e|$(echo "$T" | cut -d'|' -f2-3)|gates_run=$(grep -c '^RECHECKED|.*path_check=PASS' $N/$id.chk.txt)|gates_not_run=$(grep -c 'gate=NOT_RUN' $N/$id.chk.txt)|forge=$(grep -o '^FORGE|[^ ]*' $N/$id.mut.txt 2>/dev/null | tail -1 | cut -d'|' -f2-4)|reasons=$(echo "$T" | grep -o 'reasons=[^|]*' | cut -c9-420)|chk_h16=$(sha256sum $N/$id.chk.txt | cut -c1-16)|json=0" )
