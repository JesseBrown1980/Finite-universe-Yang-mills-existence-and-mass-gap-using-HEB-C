#!/usr/bin/env python3
# Assemble the d2-feshbach-r9 .hbp rows file from the measured row files + script hashes.
# Writes D2-FESHBACH-R9.hbp and D2-FESHBACH-R9.hbp.sha256. json=0.
import hashlib, os, sys
HERE = '/mnt/c/tmp/opus55/ym137-fable5-20261109/d2-feshbach-r9'
OUT = HERE + '/D2-FESHBACH-R9.hbp'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rows(p, prefixes):
    if not os.path.exists(p):
        return ['MISSING|file=%s|missing=1|ok=0|json=0' % os.path.basename(p)]
    out = [l.rstrip('\n') for l in open(p) if l.startswith(prefixes)]
    return out or ['EMPTY|file=%s|rows=0|ok=0|json=0' % os.path.basename(p)]


L = []
L.append('# d2-feshbach-r9: Wilson-sum transition ESTIMATE ground -> reflection-even second level, finite periodic 3x4 S3, r=JB/JE=9, issue #137.')
L.append('# Integer / exact-rational arithmetic only (Python ints, fractions.Fraction); decimals are exact-rational roundings. ESTIMATE, not a certificate.')
L.append('# All Perron-floor-dependent rows are CONDITIONAL on the #131 3x4 Perron source, exactly as #136.')
inputs = [('/mnt/c/tmp/opus55/ym137-fable5-20261109/independent/checker136.py', 'merged #136 checker, git blob 91bd1e80cbfcfb76198966aa177d097ecfbe8143, imported unchanged'),
          ('/mnt/c/tmp/opus55/ym137-fable5-20261109/native/ym/results/3x4_stream/perron/PERRON-RESULT.hbp', 'Perron source pinned by checker git blob cbd42801')]
for p, note in inputs:
    L.append('INPUT|path=%s|sha256=%s|note=%s|json=0' % (p, sha(p), note.replace(' ', '_')))
for s in ('fe_common.py', 'fe_pert.py', 'fe_main.py', 'fe_lower.py', 'fe_k3.py', 'fe_k3lower.py', 'fe_rigor.py',
          'fe_hbp.py', 'run_all.sh', 'run_k3.sh', 'run_k3amp2.sh', 'summarize.sh', 'wait_build.sh'):
    p = HERE + '/' + s
    if os.path.exists(p):
        L.append('SCRIPT|path=%s|sha256=%s|json=0' % (p, sha(p)))
for p in ('k2-graph-cache.pkl', 'k3-graph-cache.pkl'):
    q = HERE + '/' + p
    if os.path.exists(q):
        L.append('CACHE|path=%s|sha256=%s|role=cold_local_cache_not_authority|json=0' % (q, sha(q)))
L += rows(HERE + '/anchor.rows', ('FE_ANCHOR',))
L += rows(HERE + '/pert.out', ('PERT_',))
for s in ('4', '8', '16', '32', '64', '128', '64-scale15'):
    L += rows(HERE + '/run-s%s.rows' % s, ('FE_BEGIN', 'FE_LEVEL', 'FE_AMP', 'FE_NORMS', 'FE_END'))
L += rows(HERE + '/run-s64.rows', ('FE_GRID',))
L += rows(HERE + '/lower-s32.rows', ('FL_',))
for extra in sys.argv[1:]:
    L += rows(HERE + '/' + extra, ('K3_BEGIN', 'K3_EVAL', 'K3_LEVEL', 'K3_AMP', 'K3_END', 'K3L_'))
if os.path.exists(HERE + '/rigor.rows'):
    L += rows(HERE + '/rigor.rows', ('RIGOR', 'FE_SUMMARY'))
data = ('\n'.join(L) + '\n').encode()
open(OUT, 'wb').write(data)
h = hashlib.sha256(data).hexdigest()
open(OUT + '.sha256', 'w').write('%s  D2-FESHBACH-R9.hbp\n' % h)
print('HBP|path=%s|rows=%d|sha256=%s|json=0' % (OUT, len(L), h))
