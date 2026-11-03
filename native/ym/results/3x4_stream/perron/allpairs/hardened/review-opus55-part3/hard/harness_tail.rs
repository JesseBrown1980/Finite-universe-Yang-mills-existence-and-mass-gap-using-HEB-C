
// ---------------------------------------------------------------------------------------------------------------------
// Second seat's harness, third part: appended to an unchanged copy of allpairs.rs at 9c2c7e6, with main renamed tool_main and the #[path] lines made absolute.
// The oracle shares no code with the tool: its own SHA-256, header and row parser, canonical numbers, sizes rule, pair accounting by hash map, gates and identity.
// It calls the tool's run_tool with a table of its choosing, so every gate can be seen alone, and run() for the counters, on clean and malformed rows alike.
//
//   fuzz fuzz SEED ITERATIONS TMPFILE          random stores at random caps
//   fuzz sweep STORE TMPFILE                   one fault at a time on every off-diagonal entry of a real store
//   fuzz blockflip STORE TMPFILE               every bit of the real 4096-byte block, against the real TRUSTED table
//   fuzz headerbytes STORE TMPFILE             every byte of the real header line, to each other value, against the real TRUSTED table
//
// Exit 1 when the tool and the oracle disagree. Integer only, json=0.

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let code = review::main(&a);
    std::process::exit(code);
}

mod review {
    use std::collections::HashMap;
    use std::panic::{catch_unwind, AssertUnwindSafe};

    const MIB: u64 = 1 << 20;

