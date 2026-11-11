. /mnt/c/tmp/opus55/floor-v2-verify4/n_driver.sh
# tampered tool in a second checkout copy
rm -rf $V/exp1; cp -a $V/exp0 $V/exp1; echo "# x" >> $V/exp1/independent/y131-floor-cert-freeze-v2-20261110/work/design/gate_required.sh
CKDIR=$V/exp1/independent/y131-floor-cert-freeze-v2-20261110 ctl N19_tampered_gate_in_checkout none
rm -rf $V/exp2; cp -a $V/exp0 $V/exp2; echo "# x" >> $V/exp2/independent/y131-floor-cert-freeze-v2-20261110/final/tools/recheck_floor.py
CKDIR=$V/exp2/independent/y131-floor-cert-freeze-v2-20261110 ctl N19b_tampered_checker_in_checkout none
# receipt given as a symbolic link
rm -rf $N/N28; cp -a $BASE $N/N28; ln -sfn $N/N28/FLOOR-RUN-RECEIPT.hbp $N/N28.lnk.hbp
( cd $CK && python3 -I -B final/tools/recheck_floor.py receipt=$N/N28.lnk.hbp > $N/N28.chk.txt 2>&1; echo "CONTROL|id=N28_receipt_symlink|exit=$?|$(tail -1 $N/N28.chk.txt | cut -c1-200)|json=0" )
# run directory inside the checkout's final/
rm -rf $CK/final/N29; cp -a $BASE $CK/final/N29
( cd $CK && python3 -I -B final/tools/recheck_floor.py receipt=$CK/final/N29/FLOOR-RUN-RECEIPT.hbp > $N/N29.chk.txt 2>&1; echo "CONTROL|id=N29_rundir_inside_final|exit=$?|$(tail -1 $N/N29.chk.txt | cut -c1-200)|json=0" ); rm -rf $CK/final/N29
# unknown argument, missing receipt argument
( cd $CK && python3 -I -B final/tools/recheck_floor.py receipt=$BASE/FLOOR-RUN-RECEIPT.hbp extra=1 > $N/N30.chk.txt 2>&1; echo "CONTROL|id=N30_unknown_argument|exit=$?|$(tail -1 $N/N30.chk.txt | cut -c1-160)|json=0" )
# attacks that keep every field the checker compares and change only what it does not read
ctl X01_dupkey_final dupkey_final CONFIRMED ABOVE
SRCBASE=$V/second/D3 ctl X01b_dupkey_on_BELOW_receipt dupkey_final CONFIRMED ABOVE
ctl X02_predict_score_all_MET predict_score
ctl X03_step_rows_EXCEEDED step_rows
ctl X04_minimal_handwritten_receipt minimal
ctl X05_rename_fword rename_fword
# hiding a falsification: D2 decided BELOW at m0 = 8; remove both m0 = 8 certificates with their rows -> UNRESOLVED
# X06: hide a falsification. D2 decided BELOW at m0 = 8 (g0 = 1112/10). Remove both m0 = 8 certificates and their rows,
# set accepted_certificates and the verdict fields to the m0 = 7 values. The STEP and DECISION rows of m0 = 8 stay in place.
rm -rf $N/X06; cp -a $V/second/D2 $N/X06
python3 -I $S remove_recheck_and_cert $N/X06 > /dev/null && python3 -I $S remove_recheck_and_cert $N/X06 DECISION UNRESOLVED PREDICTION UNRESOLVED GAMMA 1109058/10000 UPPER_BOUND 111239467000000/1000000000000 UPPER_BOUND_VERIFIER_ONLY 111239467000000/1000000000000 > $N/X06.mut.txt 2>&1
rmdir $N/X06/RUN8 2>/dev/null; ls $N/X06/RUN8 2>/dev/null | tr '\n' ' '
( cd $CK && python3 -I -B final/tools/recheck_floor.py receipt=$N/X06/FLOOR-RUN-RECEIPT.hbp > $N/X06.chk.txt 2>&1; echo "CONTROL|id=X06_hide_BELOW_by_removing_m0_8|exit=$?|$(tail -1 $N/X06.chk.txt | cut -d'|' -f2-4)|reasons=$(tail -1 $N/X06.chk.txt | grep -o 'reasons=[^|]*' | cut -c1-300)|json=0" )
# X07: decide by adding a certificate the run never produced. D4 ran f = 1 only and ended UNRESOLVED at g0 = 1109058/10000;
# the f = 4,3,2,1 certificate of D1 (same r = 14, m0 = 7, same row hash) is copied in with its RECHECK row.
rm -rf $V/second/L; cp -a $V/out/D/L $V/second/L; rm -rf $V/second/L/tmp
SRCBASE=$V/second/D4 ctl X07_splice_foreign_fword_UNRESOLVED_to_ABOVE splice $V/second/D1 DECISION ABOVE PREDICTION CONFIRMED GAMMA 1109058/10000 UPPER_BOUND 111239467000000/1000000000000 UPPER_BOUND_VERIFIER_ONLY 111239467000000/1000000000000
# X08: a run the launcher failed (RESOURCE_LIMIT_EXCEEDED, CERTIFICATE=FAIL, no RECHECK row) turned into a PASS receipt
SRCBASE=$V/second/L ctl X08_FAIL_resource_limit_run_to_PASS fail_to_pass $V/second/D1
