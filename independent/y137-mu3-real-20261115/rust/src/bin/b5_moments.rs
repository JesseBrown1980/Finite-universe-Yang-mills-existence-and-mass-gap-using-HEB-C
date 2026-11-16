//! #137 Worker1 B5: exact Q5 principal third moments, two independent aggregations.
//! 3x4 S3 torus, integers only; ordered-row vs W-balanced upper-edge form.
//! Original frozen Q5 sources store positive V1/b; b=1000000000.
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

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
struct Wide([u64; 5]);

impl Wide {
    const ZERO: Wide = Wide([0; 5]);

    /// a * b * w for a, b below 2^128 and w below 2^64, as a nonnegative 320-bit value
    fn product(a: u128, b: u128, w: u64) -> Wide {
        let (a0, a1) = (a as u64, (a >> 64) as u64);
        let (b0, b1) = (b as u64, (b >> 64) as u64);
        // a*b as four limbs
        let p00 = u128::from(a0) * u128::from(b0);
        let p01 = u128::from(a0) * u128::from(b1);
        let p10 = u128::from(a1) * u128::from(b0);
        let p11 = u128::from(a1) * u128::from(b1);
        let l0 = p00 as u64;
        let mid = (p00 >> 64) + u128::from(p01 as u64) + u128::from(p10 as u64);
        let l1 = mid as u64;
        let hi = (mid >> 64) + (p01 >> 64) + (p10 >> 64) + u128::from(p11 as u64);
        let l2 = hi as u64;
        let l3 = ((hi >> 64) + (p11 >> 64)) as u64;
        // times w
        let mut out = [0u64; 5];
        let mut carry = 0u128;
        for (o, l) in out.iter_mut().zip([l0, l1, l2, l3]) {
            let t = u128::from(l) * u128::from(w) + carry;
            *o = t as u64;
            carry = t >> 64;
        }
        out[4] = carry as u64;
        Wide(out)
    }

    fn add(&mut self, o: &Wide) {
        let mut carry = 0u128;
        for (s, &x) in self.0.iter_mut().zip(&o.0) {
            let t = u128::from(*s) + u128::from(x) + carry;
            *s = t as u64;
            carry = t >> 64;
        }
    }

    fn sub(&mut self, o: &Wide) {
        let mut borrow = 0i128;
        for (s, &x) in self.0.iter_mut().zip(&o.0) {
            let t = i128::from(*s) - i128::from(x) - borrow;
            *s = t as u64;
            borrow = i128::from(t < 0);
        }
    }

    fn negative(&self) -> bool {
        self.0[4] >> 63 == 1
    }

    /// decimal text of the signed value
    fn decimal(&self) -> String {
        let mut mag = *self;
        let neg = self.negative();
        if neg {
            let mut z = Wide::ZERO;
            z.sub(self);
            mag = z;
        }
        let mut digits: Vec<u8> = Vec::new();
        let mut limbs = mag.0;
        while limbs.iter().any(|&l| l != 0) {
            let mut rem = 0u128;
            for l in limbs.iter_mut().rev() {
                let cur = (rem << 64) | u128::from(*l);
                *l = (cur / 1_000_000_000_000_000_000) as u64;
                rem = cur % 1_000_000_000_000_000_000;
            }
            let mut r = rem as u64;
            for _ in 0..18 {
                digits.push(b'0' + (r % 10) as u8);
                r /= 10;
            }
        }
        while digits.len() > 1 && digits.last() == Some(&b'0') {
            digits.pop();
        }
        if digits.is_empty() {
            digits.push(b'0');
        }
        digits.reverse();
        let s = String::from_utf8(digits).unwrap_or_default();
        if neg {
            format!("-{s}")
        } else {
            s
        }
    }
}


const GROUPS: usize = 8;
const COLS: usize = 8;
const B: u128 = 1_000_000_000;
const SAMPLES: [i64; 2] = [69_909_875_505, 69_949_729_820];
const ROWS_BY_GROUP: [usize; GROUPS] =
    [435324,4439918,988399,2812763,822474,3973928,1612450,3512784];
const BYTES_BY_GROUP: [u64; GROUPS] =
    [72717336,750840749,166069410,476041564,137545818,672121828,270439868,595123535];
