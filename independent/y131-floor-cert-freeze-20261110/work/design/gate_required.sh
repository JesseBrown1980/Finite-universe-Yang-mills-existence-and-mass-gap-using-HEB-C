#!/bin/bash
# FLOOR FIX-1: the REQUIRED independent gate. No gamma from floorcert may be quoted unless this prints
# GATE_REQUIRED|PASS for the written certificate file: the verifier must be the pinned py/cert_gate.py, it must end in
# VERDICT|PASS, and its own row hash must equal the rowhash= field of the certificate header (the writer's).
# Usage: gate_required.sh CERT [--freeze-commit C --prediction FILE --prediction-sha256 H]   (the last three only at r = 9)
set -u
D=/tmp/claude-0/-home-user/b2fb539a-cb4d-5f0b-a22f-ca1a7fcb500d/scratchpad/floor/work/design
PIN=6043d0897250a7c873a3c1c553a52a1e38f99046ba5131375fb3f3dddbe02889
CERT=$1
shift
got=$(sha256sum "$D/py/cert_gate.py" | cut -d' ' -f1)
if [ "$got" != "$PIN" ]; then
  echo "GATE_REQUIRED|REFUSE|verifier sha256 $got is not the pinned $PIN"
  exit 1
fi
csha=$(sha256sum "$CERT" | cut -d' ' -f1)
out=$(python3 -I -B "$D/py/cert_gate.py" "$CERT" "$@")
rc=$?
printf '%s\n' "$out"
hdr=$(head -n1 "$CERT" | tr ' ' '\n' | sed -n 's/^rowhash=//p')
own=$(printf '%s\n' "$out" | sed -n 's/^ROWHASH|[^|]*|sha256=\([0-9a-f]*\)|.*$/\1/p')
verdict=$(printf '%s\n' "$out" | grep '^VERDICT|' | tail -n1)
case "$verdict" in
  "VERDICT|PASS|"*) vp=1 ;;
  *) vp=0 ;;
esac
if [ "$rc" -eq 0 ] && [ "$vp" -eq 1 ] && [ -n "$own" ] && [ "$own" = "$hdr" ]; then
  echo "GATE_REQUIRED|PASS|cert=$CERT|cert_sha256=$csha|rowhash=$own|verifier_sha256=$got"
  exit 0
fi
echo "GATE_REQUIRED|REFUSE|cert=$CERT|cert_sha256=$csha|verifier_exit=$rc|header_rowhash=$hdr|verifier_rowhash=$own|$verdict"
exit 1
