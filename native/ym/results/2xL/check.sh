#!/bin/bash
# Re-derive every 2xL result from the committed backend shards (no tool runs):
# flat-state bound per lattice, all point certificates (compared with the
# committed certs_*.hbp), and the monotone-cell + ray continuation r in [9, inf).
set -euo pipefail
cd "$(dirname "$0")"
P=../../python
for L in "2 2" "2 3" "2 4"; do set -- $L; lat=$1x$2; d=$1$2/shards; u=$((3*2*$1*$2))
  f() { cat $d/flatcomp_$1_$2_$3_$4/run.hbp; }
  f $1 $2 1 1 | grep -q "|flat_states=7|flat_electric_diag=\[$u,$u,$u,$u,$u,$u,$u\]|flat_diag_max=$u|flat_flat_couplings=0|"
  f $1 $2 -1 -1 | grep -q "|flat_states=1|flat_electric_diag=\[$u\]|flat_diag_max=$u|flat_flat_couplings=0|"
  f $1 $2 1 -1 | grep -q "|flat_states=0|"; f $1 $2 -1 1 | grep -q "|flat_states=0|"
  for a in $d/*/; do grep -q "^ANCHOR|spec=" $a/run.anchor; done
  python3 $P/rebuild_from_shards.py $d $1 $2 > /tmp/certs_$lat.new
  cmp certs_$lat.hbp /tmp/certs_$lat.new
  [ "$(grep -c '^SHELL_GAP_CERT|.*|result=PASS|' certs_$lat.hbp)" = 6 ]
  python3 $P/monotone_cells.py --lattice $lat --ray $((u*1000000)) certs_$lat.hbp | tail -1 | tee /tmp/mono_$lat
  grep -q "|r_range=\[9,infinity\]|cells=5|ray=1|.*|result=PASS|" /tmp/mono_$lat
done
echo "CHECK_2XL|lattices=2x2,2x3,2x4|points=18|flat_bound=PASS|certificates_rebuilt_identical=PASS|continuation=[9,infinity)|result=PASS|json=0"
