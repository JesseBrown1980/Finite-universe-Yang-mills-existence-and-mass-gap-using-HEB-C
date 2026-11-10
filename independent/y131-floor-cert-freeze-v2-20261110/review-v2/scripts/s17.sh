A=/root/floor-v2-verify/arch/independent/y131-floor-cert-freeze-v2-20261110
grep -n 'FREEZE|' $A/work/design/rs/src/main.rs | cut -c1-300
grep -n -E 'freeze=|pred=' $A/work/design/rs/src/main.rs | cut -c1-250 | head
echo ===
grep -n -E 'FREEZE\||rows-only|ROWS_ONLY|^ *print\("MEM|MEM\|' $A/work/design/py/cert_gate.py | cut -c1-300
echo ===
grep -n -E 'r_policy|def .*policy|near|9\b' $A/work/design/py/cert_gate.py | head -20 | cut -c1-200
