# Makes diff/harness_tail.rs from fuzz/harness_tail.rs: the oracle takes the corrected tool's contract, written here with its own code,
# the header generator grows the forms the diff is about, and a mode substitutes every byte of the header line.
src = "C:/tmp/opus55/allpairs-review-20261103/fuzz/harness_tail.rs"
out = "C:/tmp/opus55/allpairs-review-20261103/diff/harness_tail.rs"
s = open(src, encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b)


# Own canonical number, own repeated-key test.
rep("""    fn oracle_codes(line: &str) -> Option<u128> {
        let l = fld(line, "L=")?;
        let (a, b) = l.split_once('x')?;
        let (a, b): (u32, u32) = (a.parse().ok()?, b.parse().ok()?);
        let v = a.checked_mul(b)?;
        let nl: u32 = fld(line, "nl=")?.parse().ok()?;
        if nl != v.checked_mul(2)? {
            return None;
        }
        6u128.checked_pow(v.checked_add(1)?)
    }
""", """    /// Decimal digits only, no leading zero unless the number is 0, within u64.
    fn canon(v: &str) -> Option<u64> {
        if v.is_empty() || !v.bytes().all(|c| c.is_ascii_digit()) || (v.len() > 1 && v.starts_with('0')) || v.len() > 20 {
            return None;
        }
        let mut x = 0u128;
        for c in v.bytes() {
            x = x * 10 + u128::from(c - b'0');
        }
        u64::try_from(x).ok()
    }

    fn canon32(v: &str) -> Option<u32> {
        canon(v).and_then(|x| u32::try_from(x).ok())
    }

    fn has_repeated_key(line: &str) -> bool {
        let mut seen: Vec<&str> = Vec::new();
        for part in line.split('|') {
            if let Some(eq) = part.find('=') {
                let k = &part[..eq];
                if seen.contains(&k) {
                    return true;
                }
                seen.push(k);
            }
        }
        false
    }

    fn oracle_codes(line: &str) -> Option<u128> {
        let l = fld(line, "L=")?;
        let (a, b) = l.split_once('x')?;
        let v = canon32(a)?.checked_mul(canon32(b)?)?;
        if v == 0 || canon32(fld(line, "nl=")?)? != v.checked_mul(2)? {
            return None;
        }
        6u128.checked_pow(v.checked_add(1)?)
    }
""")
rep("""        let Some(n) = fld(&line, "n=").and_then(|v| v.parse::<u64>().ok()) else {
            return Expect::Err("bad_n");
        };
        let Some(payload) = fld(&line, "payload_bytes=").and_then(|v| v.parse::<u64>().ok()) else {
            return Expect::Err("bad_payload");
        };
        if n > u64::from(u32::MAX) {
            return Expect::Err("n_too_large");
        }
        let entries_field = fld(&line, "entries=").and_then(|v| v.parse::<u64>().ok());
        let expected = oracle_codes(&line);
        if n == 0 {
            let truth = Truth { structure_clean: true, ..Truth::default() };
            let entries_ok = entries_field.map_or(true, |v| v == 0);
            let count_ok = expected.map_or(true, |v| v == 0);
            return Expect::Verdict { pass: entries_ok && count_ok, truth: Box::new(truth), n0: true, entries_open: entries_field.is_none(), count_open: expected.is_none(), sym_true: true };
        }
""", """        if has_repeated_key(&line) {
            return Expect::Err("repeated_key");
        }
        let Some(n) = fld(&line, "n=").and_then(canon) else {
            return Expect::Err("bad_n");
        };
        let Some(payload) = fld(&line, "payload_bytes=").and_then(canon) else {
            return Expect::Err("bad_payload");
        };
        if n > u64::from(u32::MAX) {
            return Expect::Err("n_too_large");
        }
        if n == 0 {
            return Expect::Err("n_zero");
        }
        let entries_field = fld(&line, "entries=").and_then(canon);
        let expected = oracle_codes(&line);
""")
rep("""        let entries_ok = entries_field.map_or(true, |v| v == t.entries);
        let count_ok = expected.map_or(true, |v| v == t.sum_w);
""", """        let entries_ok = entries_field == Some(t.entries);
        let count_ok = expected == Some(t.sum_w);
""")
# More header forms, chosen often.
rep("""    fn mutate_header(rng: &mut Rng, f: &mut Vec<(String, String)>, rows_len: usize) {
        match rng.below(19) {
""", """    fn mutate_header(rng: &mut Rng, f: &mut Vec<(String, String)>, rows_len: usize) {
        let keys = ["L", "sector", "n", "nl", "rooms", "entries", "payload_bytes", "stream_bytes", "chunk", "payload_merkle", "keys_sha256", "w_self_adjoint", "json"];
        match rng.below(45) {
            19 | 20 | 21 => {
                // A key repeated, with the same value or another, at a random place.
                let k = *rng.pick(&keys);
                let v = f.iter().find(|e| e.0 == k).map_or("1".to_string(), |e| e.1.clone());
                let v2 = if rng.below(2) == 0 { v } else { rng.below(50).to_string() };
                let at = rng.below(f.len() as u64 + 1) as usize;
                f.insert(at, (k.to_string(), v2));
            }
            22 | 23 | 24 | 25 | 26 => {
                // A number in another written form.
                let k = *rng.pick(&["n", "nl", "entries", "payload_bytes", "L"]);
                let form = rng.below(8);
                if let Some(e) = f.iter_mut().find(|e| e.0 == k) {
                    e.1 = match form {
                        0 => format!("+{}", e.1),
                        1 => format!("0{}", e.1),
                        2 => format!("{} ", e.1),
                        3 => format!(" {}", e.1),
                        4 => format!("-{}", e.1),
                        5 => format!("{}\\r", e.1),
                        6 => format!("{}.0", e.1),
                        _ => String::new(),
                    };
                }
            }
            27 | 28 => {
                // A key that only looks like one the tool reads.
                let k = *rng.pick(&["n", "nl", "entries", "L", "payload_bytes"]);
                if let Some(e) = f.iter_mut().find(|e| e.0 == k) {
                    e.0 = match rng.below(3) {
                        0 => format!("{k} "),
                        1 => format!(" {k}"),
                        _ => k.to_uppercase(),
                    };
                }
            }
            29 | 30 => {
                // The same sites under another label: the gate reads V alone.
                if let Some(e) = f.iter_mut().find(|e| e.0 == "L") {
                    if let Some((a, b)) = e.1.split_once('x') {
                        e.1 = format!("{b}x{a}");
                    }
                }
            }
            31 | 32 => {
                // Fields in another order.
                let i = rng.below(f.len() as u64) as usize;
                let j = rng.below(f.len() as u64) as usize;
                f.swap(i, j);
            }
            33 => f.push(("extra".to_string(), "1".to_string())),
            34 => {
                set(f, "n", "0".into());
                set(f, "entries", "0".into());
            }
            35 => set(f, "n", "00".into()),
            36 => set(f, "n", "4294967295".into()),
            37 => set(f, "n", "18446744073709551616".into()),
            38 => set(f, "entries", "18446744073709551616".into()),
            39 => set(f, "nl", "4294967296".into()),
            40 => set(f, "L", "65536x65536".into()),
            41 => set(f, "L", "0x0".into()),
            42 => {
                set(f, "L", "7x7".into());
                set(f, "nl", "98".into());
            }
            43 => {
                f.retain(|e| e.0 != "entries" && e.0 != "nl" && e.0 != "L");
            }
            44 => {
                set(f, "n", "0".into());
                f.retain(|e| e.0 != "entries" && e.0 != "nl" && e.0 != "L");
                set(f, "payload_bytes", "0".into());
            }
""")
rep("""            if rng.below(5) == 0 {
                mutate_header(&mut rng, &mut fields, rows.len());
            }
""", """            if rng.below(2) == 0 {
                mutate_header(&mut rng, &mut fields, rows.len());
                if rng.below(4) == 0 {
                    mutate_header(&mut rng, &mut fields, rows.len());
                }
            }
""")
# Every byte of the header line replaced by every other byte.
rep("""    pub fn main(a: &[String]) -> i32 {
        match a.get(1).map(String::as_str) {
""", """    pub fn headerbytes(store: &str, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let (base, line) = load_rows(store);
        let lattice = fld(&line, "L=").unwrap_or("").to_string();
        let nl: u32 = fld(&line, "nl=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let payload = serialize(&base);
        let fields = fields_for(&base, &payload, &sha, &lattice, Some(nl));
        let hl = header_line(&fields);
        let mut names: Vec<String> = Vec::new();
        for part in hl.split('|') {
            let name = part.split('=').next().unwrap_or("").to_string();
            for _ in 0..part.len() + 1 {
                names.push(name.clone());
            }
        }
        names.truncate(hl.len() + 1);
        names[hl.len()] = "newline".to_string();
        let clean = file_bytes(&hl, &payload);
        let mut tally: Vec<(String, [u64; 4])> = Vec::new();
        let mut panics = 0u64;
        for byte in 0..=hl.len() {
            let name = names[byte].clone();
            if !tally.iter().any(|t| t.0 == name) {
                tally.push((name.clone(), [0; 4]));
            }
            for value in 0..=255u8 {
                if value == clean[byte] {
                    continue;
                }
                let mut b = clean.clone();
                b[byte] = value;
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
            eprintln!("HEADERBYTES|field={name}|changes={}|exit0={}|exit1={}|exit2={}|json=0", e[0], e[1], e[2], e[3]);
        }
        eprintln!("HEADERBYTES_DONE|store={store}|line_bytes={}|panics={panics}|json=0", hl.len());
        i32::from(panics > 0)
    }

    pub fn main(a: &[String]) -> i32 {
        match a.get(1).map(String::as_str) {
            Some("headerbytes") => headerbytes(a.get(2).map_or("", String::as_str), a.get(3).map_or("flip.tmp", String::as_str)),
""")
open(out, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", out)
# Second step, after clippy and after the first smoke run: ranges in the match, and examples kept in this part's folder.
s = open(out, encoding="utf-8").read()
for a, b in (("19 | 20 | 21 =>", "19..=21 =>"), ("22 | 23 | 24 | 25 | 26 =>", "22..=26 =>"), ('"C:/tmp/opus55/allpairs-review-20261103/fuzz/examples"', '"C:/tmp/opus55/allpairs-review-20261103/diff/fuzz/examples"')):
    assert a in s, a
    s = s.replace(a, b)
open(out, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
