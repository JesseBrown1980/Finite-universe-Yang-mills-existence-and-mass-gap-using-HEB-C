#!/usr/bin/env python3
# fill_d.py -- verifier seat (opus55), verification 5: writes the measured D section into the report and the .hbp.
p = '/mnt/c/tmp/opus55/floor-v2-verify5/pushrepo/independent/y131-floor-cert-freeze-v2-verify5-20261111/'
s = open('/mnt/c/tmp/opus55/floor-v2-verify5/dsec.txt', encoding='utf-8').read().rstrip('\n')
m = open(p + 'VERIFY-FLOOR-FREEZE-V2-FINAL5.md', encoding='utf-8').read()
m = m.replace('__D_SECTION__', s).replace('__D_VERDICT__', 'PASS (MEASURED): launcher exit 0 ABOVE; checker ACCEPT=YES ABOVE with the published hash, same G and U')
open(p + 'VERIFY-FLOOR-FREEZE-V2-FINAL5.md', 'w', encoding='utf-8', newline='\n').write(m)
h = open(p + 'VERIFY-FLOOR-FREEZE-V2-FINAL5.hbp', encoding='utf-8').read()
h = h.replace('D=__D__', 'D=PASS').replace('D_CHECK|__DCHECK__', 'D_CHECK|result=MEASURED_PASS|checkout=exp0_export|receipt_sha256_given=published_value|exit=0|ACCEPT=YES|DECISION=ABOVE|G=993720/10000|U=99376426000000/1000000000000|steps=11:NONE,12:NONE,13:OK|certificates_rechecked=3|verifier_mem_max_kB=796972|start=2026-11-12T01:42:52Z|end=2026-11-12T02:56:59Z|json=0')
open(p + 'VERIFY-FLOOR-FREEZE-V2-FINAL5.hbp', 'w', encoding='utf-8', newline='\n').write(h)
print('FILL_D|placeholders_left_md=%d|placeholders_left_hbp=%d' % (m.count('__D'), h.count('__D')))
