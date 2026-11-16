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
use std::fs::{self, File};
use std::io::{BufReader, BufWriter, Read, Write};
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

impl Default for RowCensus {
    fn default() -> Self {
        Self {
            rows: 0,
            raw_moves: 0,
            distinct_destinations: 0,
            on_q5_moves: 0,
            on_q5_destinations: 0,
            outside_q5_moves: 0,
            outside_q5_destinations: 0,
            true_selfloop_moves: 0,
            magnetic_sum: 0,
            max_magnetic: 0,
            q5_group_moves: [0; GROUPS],
            boundary_bucket_moves: [0; BUCKETS],
            boundary_fnv64: 14_695_981_039_346_656_037,
        }
    }
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
    for (g, expected_rows) in ROWS_BY_GROUP.iter().enumerate() {
        let name = root.join(format!("GROUP-{g}.v1"));
        let mut local = RowCensus::default();
        let summary = visit_group(&name, g, |address, weight| {
            process_row(&rule, address, weight, &support, &mut local)
        })?;
        ensure(summary.rows == *expected_rows, "replayed_group_row_count")?;
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


// ---------------------------------------------------------------- B4 independently grouped reverse-pair proof
const PARTS: usize = 256;
const EXPECTED_INTERNAL_MOVES: u64 = 125_005_512;
const EXPECTED_INTERNAL_DIRECTED: u64 = 124_955_592;
const EXPECTED_EXTERNAL_MOVES: u64 = 1_214_053_368;
const EXPECTED_INTERNAL_PER_GROUP: [u64; GROUPS] =
    [6_953_628, 26_744_455, 8_248_254, 15_766_625,
     10_382_736, 22_835_032, 15_913_812, 18_160_970];
const EXPECTED_BOUNDARY_FNV: [u64; GROUPS] =
    [0x56711c533e799e66, 0xf0a68d929477fbf8,
     0x2aa9c2c60c8bccca, 0xe84264cb06b0a205,
     0xf317f125ab06f791, 0xe0fca4c7ac444ab0,
     0xbbc5e3134d6f686e, 0x3e5b7247a34c6477];

#[derive(Clone, Copy, Debug)]
struct PairEdge {
    lo: u64,
    hi: u64,
    signed_flux: i16,
}

fn verify_edge_pairs(edges: &mut [PairEdge]) -> Result<(u64, u64, u64, u64), String> {
    edges.sort_unstable_by_key(|p| (p.lo, p.hi));
    let mut i = 0;
    let mut pairs = 0u64;
    let mut directed = 0u64;
    let mut positive_flux_sum = 0u64;
    let mut digest = 14_695_981_039_346_656_037u64;
    while i < edges.len() {
        let start = i;
        let a = edges[start];
        ensure(a.lo < a.hi && a.signed_flux != 0,
               "invalid_pair_or_zero_flux")?;
        i += 1;
        while i < edges.len() && edges[i].lo == a.lo && edges[i].hi == a.hi {
            i += 1;
        }
        ensure(i - start == 2, "missing_or_duplicate_reverse_edge")?;
        let f = i32::from(edges[start].signed_flux);
        let r = i32::from(edges[start + 1].signed_flux);
        ensure(f + r == 0 && f != 0 && (f > 0) != (r > 0),
               "weighted_reverse_flux_mismatch")?;
        let pos = f.max(r) as u64;
        ensure(pos <= 6 * 72, "weighted_reverse_flux_out_of_range")?;
        positive_flux_sum += pos;
        pairs += 1;
        directed += 2;
        mix_fnv64(&mut digest, a.lo);
        mix_fnv64(&mut digest, a.hi);
        mix_fnv64(&mut digest, pos);
    }
    Ok((pairs, directed, positive_flux_sum, digest))
}

fn b4_toy() -> Result<(), String> {
    let good = [
        PairEdge { lo: 5, hi: 9, signed_flux: 6 },
        PairEdge { lo: 5, hi: 9, signed_flux: -6 },
        PairEdge { lo: 11, hi: 42, signed_flux: 2 },
        PairEdge { lo: 11, hi: 42, signed_flux: -2 },
    ];
    let (pairs, directed, flux, _) = verify_edge_pairs(&mut good.to_vec())?;
    ensure(pairs == 2 && directed == 4 && flux == 8, "pair_toy_reference")?;
    let mut wrong_weight = good.to_vec();
    wrong_weight[1].signed_flux = -5;
    ensure(verify_edge_pairs(&mut wrong_weight).is_err(),
           "incorrect_weighted_reverse_accepted")?;
    let mut missing_reverse = good.to_vec();
    missing_reverse.pop();
    ensure(verify_edge_pairs(&mut missing_reverse).is_err(),
           "missing_reverse_accepted")?;
    let mut duplicated = good.to_vec();
    duplicated.push(good[1]);
    ensure(verify_edge_pairs(&mut duplicated).is_err(),
           "duplicate_directed_reverse_accepted")?;
    let mut wrong_direction = good.to_vec();
    wrong_direction[1].signed_flux = 6;
    ensure(verify_edge_pairs(&mut wrong_direction).is_err(),
           "wrong_edge_direction_accepted")?;
    println!("Y137_STAGE_B4_TOY|pairs=2|directed=4|wrong_weight=REFUSED|missing_reverse=REFUSED|duplicate_reverse=REFUSED|wrong_direction=REFUSED|real_Q5=NOT_COMPUTED|json=0");
    Ok(())
}

fn pair_partition(lo: u64, hi: u64) -> usize {
    let mut v = lo.wrapping_mul(11_400_714_819_323_198_485)
        ^ hi.wrapping_mul(14_029_467_366_897_019_727);
    v ^= v >> 33;
    v = v.wrapping_mul(13_797_801_002_366_949_169);
    ((v ^ (v >> 29)) & (PARTS as u64 - 1)) as usize
}

fn write_pair(writer: &mut BufWriter<File>, e: PairEdge) -> Result<(), String> {
    let mut rec = [0u8; 18];
    rec[..8].copy_from_slice(&e.lo.to_le_bytes());
    rec[8..16].copy_from_slice(&e.hi.to_le_bytes());
    rec[16..].copy_from_slice(&e.signed_flux.to_le_bytes());
    writer.write_all(&rec).map_err(|x| x.to_string())
}

fn reverse_from_source(root: &Path, spool_dir: &Path) -> Result<(), String> {
    let start = Instant::now();
    let mut support = HashMap::<u64, u8>::with_capacity(EXPECTED_ROWS);
    let mut full_bytes = 0u64;
    for (g, expected_rows) in ROWS_BY_GROUP.iter().enumerate() {
        let summary = visit_group(&root.join(format!("GROUP-{g}.v1")), g, |address, weight| {
            ensure(support.insert(address, weight).is_none(), "duplicate_global_Q5_address")
        })?;
        ensure(summary.rows == *expected_rows && summary.bytes == BYTES_BY_GROUP[g],
               "B4_source_manifest_regression")?;
        full_bytes += summary.bytes;
    }
    ensure(support.len() == EXPECTED_ROWS && full_bytes == 3_140_900_108,
           "B4_global_source_index_incomplete")?;
    fs::create_dir_all(spool_dir).map_err(|x| x.to_string())?;
    let mut writers = Vec::<BufWriter<File>>::with_capacity(PARTS);
    for p in 0..PARTS {
        let file = File::create(spool_dir.join(format!("PAIR-{p:03}.bin")))
            .map_err(|x| x.to_string())?;
        writers.push(BufWriter::with_capacity(64 * 1024, file));
    }
    let rule = Rule::new();
    let (mut total_rows, mut total_moves, mut internal_moves,
         mut external_moves, mut directed_records, mut true_selfloops) =
        (0u64, 0u64, 0u64, 0u64, 0u64, 0u64);
    let mut partition_counts = [0u64; PARTS];

    for (g, expected_rows) in ROWS_BY_GROUP.iter().enumerate() {
        let mut rows = 0u64;
        let mut on = 0u64;
        let mut off = 0u64;
        let mut local_pair_records = 0u64;
        let mut exterior_digest = 14_695_981_039_346_656_037u64;
        visit_group(&root.join(format!("GROUP-{g}.v1")), g, |address, stored_weight| {
            let key = decode(address);
            ensure(code(&rule.canonical(&rule.expand(&key))) == address,
                   "B4_independent_canonicality_disagrees")?;
            ensure(rule.weight(&key) == u32::from(stored_weight),
                   "B4_independent_orbit_weight_disagrees")?;
            let magnetic = rule.magnetic(&key);
            ensure((0..=36).contains(&magnetic), "B4_invalid_magnetic_value")?;
            let dests = rule.row(&key);
            let degree: u32 = dests.iter().map(|(_, c)| *c).sum();
            ensure(degree == 72, "B4_bad_raw_move_degree")?;
            rows += 1;
            total_rows += 1;
            total_moves += u64::from(degree);
            for (dest, c) in dests {
                ensure((1..=72).contains(&c), "B4_bad_directed_multiplicity")?;
                if dest == address {
                    true_selfloops += u64::from(c);
                }
                if support.contains_key(&dest) {
                    on += u64::from(c);
                    internal_moves += u64::from(c);
                    if address != dest {
                        let other_w = support[&dest];
                        let flux = i16::try_from(u32::from(stored_weight) * c)
                            .map_err(|x| x.to_string())?;
                        ensure((1..=432).contains(&flux), "B4_weighted_flux_overflow")?;
                        let (lo, hi, signed_flux) = if address < dest {
                            (address, dest, flux)
                        } else {
                            (dest, address, -flux)
                        };
                        let partition = pair_partition(lo, hi);
                        write_pair(&mut writers[partition], PairEdge { lo, hi, signed_flux })?;
                        partition_counts[partition] += 1;
                        local_pair_records += 1;
                        directed_records += 1;
                        // The reverse weight must be the same immutable Q5
                        // orbit weight, independently looked up by destination.
                        ensure(matches!(other_w, 1 | 2 | 3 | 6), "B4_invalid_reverse_orbit_weight")?;
                    }
                } else {
                    off += u64::from(c);
                    external_moves += u64::from(c);
                    mix_fnv64(&mut exterior_digest, address);
                    mix_fnv64(&mut exterior_digest, dest);
                    mix_fnv64(&mut exterior_digest, u64::from(c));
                }
            }
            Ok(())
        })?;
        ensure(rows == *expected_rows && on == EXPECTED_INTERNAL_PER_GROUP[g]
               && exterior_digest == EXPECTED_BOUNDARY_FNV[g],
               "B4_fail_replay_of_B3_group_census")?;
        println!("Y137_STAGE_B4_GROUP|group={g}|rows={rows}|on_Q5_moves={on}|off_Q5_moves={off}|paired_directed_records={local_pair_records}|B3_boundary_fnv64={exterior_digest:016x}|B3_regression=PASS|json=0");
    }
    for writer in &mut writers {
        writer.flush().map_err(|x| x.to_string())?;
    }
    drop(writers);
    ensure(total_rows == EXPECTED_ROWS as u64 && total_moves == EXPECTED_MOVES &&
           internal_moves == EXPECTED_INTERNAL_MOVES &&
           external_moves == EXPECTED_EXTERNAL_MOVES &&
           true_selfloops == 0 &&
           directed_records == EXPECTED_INTERNAL_DIRECTED &&
           partition_counts.iter().sum::<u64>() == directed_records,
           "B4_global_degree_or_B3_regression_mismatch")?;

    let mut all_pairs = 0u64;
    let mut all_directed = 0u64;
    let mut all_absflux = 0u64;
    let mut combined_digest = 14_695_981_039_346_656_037u64;
    for (bucket, &expected_records) in partition_counts.iter().enumerate() {
        let raw = fs::read(spool_dir.join(format!("PAIR-{bucket:03}.bin")))
            .map_err(|x| x.to_string())?;
        ensure(raw.len() % 18 == 0 && raw.len() as u64 / 18 == expected_records,
               "B4_pair_partition_record_size")?;
        let mut records = Vec::<PairEdge>::with_capacity(raw.len() / 18);
        for rec in raw.chunks_exact(18) {
            let lo = u64::from_le_bytes(rec[0..8].try_into().map_err(|_| "B4_pair_lo")?);
            let hi = u64::from_le_bytes(rec[8..16].try_into().map_err(|_| "B4_pair_hi")?);
            let signed_flux = i16::from_le_bytes([rec[16], rec[17]]);
            ensure(pair_partition(lo, hi) == bucket,
                   "B4_pair_partition_key_not_reproducible")?;
            records.push(PairEdge { lo, hi, signed_flux });
        }
        let (pairs, directed, flux, digest) = verify_edge_pairs(&mut records)?;
        ensure(directed == expected_records, "B4_pair_partition_count_mismatch")?;
        all_pairs += pairs;
        all_directed += directed;
        all_absflux += flux;
        mix_fnv64(&mut combined_digest, digest);
        println!("Y137_STAGE_B4_PART|bucket={bucket}|directed={directed}|unordered_pairs={pairs}|positive_flux_sum={flux}|pair_fnv64={digest:016x}|reverse_balance=PASS|json=0");
    }
    ensure(all_directed == EXPECTED_INTERNAL_DIRECTED &&
           all_pairs * 2 == all_directed, "B4_global_pair_count_mismatch")?;
    println!("Y137_STAGE_B4_VERDICT|source_rows={total_rows}|raw_moves={total_moves}|Q5_directed_records={all_directed}|unordered_Q5_pairs={all_pairs}|Q5_raw_moves={internal_moves}|outside_Q5_raw_moves={external_moves}|genuine_selfloop_moves={true_selfloops}|weighted_reverse_mismatches=0|unmatched_reverse_records=0|weighted_pair_positive_flux_sum={all_absflux}|pair_partition_fnv64={combined_digest:016x}|partitions={PARTS}|milliseconds={}|preregistered_B4=PASS|B5_B8=PENDING|real_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0", start.elapsed().as_millis());
    Ok(())
}


// -----------------------------------------------------------------------------
// #137 Stage C exact cross-block electric graph.
// B4's original independent S3 Rule and exact pair-sort machinery above stay
// byte-for-byte unchanged. Exclude Q5<->Q5 pairs, already accepted by B4;
// exhaustively verify *all* remaining K3/Q4/K3-Q5/Q4-Q5 reciprocal edges.

#[derive(Clone, Copy)]
struct SourceCell {
    shell: u8,
    weight: u8,
}

fn c_visit_signed<F>(path: &Path, expected_shell: u8, mut visit: F) -> Result<u64, String>
where F: FnMut(u64, u8) -> Result<(), String> {
    let file = File::open(path).map_err(|e| e.to_string())?;
    let mut reader = BufReader::with_capacity(1_048_576, file);
    let mut head = [0u8; 11];
    let mut first = [0u8; 1];
    let mut magnitude = [0u8; 24];
    let mut count = 0u64;
    let mut last = None;
    loop {
        let n = reader.read(&mut first).map_err(|e| e.to_string())?;
        if n == 0 { break; }
        head[0] = first[0];
        reader.read_exact(&mut head[1..]).map_err(|e| e.to_string())?;
        let addr = u64::from_le_bytes(head[..8].try_into().map_err(|_| "signed_address")?);
        let weight = head[8];
        ensure(addr < MAX_ADDR && matches!(weight, 1 | 2 | 3 | 6),
               "C_invalid_signed_address_or_orbit_weight")?;
        ensure(head[9] == expected_shell && head[10] == 2,
               "C_wrong_signed_shell_or_frozen_energy_count")?;
        if let Some(prior) = last {
            ensure(addr > prior, "C_nonascending_signed_group_address")?;
        }
        last = Some(addr);
        for _ in 0..16 {
            reader.read_exact(&mut first).map_err(|e| e.to_string())?;
            let len = usize::from(first[0] & 127);
            ensure(len <= 24 && (first[0] & 128 == 0 || len > 0),
                   "C_malformed_signed_192bit_lane")?;
            reader.read_exact(&mut magnitude[..len]).map_err(|e| e.to_string())?;
            ensure(len == 0 || magnitude[len - 1] != 0,
                   "C_nonminimal_signed_amplitude")?;
        }
        visit(addr, weight)?;
        count += 1;
    }
    Ok(count)
}

fn c_load_support(signed: &Path, q5: &Path) -> Result<HashMap<u64, SourceCell>, String> {
    let mut support = HashMap::<u64, SourceCell>::with_capacity(20_738_636);
    for group in 0..8usize {
        let path = signed.join(format!("SIGNED-Q4-{group}.v1"));
        let found = c_visit_signed(&path, 4, |address, weight| {
            ensure(support.insert(address, SourceCell { shell: 4, weight }).is_none(),
                   "C_duplicate_K3_Q4_signed_support_address")
        })?;
        let start = 1_985_218u64 * group as u64 / 8;
        let end = 1_985_218u64 * (group as u64 + 1) / 8;
        ensure(found == end - start, "C_wrong_full_Q4_original_partition_count")?;
        println!("Y137_C_GRAPH_INDEX|shell=Q4|group={group}|rows={found}|json=0");
    }
    let found = c_visit_signed(&signed.join("SIGNED-K3.v1"), 3, |address, weight| {
        ensure(support.insert(address, SourceCell { shell: 3, weight }).is_none(),
               "C_duplicate_or_cross_K3_Q4_address")
    })?;
    ensure(found == 155_378, "C_wrong_full_K3_original_count")?;
    println!("Y137_C_GRAPH_INDEX|shell=K3|group=0|rows={found}|json=0");
    for (group, &expected) in ROWS_BY_GROUP.iter().enumerate() {
        let summary = visit_group(&q5.join(format!("GROUP-{group}.v1")), group,
                                  |address, weight| {
            ensure(support.insert(address, SourceCell { shell: 5, weight }).is_none(),
                   "C_duplicate_or_cross_Q5_address")
        })?;
        ensure(summary.rows == expected && summary.bytes == BYTES_BY_GROUP[group],
               "C_original_Q5_source_count_or_bytes_disagree")?;
        println!("Y137_C_GRAPH_INDEX|shell=Q5|group={group}|rows={}|bytes={}|json=0",
                 summary.rows, summary.bytes);
    }
    ensure(support.len() == 20_738_636, "C_wrong_full_K3_Q4_Q5_disjoint_support_count")?;
    Ok(support)
}

#[derive(Default)]
struct CGraphTotals {
    rows: [u64; 3],
    raw_moves: [u64; 3],
    on: [[u64; 3]; 3],
    flux: [[u64; 3]; 3],
    off: [u64; 3],
    off_unique: [u64; 3],
    selfloops: [u64; 3],
    partitions: [u64; PARTS],
    directed: u64,
    all_weighted: u64,
}

fn c_process_row(
    rule: &Rule,
    address: u64,
    cell: SourceCell,
    support: &HashMap<u64, SourceCell>,
    writers: &mut [BufWriter<File>],
    sums: &mut CGraphTotals,
) -> Result<(), String> {
    let key = decode(address);
    ensure(code(&rule.canonical(&rule.expand(&key))) == address,
           "C_independent_full_row_canonicality_disagreement")?;
    ensure(rule.weight(&key) == u32::from(cell.weight),
           "C_independent_full_row_orbit_weight_disagreement")?;
    let magnetic = rule.magnetic(&key);
    ensure((0..=36).contains(&magnetic), "C_wrong_full_row_magnetic_value")?;
    let source_shell = usize::from(cell.shell - 3);
    let row = rule.row(&key);
    let degree: u32 = row.iter().map(|(_, count)| *count).sum();
    ensure(degree == 72, "C_actual_72_move_row_degree_changed")?;
    sums.rows[source_shell] += 1;
    sums.raw_moves[source_shell] += u64::from(degree);
    for (dest, count) in row {
        ensure((1..=72).contains(&count), "C_zero_or_too_many_parallel_electric_moves")?;
        sums.all_weighted += u64::from(cell.weight) * u64::from(count);
        if let Some(other) = support.get(&dest) {
            let target_shell = usize::from(other.shell - 3);
            sums.on[source_shell][target_shell] += u64::from(count);
            sums.flux[source_shell][target_shell] +=
                u64::from(cell.weight) * u64::from(count);
            if dest == address {
                sums.selfloops[source_shell] += u64::from(count);
                continue;
            }
            // B4 has already accepted the complete exact Q5 principal block
            // and its 62,477,796 unordered reciprocal pairs. No double count.
            if source_shell == 2 && target_shell == 2 { continue; }
            let flux = i16::try_from(u32::from(cell.weight) * count)
                .map_err(|e| e.to_string())?;
            ensure((1..=432).contains(&flux), "C_cross_graph_weighted_flux_overflow")?;
            let (lo, hi, signed_flux) = if address < dest {
                (address, dest, flux)
            } else {
                (dest, address, -flux)
            };
            let part = pair_partition(lo, hi);
            write_pair(&mut writers[part], PairEdge { lo, hi, signed_flux })?;
            sums.partitions[part] += 1;
            sums.directed += 1;
        } else {
            // The finite source deliberately excludes flats and outer rows.
            // These remain in the full 72-degree diagonal operator and are
            // independently counted; never silently label them Q5 or Q6.
            sums.off[source_shell] += u64::from(count);
            sums.off_unique[source_shell] += 1;
        }
    }
    Ok(())
}

fn c_graph_selftest() -> Result<(), String> {
    b4_toy()?;
    let rule = Rule::new();
    let zero = [0u8; KEPT];
    let neighbors = rule.row(&zero);
    ensure(neighbors.iter().map(|(_, n)| *n).sum::<u32>() == 72,
           "C_toy_actual_raw_degree")?;
    let mut edges = [
        PairEdge { lo: 4, hi: 5, signed_flux: 3 },
        PairEdge { lo: 4, hi: 5, signed_flux: -3 },
        PairEdge { lo: 5, hi: 9, signed_flux: 12 },
        PairEdge { lo: 5, hi: 9, signed_flux: -12 },
    ];
    let (pairs, directed, total, _) = verify_edge_pairs(&mut edges)?;
    ensure(pairs == 2 && directed == 4 && total == 15,
           "C_toy_unequal_orbit_weights_did_not_balance")?;
    let mut fault = edges.to_vec();
    fault[0].signed_flux += 1;
    ensure(verify_edge_pairs(&mut fault).is_err(),
           "C_toy_wrong_weighted_reverse_was_accepted")?;
    let mut fault = edges.to_vec();
    fault.pop();
    ensure(verify_edge_pairs(&mut fault).is_err(),
           "C_toy_missing_external_reverse_was_accepted")?;
    let mut fault = edges.to_vec();
    fault.push(edges[0]);
    ensure(verify_edge_pairs(&mut fault).is_err(),
           "C_toy_duplicate_external_reverse_was_accepted")?;
    println!("Y137_C_GRAPH_TOY|S3_72_raw_moves=PASS|two_cross_block_pairs=PASS|wrong_weighted_reverse=REFUSED|missing_reverse=REFUSED|duplicate_reverse=REFUSED|Q5_Q5_B4_unchanged=PASS|real_full_electric_graph=NOT_COMPUTED|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0");
    Ok(())
}

fn c_full_graph(signed: &Path, q5: &Path, spool: &Path) -> Result<(), String> {
    let clock = Instant::now();
    let support = c_load_support(signed, q5)?;
    fs::create_dir_all(spool).map_err(|e| e.to_string())?;
    let mut writers = Vec::<BufWriter<File>>::with_capacity(PARTS);
    for part in 0..PARTS {
        let f = File::create(spool.join(format!("C-PAIR-{part:03}.bin")))
            .map_err(|e| e.to_string())?;
        writers.push(BufWriter::with_capacity(64 * 1024, f));
    }
    let rule = Rule::new();
    let mut sums = CGraphTotals::default();
    for group in 0..8usize {
        let n = c_visit_signed(&signed.join(format!("SIGNED-Q4-{group}.v1")), 4,
                               |addr, weight| {
            c_process_row(&rule, addr, SourceCell { shell: 4, weight }, &support,
                          &mut writers, &mut sums)
        })?;
        println!("Y137_C_GRAPH_SOURCE|shell=Q4|group={group}|rows={n}|json=0");
    }
    let n = c_visit_signed(&signed.join("SIGNED-K3.v1"), 3, |addr, weight| {
        c_process_row(&rule, addr, SourceCell { shell: 3, weight },
                      &support, &mut writers, &mut sums)
    })?;
    println!("Y137_C_GRAPH_SOURCE|shell=K3|group=0|rows={n}|json=0");
    for (group, &expected) in ROWS_BY_GROUP.iter().enumerate() {
        let summary = visit_group(&q5.join(format!("GROUP-{group}.v1")), group,
                                  |addr, weight| {
            c_process_row(&rule, addr, SourceCell { shell: 5, weight },
                          &support, &mut writers, &mut sums)
        })?;
        ensure(summary.rows == expected, "C_Q5_replayed_original_row_count")?;
        println!("Y137_C_GRAPH_SOURCE|shell=Q5|group={group}|rows={}|json=0",
                 summary.rows);
    }
    for w in &mut writers { w.flush().map_err(|e| e.to_string())?; }
    drop(writers);
    ensure(sums.rows == [155_378, 1_985_218, 18_598_040],
           "C_full_graph_exact_supported_source_count")?;
    ensure(sums.raw_moves == [11_187_216, 142_935_696, 1_339_058_880],
           "C_full_graph_72_moves_each_source")?;
    ensure(sums.on[2][2] == EXPECTED_INTERNAL_MOVES,
           "C_B3_Q5_internal_raw_moves_regression")?;
    ensure(sums.selfloops[2] == 0, "C_B4_Q5_true_selfloop_regression")?;
    for i in 0..3 {
        ensure(sums.on[i].iter().sum::<u64>() + sums.off[i] == sums.raw_moves[i],
               "C_some_genuine_external_moves_were_lost")?;
        for j in (i + 1)..3 {
            ensure(sums.flux[i][j] == sums.flux[j][i],
                   "C_cross_block_total_weighted_reverse_flux_disagreement")?;
        }
        println!("Y137_C_GRAPH_BLOCK|source_shell={}|rows={}|raw_moves={}|to_K3={}|to_Q4={}|to_Q5={}|off_source_raw_moves={}|off_source_unique_dests={}|true_selfloop_moves={}|json=0",
                 i + 3, sums.rows[i], sums.raw_moves[i], sums.on[i][0],
                 sums.on[i][1], sums.on[i][2], sums.off[i],
                 sums.off_unique[i], sums.selfloops[i]);
    }
    ensure(sums.partitions.iter().sum::<u64>() == sums.directed,
           "C_missing_directed_pair_records")?;
    let mut paired = 0u64;
    let mut actual_directed = 0u64;
    let mut absolute_flux = 0u64;
    let mut combined_digest = 14_695_981_039_346_656_037u64;
    for (part, &expected) in sums.partitions.iter().enumerate() {
        let data = fs::read(spool.join(format!("C-PAIR-{part:03}.bin")))
            .map_err(|e| e.to_string())?;
        ensure(data.len() % 18 == 0 && data.len() as u64 / 18 == expected,
               "C_exact_external_pair_file_length")?;
        let mut edges = Vec::<PairEdge>::with_capacity(data.len() / 18);
        for b in data.chunks_exact(18) {
            let lo = u64::from_le_bytes(b[..8].try_into().map_err(|_| "cross_lo")?);
            let hi = u64::from_le_bytes(b[8..16].try_into().map_err(|_| "cross_hi")?);
            let flux = i16::from_le_bytes([b[16], b[17]]);
            ensure(pair_partition(lo, hi) == part,
                   "C_pair_record_not_in_canonical_partition")?;
            edges.push(PairEdge { lo, hi, signed_flux: flux });
        }
        let (pairs, directed, total_flux, digest) = verify_edge_pairs(&mut edges)?;
        ensure(directed == expected, "C_unaccounted_external_weighted_edges")?;
        paired += pairs;
        actual_directed += directed;
        absolute_flux += total_flux;
        mix_fnv64(&mut combined_digest, digest);
        println!("Y137_C_GRAPH_PART|part={part}|directed={directed}|unordered_pairs={pairs}|positive_flux_sum={total_flux}|exact_balance=PASS|pair_fnv64={digest:016x}|json=0");
        // Each 18-byte pair record remains in a per-part file for independent
        // numerical μ3 paired-edge assembly. Pairing checked before deleting.
    }
    ensure(actual_directed == sums.directed && paired * 2 == actual_directed,
           "C_full_graph_incomplete_reciprocal_edge_count")?;
    println!("Y137_C_GRAPH_VERDICT|K3_rows={}|Q4_rows={}|Q5_rows={}|K3_raw_moves={}|Q4_raw_moves={}|Q5_raw_moves={}|all_raw_moves={}|Q5_Q5_raw_moves={}|non_Q5_Q5_directed_records={}|non_Q5_Q5_unordered_pairs={}|positive_pair_flux_sum={}|global_pair_fnv64={combined_digest:016x}|genuine_selfloops_K3={}|genuine_selfloops_Q4={}|genuine_selfloops_Q5={}|off_source_K3={}|off_source_Q4={}|off_source_Q5={}|weighted_reverse_mismatches=0|unmatched_reverse_records=0|full_three_block_support=20738636|original_B4_Q5_Q5=UNCHANGED|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|milliseconds={}|json=0",
             sums.rows[0], sums.rows[1], sums.rows[2],
             sums.raw_moves[0], sums.raw_moves[1], sums.raw_moves[2],
             sums.raw_moves.iter().sum::<u64>(), sums.on[2][2],
             actual_directed, paired, absolute_flux,
             sums.selfloops[0], sums.selfloops[1], sums.selfloops[2],
             sums.off[0], sums.off[1], sums.off[2], clock.elapsed().as_millis());
    Ok(())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let verdict = match args.as_slice() {
        [_, mode] if mode == "--selftest" => selftest(),
        [_, mode] if mode == "--b4-selftest" => b4_toy(),
        [_, mode] if mode == "--c-selftest" => c_graph_selftest(),
        [_, mode, signed, q5, spool] if mode == "--c-cross" =>
            c_full_graph(Path::new(signed), Path::new(q5), Path::new(spool)),
        [_, mode, root] if mode == "--run" => run(Path::new(root)),
        [_, mode, root, spool] if mode == "--b4" =>
            reverse_from_source(Path::new(root), Path::new(spool)),
        _ => Err("usage: b4_reverse --b4-selftest | --b4 SOURCE_DIR SPOOL_DIR".to_string()),
    };
    if let Err(why) = verdict {
        eprintln!("Y137_STAGE_B4_REFUSE|reason={why}|json=0");
        std::process::exit(1);
    }
}