    pub struct Rng(u64);
    impl Rng {
        fn next(&mut self) -> u64 {
            self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
            let mut z = self.0;
            z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
            z ^ (z >> 31)
        }
        fn below(&mut self, n: u64) -> u64 {
            self.next() % n.max(1)
        }
        fn pick<'a, T>(&mut self, v: &'a [T]) -> &'a T {
            &v[self.below(v.len() as u64) as usize]
        }
    }

    fn sha_tables() -> ([u32; 64], [u32; 8]) {
        let mut primes: Vec<u64> = Vec::new();
        let mut c = 2u64;
        while primes.len() < 64 {
            if primes.iter().all(|p| c % p != 0) {
                primes.push(c);
            }
            c += 1;
        }
        let root = |v: u128, e: u32| {
            let (mut lo, mut hi) = (0u128, 1u128 << 37);
            while hi - lo > 1 {
                let m = (lo + hi) / 2;
                if m.pow(e) <= v {
                    lo = m;
                } else {
                    hi = m;
                }
            }
            lo
        };
        let mut k = [0u32; 64];
        let mut h = [0u32; 8];
        for (i, s) in k.iter_mut().enumerate() {
            *s = (root(u128::from(primes[i]) << 96, 3) & 0xFFFF_FFFF) as u32;
        }
        for (i, s) in h.iter_mut().enumerate() {
            *s = (root(u128::from(primes[i]) << 64, 2) & 0xFFFF_FFFF) as u32;
        }
        (k, h)
    }

    pub struct Sha256 {
        k: [u32; 64],
        h0: [u32; 8],
    }

    impl Sha256 {
        pub fn new() -> Sha256 {
            let (k, h0) = sha_tables();
            Sha256 { k, h0 }
        }
        pub fn hex(&self, d: &[u8]) -> String {
            let mut h = self.h0;
            let mut tail = d[d.len() - d.len() % 64..].to_vec();
            tail.push(0x80);
            while tail.len() % 64 != 56 {
                tail.push(0);
            }
            tail.extend_from_slice(&((d.len() as u64).wrapping_mul(8)).to_be_bytes());
            let body = &d[..d.len() - d.len() % 64];
            for b in body.chunks_exact(64).chain(tail.chunks_exact(64)) {
                let mut w = [0u32; 64];
                for (i, c) in b.chunks_exact(4).enumerate() {
                    w[i] = u32::from_be_bytes([c[0], c[1], c[2], c[3]]);
                }
                for i in 16..64 {
                    let (a, e) = (w[i - 15], w[i - 2]);
                    let s0 = a.rotate_right(7) ^ a.rotate_right(18) ^ (a >> 3);
                    let s1 = e.rotate_right(17) ^ e.rotate_right(19) ^ (e >> 10);
                    w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
                }
                let mut v = h;
                for (wi, ki) in w.iter().zip(self.k.iter()) {
                    let bs1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
                    let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
                    let t1 = v[7].wrapping_add(bs1).wrapping_add(ch).wrapping_add(*ki).wrapping_add(*wi);
                    let bs0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
                    let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
                    let t2 = bs0.wrapping_add(maj);
                    v = [t1.wrapping_add(t2), v[0], v[1], v[2], v[3].wrapping_add(t1), v[4], v[5], v[6]];
                }
                for (x, y) in h.iter_mut().zip(v) {
                    *x = x.wrapping_add(y);
                }
            }
            let mut s = String::with_capacity(64);
            for w in h {
                for b in w.to_be_bytes() {
                    s.push(char::from_digit(u32::from(b >> 4), 16).unwrap_or('?'));
                    s.push(char::from_digit(u32::from(b & 15), 16).unwrap_or('?'));
                }
            }
            s
        }
        pub fn merkle(&self, payload: &[u8]) -> String {
            let mut hx = String::new();
            for c in payload.chunks(16 << 20) {
                hx.push_str(&self.hex(c));
            }
            self.hex(hx.as_bytes())
        }
    }

    #[derive(Clone)]
    pub struct R {
        w: u32,
        mag: u16,
        ent: Vec<(u32, i32)>,
    }

    fn gcd(a: u32, b: u32) -> u32 {
        if b == 0 {
            a
        } else {
            gcd(b, a % b)
        }
    }

    fn clean_store(rng: &mut Rng, n: usize, target: Option<u64>) -> Vec<R> {
        let mut w: Vec<u32> = (0..n).map(|_| 1 + rng.below(12) as u32).collect();
        if let Some(t) = target {
            w = vec![1; n];
            let mut left = t - n as u64;
            while left > 0 {
                let i = rng.below(n as u64) as usize;
                let add = 1 + rng.below(left.min(97));
                w[i] += add as u32;
                left -= add;
            }
        }
        let mut edges: HashMap<(usize, usize), i32> = HashMap::new();
        for a in 0..n {
            let b = (a + 1) % n;
            if a != b {
                edges.insert((a.min(b), a.max(b)), 1 + rng.below(3) as i32);
            }
        }
        for _ in 0..rng.below(2 * n as u64) {
            let (a, b) = (rng.below(n as u64) as usize, rng.below(n as u64) as usize);
            if a != b {
                edges.insert((a.min(b), a.max(b)), 1 + rng.below(3) as i32);
            }
        }
        let mut rows: Vec<R> = (0..n).map(|h| R { w: w[h], mag: if rng.below(5) == 0 { 0 } else { 3 + rng.below(9) as u16 }, ent: Vec::new() }).collect();
        for (&(a, b), &k) in &edges {
            let g = gcd(w[a], w[b]);
            rows[a].ent.push((b as u32, -((w[b] / g) as i32) * k));
            rows[b].ent.push((a as u32, -((w[a] / g) as i32) * k));
        }
        for (h, r) in rows.iter_mut().enumerate() {
            let s: i32 = r.ent.iter().map(|e| e.1).sum();
            r.ent.push((h as u32, -s));
            r.ent.sort_unstable_by_key(|e| e.0);
        }
        rows
    }

    pub fn serialize(rows: &[R]) -> Vec<u8> {
        let mut p = Vec::new();
        for r in rows {
            p.extend_from_slice(&r.w.to_le_bytes());
            p.extend_from_slice(&r.mag.to_le_bytes());
            p.extend_from_slice(&(r.ent.len() as u16).to_le_bytes());
            for (j, z) in &r.ent {
                p.extend_from_slice(&j.to_le_bytes());
                p.extend_from_slice(&z.to_le_bytes());
            }
        }
        p
    }

    fn file_bytes(line: &str, payload: &[u8]) -> Vec<u8> {
        let mut b = line.as_bytes().to_vec();
        b.push(b'\n');
        if b.len() < 4096 {
            b.resize(4096, 0);
        }
        b.extend_from_slice(payload);
        b
    }

    fn header_line(fields: &[(String, String)]) -> String {
        let mut s = String::from("YMROOMHDR");
        for (k, v) in fields {
            s.push('|');
            s.push_str(k);
            s.push('=');
            s.push_str(v);
        }
        s
    }

    fn fld<'a>(line: &'a str, key: &str) -> Option<&'a str> {
        line.split('|').find_map(|kv| kv.strip_prefix(key))
    }

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

    /// What the rows hold, by exact rule: on each pair (lo, hi), the k-th lower entry answers the k-th upper entry, in stored order.
    #[derive(Default, Clone, PartialEq, Eq, Debug)]
    pub struct Counts {
        rows: u64,
        entries: u64,
        diag: u64,
        upper: u64,
        lower: u64,
        not_ascending: u64,
        out_of_range: u64,
        zero_z: u64,
        positive_off: u64,
        row_sum_nonzero: u64,
        zero_weight: u64,
        missing_diag: u64,
        sum_w: u128,
        flats: u64,
        mismatch: u64,
        lonely_lower: u64,
        lonely_upper: u64,
        repeated: u64,
        found: u64,
        answered: u64,
        row_bytes: u64,
        uppers: Vec<u64>,
    }

    impl Counts {
        fn structure_clean(&self) -> bool {
            self.not_ascending == 0 && self.out_of_range == 0 && self.zero_z == 0 && self.positive_off == 0 && self.row_sum_nonzero == 0 && self.zero_weight == 0 && self.missing_diag == 0
        }
        fn pairs_clean(&self) -> bool {
            self.mismatch == 0 && self.lonely_lower == 0 && self.lonely_upper == 0 && self.repeated == 0 && self.upper == self.lower
        }
    }

    pub fn count_rows(pl: &[u8], n: u64) -> Option<Counts> {
        let mut t = Counts::default();
        let mut p = 0usize;
        type Sides = (Vec<i64>, Vec<i64>);
        let mut pairs: HashMap<(u32, u32), Sides> = HashMap::new();
        for h in 0..n {
            if p + 8 > pl.len() {
                return None;
            }
            let w = u32::from_le_bytes([pl[p], pl[p + 1], pl[p + 2], pl[p + 3]]);
            let mag = u16::from_le_bytes([pl[p + 4], pl[p + 5]]);
            let cnt = usize::from(u16::from_le_bytes([pl[p + 6], pl[p + 7]]));
            if p + 8 + 8 * cnt > pl.len() {
                return None;
            }
            let mut q = p + 8;
            let mut prev: Option<u32> = None;
            let mut sum = 0i64;
            let mut has_diag = false;
            let mut row_upper = 0u64;
            t.rows += 1;
            t.sum_w += u128::from(w);
            t.zero_weight += u64::from(w == 0);
            t.flats += u64::from(mag == 0);
            for _ in 0..cnt {
                let j = u32::from_le_bytes([pl[q], pl[q + 1], pl[q + 2], pl[q + 3]]);
                let z = i32::from_le_bytes([pl[q + 4], pl[q + 5], pl[q + 6], pl[q + 7]]);
                q += 8;
                t.entries += 1;
                t.not_ascending += u64::from(prev.is_some_and(|x| j <= x));
                prev = Some(j);
                t.out_of_range += u64::from(u64::from(j) >= n);
                t.zero_z += u64::from(z == 0);
                t.positive_off += u64::from(u64::from(j) != h && z > 0);
                sum += i64::from(z);
                let v = i128::from(w) * i128::from(z);
                let v64 = i64::try_from(v).unwrap_or(i64::MAX);
                match u64::from(j).cmp(&h) {
                    std::cmp::Ordering::Equal => {
                        t.diag += 1;
                        has_diag = true;
                    }
                    std::cmp::Ordering::Greater => {
                        t.upper += 1;
                        row_upper += 1;
                        pairs.entry((h as u32, j)).or_default().0.push(v64);
                    }
                    std::cmp::Ordering::Less => {
                        t.lower += 1;
                        pairs.entry((j, h as u32)).or_default().1.push(v64);
                    }
                }
            }
            t.row_sum_nonzero += u64::from(sum != 0);
            t.uppers.push(row_upper);
            t.missing_diag += u64::from(!has_diag);
            p = q;
        }
        t.row_bytes = p as u64;
        for (u, l) in pairs.values() {
            if u.is_empty() {
                t.lonely_lower += l.len() as u64;
                continue;
            }
            t.found += l.len() as u64;
            let m = u.len().min(l.len());
            t.answered += m as u64;
            t.repeated += (l.len() - m) as u64;
            t.lonely_upper += (u.len() - m) as u64;
            t.mismatch += (0..m).filter(|&k| u[k] != l[k]).count() as u64;
        }
        Some(t)
    }

    /// The windows rule from the brief, on any rows: a window closes before a row that takes it past cap upper entries or max(cap, 2^20) rows, unless that row is its first.
    fn rule_windows(uppers: &[u64], cap: usize) -> Vec<(usize, usize)> {
        let cap = (cap.clamp(1, 4_000_000_000)) as u64;
        let row_cap = cap.max(1 << 20);
        let mut out = Vec::new();
        let (mut start, mut ent, mut rows) = (0usize, 0u64, 0u64);
        for (h, &c) in uppers.iter().enumerate() {
            if h > start && (ent + c > cap || rows >= row_cap) {
                out.push((start, h));
                start = h;
                ent = 0;
                rows = 0;
            }
            ent += c;
            rows += 1;
        }
        out.push((start, uppers.len()));
        out
    }

    pub enum Expect {
        Err(&'static str),
        Verdict { pass: bool, counts: Box<Counts>, gates: [u8; 5], identity_open: bool },
    }

    /// (line, block hash), as the tool's table holds them.
    type Row = (String, String);

    pub fn oracle(file: &[u8], sha: &Sha256, table: &[Row]) -> Expect {
        if file.len() < 4096 {
            return Expect::Err("short_header");
        }
        let block = &file[..4096];
        let Some(eol) = block.iter().position(|&b| b == b'\n') else {
            return Expect::Err("no_newline");
        };
        let line = String::from_utf8_lossy(&block[..eol]).to_string();
        if !line.starts_with("YMROOMHDR|") || fld(&line, "w_self_adjoint=") != Some("PASS") {
            return Expect::Err("not_header");
        }
        if has_repeated_key(&line) {
            return Expect::Err("repeated_key");
        }
        let Some(n) = fld(&line, "n=").and_then(canon) else {
            return Expect::Err("bad_n");
        };
        let Some(payload) = fld(&line, "payload_bytes=").and_then(canon) else {
            return Expect::Err("bad_payload");
        };
        if n == 0 {
            return Expect::Err("n_zero");
        }
        if n > u64::from(u32::MAX) {
            return Expect::Err("n_too_large");
        }
        let Some(rooms) = fld(&line, "rooms=").and_then(canon) else {
            return Expect::Err("bad_rooms");
        };
        let Some(stream) = fld(&line, "stream_bytes=").and_then(canon) else {
            return Expect::Err("bad_stream");
        };
        if payload.checked_add(4096) != Some(stream) || stream % MIB != 0 {
            return Expect::Err("stream_layout");
        }
        let Some(used) = rooms.checked_mul(8).filter(|&u| u <= payload) else {
            return Expect::Err("rooms_do_not_fit");
        };
        if payload - used >= MIB || n > rooms || stream > file.len() as u64 {
            return Expect::Err("sizes");
        }
        let pl = &file[4096..stream as usize];
        let Some(t) = count_rows(pl, n) else {
            return Expect::Err("rows_past_payload");
        };
        if sha.merkle(pl) != fld(&line, "payload_merkle=").unwrap_or("") {
            return Expect::Err("merkle");
        }
        let padding = &pl[t.row_bytes as usize..];
        let padding_nonzero = padding.iter().filter(|&&b| b != 0).count();
        let entries_gate = fld(&line, "entries=").and_then(canon) == Some(t.entries);
        let count_gate = oracle_codes(&line) == Some(t.sum_w);
        let rooms_gate = rooms == t.rows + t.entries;
        let padding_gate = rooms * 8 == t.row_bytes && padding_nonzero == 0 && (padding.len() as u64) < MIB;
        let block_hash = sha.hex(block);
        let identity_pass = table.iter().any(|r| r.1 == block_hash && r.0 == line);
        let lattice = fld(&line, "L=");
        let identity_open = !identity_pass && !table.iter().any(|r| fld(&r.0, "L=") == lattice);
        let gates = [u8::from(entries_gate), u8::from(count_gate), u8::from(rooms_gate), u8::from(padding_gate), u8::from(identity_pass)];
        let pass = t.structure_clean() && t.pairs_clean() && gates.iter().all(|&g| g == 1);
        Expect::Verdict { pass, counts: Box::new(t), gates, identity_open }
    }

    #[derive(Default)]
    struct Tally {
        cases: u64,
        exit0: u64,
        exit1: u64,
        exit2: u64,
        disagree_verdict: u64,
        disagree_exit_class: u64,
        disagree_counters: u64,
        disagree_identity: u64,
        disagree_padding: u64,
        disagree_gates: u64,
        disagree_pairs_clean: u64,
        disagree_windows: u64,
        disagree_caps: u64,
        cap_variant: u64,
        dirty_rows_with_exact_counters: u64,
        repeat_cases: u64,
        panics: u64,
    }

    /// The tool's table, from our rows.
    fn to_table(rows: &[Row]) -> Vec<super::Trusted<'_>> {
        rows.iter().map(|r| super::Trusted { line: &r.0, header_sha256: &r.1 }).collect()
    }

    fn outcome(path: &str, cap: usize) -> Result<super::Outcome, String> {
        let mut dev = super::segio::open(path, false).map_err(|e| e.to_string())?;
        let hdr = super::roomio::read_hdr(&mut dev, 0)?;
        super::run(&mut dev, 0, &hdr, cap, |_, _| {})
    }

    fn counters(o: &super::Outcome) -> (u64, u64, u64, u64, u64, u64) {
        (o.total(|p| p.value_mismatch), o.total(|p| p.lower_without_upper), o.total(|p| p.upper_without_lower), o.total(|p| p.lower_repeated), o.total(|p| p.found), o.total(|p| p.answered))
    }

    fn record(tag: &str, file: &[u8], seed: u64, iter: u64, shown: &mut HashMap<String, u32>, note: String) {
        let seen = shown.entry(tag.to_string()).or_insert(0);
        if *seen < 3 {
            *seen += 1;
            eprintln!("FUZZ_EXAMPLE|class={tag}|seed={seed}|iter={iter}|{note}|json=0");
            let dir = "C:/tmp/opus55/allpairs-review-20261103/hard/examples";
            let _ = std::fs::create_dir_all(dir);
            let _ = std::fs::write(format!("{dir}/{tag}-{seed}-{iter}.bin"), file);
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn one_case(file: &[u8], rows: &[Row], cap: usize, cap2: usize, tmp: &str, sha: &Sha256, t: &mut Tally, seed: u64, iter: u64, shown: &mut HashMap<String, u32>) {
        if std::fs::write(tmp, file).is_err() {
            eprintln!("FUZZ_FAIL|write|json=0");
            std::process::exit(9);
        }
        t.cases += 1;
        let table = to_table(rows);
        let args: Vec<String> = vec!["allpairs".into(), tmp.to_string(), "0".into(), cap.to_string()];
        let got = catch_unwind(AssertUnwindSafe(|| super::run_tool(&args, &table, "-")));
        let want = oracle(file, sha, rows);
        let Ok(got) = got else {
            t.panics += 1;
            record("panic", file, seed, iter, shown, format!("cap={cap}"));
            return;
        };
        match (&got, &want) {
            (Err(_), Expect::Err(_)) => t.exit1 += 1,
            (Err(e), Expect::Verdict { .. }) => {
                t.exit1 += 1;
                t.disagree_exit_class += 1;
                record("tool_err_oracle_verdict", file, seed, iter, shown, format!("cap={cap}|tool={e}"));
            }
            (Ok(r), Expect::Err(why)) => {
                t.disagree_exit_class += 1;
                record("tool_verdict_oracle_err", file, seed, iter, shown, format!("cap={cap}|tool_pass={}|oracle={why}", r.pass));
            }
            (Ok(r), Expect::Verdict { pass, counts, gates, identity_open }) => {
                if r.pass {
                    t.exit0 += 1;
                } else {
                    t.exit2 += 1;
                }
                if r.pass != *pass {
                    t.disagree_verdict += 1;
                    record("verdict", file, seed, iter, shown, format!("cap={cap}|tool={}|oracle={pass}|gates={gates:?}", r.pass));
                }
                let want_identity = if gates[4] == 1 {
                    super::Gate::Pass
                } else if *identity_open {
                    super::Gate::Open
                } else {
                    super::Gate::Fail
                };
                if r.identity != want_identity {
                    t.disagree_identity += 1;
                    record("identity", file, seed, iter, shown, format!("cap={cap}|tool={}|want={want_identity}", r.identity));
                }
                if (r.entries == super::Gate::Pass) != (gates[0] == 1) || (r.count == super::Gate::Pass) != (gates[1] == 1) || (r.rooms == super::Gate::Pass) != (gates[2] == 1) {
                    t.disagree_gates += 1;
                    record("gates", file, seed, iter, shown, format!("cap={cap}|entries={}|count={}|rooms={}|want={gates:?}", r.entries, r.count, r.rooms));
                }
                if r.requested != cap || r.effective != cap.clamp(1, 4_000_000_000) {
                    t.disagree_caps += 1;
                    record("caps", file, seed, iter, shown, format!("cap={cap}|requested={}|effective={}", r.requested, r.effective));
                }
                if (r.padding == super::Gate::Pass) != (gates[3] == 1) {
                    t.disagree_padding += 1;
                    record("padding", file, seed, iter, shown, format!("cap={cap}|tool={}", r.padding));
                }
                // Counters must be exact at both caps, on clean rows and on any others.
                let want6 = (counts.mismatch, counts.lonely_lower, counts.lonely_upper, counts.repeated, counts.found, counts.answered);
                match (outcome(tmp, cap), outcome(tmp, cap2)) {
                    (Ok(a), Ok(b)) => {
                        let (ca, cb) = (counters(&a), counters(&b));
                        if ca != want6 || cb != want6 {
                            t.disagree_counters += 1;
                            record("counters", file, seed, iter, shown, format!("cap={cap}|cap2={cap2}|tool={ca:?}|tool2={cb:?}|want={want6:?}"));
                        }
                        let wa: Vec<(usize, usize)> = a.passes.iter().map(|p| (p.start, p.end)).collect();
                        let wb: Vec<(usize, usize)> = b.passes.iter().map(|p| (p.start, p.end)).collect();
                        if wa != rule_windows(&counts.uppers, cap) || wb != rule_windows(&counts.uppers, cap2) {
                            t.disagree_windows += 1;
                            record("windows", file, seed, iter, shown, format!("cap={cap}|cap2={cap2}|tool={wa:?}|tool2={wb:?}"));
                        }
                        if a.pairs_clean(counts.rows as usize) != counts.pairs_clean() || b.pairs_clean(counts.rows as usize) != counts.pairs_clean() {
                            t.disagree_pairs_clean += 1;
                            record("pairs_clean", file, seed, iter, shown, format!("cap={cap}|cap2={cap2}"));
                        }
                        if ca != cb {
                            t.cap_variant += 1;
                        }
                        if !counts.structure_clean() {
                            t.dirty_rows_with_exact_counters += u64::from(ca == want6);
                        }
                        t.repeat_cases += u64::from(counts.repeated > 0 || counts.not_ascending > 0);
                        let cen = &a.census;
                        if cen.entries != counts.entries || cen.upper != counts.upper || cen.lower != counts.lower || cen.diag != counts.diag || cen.not_ascending != counts.not_ascending || cen.out_of_range != counts.out_of_range || cen.sum_w != counts.sum_w || cen.flats != counts.flats {
                            t.disagree_counters += 1;
                            record("census", file, seed, iter, shown, format!("cap={cap}"));
                        }
                    }
                    _ => {
                        t.disagree_exit_class += 1;
                        record("counter_run_err", file, seed, iter, shown, format!("cap={cap}"));
                    }
                }
            }
        }
    }

    fn fields_for(rooms: u64, entries: u64, n: u64, payload: &[u8], sha: &Sha256, lattice: &str, nl: Option<u32>) -> Vec<(String, String)> {
        let mut f = vec![("L".to_string(), lattice.to_string()), ("sector".to_string(), "Sx+Sy+".to_string()), ("n".to_string(), n.to_string())];
        if let Some(v) = nl {
            f.push(("nl".to_string(), v.to_string()));
        }
        f.push(("rooms".to_string(), rooms.to_string()));
        f.push(("entries".to_string(), entries.to_string()));
        f.push(("payload_bytes".to_string(), payload.len().to_string()));
        f.push(("stream_bytes".to_string(), (payload.len() + 4096).to_string()));
        f.push(("chunk".to_string(), "16MiB".to_string()));
        f.push(("payload_merkle".to_string(), sha.merkle(payload)));
        f.push(("keys_sha256".to_string(), "0".repeat(64)));
        f.push(("w_self_adjoint".to_string(), "PASS".to_string()));
        f.push(("json".to_string(), "0".to_string()));
        f
    }

    fn set(f: &mut [(String, String)], k: &str, v: String) {
        if let Some(e) = f.iter_mut().find(|e| e.0 == k) {
            e.1 = v;
        }
    }

    fn mutate_rows(rng: &mut Rng, rows: &mut Vec<R>) {
        let n = rows.len();
        if n == 0 {
            return;
        }
        let h = rng.below(n as u64) as usize;
        let e = rows[h].ent.len();
        let k = if e == 0 { 0 } else { rng.below(e as u64) as usize };
        match rng.below(24) {
            0 if e > 0 => rows[h].ent[k].1 -= 1,
            1 if e > 0 => {
                rows[h].ent[k].1 -= 1;
                if let Some(d) = rows[h].ent.iter_mut().find(|x| x.0 == h as u32) {
                    d.1 += 1;
                }
            }
            2 if e > 0 => {
                rows[h].ent.remove(k);
            }
            3 => {
                let j = rng.below(n as u64 + 2) as u32;
                let z = -1 - rng.below(5) as i32;
                rows[h].ent.push((j, z));
                rows[h].ent.sort_by_key(|x| x.0);
            }
            4 if e > 1 => rows[h].ent.swap(k, 0),
            5 if e > 0 => {
                // A repeated column, with the same value.
                let c = rows[h].ent[k];
                rows[h].ent.insert(k, c);
            }
            6 if e > 0 => rows[h].ent[k].0 = *rng.pick(&[n as u32, n as u32 + 1, u32::MAX, 0x8000_0000]),
            7 if e > 0 => rows[h].ent[k].1 = *rng.pick(&[0, i32::MIN, i32::MAX, 1, -1]),
            8 => rows[h].w = *rng.pick(&[0, 1, u32::MAX, rows[h].w.wrapping_add(1), rows[h].w.wrapping_mul(2)]),
            9 => {
                for r in rows.iter_mut() {
                    r.w = r.w.wrapping_mul(2);
                }
            }
            10 => rows[h].mag = rng.below(40) as u16,
            11 => {
                rows.pop();
            }
            12 => {
                let r = R { w: 1, mag: 3, ent: vec![(n as u32, 0)] };
                rows.push(r);
            }
            13 if n > 1 => rows.swap(h, (h + 1) % n),
            14 if e > 1 => {
                // The reviewer's D7 store: a lower entry doubled here, and a partner deleted elsewhere.
                let lower: Vec<(u32, i32)> = rows[h].ent.iter().copied().filter(|x| (x.0 as usize) < h).collect();
                if let Some(&(i, z)) = lower.first() {
                    let pos = rows[h].ent.iter().position(|x| x.0 == i).unwrap_or(0);
                    rows[h].ent.insert(pos, (i, z));
                    let ups: Vec<u32> = rows[i as usize].ent.iter().map(|x| x.0).filter(|&j| j as usize > i as usize && j as usize != h && (j as usize) < n).collect();
                    if let Some(&m) = ups.first() {
                        rows[m as usize].ent.retain(|x| x.0 != i);
                    }
                }
            }
            15 if e > 0 => {
                // A symmetric change that keeps the weighted equality, and both diagonals.
                let (j, _) = rows[h].ent[k];
                if j as usize != h && (j as usize) < n {
                    let (wa, wb) = (rows[h].w, rows[j as usize].w);
                    if wa > 0 && wb > 0 {
                        let g = gcd(wa, wb);
                        let (da, db) = ((wb / g) as i32, (wa / g) as i32);
                        for (row, col, d) in [(h, j, da), (j as usize, h as u32, db)] {
                            if let Some(x) = rows[row].ent.iter_mut().find(|x| x.0 == col) {
                                x.1 = x.1.wrapping_sub(d);
                            }
                            let dg = row as u32;
                            if let Some(x) = rows[row].ent.iter_mut().find(|x| x.0 == dg) {
                                x.1 = x.1.wrapping_add(d);
                            }
                        }
                    }
                }
            }
            16 if e > 0 => {
                // Delete both sides of a pair, keep the row sums.
                let (j, z) = rows[h].ent[k];
                if j as usize != h && (j as usize) < n {
                    let z2 = rows[j as usize].ent.iter().find(|x| x.0 == h as u32).map(|x| x.1);
                    rows[h].ent.retain(|x| x.0 != j);
                    if let Some(d) = rows[h].ent.iter_mut().find(|x| x.0 == h as u32) {
                        d.1 = d.1.wrapping_add(z);
                    }
                    if let Some(z2) = z2 {
                        rows[j as usize].ent.retain(|x| x.0 != h as u32);
                        if let Some(d) = rows[j as usize].ent.iter_mut().find(|x| x.0 == j) {
                            d.1 = d.1.wrapping_add(z2);
                        }
                    }
                }
            }
            17 if e > 0 => {
                let (j, z) = rows[h].ent[k];
                rows[h].ent[k] = (j.wrapping_add(1), z);
            }
            18 => rows[h].ent.clear(),
            19 if e > 0 => {
                // Both sides repeated, values in opposite order on the two sides.
                let (j, z) = rows[h].ent[k];
                if j as usize != h && (j as usize) < n {
                    rows[h].ent.insert(k, (j, z - 1));
                    let jr = j as usize;
                    if let Some(pos) = rows[jr].ent.iter().position(|x| x.0 == h as u32) {
                        let zb = rows[jr].ent[pos].1;
                        rows[jr].ent.insert(pos + 1, (h as u32, zb - 1));
                    }
                }
            }
            20 if e > 1 => rows[h].ent.reverse(),
            21 if e > 0 => {
                // One column repeated many times on one side.
                let c = rows[h].ent[k];
                for _ in 0..(2 + rng.below(6)) {
                    rows[h].ent.insert(k, c);
                }
            }
            _ => {}
        }
    }

    fn mutate_header(rng: &mut Rng, f: &mut Vec<(String, String)>, rows_len: usize) {
        let keys = ["L", "sector", "n", "nl", "rooms", "entries", "payload_bytes", "stream_bytes", "chunk", "payload_merkle", "keys_sha256", "w_self_adjoint", "json"];
        match rng.below(40) {
            0 => set(f, "n", "0".into()),
            1 => set(f, "n", (rows_len + 1 + rng.below(3) as usize).to_string()),
            2 => set(f, "n", rows_len.saturating_sub(1 + rng.below(3) as usize).to_string()),
            3 => f.retain(|e| e.0 != "entries"),
            4 => set(f, "entries", "abc".into()),
            5 => set(f, "entries", "1".into()),
            6 => f.retain(|e| e.0 != "nl"),
            7 => set(f, "nl", "7".into()),
            8 => set(f, "L", "3y4".into()),
            9 => f.retain(|e| e.0 != "L"),
            10 => f.retain(|e| e.0 != "w_self_adjoint"),
            11 => set(f, "w_self_adjoint", "FAIL".into()),
            12 => f.retain(|e| e.0 != "payload_merkle"),
            13 => f.retain(|e| e.0 != "n"),
            14 => f.retain(|e| e.0 != "payload_bytes"),
            15 => set(f, "n", "4294967296".into()),
            16 => f.retain(|e| e.0 != "rooms"),
            17 => f.retain(|e| e.0 != "stream_bytes"),
            18 => set(f, "rooms", (rng.below(100_000)).to_string()),
            19 => set(f, "stream_bytes", (rng.below(3) * MIB + rng.below(2)).to_string()),
            20 => set(f, "rooms", "2305843009213693952".into()),
            21 => set(f, "rooms", "+1".into()),
            22 | 23 => {
                let k = *rng.pick(&keys);
                let v = f.iter().find(|e| e.0 == k).map_or("1".to_string(), |e| e.1.clone());
                let at = rng.below(f.len() as u64 + 1) as usize;
                f.insert(at, (k.to_string(), v));
            }
            24..=26 => {
                let k = *rng.pick(&["n", "nl", "entries", "payload_bytes", "L", "rooms", "stream_bytes"]);
                let form = rng.below(6);
                if let Some(e) = f.iter_mut().find(|e| e.0 == k) {
                    e.1 = match form {
                        0 => format!("+{}", e.1),
                        1 => format!("0{}", e.1),
                        2 => format!("{} ", e.1),
                        3 => format!("{}\r", e.1),
                        4 => format!("{}.0", e.1),
                        _ => String::new(),
                    };
                }
            }
            27 => set(f, "sector", "NOT-THIS".into()),
            28 => set(f, "keys_sha256", "1".repeat(64)),
            29 => set(f, "chunk", "1MiB".into()),
            30 => f.push(("extra".to_string(), "1".to_string())),
            31 => {
                let i = rng.below(f.len() as u64) as usize;
                let j = rng.below(f.len() as u64) as usize;
                f.swap(i, j);
            }
            32 => {
                if let Some(e) = f.iter_mut().find(|e| e.0 == "L") {
                    if let Some((a, b)) = e.1.split_once('x') {
                        e.1 = format!("{b}x{a}");
                    }
                }
            }
            33 => {
                set(f, "n", "0".into());
                f.retain(|e| e.0 != "entries" && e.0 != "nl" && e.0 != "L");
            }
            34 => {
                set(f, "payload_bytes", "18446744073709551615".into());
            }
            36 | 37 => set(f, "rooms", (rows_len / 2).to_string()),
            35 => {
                set(f, "stream_bytes", "18446744073709551615".into());
            }
            _ => {}
        }
    }

    pub fn fuzz(seed: u64, iters: u64, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let mut rng = Rng(seed);
        let mut t = Tally::default();
        let mut shown: HashMap<String, u32> = HashMap::new();
        let t0 = std::time::Instant::now();
        let room = (MIB - 4096) as usize;
        for iter in 0..iters {
            let (lattice, nl, target): (String, Option<u32>, Option<u64>) = match rng.below(4) {
                0 => ("1x1".into(), Some(2), Some(36)),
                1 => ("1x2".into(), Some(4), Some(216)),
                2 => ("1x40".into(), None, None),
                _ => ("2x2".into(), Some(8), Some(7776)),
            };
            let n = 2 + rng.below(20) as usize;
            let clean = clean_store(&mut rng, n, target);
            let mut rows = clean.clone();
            let muts = match rng.below(10) {
                0..=3 => 0,
                4..=7 => 1,
                _ => 2 + rng.below(3),
            };
            for _ in 0..muts {
                mutate_rows(&mut rng, &mut rows);
            }
            let room_of = |r: &[R]| -> (u64, u64) { (r.len() as u64 + r.iter().map(|x| x.ent.len() as u64).sum::<u64>(), r.iter().map(|x| x.ent.len() as u64).sum::<u64>()) };
            let mut payload = serialize(&rows);
            let wide = rng.below(25) == 0;
            let rows_len = payload.len();
            payload.resize(if wide { room.max(rows_len) + (1 + rng.below(2) as usize) * (MIB as usize) } else { room.max(rows_len) }, 0);
            // Padding: zero, one stray byte, or a stream that is no multiple of 1 MiB.
            match rng.below(12) {
                0 => {
                    let used = serialize(&rows).len();
                    let i = used + rng.below((payload.len() - used) as u64 + 1) as usize;
                    if i < payload.len() {
                        payload[i] = 1 + rng.below(255) as u8;
                    }
                }
                1 => {
                    payload.truncate(payload.len().saturating_sub(8 * rng.below(4) as usize));
                }
                _ => {}
            }
            let (rooms, entries) = room_of(&rows);
            let (crooms, centries) = room_of(&clean);
            let stale = rng.below(10) == 0;
            let (hrooms, hentries, hn) = if stale { (crooms, centries, clean.len() as u64) } else { (rooms, entries, rows.len() as u64) };
            let hrooms = if wide && rng.below(2) == 0 { payload.len() as u64 / 8 } else { hrooms };
            let mut fields = fields_for(hrooms, hentries, hn, &payload, &sha, &lattice, nl);
            match rng.below(16) {
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
            }
            let before = file_bytes(&header_line(&fields), &payload);
            if rng.below(3) == 0 {
                mutate_header(&mut rng, &mut fields, rows.len());
                if rng.below(4) == 0 {
                    mutate_header(&mut rng, &mut fields, rows.len());
                }
            }
            let line = header_line(&fields);
            let mut file = file_bytes(&line, &payload);
            if rng.below(30) == 0 && file.len() > 4096 {
                // A byte after the line, in the zeros of the block.
                let i = (line.len() + 1 + rng.below(64) as usize).min(4095);
                file[i] = 1;
            }
            if rng.below(60) == 0 {
                let cut = rng.below(file.len() as u64) as usize;
                file.truncate(cut);
            }
            if rng.below(30) == 0 {
                file.extend_from_slice(&[0xAB; 16]);
            }
            // The table: half the time it trusts this very block, so every other gate decides alone.
            let table: Vec<Row> = match rng.below(4) {
                0 | 1 => {
                    if file.len() >= 4096 {
                        vec![(String::from_utf8_lossy(&file[..file[..4096].iter().position(|&b| b == b'\n').unwrap_or(0)]).to_string(), sha.hex(&file[..4096]))]
                    } else {
                        Vec::new()
                    }
                }
                2 => {
                    let cl = String::from_utf8_lossy(&before[..before[..4096].iter().position(|&b| b == b'\n').unwrap_or(0)]).to_string();
                    vec![(cl, sha.hex(&before[..4096]))]
                }
                _ => Vec::new(),
            };
            let pairs: u64 = rows.iter().enumerate().map(|(h, r)| r.ent.iter().filter(|e| e.0 as usize > h).count() as u64).sum();
            let caps = [0usize, 1, 2, 3, 5, 8, 13, pairs as usize, pairs as usize + 1, 470_000_000, 470_000_000, 470_000_000];
            let cap = *rng.pick(&caps);
            let cap2 = *rng.pick(&caps);
            one_case(&file, &table, cap, cap2, tmp, &sha, &mut t, seed, iter, &mut shown);
        }
        let _ = std::fs::remove_file(tmp);
        eprintln!(
            "FUZZ_DONE|seed={seed}|cases={}|exit0={}|exit1={}|exit2={}|disagree_verdict={}|disagree_exit_class={}|disagree_counters_on_any_rows={}|disagree_identity={}|disagree_padding={}|disagree_gates={}|disagree_pairs_clean={}|disagree_windows={}|disagree_caps={}|cap_variant_counters={}|dirty_rows_with_exact_counters={}|cases_with_repeats_or_disorder={}|panics={}|secs={}|json=0",
            t.cases, t.exit0, t.exit1, t.exit2, t.disagree_verdict, t.disagree_exit_class, t.disagree_counters, t.disagree_identity, t.disagree_padding, t.disagree_gates, t.disagree_pairs_clean, t.disagree_windows, t.disagree_caps, t.cap_variant, t.dirty_rows_with_exact_counters, t.repeat_cases, t.panics, t0.elapsed().as_secs()
        );
        i32::from(t.disagree_verdict > 0 || t.disagree_exit_class > 0 || t.disagree_counters > 0 || t.disagree_identity > 0 || t.disagree_padding > 0 || t.disagree_gates > 0 || t.disagree_pairs_clean > 0 || t.disagree_windows > 0 || t.disagree_caps > 0 || t.cap_variant > 0 || t.panics > 0)
    }

    fn load_rows(path: &str) -> (Vec<R>, String) {
        let b = std::fs::read(path).unwrap_or_default();
        let eol = b.iter().position(|&x| x == b'\n').unwrap_or(0);
        let line = String::from_utf8_lossy(&b[..eol]).to_string();
        let n: usize = fld(&line, "n=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let mut p = 4096usize;
        let mut rows = Vec::with_capacity(n);
        for _ in 0..n {
            let w = u32::from_le_bytes([b[p], b[p + 1], b[p + 2], b[p + 3]]);
            let mag = u16::from_le_bytes([b[p + 4], b[p + 5]]);
            let cnt = usize::from(u16::from_le_bytes([b[p + 6], b[p + 7]]));
            p += 8;
            let mut ent = Vec::with_capacity(cnt);
            for _ in 0..cnt {
                ent.push((u32::from_le_bytes([b[p], b[p + 1], b[p + 2], b[p + 3]]), i32::from_le_bytes([b[p + 4], b[p + 5], b[p + 6], b[p + 7]])));
                p += 8;
            }
            rows.push(R { w, mag, ent });
        }
        (rows, line)
    }

    /// A rows-only stream for run(): the sizes rule sits in run_tool, and these faults are about the pair logic.
    fn write_rows(rows: &[R], lattice: &str, nl: u32, sha: &Sha256, tmp: &str) -> Vec<u8> {
        let payload = serialize(rows);
        let entries: u64 = rows.iter().map(|x| x.ent.len() as u64).sum();
        let f = fields_for(rows.len() as u64 + entries, entries, rows.len() as u64, &payload, sha, lattice, Some(nl));
        let b = file_bytes(&header_line(&f), &payload);
        let _ = std::fs::write(tmp, &b);
        b
    }

    pub fn sweep(store: &str, tmp: &str) -> i32 {
        let sha = Sha256::new();
        let (base, line) = load_rows(store);
        let lattice = fld(&line, "L=").unwrap_or("").to_string();
        let nl: u32 = fld(&line, "nl=").and_then(|v| v.parse().ok()).unwrap_or(0);
        let n = base.len();
        let pairs: u64 = base.iter().enumerate().map(|(h, r)| r.ent.iter().filter(|e| e.0 as usize > h).count() as u64).sum();
        let caps = [1usize, 13, 100, 470_000_000];
        let t0 = std::time::Instant::now();
        let mut tried: HashMap<&str, u64> = HashMap::new();
        let mut bad = 0u64;
        let mut repeats_right = 0u64;
        let mut check = |name: &'static str, rows: &[R], tally: &mut HashMap<&str, u64>| {
            let b = write_rows(rows, &lattice, nl, &sha, tmp);
            let want = count_rows(&b[4096..], n as u64).unwrap_or_default();
            let want6 = (want.mismatch, want.lonely_lower, want.lonely_upper, want.repeated, want.found, want.answered);
            for cap in caps {
                *tally.entry(name).or_insert(0) += 1;
                let ok = outcome(tmp, cap).is_ok_and(|o| {
                    let same = counters(&o) == want6 && o.census.not_ascending == want.not_ascending && o.census.upper == want.upper && o.census.lower == want.lower;
                    let verdict_right = o.pairs_clean(n) == want.pairs_clean();
                    same && verdict_right
                });
                if !ok {
                    bad += 1;
                    eprintln!("SWEEP_BAD|case={name}|cap={cap}|json=0");
                }
                repeats_right += u64::from(ok && want.repeated > 0);
            }
        };
        for h in 0..n {
            for k in 0..base[h].ent.len() {
                let (j, z) = base[h].ent[k];
                if j as usize == h {
                    continue;
                }
                // A changed value, row sum kept.
                let mut r = base.clone();
                r[h].ent[k].1 = z - 1;
                if let Some(d) = r[h].ent.iter_mut().find(|e| e.0 == h as u32) {
                    d.1 += 1;
                }
                check("value", &r, &mut tried);
                // A deleted entry, row sum kept.
                let mut r = base.clone();
                r[h].ent.remove(k);
                if let Some(d) = r[h].ent.iter_mut().find(|e| e.0 == h as u32) {
                    d.1 += z;
                }
                check("delete", &r, &mut tried);
                // The same column twice on this side only.
                let mut r = base.clone();
                r[h].ent.insert(k, (j, z));
                check("repeat_one_side", &r, &mut tried);
                // The same column twice on both sides, values crossed.
                let mut r = base.clone();
                r[h].ent.insert(k, (j, z - 1));
                let jr = j as usize;
                if let Some(pos) = r[jr].ent.iter().position(|e| e.0 == h as u32) {
                    let zb = r[jr].ent[pos].1;
                    r[jr].ent.insert(pos + 1, (h as u32, zb - 1));
                }
                check("repeat_both_sides", &r, &mut tried);
            }
            // The row's entries in reverse order.
            let mut r = base.clone();
            r[h].ent.reverse();
            check("row_reversed", &r, &mut tried);
        }
        let _ = std::fs::remove_file(tmp);
        let mut names: Vec<_> = tried.into_iter().collect();
        names.sort();
        eprintln!("SWEEP_DONE|store={store}|n={n}|pairs={pairs}|caps={caps:?}|runs={names:?}|runs_with_repeats_exact={repeats_right}|bad={bad}|secs={}|json=0", t0.elapsed().as_secs());
        i32::from(bad > 0)
    }

    fn call_real(tmp: &str, cap: usize) -> Result<i32, ()> {
        let args: Vec<String> = vec!["allpairs".into(), tmp.to_string(), "0".into(), cap.to_string()];
        match catch_unwind(AssertUnwindSafe(|| super::run_tool(&args, &super::TRUSTED, "-"))) {
            Ok(Ok(r)) => Ok(if r.pass { 0 } else { 2 }),
            Ok(Err(_)) => Ok(1),
            Err(_) => Err(()),
        }
    }

    fn field_map(line: &str) -> Vec<String> {
        let mut names: Vec<String> = Vec::new();
        for part in line.split('|') {
            let name = part.split('=').next().unwrap_or("").to_string();
            for _ in 0..part.len() + 1 {
                names.push(name.clone());
            }
        }
        names.truncate(line.len() + 1);
        names[line.len()] = "newline".to_string();
        names
    }

    pub fn blockflip(store: &str, tmp: &str) -> i32 {
        let clean = std::fs::read(store).unwrap_or_default();
        let eol = clean[..4096].iter().position(|&b| b == b'\n').unwrap_or(0);
        let line = String::from_utf8_lossy(&clean[..eol]).to_string();
        let names = field_map(&line);
        let mut tally: Vec<(String, [u64; 4])> = Vec::new();
        let mut panics = 0u64;
        let t0 = std::time::Instant::now();
        // The clean store first, then every bit of the 4096-byte block.
        if std::fs::write(tmp, &clean).is_err() {
            return 9;
        }
        let clean_exit = call_real(tmp, 470_000_000);
        for byte in 0..4096usize {
            let name = if byte <= eol {
                names[byte].clone()
            } else if byte <= eol + 64 {
                "zeros_after_newline_first_64".to_string()
            } else {
                "zeros_rest_of_block".to_string()
            };
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
                match (call_real(tmp, 470_000_000), e) {
                    (Ok(c), Some(e)) => {
                        e[0] += 1;
                        e[1 + if c == 0 { 0 } else if c == 1 { 1 } else { 2 }] += 1;
                    }
                    _ => panics += 1,
                }
            }
        }
        let _ = std::fs::remove_file(tmp);
        let mut total = [0u64; 4];
        for (name, e) in &tally {
            eprintln!("BLOCKFLIP|field={name}|flips={}|exit0={}|exit1={}|exit2={}|json=0", e[0], e[1], e[2], e[3]);
            for k in 0..4 {
                total[k] += e[k];
            }
        }
        eprintln!("BLOCKFLIP_DONE|store={store}|clean_exit={clean_exit:?}|flips={}|exit0={}|exit1={}|exit2={}|panics={panics}|secs={}|json=0", total[0], total[1], total[2], total[3], t0.elapsed().as_secs());
        i32::from(panics > 0 || total[1] > 0 || clean_exit != Ok(0))
    }

    pub fn headerbytes(store: &str, tmp: &str) -> i32 {
        let clean = std::fs::read(store).unwrap_or_default();
        let eol = clean[..4096].iter().position(|&b| b == b'\n').unwrap_or(0);
        let line = String::from_utf8_lossy(&clean[..eol]).to_string();
        let names = field_map(&line);
        let mut tally: Vec<(String, [u64; 4])> = Vec::new();
        let mut panics = 0u64;
        for byte in 0..=eol {
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
                match (call_real(tmp, 470_000_000), e) {
                    (Ok(c), Some(e)) => {
                        e[0] += 1;
                        e[1 + if c == 0 { 0 } else if c == 1 { 1 } else { 2 }] += 1;
                    }
                    _ => panics += 1,
                }
            }
        }
        let _ = std::fs::remove_file(tmp);
        let mut total = [0u64; 4];
        for (name, e) in &tally {
            eprintln!("HEADERBYTES|field={name}|changes={}|exit0={}|exit1={}|exit2={}|json=0", e[0], e[1], e[2], e[3]);
            for k in 0..4 {
                total[k] += e[k];
            }
        }
        eprintln!("HEADERBYTES_DONE|store={store}|changes={}|exit0={}|exit1={}|exit2={}|panics={panics}|json=0", total[0], total[1], total[2], total[3]);
        i32::from(panics > 0 || total[1] > 0)
    }

    pub fn main(a: &[String]) -> i32 {
        let arg = |i: usize| a.get(i).map_or("", String::as_str);
        match arg(1) {
            "fuzz" => fuzz(arg(2).parse().unwrap_or(1), arg(3).parse().unwrap_or(1000), arg(4)),
            "sweep" => sweep(arg(2), arg(3)),
            "blockflip" => blockflip(arg(2), arg(3)),
            "headerbytes" => headerbytes(arg(2), arg(3)),
            _ => {
                eprintln!("usage: fuzz fuzz SEED ITERS TMP | sweep STORE TMP | blockflip STORE TMP | headerbytes STORE TMP");
                9
            }
        }
    }

    #[cfg(test)]
    mod t {
        use super::*;
        #[test]
        fn sha_known_answers() {
            let s = Sha256::new();
            assert_eq!(s.hex(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
            assert_eq!(s.hex(b""), "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
            assert_eq!(s.hex(&vec![b'a'; 1_000_000]), "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
        }
    }
}
