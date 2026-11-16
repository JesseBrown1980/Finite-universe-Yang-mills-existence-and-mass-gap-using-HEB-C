//! #137, stage A: an independent enumerator of the raw electric rows of the 3x4 S3 torus, and the exact wide
//! integers the third moment will be accumulated in.
//!
//! Written from the public definition only: the group S3 as the six permutations of (0,1,2) in lexicographic
//! order, the periodic 3x4 lattice, a spanning tree of 11 links, 13 kept links, and the six global conjugations.
//! A state is the tuple of its 13 kept links, taken to the smallest tuple under conjugation; its address is that
//! tuple read as a base-6 number, first entry least significant. A raw move multiplies one of the 24 links on the
//! left by one of the 3 transpositions: 72 moves per state.
//!
//!   y137_rows rows            read addresses (decimal, one per line) on stdin; one ROW line each
//!   y137_rows bench N         time N rows from generated states
//!   y137_rows wide            read lines "a b w" (decimal) on stdin; print the exact value of sum(w*a*b)
//!                             and of its negation, from the 320-bit accumulator
//!
//! Integers only.

use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::time::Instant;

const LX: usize = 3;
const LY: usize = 4;
const SITES: usize = 12;
const LINKS: usize = 24;
const KEPT: usize = 13;
const PERMS: [[u8; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];

struct Rule {
    mul: [[u8; 6]; 6],
    inv: [u8; 6],
    trans: [u8; 3],
    tree: [(usize, usize, usize); 11],
    keep: [usize; KEPT],
    chr: [i32; 6],
}

fn at(x: usize, y: usize) -> usize {
    (x % LX) * LY + (y % LY)
}

fn index_of(p: [u8; 3]) -> u8 {
    PERMS.iter().position(|q| *q == p).map_or(255, |i| i as u8)
}

impl Rule {
    fn new() -> Self {
        let mut mul = [[0u8; 6]; 6];
        let mut inv = [0u8; 6];
        let mut chr = [0i32; 6];
        for (a, &ga) in PERMS.iter().enumerate() {
            for (b, &gb) in PERMS.iter().enumerate() {
                mul[a][b] = index_of([ga[gb[0] as usize], ga[gb[1] as usize], ga[gb[2] as usize]]);
            }
            let p = ga;
            let mut q = [0u8; 3];
            for (i, &v) in p.iter().enumerate() {
                q[v as usize] = i as u8;
            }
            inv[a] = index_of(q);
            chr[a] = p.iter().enumerate().filter(|(i, &v)| *i == v as usize).count() as i32 - 1;
        }
        let mut trans = [0u8; 3];
        let mut nt = 0;
        for (a, line) in mul.iter().enumerate().skip(1) {
            if line[a] == 0 {
                trans[nt] = a as u8;
                nt += 1;
            }
        }
        assert_eq!(nt, 3);
        let mut tree = [(0usize, 0usize, 0usize); 11];
        let mut n = 0;
        for y in 0..LY - 1 {
            tree[n] = (at(0, y), at(0, y + 1), SITES + at(0, y));
            n += 1;
        }
        for y in 0..LY {
            for x in 0..LX - 1 {
                tree[n] = (at(x, y), at(x + 1, y), at(x, y));
                n += 1;
            }
        }
        assert_eq!(n, 11);
        let mut keep = [0usize; KEPT];
        let mut k = 0;
        for j in 0..LINKS {
            if !tree.iter().any(|t| t.2 == j) {
                keep[k] = j;
                k += 1;
            }
        }
        assert_eq!(k, KEPT);
        Rule { mul, inv, trans, tree, keep, chr }
    }

    fn m(&self, a: u8, b: u8) -> u8 {
        self.mul[a as usize][b as usize]
    }

    /// tree transport, then the smallest tuple under the six conjugations
    fn canonical(&self, links: &[u8; LINKS]) -> [u8; KEPT] {
        let mut gauge = [0u8; SITES];
        for &(src, dst, edge) in &self.tree {
            gauge[dst] = self.m(gauge[src], links[edge]);
        }
        let mut flat = [0u8; LINKS];
        for x in 0..LX {
            for y in 0..LY {
                let i = at(x, y);
                flat[i] = self.m(self.m(gauge[i], links[i]), self.inv[gauge[at(x + 1, y)] as usize]);
                flat[SITES + i] = self.m(self.m(gauge[i], links[SITES + i]), self.inv[gauge[at(x, y + 1)] as usize]);
            }
        }
        let mut res = [0u8; KEPT];
        for (r, &k) in res.iter_mut().zip(&self.keep) {
            *r = flat[k];
        }
        let mut best = res;
        for a in 1..6u8 {
            let ia = self.inv[a as usize];
            let mut c = [0u8; KEPT];
            for (o, &u) in c.iter_mut().zip(&res) {
                *o = self.m(self.m(a, u), ia);
            }
            if c < best {
                best = c;
            }
        }
        best
    }

    fn expand(&self, key: &[u8; KEPT]) -> [u8; LINKS] {
        let mut full = [0u8; LINKS];
        for (&j, &a) in self.keep.iter().zip(key) {
            full[j] = a;
        }
        full
    }

    /// the 72 raw moves of a state, as (destination address, multiplicity), sorted by address
    fn row(&self, key: &[u8; KEPT]) -> Vec<(u64, u32)> {
        let mut full = self.expand(key);
        let mut dest = [0u64; 72];
        let mut n = 0;
        for i in 0..LINKS {
            let old = full[i];
            for &t in &self.trans {
                full[i] = self.m(t, old);
                dest[n] = code(&self.canonical(&full));
                n += 1;
            }
            full[i] = old;
        }
        dest.sort_unstable();
        let mut out: Vec<(u64, u32)> = Vec::with_capacity(72);
        for &d in &dest {
            match out.last_mut() {
                Some(last) if last.0 == d => last.1 += 1,
                _ => out.push((d, 1)),
            }
        }
        out
    }

    fn weight(&self, key: &[u8; KEPT]) -> u32 {
        let mut seen: Vec<[u8; KEPT]> = Vec::with_capacity(6);
        for a in 0..6u8 {
            let ia = self.inv[a as usize];
            let mut c = [0u8; KEPT];
            for (o, &u) in c.iter_mut().zip(key) {
                *o = self.m(self.m(a, u), ia);
            }
            if !seen.contains(&c) {
                seen.push(c);
            }
        }
        seen.len() as u32
    }

    fn magnetic(&self, key: &[u8; KEPT]) -> i32 {
        let u = self.expand(key);
        let mut total = 0;
        for x in 0..LX {
            for y in 0..LY {
                let i = at(x, y);
                let mut p = self.m(u[i], u[SITES + at(x + 1, y)]);
                p = self.m(p, self.inv[u[at(x, y + 1)] as usize]);
                p = self.m(p, self.inv[u[SITES + i] as usize]);
                total += 2 - self.chr[p as usize];
            }
        }
        total
    }
}

fn code(key: &[u8; KEPT]) -> u64 {
    let mut v = 0u64;
    for &x in key.iter().rev() {
        v = v * 6 + u64::from(x);
    }
    v
}

fn decode(mut v: u64) -> [u8; KEPT] {
    let mut out = [0u8; KEPT];
    for o in &mut out {
        *o = (v % 6) as u8;
        v /= 6;
    }
    out
}


const GROUPS: usize = 8;
const BUCKETS: usize = 64;
const EXPECTED_ROWS: usize = 18_598_040;
const EXPECTED_MOVES: u64 = 1_339_058_880;
const MAX_ADDR: u64 = 13_060_694_016; // 6^13
const ROWS_BY_GROUP: [u64; GROUPS] =
    [435324, 4439918, 988399, 2812763, 822474, 3973928, 1612450, 3512784];
const BYTES_BY_GROUP: [u64; GROUPS] =
    [72717336, 750840749, 166069410, 476041564, 137545818, 672121828, 270439868, 595123535];

fn ensure(ok: bool, message: &str) -> Result<(), String> {
    if ok { Ok(()) } else { Err(message.to_string()) }
}

#[derive(Default)]
struct SourceSummary { rows: u64, bytes: u64 }

fn visit_group<F>(path: &Path, group: usize, mut visit: F) -> Result<SourceSummary, String>
where F: FnMut(u64, u8) -> Result<(), String> {
    let file = File::open(path).map_err(|x| format!("opening_source_group_{group}: {x}"))?;
    let mut reader = BufReader::with_capacity(1_048_576, file);
    let mut first = [0u8; 1];
    let mut head = [0u8; 13];
    let mut payload = [0u8; 164];
    let mut bucket_index = 0usize;
    let mut last_key: Option<u64> = None;
    let mut total = SourceSummary::default();
    loop {
        let n = reader.read(&mut first).map_err(|x| x.to_string())?;
        if n == 0 { break; }
        head[0] = first[0];
        reader.read_exact(&mut head[1..]).map_err(|x| format!("truncated_header: {x}"))?;
        let address = u64::from_le_bytes(head[0..8].try_into().map_err(|_| "address_header")?);
        let weight = head[8];
        let n0 = usize::from(u16::from_le_bytes([head[9], head[10]]));
        let n1 = usize::from(u16::from_le_bytes([head[11], head[12]]));
        ensure(address < MAX_ADDR, "noncanonical_address_out_of_range")?;
        ensure(matches!(weight, 1 | 2 | 3 | 6), "bad_orbit_weight")?;
        ensure(n0 <= 82 && n1 <= 82, "packed_lane_length")?;
        let body_len = n0 + n1;
        reader.read_exact(&mut payload[..body_len])
            .map_err(|x| format!("truncated_amplitude: {x}"))?;
        let bucket = (address % BUCKETS as u64) as usize;
        ensure(bucket % GROUPS == group, "address_group_mismatch")?;
        let expected_bucket = group + bucket_index * GROUPS;
        if bucket != expected_bucket {
            ensure(bucket_index < 7 && bucket == expected_bucket + GROUPS,
                   "out_of_order_or_skipped_bucket")?;
            bucket_index += 1;
            last_key = None;
        }
        if let Some(previous) = last_key {
            ensure(address > previous, "nonincreasing_bucket_key")?;
        }
        last_key = Some(address);
        visit(address, weight)?;
        total.rows += 1;
        total.bytes += (13 + body_len) as u64;
    }
    ensure(bucket_index == 7, "incomplete_eight_bucket_source")?;
    Ok(total)
}

#[derive(Default)]
struct RowCensus {
    rows: u64,
    raw_moves: u64,
    distinct_destinations: u64,
    on_q5_moves: u64,
    on_q5_destinations: u64,
    outside_q5_moves: u64,
    outside_q5_destinations: u64,
    true_selfloop_moves: u64,
    magnetic_sum: i64,
    max_magnetic: i32,
    q5_group_moves: [u64; GROUPS],
    boundary_bucket_moves: [u64; BUCKETS],
    boundary_fnv64: u64,
}

fn mix_fnv64(state: &mut u64, v: u64) {
    for x in v.to_le_bytes() {
        *state ^= u64::from(x);
        *state = state.wrapping_mul(1_099_511_628_211);
    }
}

fn process_row(
    rule: &Rule, address: u64, stored_weight: u8,
    support: &HashMap<u64, u8>, totals: &mut RowCensus
) -> Result<(), String> {
    let key = decode(address);
    ensure(code(&rule.canonical(&rule.expand(&key))) == address,
           "stage_a_canonicality_disagreement")?;
    ensure(rule.weight(&key) == u32::from(stored_weight),
           "stage_a_orbit_weight_disagreement")?;
    let magnetic = rule.magnetic(&key);
    ensure((0..=36).contains(&magnetic), "invalid_magnetic_number")?;
    let moves = rule.row(&key);
    let degree: u32 = moves.iter().map(|(_, c)| *c).sum();
    ensure(degree == 72, "raw_electric_degree_not_72")?;
    totals.rows += 1;
    totals.raw_moves += u64::from(degree);
    totals.distinct_destinations += moves.len() as u64;
    totals.magnetic_sum += i64::from(magnetic);
    totals.max_magnetic = totals.max_magnetic.max(magnetic);
    for (dest, c) in moves {
        let count = u64::from(c);
        if dest == address {
            totals.true_selfloop_moves += count;
        }
        if support.contains_key(&dest) {
            totals.on_q5_moves += count;
            totals.on_q5_destinations += 1;
            totals.q5_group_moves[(dest % GROUPS as u64) as usize] += count;
        } else {
            totals.outside_q5_moves += count;
            totals.outside_q5_destinations += 1;
            totals.boundary_bucket_moves[(dest % BUCKETS as u64) as usize] += count;
            mix_fnv64(&mut totals.boundary_fnv64, address);
            mix_fnv64(&mut totals.boundary_fnv64, dest);
            mix_fnv64(&mut totals.boundary_fnv64, count);
        }
    }
    ensure(totals.on_q5_moves + totals.outside_q5_moves == totals.raw_moves,
           "Q5_destination_classification_incomplete")?;
    Ok(())
}

fn histogram(values: &[u64]) -> String {
    values.iter().map(u64::to_string).collect::<Vec<_>>().join(",")
}

fn selftest() -> Result<(), String> {
    let rule = Rule::new();
    let zero = [0u8; KEPT];
    ensure(code(&rule.canonical(&rule.expand(&zero))) == 0, "zero_canonical")?;
    ensure(rule.weight(&zero) == 1, "zero_orbit_weight")?;
    ensure(rule.magnetic(&zero) == 0, "zero_magnetic")?;
    let edges = rule.row(&zero);
    ensure(edges.iter().map(|x| x.1).sum::<u32>() == 72, "zero_degree")?;
    ensure(edges.iter().all(|x| x.0 != 0), "zero_unexpected_self_loop")?;
    let mut support = HashMap::new();
    support.insert(0u64, 1u8);
    let mut counts = RowCensus::default();
    counts.boundary_fnv64 = 14_695_981_039_346_656_037;
    process_row(&rule, 0, 1, &support, &mut counts)?;
    ensure(counts.rows == 1 && counts.raw_moves == 72 &&
           counts.on_q5_moves == 0 && counts.outside_q5_moves == 72,
           "zero_source_partition")?;
    let mut planted_bad_weight = false;
    if process_row(&rule, 0, 2, &support, &mut RowCensus::default()).is_err() {
        planted_bad_weight = true;
    }
    ensure(planted_bad_weight, "incorrect_orbit_weight_was_accepted")?;
    println!("Y137_STAGE_B3_TOY|zero_72_moves=PASS|zero_magnetic=PASS|known_orbit_weight=PASS|off_Q5_census=PASS|bad_orbit_weight=REFUSED|real_rows=NOT_COMPUTED|json=0");
    Ok(())
}

fn run(root: &Path) -> Result<(), String> {
    let began = Instant::now();
    let mut support = HashMap::<u64, u8>::with_capacity(EXPECTED_ROWS);
    let mut bytes = 0u64;
    for g in 0..GROUPS {
        let name = root.join(format!("GROUP-{g}.v1"));
        let summary = visit_group(&name, g, |address, weight| {
            ensure(support.insert(address, weight).is_none(), "duplicate_global_Q5_address")
        })?;
        ensure(summary.rows == ROWS_BY_GROUP[g] && summary.bytes == BYTES_BY_GROUP[g],
               "B1_source_receipt_changed")?;
        bytes += summary.bytes;
        println!("Y137_STAGE_B3_INDEX|group={g}|source_rows={}|source_bytes={}|json=0",
                 summary.rows, summary.bytes);
    }
    ensure(support.len() == EXPECTED_ROWS && bytes == 3_140_900_108,
           "global_Q5_index_incomplete")?;
    println!("Y137_STAGE_B3_INDEX_VERDICT|addresses={}|source_bytes={bytes}|lookup=GLOBAL_HASH_MAP|duplicate_keys=0|json=0",
             support.len());
    let rule = Rule::new();
    let mut whole = RowCensus::default();
    whole.boundary_fnv64 = 14_695_981_039_346_656_037;
    for g in 0..GROUPS {
        let name = root.join(format!("GROUP-{g}.v1"));
        let mut local = RowCensus::default();
        local.boundary_fnv64 = 14_695_981_039_346_656_037;
        let summary = visit_group(&name, g, |address, weight| {
            process_row(&rule, address, weight, &support, &mut local)
        })?;
        ensure(summary.rows == ROWS_BY_GROUP[g], "replayed_group_row_count")?;
        ensure(local.rows == summary.rows && local.raw_moves == 72 * summary.rows,
               "replayed_group_electric_degree")?;
        println!("Y137_STAGE_B3_GROUP|group={g}|rows={}|raw_moves={}|on_Q5_moves={}|off_Q5_moves={}|on_Q5_unique_dests={}|off_Q5_unique_dests={}|selfloop_moves={}|magnetic_sum={}|magnetic_max={}|on_group_moves={}|off_bucket_moves={}|boundary_fnv64={:016x}|json=0",
                 local.rows, local.raw_moves, local.on_q5_moves,
                 local.outside_q5_moves, local.on_q5_destinations,
                 local.outside_q5_destinations, local.true_selfloop_moves,
                 local.magnetic_sum, local.max_magnetic, histogram(&local.q5_group_moves),
                 histogram(&local.boundary_bucket_moves), local.boundary_fnv64);
        whole.rows += local.rows;
        whole.raw_moves += local.raw_moves;
        whole.distinct_destinations += local.distinct_destinations;
        whole.on_q5_moves += local.on_q5_moves;
        whole.on_q5_destinations += local.on_q5_destinations;
        whole.outside_q5_moves += local.outside_q5_moves;
        whole.outside_q5_destinations += local.outside_q5_destinations;
        whole.true_selfloop_moves += local.true_selfloop_moves;
        whole.magnetic_sum += local.magnetic_sum;
        whole.max_magnetic = whole.max_magnetic.max(local.max_magnetic);
        for i in 0..GROUPS { whole.q5_group_moves[i] += local.q5_group_moves[i]; }
        for i in 0..BUCKETS { whole.boundary_bucket_moves[i] += local.boundary_bucket_moves[i]; }
        mix_fnv64(&mut whole.boundary_fnv64, local.boundary_fnv64);
    }
    ensure(whole.rows == EXPECTED_ROWS as u64 &&
           whole.raw_moves == EXPECTED_MOVES &&
           whole.on_q5_moves + whole.outside_q5_moves == whole.raw_moves &&
           whole.q5_group_moves.iter().sum::<u64>() == whole.on_q5_moves &&
           whole.boundary_bucket_moves.iter().sum::<u64>() == whole.outside_q5_moves,
           "full_Q5_72_move_or_classification_census_mismatch")?;
    println!("Y137_STAGE_B3_VERDICT|source_rows={}|raw_moves={}|on_Q5_moves={}|outside_Q5_moves={}|on_Q5_unique_dests={}|outside_Q5_unique_dests={}|selfloop_moves={}|magnetic_sum={}|magnetic_max={}|on_Q5_by_group={}|boundary_by_bucket={}|boundary_fnv64={:016x}|index_keys={}|milliseconds={}|preregistered_B3=PASS|B4_B8=PENDING|real_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0",
             whole.rows, whole.raw_moves, whole.on_q5_moves, whole.outside_q5_moves,
             whole.on_q5_destinations, whole.outside_q5_destinations,
             whole.true_selfloop_moves, whole.magnetic_sum, whole.max_magnetic,
             histogram(&whole.q5_group_moves), histogram(&whole.boundary_bucket_moves),
             whole.boundary_fnv64, support.len(), began.elapsed().as_millis());
    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let verdict = match args.as_slice() {
        [_, mode] if mode == "--selftest" => selftest(),
        [_, mode, root] if mode == "--run" => run(Path::new(root)),
        _ => Err("usage: b3_census --selftest | --run SOURCE_FOLDER".to_string()),
    };
    if let Err(why) = verdict {
        eprintln!("Y137_STAGE_B3_REFUSE|reason={why}|json=0");
        std::process::exit(1);
    }
}
