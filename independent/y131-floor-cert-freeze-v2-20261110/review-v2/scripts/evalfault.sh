set -u
PK=/root/floor-v2-verify/clone/independent/y131-floor-cert-freeze-v2-20261110
EV="python3 -I -B $PK/final/tools/floor_eval.py"
PRED=$PK/final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
SRC=/root/floor-v2-verify/reh/A2
FS='1;4,3,2,1'
run() { # name : expects $D prepared
  local D=$1 n=$2
  rm -f $D/log/m7_step.hbp
  ( cd $PK && $EV step pred=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp out=$D m0=7 r=12 fspec="$FS" mode=test census=0 commit=NONE psha=x fbsha=x > $D/step.out 2>&1 )
  if [ -f $D/log/m7_step.hbp ]; then
    ( cd $PK && $EV decide out=$D steps=7 g0=100/1 allowed=3 > $D/decide.out 2>&1 )
    ( cd $PK && $EV final out=$D pred=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp steps=7 g0=100/1 allowed=3 mode=test r=12 stop=DECIDED commit=NONE fbsha=x drvsha=x receipt=$D/R.hbp > $D/final.out 2>&1 )
  else
    ( cd $PK && $EV final out=$D pred=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp steps= g0=100/1 allowed=3 mode=test r=12 stop=EVALUATOR_FAILED_m0_7 commit=NONE fbsha=x drvsha=x receipt=$D/R.hbp > $D/final.out 2>&1 )
  fi
  echo "$n | step: $(grep -oE '^STEP\|m0=7\|status=[A-Z]+\|accepted=[0-9]+' $D/step.out) $(grep -oE 'bad=[^|]*' $D/step.out | head -1 | cut -c1-150) $(grep EVAL_ERROR $D/step.out) | final: $(sed -E 's/\|scope=.*accepted_certificates=([0-9]+).*/|accepted=\1/' $D/final.out)"
}
fresh() { local D=/root/floor-v2-verify/evf/$1; rm -rf $D; mkdir -p /root/floor-v2-verify/evf; cp -r $SRC $D; echo $D; }
C1=cert_m7_r12_1_f1.txt; C2=cert_m7_r12_1_f4-3-2-1.txt
D=$(fresh E0); run $D E0_untouched_copy
D=$(fresh E1); echo "# trailing comment" >> $D/RUN7/$C2; run $D E1_cert_appended_after_gate
D=$(fresh E2); sed -i -E 's/^(ROWHASH_ONLY\|m0=7\|sha256=)[0-9a-f]/\10/; s/^(ROWHASH_ONLY\|m0=7\|sha256=)0/\11/' $D/log/m7_rowhash.txt; grep -c ROWHASH_ONLY $D/log/m7_rowhash.txt >/dev/null; run $D E2_rowhash_printed_wrong
D=$(fresh E3); f=$D/log/m7_gate_$C1.txt; n=$(wc -l < $f); head -n $((n/2)) $f > $f.t && mv $f.t $f; run $D E3_gate_log_truncated
D=$(fresh E4); rm $D/log/m7_gate_$C2.txt; run $D E4_gate_log_missing
D=$(fresh E5); sed -i -E 's/(GATE_REQUIRED\|PASS\|.*verifier_sha256=)6/\17/' $D/log/m7_gate_$C1.txt; run $D E5_gate_verifier_sha_altered
D=$(fresh E6); sed -i '/^PEAK_RSS/d' $D/log/m7_cert.txt; run $D E6_cert_PEAK_RSS_removed
D=$(fresh E7); echo x > $D/RUN7/cert_m7_r12_1_fextra.txt; run $D E7_unlisted_cert_file
D=$(fresh E8); sed -i -E 's/^GATE_REQUIRED\|PASS\|/GATE_REQUIRED|REFUSE|/' $D/log/m7_gate_$C2.txt; run $D E8_gate_refuse
D=$(fresh E9); sed -i -E 's/^(VERDICT\|PASS\|lambda_min\(QHQ\) >= )1042273/\11042274/' $D/log/m7_gate_*.txt; run $D E9_verdict_gamma_raised
D=$(fresh E10); sed -i -E '/^GATE\|row_check\|/d' $D/log/m7_gate_$C1.txt; run $D E10_verifier_row_check_gate_line_removed
D=$(fresh E11); sed -i -E 's/^(PEAK_RSS\|kB=)[0-9]+/\12097152/' $D/log/m7_cert.txt; run $D E11_writer_peak_2GB
D=$(fresh E12); sed -i -E 's/^(MEM\|)[0-9]+kB/\12097152kB/' $D/log/m7_gate_$C1.txt; run $D E12_verifier_mem_2GB
