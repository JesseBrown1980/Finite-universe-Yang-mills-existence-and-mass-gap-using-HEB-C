#!/usr/bin/env python3
"""Inject full sparse core graph CLI only into pinned temporary Rust checkout."""
from pathlib import Path
from hashlib import sha256
import sys

def patch(source,extra,receipt):
    original=source.read_text(encoding="utf-8")
    code=extra.read_text(encoding="utf-8")
    needle='        Some("orbit-irreps") => gauge_orbit_irrep_census(&args),'
    assert original.count(needle)==1
    assert original.count("fn main() {")==1
    assert original.count("fn full_gauge_sparse_r12(")==0
    assert code.count("fn full_gauge_sparse_r12(")==1
    updated=original.replace(needle,needle+'\n        Some("gauge-core-r12") => full_gauge_sparse_r12(&args),',1)
    updated=updated.replace("fn main() {",code+"\nfn main() {",1)
    source.write_text(updated,encoding="utf-8")
    h=lambda s:sha256(s.encode("utf-8")).hexdigest()
    receipt.write_text(
        "FULL_R12_CORE_PATCH|before_sha256=%s|after_sha256=%s|extension_sha256=%s|cli=gauge-core-r12|r=12|r9=HOLD|json=0\n"%
        (h(original),h(updated),h(code)),encoding="ascii"
    )

if __name__=="__main__":
    assert len(sys.argv)==4
    patch(*(Path(arg) for arg in sys.argv[1:]))
