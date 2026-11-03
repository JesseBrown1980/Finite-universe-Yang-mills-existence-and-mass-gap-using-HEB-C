# Fixes two bounds faults in this seat's fuzz generator and limits examples per class. The tool's code is not touched.
p = "C:/tmp/opus55/allpairs-review-20261103/fuzz/harness_tail.rs"
s = open(p, encoding="utf-8").read()
a = """                    let ups: Vec<u32> = rows[i as usize].ent.iter().map(|x| x.0).filter(|&j| j as usize > i as usize && j as usize != h).collect();"""
b = """                    let ups: Vec<u32> = rows[i as usize].ent.iter().map(|x| x.0).filter(|&j| j as usize > i as usize && j as usize != h && (j as usize) < n).collect();"""
assert a in s
s = s.replace(a, b)
a = """            match rng.below(12) {
                0 => {
                    let i = rng.below(payload.len() as u64) as usize;
                    payload[i] ^= 1 << rng.below(8);
                    set(&mut fields, "payload_merkle", sha.merkle(&payload));
                }
                1 => {
                    let i = rng.below(payload.len() as u64) as usize;
                    payload[i] ^= 1 << rng.below(8);
                }
                _ => {}
            }"""
b = """            match rng.below(12) {
                0 if !payload.is_empty() => {
                    let i = rng.below(payload.len() as u64) as usize;
                    payload[i] ^= 1 << rng.below(8);
                    set(&mut fields, "payload_merkle", sha.merkle(&payload));
                }
                1 if !payload.is_empty() => {
                    let i = rng.below(payload.len() as u64) as usize;
                    payload[i] ^= 1 << rng.below(8);
                }
                _ => {}
            }"""
assert a in s
s = s.replace(a, b)
a = """    fn record(tag: &str, file: &[u8], seed: u64, iter: u64, shown: &mut u32, note: String) {
        if *shown < 40 {
            *shown += 1;"""
b = """    fn record(tag: &str, file: &[u8], seed: u64, iter: u64, shown: &mut HashMap<String, u32>, note: String) {
        let seen = shown.entry(tag.to_string()).or_insert(0);
        if *seen < 3 {
            *seen += 1;"""
assert a in s
s = s.replace(a, b)
s = s.replace("seed: u64, iter: u64, shown: &mut u32) {", "seed: u64, iter: u64, shown: &mut HashMap<String, u32>) {")
s = s.replace("let mut shown = 0u32;", "let mut shown: HashMap<String, u32> = HashMap::new();")
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
