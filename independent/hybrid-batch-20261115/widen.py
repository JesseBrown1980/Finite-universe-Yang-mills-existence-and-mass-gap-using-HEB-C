# Writes widened copies of the two hybrid programs, beside the originals, which stay as they are.
#
# Why: both programs order the lattice symmetries by a pattern of plaquette classes packed at 2 bits per plaquette into a u64, which holds 32
# plaquettes. On 6 x 6 (36 plaquettes) ritz stops with "attempt to shift left with overflow" (ritz.rs:181) and hybridcheck refuses with "at most 32
# plaquettes". The copies pack the pattern into a u128 (64 plaquettes). The configuration key is a base-6 number of P + 1 digits in a u128, which
# holds 49 digits, so the copies admit tori of up to 48 plaquettes. For P <= 32 a u128 pattern compares exactly as the u64 one did, so every
# earlier result is unchanged; the workflow checks that on 4 x 4.
#
# usage: widen.py RITZ_IN RITZ_OUT HYBRIDCHECK_IN HYBRIDCHECK_OUT
# Every replacement must match exactly once, or the script stops.
import sys


def patch(path_in, path_out, edits):
    s = open(path_in, encoding="utf-8").read()
    for old, new in edits:
        if s.count(old) != 1:
            sys.exit("WIDEN_REFUSE|file=%s|pattern_count=%d|pattern=%s|json=0" % (path_in, s.count(old), old[:50].replace("|", "/")))
        s = s.replace(old, new)
    open(path_out, "w", encoding="utf-8", newline="\n").write(s)
    print("WIDEN|in=%s|out=%s|edits=%d|json=0" % (path_in, path_out, len(edits)))


patch(sys.argv[1], sys.argv[2], [
    ("        let mut low = u64::MAX;\n        sc.cand.clear();", "        let mut low = u128::MAX;\n        sc.cand.clear();"),
    ("            let mut pat: u64 = 0;", "            let mut pat: u128 = 0;"),
    ("                pat |= u64::from(*c) << (2 * a.plaq[p]);", "                pat |= u128::from(*c) << (2 * a.plaq[p]);"),
])
patch(sys.argv[3], sys.argv[4], [
    ("        if lx < 3 || ly < 3 || lx * ly > 32 {\n            return Err(\"each side at least 3, at most 32 plaquettes\".into());",
     "        if lx < 3 || ly < 3 || lx * ly > 48 {\n            return Err(\"each side at least 3, at most 48 plaquettes\".into());"),
    ("        let mut top = u64::MAX;", "        let mut top = u128::MAX;"),
    ("            let mut pattern = 0u64;", "            let mut pattern = 0u128;"),
    ("                pattern |= u64::from(k) << (2 * u32::from(s.plaq[q as usize]));", "                pattern |= u128::from(k) << (2 * u32::from(s.plaq[q as usize]));"),
])