const STATES: usize = 18_598_040;
const RAW_MOVES: u64 = 1_339_058_880;
const Q5_MOVES: u64 = 125_005_512;
const Q5_DIRECTED: u64 = 124_955_592;
const Q5_PAIRS: u64 = 62_477_796;
const LIMIT_A: u128 = 1u128 << 112;
const LIMIT_B: u128 = 1u128 << 123;
const LIMIT_COEFF: u64 = 1u64 << 37;
const MAX_TERMS: u64 = 1u64 << 31;
const MAGNITUDE_TOP_LIMIT: u64 = 1u64 << 48;

fn ensure(ok: bool, why: &str) -> Result<(), String> {
    if ok { Ok(()) } else { Err(why.to_string()) }
}

impl Wide {
    fn raw_checked_add(&mut self, rhs: &Wide) -> Result<(), String> {
        let a = self.negative();
        let b = rhs.negative();
        let mut out = *self;
        out.add(rhs);
        ensure(a != b || out.negative() == a, "signed_320_bit_overflow")?;
        *self = out;
        Ok(())
    }

    fn abs_lt_2pow304(&self) -> bool {
        let mut mag = *self;
        if self.negative() {
            let mut zero = Wide::ZERO;
            zero.sub(self);
            mag = zero;
        }
        mag.0[4] < MAGNITUDE_TOP_LIMIT
    }
}


#[derive(Clone, Copy)]
struct CheckedMoment { total: Wide, terms: u64 }
impl CheckedMoment {
    fn zero() -> Self { Self { total: Wide::ZERO, terms: 0 } }
    // a is a physical single Q5 source amplitude; b is a contracted
    // physical row or paired-edge component. Bounds:
    // a<2^112, b<2^123, |c|<2^37, terms<2^31 => |partial|<2^303.
    fn add_contracted(&mut self, a: u128, b: u128, coefficient: i64)
        -> Result<(), String> {
        ensure(a < LIMIT_A, "B5_physical_Q5_amplitude_bound")?;
        ensure(b < LIMIT_B, "B5_contracted_Q5_amplitude_bound")?;
        ensure(coefficient.unsigned_abs() < LIMIT_COEFF,
               "B5_weighted_coefficient_bound")?;
        ensure(self.terms < MAX_TERMS, "B5_max_terms_exceeded")?;
        let mut term = Wide::product(a, b, coefficient.unsigned_abs());
        if coefficient < 0 {
            let mut neg = Wide::ZERO;
            neg.sub(&term);
            term = neg;
        }
        let mut candidate = self.total;
        candidate.raw_checked_add(&term)?;
        ensure(candidate.abs_lt_2pow304(), "B5_partial_sum_exceeds_2pow304")?;
        self.total = candidate;
        self.terms += 1;
        Ok(())
    }
}

