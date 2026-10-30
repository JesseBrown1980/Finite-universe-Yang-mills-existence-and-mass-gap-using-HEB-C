#!/usr/bin/env python3
"""Controls for pecmp.py, run on in-memory copies of an original executable (originals never written)."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pecmp
src = sys.argv[1]; a = open(src, 'rb').read(); ex, _ = pecmp.excluded(a)
off = {n: o for n, o, _ in ex}
def mut(fn):
    b = bytearray(a); fn(b); return bytes(b)
def flip(o): return lambda b: b.__setitem__(o, b[o] ^ 0xff)
cases = [
  ('identical', a, 'PASS'),
  ('coff_timestamp_changed', mut(flip(off['coff_timestamp'])), 'PASS'),
  ('debug_timestamp_changed', mut(flip(off['debugdir0_type2_timestamp'])), 'PASS'),
  ('rsds_guid_changed', mut(flip(off['rsds_guid_age'] + 3)), 'PASS'),
  ('pdb_path_char_changed', mut(flip(off['pdb_path'])), 'PASS'),
  ('byte_outside_changed', mut(flip(0x400)), 'MISMATCH'),
  ('byte_next_to_coff_ts', mut(flip(off['coff_timestamp'] + 4)), 'MISMATCH'),
  ('size_differs', a + b'\0', 'INCONCLUSIVE'),
]
ok = 0
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'x.exe')
    for name, data, want in cases:
        open(p, 'wb').write(data); got, _ = pecmp.compare('control', src, p)
        good = int(got == want); ok += good
        print(f'PECMP_CONTROL|case={name}|want={want}|got={got}|ok={good}|json=0')
print(f'PECMP_CONTROLS_TOTAL|cases={len(cases)}|ok={ok}|result={"PASS" if ok == len(cases) else "FAIL"}|json=0')
