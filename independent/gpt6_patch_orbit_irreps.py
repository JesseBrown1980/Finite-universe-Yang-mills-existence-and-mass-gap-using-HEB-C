#!/usr/bin/env python3
"""Extend the already patched gauge-only census copy with D3xD4 characters."""
from hashlib import sha256
from pathlib import Path
import sys

def digest(text):
    return sha256(text.encode("utf-8")).hexdigest()

def append(source, extension, receipt):
    s=source.read_text(encoding="utf-8")
    e=extension.read_text(encoding="utf-8")
    assert s.count("fn independent_orbit_census(args: &[String])")==1
    assert s.count("Some(\"orbit-census\") => independent_orbit_census(&args),")==1
    assert s.count("fn main() {")==1
    selector='        Some("orbit-census") => independent_orbit_census(&args),'
    nextselector='        Some("orbit-irreps") => gauge_orbit_irrep_census(&args),'
    assert s.count(selector)==1 and nextselector not in s
    t=s.replace(selector,selector+"\n"+nextselector,1)
    t=t.replace("fn main() {",e+"\nfn main() {",1)
    assert t.count("fn gauge_orbit_irrep_census(args: &[String])")==1
    assert t.count(nextselector)==1
    source.write_text(t,encoding="utf-8")
    receipt.write_text(
        "IRREP_SOURCE_PATCH|schema=D3xD4-CHARACTER-V1|before_sha256=%s|after_sha256=%s|extension_sha256=%s|cli=orbit-irreps|coupling_r=NOT_COMPUTED|r9=HOLD|json=0\n"
        %(digest(s),digest(t),digest(e)),encoding="ascii"
    )
    print(receipt.read_text(),end="")

if __name__=="__main__":
    assert len(sys.argv)==4
    append(*(Path(x) for x in sys.argv[1:]))