struct Source {
    address: u64,
    weight: u8,
    amp: [[u128; COLS]; 2],
}
fn decode_lanes(encoded: &[u8]) -> Result<[u128; COLS], String> {
    ensure(encoded.len() <= 82, "B5_invalid_packed_length")?;
    ensure(encoded.is_empty() || encoded[encoded.len() - 1] != 0,
           "B5_nonminimal_unsigned_packed_vector")?;
    let mut padded = [0u8; 96];
    padded[..encoded.len()].copy_from_slice(encoded);
    let mut values = [0u128; COLS];
    let mask = (1u128 << 82) - 1;
    for (i, val) in values.iter_mut().enumerate() {
        let bit = 82 * i;
        let start = bit / 8;
        let shift = bit % 8;
        let mut chunk = [0u8; 16];
        chunk.copy_from_slice(&padded[start..start + 16]);
        *val = (u128::from_le_bytes(chunk) >> shift) & mask;
    }
    Ok(values)
}
fn read_group<F: FnMut(Source) -> Result<(), String>>(
    path: &Path, group: usize, mut accept: F
) -> Result<(usize, u64), String> {
    let file = File::open(path).map_err(|x| format!("B5_open_source_{group}:{x}"))?;
    let mut reader = BufReader::with_capacity(1_048_576, file);
    let mut head = [0u8; 13];
    let mut n = 0usize;
    let mut bytes = 0u64;
    let mut last_bucket: Option<u64> = None;
    let mut previous: Option<u64> = None;
    loop {
        let count = reader.read(&mut head[..1]).map_err(|x| x.to_string())?;
        if count == 0 { break; }
        reader.read_exact(&mut head[1..]).map_err(|x| format!("B5_truncated_header:{x}"))?;
        let address = u64::from_le_bytes(head[..8].try_into()
                 .map_err(|_|"B5_address_header")?);
        let weight = head[8];
        let n0 = usize::from(u16::from_le_bytes([head[9], head[10]]));
        let n1 = usize::from(u16::from_le_bytes([head[11], head[12]]));
        ensure(n0<=82 && n1<=82, "B5_packed_length_overflow")?;
        ensure(matches!(weight, 1|2|3|6), "B5_invalid_orbit_weight")?;
        let bucket = address%64;
        ensure(bucket%8==group as u64, "B5_group_partition")?;
        if let Some(old) = last_bucket {
            if bucket!=old {
                ensure(bucket==old+8, "B5_bucket_order_or_missing")?;
                previous=None;
            }
        } else {
            ensure(bucket==group as u64, "B5_wrong_first_bucket")?;
        }
        if let Some(last) = previous {
            ensure(address>last, "B5_source_not_strictly_sorted_in_bucket")?;
        }
        previous=Some(address);
        last_bucket=Some(bucket);
        let mut buf0 = [0u8;82];
        let mut buf1 = [0u8;82];
        reader.read_exact(&mut buf0[..n0]).map_err(|x|format!("B5_truncated_E1:{x}"))?;
        reader.read_exact(&mut buf1[..n1]).map_err(|x|format!("B5_truncated_E2:{x}"))?;
        let a0=decode_lanes(&buf0[..n0])?;
        let a1=decode_lanes(&buf1[..n1])?;
        accept(Source{address,weight,amp:[a0,a1]})?;
        n+=1;
        bytes+=(13+n0+n1) as u64;
    }
    ensure(last_bucket==Some((group+56) as u64), "B5_missing_last_bucket")?;
    Ok((n,bytes))
}
fn mul_u128(a: u128, b: u128) -> Result<u128,String> {
    a.checked_mul(b).ok_or_else(||"B5_contraction_product_overflow".to_string())
}
fn add_u128(dst: &mut u128, value: u128) -> Result<(),String> {
    *dst=dst.checked_add(value).ok_or_else(||"B5_contraction_sum_overflow".to_string())?;
    Ok(())
}
fn new_matrices() -> [[CheckedMoment;64];2] {
    [[CheckedMoment::zero();64];2]
}
fn matrix_text(matrix: &[CheckedMoment;64], symmetric:bool) -> String {
    let mut rows=Vec::with_capacity(8);
    for i in 0..COLS {
        let mut cells=Vec::with_capacity(8);
        for j in 0..COLS {
            let k=if symmetric && j<i {j*8+i} else {i*8+j};
            cells.push(matrix[k].total.decimal());
        }
        rows.push(cells.join(","));
    }
    rows.join(";")
}
fn check_matrix(row: &[CheckedMoment;64], pair: &[CheckedMoment;64])
    -> Result<(),String> {
    for i in 0..COLS {
        for j in 0..COLS {
            let k=i*8+j;
            let p=if j<i {j*8+i} else {k};
            ensure(row[k].total==pair[p].total,
                   "B5_ordered_row_disagrees_with_unordered_pair")?;
        }
    }
    Ok(())
}


