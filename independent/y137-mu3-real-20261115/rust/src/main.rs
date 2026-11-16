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

use std::io::{BufRead, Write};

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

// ---------------------------------------------------------------- exact wide integers
//
// The accumulators of the third moment. Bound, proved from the data format: a Q5 amplitude over b is below 2^82,
// so an amplitude is below 2^82 * 10^9 < 2^112; a product of two is below 2^224; times an orbit weight (at most 6)
// and a multiplicity (at most 72) and b = 10^9 or a diagonal D below 2^40: below 2^273; summed over at most
// 2^31 terms: below 2^304. A 320-bit two's-complement accumulator holds every partial sum with 15 bits to spare.
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

fn mode_rows(rule: &Rule) {
    let stdin = std::io::stdin();
    let mut out = std::io::BufWriter::new(std::io::stdout().lock());
    for line in stdin.lock().lines().map_while(Result::ok) {
        let Ok(c) = line.trim().parse::<u64>() else { continue };
        let key = decode(c);
        let canon = code(&rule.canonical(&rule.expand(&key)));
        let row = rule.row(&key);
        let own = row.iter().find(|d| d.0 == c).map_or(0, |d| d.1);
        let dest: Vec<String> = row.iter().map(|d| format!("{}:{}", d.0, d.1)).collect();
        let _ = writeln!(
            out,
            "ROW|code={c}|canonical={}|w={}|m={}|moves={}|self={own}|dest={}|json=0",
            u8::from(canon == c),
            rule.weight(&key),
            rule.magnetic(&key),
            row.iter().map(|d| d.1).sum::<u32>(),
            dest.join(",")
        );
    }
}

fn mode_bench(rule: &Rule, n: u64) {
    let mut seed = 20_261_115u64;
    let (mut moves, mut distinct, mut check) = (0u64, 0u64, 0u64);
    for _ in 0..n {
        let mut key = [0u8; KEPT];
        for k in &mut key {
            seed = seed.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407);
            *k = ((seed >> 33) % 6) as u8;
        }
        let canon = rule.canonical(&rule.expand(&key));
        let row = rule.row(&canon);
        moves += u64::from(row.iter().map(|d| d.1).sum::<u32>());
        distinct += row.len() as u64;
        check = check.wrapping_mul(1_000_003).wrapping_add(row[0].0);
    }
    println!("BENCH|rows={n}|moves={moves}|distinct_destinations={distinct}|check={check}|json=0");
}

fn mode_wide() {
    let stdin = std::io::stdin();
    let (mut acc, mut neg) = (Wide::ZERO, Wide::ZERO);
    let mut n = 0u64;
    for line in stdin.lock().lines().map_while(Result::ok) {
        let f: Vec<&str> = line.split_whitespace().collect();
        if f.len() != 3 {
            continue;
        }
        let (Ok(a), Ok(b), Ok(w)) = (f[0].parse::<u128>(), f[1].parse::<u128>(), f[2].parse::<u64>()) else { continue };
        let p = Wide::product(a, b, w);
        acc.add(&p);
        neg.sub(&p);
        n += 1;
    }
    println!("WIDE|terms={n}|sum={}|negated={}|json=0", acc.decimal(), neg.decimal());
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule = Rule::new();
    match (a.get(1).map(String::as_str), a.len()) {
        (Some("rows"), 2) => mode_rows(&rule),
        (Some("bench"), 3) => mode_bench(&rule, a[2].parse::<u64>().unwrap_or(0)),
        (Some("wide"), 2) => mode_wide(),
        _ => {
            println!("Y137_ROWS_REFUSE|reason=usage:_rows_|_bench_N_|_wide|json=0");
            std::process::exit(1);
        }
    }
}
