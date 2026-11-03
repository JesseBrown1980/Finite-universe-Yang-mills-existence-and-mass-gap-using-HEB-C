# The smallest fix for the merkle-identity race: the two reads of the header block must agree on what the first gave the run.
R = "C:/tmp/opus55/allpairs-review-20261103/hard/"
s = open(R + "src/native/ym/crates/evolvers/src/bin/allpairs.rs", encoding="utf-8").read()
a = """    if field(line, "n=").and_then(number::<usize>) != Some(hdr.n) || field(line, "payload_bytes=").and_then(number::<u64>) != Some(hdr.payload) {
        return Err("header writes n= or payload_bytes= outside canonical form".into());
    }
"""
assert s.count(a) == 1
s = s.replace(a, a + """    if field(line, "payload_merkle=") != Some(hdr.merkle.as_str()) || field(line, "L=").unwrap_or("") != hdr.lattice || field(line, "sector=").unwrap_or("") != hdr.sector {
        return Err("the header changed between two reads".into());
    }
""")
s = s.replace('"../../../torusl/src/', '"' + R + 'src/native/ym/crates/torusl/src/')
open(R + "fix/src/main.rs", "w", encoding="utf-8", newline="\n").write(s)