fn run(root: &Path, limit: Option<usize>) -> Result<(),String> {
    let begin=Instant::now();
    let mut index=HashMap::<u64,u32>::with_capacity(STATES);
    let mut states=Vec::<Source>::with_capacity(STATES);
    for group in 0..GROUPS {
        let name=root.join(format!("GROUP-{group}.v1"));
        let (rows,bytes)=read_group(&name,group,|state|{
            let pos=u32::try_from(states.len())
                .map_err(|_|"B5_u32_index_capacity".to_string())?;
            ensure(index.insert(state.address,pos).is_none(),
                   "B5_duplicate_global_source")?;
            states.push(state);
            Ok(())
        })?;
        ensure(rows==ROWS_BY_GROUP[group] && bytes==BYTES_BY_GROUP[group],
               "B5_original_group_census_regression")?;
        println!("Y137_B5_INDEX_GROUP|group={group}|rows={rows}|bytes={bytes}|json=0");
    }
    ensure(states.len()==STATES && index.len()==STATES, "B5_global_index_count")?;
    println!("Y137_B5_INDEX|states={}|samples=2|eight_packed_lanes=PASS|json=0",
             states.len());
    let mut ordered=new_matrices();
    let mut paired=new_matrices();
    let rule=Rule::new();
    let mut rows=0usize;
    let mut raw_moves=0u64;
    let mut on_q5_moves=0u64;
    let mut directed=0u64;
    let mut pairs=0u64;
    let mut self_moves=0u64;
    for state in &states {
        if let Some(stop)=limit {
            if rows>=stop {break;}
        }
        let key=decode(state.address);
        ensure(code(&rule.canonical(&rule.expand(&key)))==state.address,
               "B5_independent_canonical_replay")?;
        ensure(rule.weight(&key)==u32::from(state.weight),
               "B5_independent_weight_replay")?;
        let magnetic=rule.magnetic(&key);
        ensure((0..=36).contains(&magnetic),"B5_independent_magnetic_range")?;
        let neighbors=rule.row(&key);
        let degree=neighbors.iter().map(|(_,count)|u64::from(*count)).sum::<u64>();
        ensure(degree==72,"B5_row_degree_not_72")?;
        raw_moves+=degree;
        let mut complete=[[0u128;COLS];2];
        let mut upper=[[0u128;COLS];2];
        let mut self_count=0u32;
        for (dest,multiplicity) in neighbors {
            if dest==state.address { self_count+=multiplicity; }
            if let Some(&id)=index.get(&dest) {
                on_q5_moves+=u64::from(multiplicity);
                directed+=1;
                if dest!=state.address {
                    let next=&states[id as usize];
                    if dest>state.address {pairs+=1;}
                    for e in 0..2 {
                        for c in 0..COLS {
                            add_u128(&mut complete[e][c],
                                     mul_u128(next.amp[e][c],u128::from(multiplicity))?)?;
                            if dest>state.address {
                                let flux=u128::from(multiplicity)
                                    *u128::from(state.weight);
                                add_u128(&mut upper[e][c],
                                         mul_u128(next.amp[e][c],flux)?)?;
                            }
                        }
                    }
                }
            }
        }
        self_moves+=u64::from(self_count);
        for energy in 0..2 {
            let diag=(1_000_000_000i64)
                .checked_mul(i64::from(72+9*magnetic))
                .and_then(|x|x.checked_sub(SAMPLES[energy]))
                .ok_or_else(||"B5_operator_diagonal_overflow".to_string())?;
            let dself=diag
                .checked_sub(1_000_000_000i64*i64::from(self_count))
                .ok_or_else(||"B5_selfloop_diagonal_overflow".to_string())?;
            let mut v=[0u128;COLS];
            let mut t=[0i128;COLS];
            let mut flux=[0u128;COLS];
            for c in 0..COLS {
                let q=state.amp[energy][c];
                v[c]=mul_u128(q,B)?;
                ensure(v[c]<LIMIT_A,"B5_source_physical_amplitude")?;
                let diagonal=i128::from(dself)
                    .checked_mul(i128::try_from(q)
                                 .map_err(|_|"B5_source_to_i128")?)
                    .ok_or_else(||"B5_operator_diagonal_term_overflow".to_string())?;
                let neighbors=mul_u128(complete[energy][c],B)?;
                t[c]=diagonal.checked_sub(
                    i128::try_from(neighbors).map_err(|_|"B5_neighbor_to_i128")?)
                    .ok_or_else(||"B5_signed_contracted_vector_overflow".to_string())?;
                flux[c]=mul_u128(upper[energy][c],B)?;
                ensure(t[c].unsigned_abs()<LIMIT_B && flux[c]<LIMIT_B,
                       "B5_contracted_physical_vector_range")?;
            }
            let diag_coefficient=6*i64::from(state.weight)*1_000_000_000i64;
            let pair_off_coefficient=-(6i64*1_000_000_000);
            let mut pair_diag=[0u128;COLS];
            for c in 0..COLS {
                pair_diag[c]=mul_u128(state.amp[energy][c],
                                      u128::from(dself.unsigned_abs()))?;
                ensure(pair_diag[c]<LIMIT_B,"B5_paired_diagonal_bound")?;
            }
            for a in 0..COLS {
                for b in 0..COLS {
                    let k=a*COLS+b;
                    ordered[energy][k].add_contracted(
                        v[a],t[b].unsigned_abs(),
                        if t[b]<0 {-diag_coefficient} else {diag_coefficient}
                    )?;
                    if a<=b {
                        paired[energy][k].add_contracted(
                            v[a],pair_diag[b],
                            if dself<0 {-diag_coefficient} else {diag_coefficient}
                        )?;
                        paired[energy][k].add_contracted(
                            v[a],flux[b],pair_off_coefficient
                        )?;
                        paired[energy][k].add_contracted(
                            v[b],flux[a],pair_off_coefficient
                        )?;
                    }
                }
            }
        }
        rows+=1;
        if rows%1_000_000==0 {
            println!("Y137_B5_PROGRESS|rows={rows}|raw_moves={raw_moves}|Q5_moves={on_q5_moves}|paired_upper_edges={pairs}|json=0");
        }
    }
    if limit.is_some() {
        println!("Y137_B5_BENCH|rows={rows}|raw_moves={raw_moves}|Q5_moves={on_q5_moves}|paired_upper_edges={pairs}|millis={}|real_mu3=NOT_COMPUTED|json=0",
                 begin.elapsed().as_millis());
        return Ok(());
    }
    ensure(rows==STATES && raw_moves==RAW_MOVES && on_q5_moves==Q5_MOVES &&
           directed==Q5_DIRECTED && pairs==Q5_PAIRS && self_moves==0,
           "B5_frozen_B3_B4_graph_count_regression")?;
    for energy in 0..2 {
        check_matrix(&ordered[energy],&paired[energy])?;
        let row_text=matrix_text(&ordered[energy],false);
        let pair_text=matrix_text(&paired[energy],true);
        ensure(row_text==pair_text,"B5_matrix_encoding_disagreement")?;
        println!("Y137_B5_MATRIX|sample_num={}|quantity=Q5_principal_mu3_six|row={row_text}|paired={pair_text}|all_64_entries_exact=PASS|json=0",
                 SAMPLES[energy]);
    }
    println!("Y137_B5_VERDICT|source_states={rows}|raw_moves={raw_moves}|Q5_raw_moves={on_q5_moves}|directed_Q5_records={directed}|unordered_Q5_pairs={pairs}|genuine_selfloop_moves={self_moves}|samples=2|matrix_entries_checked=128|preregistered_B5=PASS|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|millis={}|json=0",
             begin.elapsed().as_millis());
    Ok(())
}

