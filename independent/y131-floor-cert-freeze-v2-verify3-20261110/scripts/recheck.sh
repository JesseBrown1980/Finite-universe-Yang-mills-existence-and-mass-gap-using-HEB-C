# second-environment recheck of one receipt (row 125), from a clean export of the freeze commit; the FLOOR_RUN line is never read
set -u
B=/root/floor-v2-final3; RC=$B/recheck; RCPT=$1; RUND=$(dirname $RCPT)
C=78c89c312a265fe4090071fc1abdc7d6eb102e7e; V=independent/y131-floor-cert-freeze-v2-20261110
rm -rf $RC; mkdir -p $RC; git -C /root/floor-v2/repo archive $C | tar -x -C $RC; cd $RC/$V
R=final/PREDICT-S3-3X4-R9-FLOOR-CERT-20261109.hbp
pin() { grep -E "^PIN\|id=$1\|" $R | sed -n 's/.*|value=\([0-9a-f]\{64\}\)|.*/\1/p'; }
psha=$(sha256sum $R | cut -d' ' -f1)
rpsha=$(grep '^TOOL|private_copy=PREDICT' $RCPT | sed -n 's/.*|sha256=\([0-9a-f]*\)|.*/\1/p')
echo "RECORD|clean=$psha|receipt_tool_line=$rpsha|equal=$([ "$psha" = "$rpsha" ] && echo 1 || echo 0)"
for p in "020 work/design/gate_required.sh" "019 work/design/py/cert_gate.py" "021 work/design/py/indep_verify.py"; do set -- $p; echo "TOOLPIN|row=$1|equal=$([ "$(sha256sum $2 | cut -d' ' -f1)" = "$(pin $1)" ] && echo 1 || echo 0)"; done
grep -c '^FLOOR_RUN' $RCPT > /dev/null   # counted only, not read
G=""; U=""; nok=0; n=0
python3 -I -B - $RCPT $RUND "$PWD" <<'PY' > $B/recheck.rows
import sys, re
rc, rund, here = sys.argv[1:4]
for l in open(rc):
    if l.startswith('RECHECK|') or l.startswith('VERDICT_FIELDS|'):
        print(l.rstrip('\n'))
PY
cat $B/recheck.rows | cut -c1-160
while IFS= read -r row; do
  case "$row" in RECHECK\|*) ;; *) continue;; esac
  n=$((n+1))
  cert=$(echo "$row" | sed -n 's/.*|certificate=\([^|]*\)|.*/\1/p'); want=$(echo "$row" | sed -n 's/.*|sha256=\([0-9a-f]*\)|.*/\1/p')
  f=$RUND/$cert; got=$(sha256sum $f | cut -d' ' -f1)
  out=$(bash work/design/gate_required.sh $f); rc=$?
  gr=$(printf '%s\n' "$out" | grep '^GATE_REQUIRED|'); vd=$(printf '%s\n' "$out" | grep '^VERDICT|PASS|')
  gam=$(echo "$vd" | sed -n 's/.*>= \([0-9]*\/[0-9]*\) at r.*/\1/p'); rz=$(printf '%s\n' "$out" | grep '^RITZ_CLASS_VECTOR|' | cut -d'|' -f2)
  echo "RECHECKED|cert=$cert|sha_equal=$([ "$got" = "$want" ] && echo 1 || echo 0)|gate_rc=$rc|gate=$(echo "$gr" | cut -d'|' -f2)|cert_sha_in_gate_equal=$(echo "$gr" | grep -c "cert_sha256=$want")|gamma_verifier=$gam|gamma_row=$(echo "$row" | sed -n 's/.*|gamma=\([^|]*\)|.*/\1/p')|ritz_verifier_own=$rz|ritz_verifier_row=$(echo "$row" | sed -n 's/.*|ritz_verifier=\([^|]*\)|.*/\1/p')|ritz_writer_row=$(echo "$row" | sed -n 's/.*|ritz_writer=\([^|]*\)|.*/\1/p')"
  head -1 $f | tr ' ' '\n' | grep -iE '^(ritz|u=|upper|t=)' | tr '\n' ' '; echo
done < $B/recheck.rows
