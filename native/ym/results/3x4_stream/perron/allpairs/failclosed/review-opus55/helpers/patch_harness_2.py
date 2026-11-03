# Adds two exhaustive modes to this seat's harness: every bit of a real store's rows, and every bit of its header line.
p = "C:/tmp/opus55/allpairs-review-20261103/fuzz/harness_tail.rs"
s = open(p, encoding="utf-8").read()
new_fns = r'''
    // ------------------------------------------------------------ every bit, with the merkle repaired
    fn call(tmp: &str, cap: usize) -> Result<i32, ()> {
        let args: Vec<String> = vec!["allpairs".into(), tmp.to_string(), "0".into(), cap.to_string()];
        match catch_unwind(AssertUnwindSafe(|| super::real_main(&args))) {
            Ok(Ok(true)) => Ok(0),
            Ok(Ok(false)) => Ok(2),
            Ok(Err(_)) => Ok(1),
            Err(_) => Err(()),
        }
    }

    pub fn bitflip(store: &str, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let (base, line) = load_rows(store);
        let lattice = fld(&line, "L=").unwrap_or("").to_string();
        let nl: u32 = fld(&line, "nl=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let payload = serialize(&base);
        let fields = fields_for(&base, &payload, &sha, &lattice, Some(nl));
        const NAMES: [&str; 7] = ["w", "mag", "cnt", "off_column", "off_value", "diag_column", "diag_value"];
        let mut kind = vec![0u8; payload.len()];
        let mut q = 0usize;
        for (h, r) in base.iter().enumerate() {
            for (b, k) in [(4usize, 0u8), (2, 1), (2, 2)] {
                for _ in 0..b {
                    kind[q] = k;
                    q += 1;
                }
            }
            for e in &r.ent {
                let (c, v) = if e.0 as usize == h { (5u8, 6u8) } else { (3, 4) };
                for t in 0..8 {
                    kind[q] = if t < 4 { c } else { v };
                    q += 1;
                }
            }
        }
        let caps = [470_000_000usize, 100, 13];
        let mut flips = [0u64; 7];
        let mut exits = [[0u64; 3]; 7];
        let mut panics = 0u64;
        let t0 = std::time::Instant::now();
        let mut turn = 0usize;
        for byte in 0..payload.len() {
            for bit in 0..8 {
                let mut p = payload.clone();
                p[byte] ^= 1 << bit;
                let mut f = fields.clone();
                set(&mut f, "payload_merkle", sha.merkle(&p));
                if std::fs::write(tmp, file_bytes(&header_line(&f), &p)).is_err() {
                    return 9;
                }
                let k = kind[byte] as usize;
                flips[k] += 1;
                turn += 1;
                match call(tmp, caps[turn % 3]) {
                    Ok(c) => exits[k][if c == 0 { 0 } else if c == 1 { 1 } else { 2 }] += 1,
                    Err(()) => panics += 1,
                }
            }
        }
        let _ = std::fs::remove_file(tmp);
        for k in 0..7 {
            eprintln!("BITFLIP|field={}|flips={}|exit0={}|exit1={}|exit2={}|json=0", NAMES[k], flips[k], exits[k][0], exits[k][1], exits[k][2]);
        }
        eprintln!("BITFLIP_DONE|store={store}|payload_bytes={}|flips={}|panics={panics}|secs={}|json=0", payload.len(), payload.len() * 8, t0.elapsed().as_secs());
        i32::from(panics > 0)
    }

    pub fn headerflip(store: &str, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let (base, line) = load_rows(store);
        let lattice = fld(&line, "L=").unwrap_or("").to_string();
        let nl: u32 = fld(&line, "nl=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let payload = serialize(&base);
        let fields = fields_for(&base, &payload, &sha, &lattice, Some(nl));
        let hl = header_line(&fields);
        // Which field each byte of the line belongs to. A separator belongs to the field before it.
        let mut names: Vec<String> = Vec::new();
        let mut cur = String::new();
        for part in hl.split('|') {
            let name = part.split('=').next().unwrap_or("").to_string();
            for _ in 0..part.len() + 1 {
                names.push(name.clone());
            }
            cur = name;
        }
        names.truncate(hl.len() + 1);
        names[hl.len()] = "newline".to_string();
        let _ = cur;
        let clean = file_bytes(&hl, &payload);
        let mut tally: Vec<(String, [u64; 4])> = Vec::new();
        let mut panics = 0u64;
        // Every bit of the line and its newline, then every bit of 64 bytes of the zeros after it.
        for byte in 0..hl.len() + 1 + 64 {
            let name = if byte <= hl.len() { names[byte].clone() } else { "zeros_after_newline".to_string() };
            if !tally.iter().any(|t| t.0 == name) {
                tally.push((name.clone(), [0; 4]));
            }
            for bit in 0..8 {
                let mut b = clean.clone();
                b[byte] ^= 1 << bit;
                if std::fs::write(tmp, &b).is_err() {
                    return 9;
                }
                let e = tally.iter_mut().find(|t| t.0 == name).map(|t| &mut t.1);
                match (call(tmp, 470_000_000), e) {
                    (Ok(c), Some(e)) => {
                        e[0] += 1;
                        e[1 + if c == 0 { 0 } else if c == 1 { 1 } else { 2 }] += 1;
                    }
                    _ => panics += 1,
                }
            }
        }
        let _ = std::fs::remove_file(tmp);
        for (name, e) in &tally {
            eprintln!("HEADERFLIP|field={name}|flips={}|exit0={}|exit1={}|exit2={}|json=0", e[0], e[1], e[2], e[3]);
        }
        eprintln!("HEADERFLIP_DONE|store={store}|line_bytes={}|panics={panics}|json=0", hl.len());
        i32::from(panics > 0)
    }

    pub fn main(a: &[String]) -> i32 {
        match a.get(1).map(String::as_str) {
            Some("bitflip") => bitflip(a.get(2).map_or("", String::as_str), a.get(3).map_or("flip.tmp", String::as_str)),
            Some("headerflip") => headerflip(a.get(2).map_or("", String::as_str), a.get(3).map_or("flip.tmp", String::as_str)),
'''
a = """
    pub fn main(a: &[String]) -> i32 {
        match a.get(1).map(String::as_str) {
"""
assert a in s
s = s.replace(a, new_fns)
s = s.replace('eprintln!("usage: fuzz fuzz SEED ITERS TMP | fuzz sweep STORE TMP");', 'eprintln!("usage: fuzz fuzz SEED ITERS TMP | sweep STORE TMP | bitflip STORE TMP | headerflip STORE TMP");')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