fn selftest() -> Result<(),String> {
    let vals=[0u128,1,17,(1u128<<82)-1,4,99,1024,8192];
    let mut packed=[0u8;82];
    for (lane,&value) in vals.iter().enumerate() {
        for b in 0..82 {
            if ((value>>b)&1)!=0 {
                let bit=lane*82+b;
                packed[bit/8]|=1<<(bit%8);
            }
        }
    }
    ensure(decode_lanes(&packed)?==vals,"B5_bit82_pack_roundtrip")?;
    let mut exact=CheckedMoment::zero();
    exact.add_contracted(B*17,B*22,36*1_000_000_000)?;
    exact.add_contracted(B*17,B*22,-36*1_000_000_000)?;
    ensure(exact.total==Wide::ZERO,"B5_signed_wide_cancellation")?;
    let mut bad=CheckedMoment::zero();
    ensure(bad.add_contracted(LIMIT_A,1,1).is_err(),"B5_oversized_src_accepted")?;
    ensure(bad.add_contracted(1,LIMIT_B,1).is_err(),"B5_oversized_contraction_accepted")?;
    ensure(bad.add_contracted(1,1,LIMIT_COEFF as i64).is_err(),
           "B5_oversized_coefficient_accepted")?;
    let rule=Rule::new();
    let zero=[0u8;KEPT];
    ensure(rule.magnetic(&zero)==0 &&
           rule.row(&zero).iter().map(|(_,c)|*c).sum::<u32>()==72,
           "B5_original_rule_replay")?;
    println!("Y137_B5_TOY|packed_82bit_lanes=PASS|signed_320_cancellation=PASS|oversized_source=REFUSED|oversized_contraction=REFUSED|oversized_coefficient=REFUSED|electric_72_moves=PASS|real_mu3=NOT_COMPUTED|json=0");
    Ok(())
}
fn main() {
    let args:Vec<String>=std::env::args().collect();
    let result=match args.as_slice() {
        [_,a] if a=="--selftest"=>selftest(),
        [_,a,root] if a=="--run"=>run(Path::new(root),None),
        [_,a,root,limit] if a=="--bench"=>
            match limit.parse::<usize>() {
                Ok(n)=>run(Path::new(root),Some(n)),
                Err(e)=>Err(format!("B5_invalid_bench_count:{e}"))
            },
        _=>Err("usage: b5_moments --selftest | --run SOURCE_DIR | --bench SOURCE_DIR N".to_string())
    };
    if let Err(e)=result {
        eprintln!("Y137_B5_REFUSE|reason={e}|json=0");
        std::process::exit(1);
    }
}
