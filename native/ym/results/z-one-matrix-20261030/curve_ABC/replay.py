#!/usr/bin/env python3
"""Byte-exact replay in temporary isolated folders. Existing evidence never overwritten."""
from pathlib import Path
import subprocess
import tempfile
import shutil
root = Path(__file__).resolve().parent
for case in ('B', 'A', 'C'):
    with tempfile.TemporaryDirectory(prefix=f'dict_{case.lower()}_') as name:
        dest=Path(name)
        script={'B':'test_b.py','A':'test_a.py','C':'test_c.py'}[case]
        shutil.copyfile(root/case/script, dest/script)
        if case=='C':shutil.copyfile(root/case/'EVIDENCE.hbp',dest/'EVIDENCE.hbp')
        subprocess.run(['python3',str(dest/script)],check=True,capture_output=True,text=True)
        recorded=(root/case/'RESULT.hbp').read_bytes()
        replay=(dest/'RESULT.hbp').read_bytes()
        assert recorded==replay, case + ': mismatch'
        print(f'REPLAY|case={case}|byte_identical=1|json=0')
