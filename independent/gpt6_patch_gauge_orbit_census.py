#!/usr/bin/env python3
"""Create a strictly isolated gauge-only census binary from pinned Rust source.

The patched copy enumerates all global S3 gauge orbits at cutoff m0=9
instead of collapsing the 48 lattice symmetries; it adds only the new
"orbit-census" CLI and never calls the certificate-writer or any coupling
selection. No change is made to the original repository or r=9 launcher.
"""
from hashlib import sha256
from pathlib import Path
import sys

def digest(b):
    return sha256(b).hexdigest()

def patch(source, extension, receipt):
    original=source.read_text(encoding="utf-8")
    extra=extension.read_text(encoding="utf-8")
    minimum="if tab.is_min(u, &z) {\n                    out.push(Tab::encode(&z));"
    replacement="if tab.orbit_min(&z) == Tab::encode(&z) {\n                    out.push(Tab::encode(&z));"
    assert original.count(minimum)==1
    assert original.count(replacement)==0
    assert original.count("fn main() {")==1
    selector='        Some("census") => census(&args),'
    assert original.count(selector)==1
    updated=original.replace(minimum,replacement,1)
    updated=updated.replace(selector,selector+"\n        Some(\"orbit-census\") => independent_orbit_census(&args),",1)
    updated=updated.replace("fn main() {",extra+"\nfn main() {",1)
    assert updated.count("Some(\"orbit-census\")")==1
    assert updated.count("fn independent_orbit_census(args: &[String])")==1
    assert updated.count("if tab.orbit_min(&z) == Tab::encode(&z)")==1
    source.write_text(updated,encoding="utf-8")
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(
        "SOURCE_PATCH|schema=R12-GAUGE-ORBIT-V1|original_sha256=%s|patched_sha256=%s|extension_sha256=%s|changes=enumerator_condition_and_orbit_census_cli_only|m0=9|coupling_r=NOT_USED|r9=HOLD|json=0\n"
        %(digest(original.encode()),digest(updated.encode()),digest(extra.encode())),
        encoding="ascii"
    )
    print(receipt.read_text(),end="")

if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("python3 -B independent/gpt6_patch_gauge_orbit_census.py COPY_MAIN_RS EXTENSION_RS RECEIPT_HBP")
    patch(*(Path(x) for x in sys.argv[1:]))
