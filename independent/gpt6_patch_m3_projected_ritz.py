#!/usr/bin/env python3
"""Patch only the experimental full-gauge research checkout; never main."""
from pathlib import Path
from hashlib import sha256
import sys

def fhash(data):
    return sha256(data.encode("utf-8")).hexdigest()

def run(source,extension,receipt):
    original=source.read_text(encoding="utf-8")
    new_code=extension.read_text(encoding="utf-8")
    assert original.count("fn gauge_orbit_irrep_census(args: &[String])")==1
    assert original.count("fn gauge_only_neighbours(")==1
    assert original.count('        Some("orbit-irreps") => gauge_orbit_irrep_census(&args),')==1
    assert original.count("fn main() {")==1
    assert original.count("fn gauge_m3_projected_ritz(")==0
    assert "fn gauge_m3_projected_ritz(" in new_code
    needle='        Some("orbit-irreps") => gauge_orbit_irrep_census(&args),'
    updated=original.replace(needle,needle+'\n        Some("m3-project-ritz") => gauge_m3_projected_ritz(&args),',1)
    updated=updated.replace("fn main() {",new_code+"\nfn main() {",1)
    assert updated.count("fn gauge_m3_projected_ritz(")==1
    source.write_text(updated,encoding="utf-8")
    receipt.write_text(
        "M3_SOURCE_PATCH|before_sha256=%s|after_sha256=%s|extension_sha256=%s|cli=m3-project-ritz|r=12|magnetic_support=3|r9=HOLD|json=0\n"%
        (fhash(original),fhash(updated),fhash(new_code)),encoding="ascii"
    )
    print(receipt.read_text(encoding="ascii"),end="")

if __name__=="__main__":
    assert len(sys.argv)==4
    run(*(Path(x) for x in sys.argv[1:]))
