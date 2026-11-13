// floorcert (floor lane, DESIGN, 2026-11-09). Schur-Collatz-Wielandt floor certificate for lambda_min(QHQ) on the
// periodic 3x4 S3 lattice, H/J_E = 72 - T + r M on the gauge orbits. Core = nonflat orbits with M <= m0 (exact, in
// 48-symmetry classes, CW rows hold for every orbit of a class); tail = M > m0, bounded below in form order by the
// ground-state substitution H_TT >= diag((H_TT f)/f) with a layered positive f(M). Integers only; std only.
// Tables, letters(), canon() and info() are copied from the cloud seat's engine ym137/engine/rs/src/main.rs.
// FIX-1 (2026-11-09): prediction first by a whitelist: r in {21/2, 12, 14} or r >= 20 (nothing within 1 of r = 9);
// r = 9 runs only in the frozen binary (compiled-in freeze commit and prediction sha256, matched at run time). Every
// certificate carries the sha256 of its canonical rows; the independent verifier design/py/cert_gate.py must PASS the
// written file with the same row hash before any gamma is quoted (design/gate_required.sh). SHA-256 is std-only, below.
// V2 (2026-11-10, operational review of the freeze e74d8a46): `rowhash` creates its --dir when it is absent; the 22
// clippy 1.81 findings are rewritten with the same integer results (regression receipts in review-v1/ and the record).
use std::collections::{HashMap, HashSet};
use std::fmt::Write as FmtWrite;
use std::io::{Read, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

const V: usize = 12;
const NL: usize = 24;
const NK: usize = 13;
const NSYM: usize = 48;

fn pos(x: i64, y: i64) -> usize {
    (x.rem_euclid(3) * 4 + y.rem_euclid(4)) as usize
}

// ---------------------------------------------------------------- SHA-256 (FIPS 180-4), std only, written for FIX-1
// The constants are rederived in integers by sha_constants_gate (first 32 fractional bits of the square and cube roots
// of the first primes) and must equal this table; `floorcert selftest` also checks the FIPS 180-4 example messages.
const SHA_K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01,
    0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08,
    0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];
const SHA_H0: [u32; 8] = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
fn first_primes(n: usize) -> Vec<u128> {
    let mut p: Vec<u128> = Vec::new();
    let mut c: u128 = 2;
    while p.len() < n {
        if p.iter().all(|&q| c % q != 0) {
            p.push(c);
        }
        c += 1;
    }
    p
}
// largest x with x^k <= n
fn iroot(n: u128, k: u32) -> u128 {
    let (mut lo, mut hi) = (0u128, 1u128 << 40);
    while lo < hi {
        let mid = (lo + hi + 1) / 2;
        if mid.checked_pow(k).map_or(false, |x| x <= n) {
            lo = mid;
        } else {
            hi = mid - 1;
        }
    }
    lo
}
fn sha_constants_gate() {
    let p = first_primes(64);
    for i in 0..8 {
        assert_eq!((iroot(p[i] << 64, 2) & 0xffff_ffff) as u32, SHA_H0[i], "SHA-256 H0[{}]", i);
    }
    for i in 0..64 {
        assert_eq!((iroot(p[i] << 96, 3) & 0xffff_ffff) as u32, SHA_K[i], "SHA-256 K[{}]", i);
    }
}
struct Sha256 {
    h: [u32; 8],
    buf: [u8; 64],
    nbuf: usize,
    len: u64,
}
impl Sha256 {
    fn new() -> Sha256 {
        Sha256 { h: SHA_H0, buf: [0u8; 64], nbuf: 0, len: 0 }
    }
    fn compress(h: &mut [u32; 8], b: &[u8]) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([b[4 * i], b[4 * i + 1], b[4 * i + 2], b[4 * i + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let mut s = *h;
        for i in 0..64 {
            let (a, b1, c, d, e, f, g, hh) = (s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]);
            let big1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ (!e & g);
            let t1 = hh.wrapping_add(big1).wrapping_add(ch).wrapping_add(SHA_K[i]).wrapping_add(w[i]);
            let big0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b1) ^ (a & c) ^ (b1 & c);
            let t2 = big0.wrapping_add(maj);
            s = [t1.wrapping_add(t2), a, b1, c, d.wrapping_add(t1), e, f, g];
        }
        for i in 0..8 {
            h[i] = h[i].wrapping_add(s[i]);
        }
    }
    fn update(&mut self, data: &[u8]) {
        self.len = self.len.checked_add(data.len() as u64).expect("sha256 length");
        let mut d = data;
        if self.nbuf > 0 {
            let take = (64 - self.nbuf).min(d.len());
            self.buf[self.nbuf..self.nbuf + take].copy_from_slice(&d[..take]);
            self.nbuf += take;
            d = &d[take..];
            if self.nbuf == 64 {
                let b = self.buf;
                Sha256::compress(&mut self.h, &b);
                self.nbuf = 0;
            }
        }
        while d.len() >= 64 {
            Sha256::compress(&mut self.h, &d[..64]);
            d = &d[64..];
        }
        if !d.is_empty() {
            self.buf[..d.len()].copy_from_slice(d);
            self.nbuf = d.len();
        }
    }
    fn finish(mut self) -> [u8; 32] {
        let bits = self.len.checked_mul(8).expect("sha256 length");
        let rem = (self.nbuf + 1) % 64;
        let zeros = if rem <= 56 { 56 - rem } else { 120 - rem };
        let mut pad = vec![0x80u8];
        pad.resize(1 + zeros, 0);
        pad.extend_from_slice(&bits.to_be_bytes());
        self.update(&pad);
        assert_eq!(self.nbuf, 0);
        let mut out = [0u8; 32];
        for i in 0..8 {
            out[4 * i..4 * i + 4].copy_from_slice(&self.h[i].to_be_bytes());
        }
        out
    }
}
fn hex(b: &[u8]) -> String {
    let mut s = String::with_capacity(2 * b.len());
    for x in b.iter() {
        write!(s, "{:02x}", x).unwrap();
    }
    s
}
fn sha256_hex(data: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(data);
    hex(&h.finish())
}
struct Tab {
    mul: [[u8; 6]; 6],
    inv: [u8; 6],
    trans: [u8; 3],
    chr: [i64; 6],
    conj: [[u8; 6]; 6],
    tree: Vec<(usize, usize, usize)>,
    kept: [usize; NK],
    kst: [(usize, usize); NK],
    src: Vec<[(u8, bool); NL]>,
    plq: [[(usize, bool); 4]; V],
    linkp: [[usize; 2]; NL],
}
fn tables() -> Tab {
    let perms: [[usize; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
    let idx = |p: [usize; 3]| perms.iter().position(|q| *q == p).unwrap() as u8;
    let mut mul = [[0u8; 6]; 6];
    for a in 0..6 {
        for b in 0..6 {
            mul[a][b] = idx([perms[a][perms[b][0]], perms[a][perms[b][1]], perms[a][perms[b][2]]]);
        }
    }
    let mut inv = [0u8; 6];
    for a in 0..6 {
        let bs: Vec<usize> = (0..6).filter(|&b| mul[a][b] == 0).collect();
        assert_eq!(bs.len(), 1);
        inv[a] = bs[0] as u8;
    }
    let tr: Vec<u8> = (1..6).filter(|&i| mul[i][i] == 0).map(|i| i as u8).collect();
    assert_eq!(tr, vec![1, 2, 5]);
    let mut chr = [0i64; 6];
    for a in 0..6 {
        chr[a] = (0..3).filter(|&j| perms[a][j] == j).count() as i64 - 1;
    }
    assert_eq!(chr, [2, 0, 0, -1, -1, 0]);
    let mut conj = [[0u8; 6]; 6];
    for g in 0..6 {
        for a in 0..6 {
            conj[g][a] = mul[mul[g][a] as usize][inv[g] as usize];
        }
    }
    let mut tree = Vec::new();
    for y in 0..3 {
        tree.push((pos(0, y), pos(0, y + 1), V + pos(0, y)));
    }
    for y in 0..4 {
        for x in 0..2 {
            tree.push((pos(x, y), pos(x + 1, y), pos(x, y)));
        }
    }
    let ids: Vec<usize> = tree.iter().map(|t| t.2).collect();
    let kv: Vec<usize> = (0..NL).filter(|k| !ids.contains(k)).collect();
    assert_eq!(kv.len(), NK);
    let mut kept = [0usize; NK];
    let mut kst = [(0usize, 0usize); NK];
    for j in 0..NK {
        let k = kv[j];
        kept[j] = k;
        if k < V {
            let (x, y) = ((k / 4) as i64, (k % 4) as i64);
            kst[j] = (k, pos(x + 1, y));
        } else {
            let s = k - V;
            let (x, y) = ((s / 4) as i64, (s % 4) as i64);
            kst[j] = (s, pos(x, y + 1));
        }
    }
    let mut src = Vec::new();
    for sx in [1i64, -1] {
        for sy in [1i64, -1] {
            for dx in 0..3i64 {
                for dy in 0..4i64 {
                    let mut dst = [(0usize, false); NL];
                    for x in 0..3i64 {
                        for y in 0..4i64 {
                            let (xx, yy) = (sx * x + dx, sy * y + dy);
                            dst[pos(x, y)] = if sx == 1 { (pos(xx, yy), false) } else { (pos(xx - 1, yy), true) };
                            dst[V + pos(x, y)] = if sy == 1 { (V + pos(xx, yy), false) } else { (V + pos(xx, yy - 1), true) };
                        }
                    }
                    let mut s = [(255u8, false); NL];
                    for (k, &(d, iv)) in dst.iter().enumerate() {
                        assert_eq!(s[d].0, 255);
                        s[d] = (k as u8, iv);
                    }
                    src.push(s);
                }
            }
        }
    }
    assert_eq!(src.len(), NSYM);
    // plaquette (x,y): h(x,y) v(x+1,y) h(x,y+1)^-1 v(x,y)^-1, as in the engine's magnetic()
    let mut plq = [[(0usize, false); 4]; V];
    let mut lp: Vec<Vec<usize>> = vec![Vec::new(); NL];
    for x in 0..3i64 {
        for y in 0..4i64 {
            let p = pos(x, y);
            plq[p] = [(pos(x, y), false), (V + pos(x + 1, y), false), (pos(x, y + 1), true), (V + pos(x, y), true)];
            for &(k, _) in plq[p].iter() {
                lp[k].push(p);
            }
        }
    }
    let mut linkp = [[0usize; 2]; NL];
    for k in 0..NL {
        assert_eq!(lp[k].len(), 2, "each link borders two plaquettes");
        assert_ne!(lp[k][0], lp[k][1], "the two plaquettes of a link are distinct");
        linkp[k] = [lp[k][0], lp[k][1]];
    }
    Tab { mul, inv, trans: [tr[0], tr[1], tr[2]], chr, conj, tree, kept, kst, src, plq, linkp }
}

impl Tab {
    fn encode(z: &[u8; NK]) -> u64 {
        let mut k = 0u64;
        for &zj in z.iter() {
            k = k * 6 + zj as u64;
        }
        k
    }
    fn decode(key: u64) -> [u8; NK] {
        let mut z = [0u8; NK];
        let mut k = key;
        for j in (0..NK).rev() {
            z[j] = (k % 6) as u8;
            k /= 6;
        }
        assert_eq!(k, 0);
        z
    }
    fn links_of_key(&self, key: u64) -> [u8; NL] {
        let z = Tab::decode(key);
        let mut u = [0u8; NL];
        for j in 0..NK {
            u[self.kept[j]] = z[j];
        }
        u
    }
    #[inline(always)]
    fn val(&self, s: usize, u: &[u8; NL], d: usize) -> u8 {
        let (k, iv) = self.src[s][d];
        let x = u[k as usize];
        if iv {
            self.inv[x as usize]
        } else {
            x
        }
    }
    #[inline(always)]
    fn letters(&self, s: usize, u: &[u8; NL], z: &mut [u8; NK]) {
        let mut h = [0u8; V];
        for &(a, b, k) in self.tree.iter() {
            h[b] = self.mul[h[a] as usize][self.val(s, u, k) as usize];
        }
        for (j, zj) in z.iter_mut().enumerate() {
            let (s0, t0) = self.kst[j];
            let x = self.val(s, u, self.kept[j]);
            *zj = self.mul[self.mul[h[s0] as usize][x as usize] as usize][self.inv[h[t0] as usize] as usize];
        }
    }
    fn orbit_min(&self, z: &[u8; NK]) -> u64 {
        let mut best = u64::MAX;
        for g in 0..6 {
            let mut c = [0u8; NK];
            for j in 0..NK {
                c[j] = self.conj[g][z[j] as usize];
            }
            best = best.min(Tab::encode(&c));
        }
        best
    }
    // class key = lexicographic minimum over 48 symmetries x 6 conjugations of the tree-gauge letters
    fn canon(&self, u: &[u8; NL]) -> u64 {
        let mut best = [255u8; NK];
        let mut z = [0u8; NK];
        for s in 0..NSYM {
            self.letters(s, u, &mut z);
            for g in 0..6 {
                let cg = &self.conj[g];
                for j in 0..NK {
                    let c = cg[z[j] as usize];
                    if c != best[j] {
                        if c < best[j] {
                            best[j] = c;
                            for jj in j + 1..NK {
                                best[jj] = cg[z[jj] as usize];
                            }
                        }
                        break;
                    }
                }
            }
        }
        Tab::encode(&best)
    }
    // true iff the tree-gauge letters z0 of u are the class minimum (early exit)
    fn is_min(&self, u: &[u8; NL], z0: &[u8; NK]) -> bool {
        let mut z = [0u8; NK];
        for s in 0..NSYM {
            self.letters(s, u, &mut z);
            for g in 0..6 {
                let cg = &self.conj[g];
                for j in 0..NK {
                    let c = cg[z[j] as usize];
                    if c != z0[j] {
                        if c < z0[j] {
                            return false;
                        }
                        break;
                    }
                }
            }
        }
        true
    }
    fn apply(&self, s: usize, u: &[u8; NL]) -> [u8; NL] {
        let mut o = [0u8; NL];
        for (d, od) in o.iter_mut().enumerate() {
            *od = self.val(s, u, d);
        }
        o
    }
    #[inline(always)]
    fn hol(&self, u: &[u8; NL], p: usize) -> u8 {
        let mut g = 0u8;
        for &(k, iv) in self.plq[p].iter() {
            let x = if iv { self.inv[u[k] as usize] } else { u[k] };
            g = self.mul[g as usize][x as usize];
        }
        g
    }
    #[inline(always)]
    fn pcost(&self, u: &[u8; NL], p: usize) -> i64 {
        2 - self.chr[self.hol(u, p) as usize]
    }
    // independent full recomputation, as in the engine's magnetic()
    fn magnetic(&self, u: &[u8; NL]) -> i64 {
        let mut s = 0;
        for x in 0..3i64 {
            for y in 0..4i64 {
                let (i, r, up) = (pos(x, y), pos(x + 1, y), pos(x, y + 1));
                let m = &self.mul;
                let p = m[m[m[u[i] as usize][u[V + r] as usize] as usize][self.inv[u[up] as usize] as usize] as usize]
                    [self.inv[u[V + i] as usize] as usize];
                s += 2 - self.chr[p as usize];
            }
        }
        s
    }
    // (wconj, norb, wt, mag) with the engine's orbit-stabilizer and symmetry asserts
    fn info(&self, key: u64) -> (u8, u8, u32, u8) {
        let u = self.links_of_key(key);
        let z0 = Tab::decode(key);
        assert_eq!(self.orbit_min(&z0), key, "key not conjugation-minimal");
        let mut cj: Vec<u64> = (0..6)
            .map(|g| {
                let mut c = [0u8; NK];
                for j in 0..NK {
                    c[j] = self.conj[g][z0[j] as usize];
                }
                Tab::encode(&c)
            })
            .collect();
        cj.sort_unstable();
        cj.dedup();
        let mag = self.magnetic(&u);
        let mut orbs: Vec<u64> = Vec::with_capacity(NSYM);
        let mut stab = 0usize;
        let mut z = [0u8; NK];
        for s in 0..NSYM {
            self.letters(s, &u, &mut z);
            let ok = self.orbit_min(&z);
            if ok == key {
                stab += 1;
            }
            orbs.push(ok);
            let us = self.apply(s, &u);
            assert_eq!(self.magnetic(&us), mag, "magnetic not symmetric");
        }
        orbs.sort_unstable();
        orbs.dedup();
        assert_eq!(orbs[0], key, "class key not minimal");
        assert_eq!(orbs.len() * stab, NSYM, "orbit-stabilizer");
        (cj.len() as u8, orbs.len() as u8, (cj.len() * orbs.len()) as u32, mag as u8)
    }
}

// per-link move table (Lemma 0): class pair -> multiset of Delta M over the three transpositions
// types: 0 ee, 1 et, 2 ec, 3 tt aligned, 4 tt non-aligned, 5 tc, 6 cc
const DELTAS: [[i64; 3]; 7] = [[4, 4, 4], [0, 3, 3], [1, 1, 1], [-4, 2, 2], [-1, -1, 2], [-3, 0, 0], [-2, -2, -2]];
fn cls(tab: &Tab, g: u8) -> u8 {
    match 2 - tab.chr[g as usize] {
        0 => 0,
        2 => 1,
        3 => 2,
        _ => panic!(),
    }
}
fn s3_table_gate(tab: &Tab) {
    // every pair of based holonomies (X, Y) and the three transpositions tau: (class tau X, class tau Y)
    for x in 0..6u8 {
        for y in 0..6u8 {
            let (cx, cy) = (cls(tab, x), cls(tab, y));
            let mut d: Vec<i64> = tab
                .trans
                .iter()
                .map(|&t| {
                    let (a, b) = (tab.mul[t as usize][x as usize], tab.mul[t as usize][y as usize]);
                    (2 - tab.chr[a as usize]) + (2 - tab.chr[b as usize]) - (2 - tab.chr[x as usize]) - (2 - tab.chr[y as usize])
                })
                .collect();
            d.sort();
            let (lo, hi) = if cx <= cy { (cx, cy) } else { (cy, cx) };
            let ty = match (lo, hi) {
                (0, 0) => 0,
                (0, 1) => 1,
                (0, 2) => 2,
                (1, 1) => {
                    if x == y {
                        3
                    } else {
                        4
                    }
                }
                (1, 2) => 5,
                (2, 2) => 6,
                _ => panic!(),
            };
            let mut e = DELTAS[ty].to_vec();
            e.sort();
            assert_eq!(d, e, "S3 per-link table x={} y={}", x, y);
        }
    }
    println!("GATE|s3_link_table|PASS|36 holonomy pairs x 3 transpositions match the 7-type table");
}

// ---------------------------------------------------------------- census (closed form, as in map/scripts/mhist.py)
fn pmul(a: &[i128], b: &[i128]) -> Vec<i128> {
    let mut c = vec![0i128; a.len() + b.len() - 1];
    for (i, &x) in a.iter().enumerate() {
        for (j, &y) in b.iter().enumerate() {
            c[i + j] += x * y;
        }
    }
    c
}
fn ppow(a: &[i128], n: usize) -> Vec<i128> {
    let mut r = vec![1i128];
    for _ in 0..n {
        r = pmul(&r, a);
    }
    r
}
fn closed_form() -> (Vec<i128>, Vec<i128>) {
    let a = ppow(&[1, 0, 3, 2], 12);
    let b = ppow(&[1, 0, -3, 2], 12);
    let c = ppow(&[1, 0, 0, -1], 12);
    let d = ppow(&[1, 0, 1], 12);
    let e = ppow(&[1, 0, -1], 12);
    let f = ppow(&[1, 0, 0, 2], 12);
    let mut orb = vec![0i128; 37];
    let mut wgt = vec![0i128; 37];
    for m in 0..37 {
        let g = |p: &Vec<i128>| if m < p.len() { p[m] } else { 0 };
        orb[m] = g(&a) + g(&b) + 3 * g(&c) + g(&d) + g(&e) + g(&f);
        wgt[m] = 6 * (g(&a) + g(&b) + g(&c));
    }
    assert_eq!(orb.iter().sum::<i128>(), 2177317873);
    assert_eq!(wgt.iter().sum::<i128>(), 13060694016);
    (orb, wgt)
}

// ---------------------------------------------------------------- enumeration of the core {1 <= M <= m0}
fn enumerate(tab: &Tab, m0: i64, threads: usize) -> Vec<u64> {
    let order: [usize; NK] = [16, 17, 18, 19, 15, 20, 21, 22, 23, 8, 9, 10, 11];
    let mut sorted = order.to_vec();
    sorted.sort();
    assert_eq!(sorted, tab.kept.to_vec(), "DFS order covers the kept links");
    let mut assigned = [true; NL];
    for &k in order.iter() {
        assigned[k] = false;
    }
    let mut done_at: Vec<Vec<usize>> = vec![Vec::new(); NK];
    let mut pdone = [false; V];
    for (lev, &k) in order.iter().enumerate() {
        assigned[k] = true;
        for (p, pd) in pdone.iter_mut().enumerate() {
            if !*pd && tab.plq[p].iter().all(|&(l, _)| assigned[l]) {
                *pd = true;
                done_at[lev].push(p);
            }
        }
    }
    assert!(pdone.iter().all(|&b| b));
    struct Dfs<'a> {
        tab: &'a Tab,
        order: &'a [usize; NK],
        done_at: &'a [Vec<usize>],
        m0: i64,
    }
    fn dfs(cx: &Dfs, lev: usize, u: &mut [u8; NL], msum: i64, out: &mut Vec<u64>) {
        let (tab, order, done_at, m0) = (cx.tab, cx.order, cx.done_at, cx.m0);
        if lev == NK {
            if msum >= 1 {
                let mut z = [0u8; NK];
                for j in 0..NK {
                    z[j] = u[tab.kept[j]];
                }
                if tab.is_min(u, &z) {
                    out.push(Tab::encode(&z));
                }
            }
            return;
        }
        let k = order[lev];
        for a in 0..6u8 {
            u[k] = a;
            let mut m = msum;
            for &p in done_at[lev].iter() {
                m += tab.pcost(u, p);
            }
            if m <= m0 {
                dfs(cx, lev + 1, u, m, out);
            }
        }
        u[k] = 0;
    }
    let next = AtomicUsize::new(0);
    let mut all: Vec<u64> = Vec::new();
    std::thread::scope(|sc| {
        let hs: Vec<_> = (0..threads)
            .map(|_| {
                let (next, order, done_at) = (&next, &order, &done_at);
                sc.spawn(move || {
                    let mut out = Vec::new();
                    loop {
                        let c = next.fetch_add(1, Ordering::Relaxed);
                        if c >= 216 {
                            break;
                        }
                        let mut u = [0u8; NL];
                        let (a0, a1, a2) = ((c / 36) as u8, ((c / 6) % 6) as u8, (c % 6) as u8);
                        u[order[0]] = a0;
                        u[order[1]] = a1;
                        u[order[2]] = a2;
                        let mut m = 0;
                        for at in done_at.iter().take(3) {
                            for &p in at.iter() {
                                m += tab.pcost(&u, p);
                            }
                        }
                        if m <= m0 {
                            dfs(&Dfs { tab, order, done_at, m0 }, 3, &mut u, m, &mut out);
                        }
                    }
                    out
                })
            })
            .collect();
        for h in hs {
            all.extend(h.join().unwrap());
        }
    });
    all.sort_unstable();
    let n0 = all.len();
    all.dedup();
    assert_eq!(n0, all.len(), "each class minimum is enumerated once");
    all
}

fn par_map<T: Send, F: Fn(usize) -> T + Sync>(n: usize, threads: usize, f: F) -> Vec<T> {
    if n == 0 {
        return Vec::new();
    }
    let nchunks = (threads * 64).min(n);
    let chunk = (n + nchunks - 1) / nchunks;
    let next = AtomicUsize::new(0);
    let mut parts: Vec<(usize, Vec<T>)> = Vec::new();
    let (f, next) = (&f, &next);
    std::thread::scope(|sc| {
        let hs: Vec<_> = (0..threads)
            .map(|_| {
                sc.spawn(move || {
                    let mut out = Vec::new();
                    loop {
                        let c = next.fetch_add(1, Ordering::Relaxed);
                        let a = c * chunk;
                        if a >= n {
                            break;
                        }
                        let b = (a + chunk).min(n);
                        out.push((c, (a..b).map(f).collect::<Vec<T>>()));
                    }
                    out
                })
            })
            .collect();
        for h in hs {
            parts.extend(h.join().unwrap());
        }
    });
    parts.sort_by_key(|p| p.0);
    parts.into_iter().flat_map(|p| p.1).collect()
}

fn mem() -> String {
    let s = std::fs::read_to_string("/proc/self/status").unwrap_or_default();
    for l in s.lines() {
        if let Some(rest) = l.strip_prefix("VmHWM:") {
            return rest.trim().replace(' ', "");
        }
    }
    String::new()
}

// ---------------------------------------------------------------- rows
// field order = canonical order of the tail moves of a row (M_k, histogram, sorted back classes)
#[derive(Clone, PartialEq, Eq, PartialOrd, Ord, Debug)]
struct Tail {
    m: u8,
    hist: [u8; 9], // moves from the tail orbit that stay in the tail, by Delta M + 4
    back: Vec<u32>, // core classes reached by the moves that leave the tail (with multiplicity, sorted)
}
#[derive(Clone)]
struct Row {
    key: u64,
    mag: u8,
    wt: u32,
    norb: u8,
    core: Vec<(u32, i32)>, // (core class, count) of the moves that stay in the core
    nflat: u8,
    tails: Vec<Tail>,
}

struct Gates {
    local_vs_full: usize,
    link_multisets: usize,
    images: usize,
}

// all 72 moves of u with local Delta M; returns (link, tau, Delta)
#[inline(always)]
fn local_moves(tab: &Tab, u: &mut [u8; NL], pc: &[i64; V], out: &mut Vec<(usize, u8, i64)>) {
    out.clear();
    for k in 0..NL {
        let old = u[k];
        let [p1, p2] = tab.linkp[k];
        for &t in tab.trans.iter() {
            u[k] = tab.mul[t as usize][old as usize];
            let d = tab.pcost(u, p1) + tab.pcost(u, p2) - pc[p1] - pc[p2];
            out.push((k, t, d));
        }
        u[k] = old;
    }
}
fn plaquette_costs(tab: &Tab, u: &[u8; NL]) -> ([i64; V], i64) {
    let mut pc = [0i64; V];
    let mut m = 0;
    for (p, c) in pc.iter_mut().enumerate() {
        *c = tab.pcost(u, p);
        m += *c;
    }
    (pc, m)
}
// gate: the 3-move Delta multiset of every link equals the table entry of its class pair
fn link_gate(tab: &Tab, u: &[u8; NL], pc: &[i64; V], mv: &[(usize, u8, i64)]) {
    for k in 0..NL {
        let mut d: Vec<i64> = mv[3 * k..3 * k + 3].iter().map(|x| x.2).collect();
        d.sort();
        let [p1, p2] = tab.linkp[k];
        let c = |x: i64| match x {
            0 => 0u8,
            2 => 1,
            3 => 2,
            _ => panic!(),
        };
        let (a, b) = (c(pc[p1]), c(pc[p2]));
        let (lo, hi) = if a <= b { (a, b) } else { (b, a) };
        let cands: Vec<usize> = match (lo, hi) {
            (0, 0) => vec![0],
            (0, 1) => vec![1],
            (0, 2) => vec![2],
            (1, 1) => vec![3, 4],
            (1, 2) => vec![5],
            (2, 2) => vec![6],
            _ => panic!(),
        };
        let ok = cands.iter().any(|&ty| {
            let mut e = DELTAS[ty].to_vec();
            e.sort();
            e == d
        });
        assert!(ok, "link multiset gate: link {} classes ({},{}) deltas {:?} u={:?}", k, a, b, d, u);
    }
}

// The row data of one configuration u0: (M, core targets (class, count) aggregated, flat moves, tail moves in canonical
// order). The data is a class invariant, which the image gate in build_rows checks.
fn row_at(tab: &Tab, u0: &[u8; NL], index: &HashMap<u64, u32>, m0: i64, gates: bool, lv: &AtomicUsize, lm: &AtomicUsize) -> (i64, Vec<(u32, i32)>, u8, Vec<Tail>) {
    let mut u = *u0;
    let (pc, m) = plaquette_costs(tab, &u);
    let mut mv = Vec::with_capacity(72);
    local_moves(tab, &mut u, &pc, &mut mv);
    if gates {
        link_gate(tab, &u, &pc, &mv);
        lm.fetch_add(1, Ordering::Relaxed);
    }
    let mut core: Vec<(u32, i32)> = Vec::new();
    let mut nflat = 0u8;
    let mut tails: Vec<Tail> = Vec::new();
    let mut mv2 = Vec::with_capacity(72);
    for &(k, t, d) in mv.iter() {
        let old = u[k];
        u[k] = tab.mul[t as usize][old as usize];
        let m1 = m + d;
        if gates {
            assert_eq!(tab.magnetic(&u), m1, "local Delta M vs full recomputation");
            lv.fetch_add(1, Ordering::Relaxed);
        }
        if m1 == 0 {
            nflat += 1;
        } else if m1 <= m0 {
            let kk = tab.canon(&u);
            let j = *index.get(&kk).expect("core completeness: a core target is missing from the enumeration");
            core.push((j, 1));
        } else {
            let (pc1, mm1) = plaquette_costs(tab, &u);
            assert_eq!(mm1, m1);
            local_moves(tab, &mut u, &pc1, &mut mv2);
            if gates {
                link_gate(tab, &u, &pc1, &mv2);
                lm.fetch_add(1, Ordering::Relaxed);
            }
            let mut hist = [0u8; 9];
            let mut back = Vec::new();
            for &(k2, t2, d2) in mv2.iter() {
                let m2 = m1 + d2;
                if gates {
                    let o2 = u[k2];
                    u[k2] = tab.mul[t2 as usize][o2 as usize];
                    assert_eq!(tab.magnetic(&u), m2, "local Delta M vs full recomputation (tail)");
                    u[k2] = o2;
                    lv.fetch_add(1, Ordering::Relaxed);
                }
                if m2 > m0 {
                    hist[(d2 + 4) as usize] += 1;
                } else {
                    assert!(m2 >= 1, "a tail orbit one move from a flat (needs m0 >= 4)");
                    let o2 = u[k2];
                    u[k2] = tab.mul[t2 as usize][o2 as usize];
                    let kk = tab.canon(&u);
                    u[k2] = o2;
                    let j = *index.get(&kk).expect("core completeness (two-step target)");
                    back.push(j);
                }
            }
            back.sort_unstable();
            tails.push(Tail { m: m1 as u8, hist, back });
        }
        u[k] = old;
    }
    core.sort_unstable();
    let mut agg: Vec<(u32, i32)> = Vec::new();
    for (j, c) in core {
        match agg.last_mut() {
            Some(l) if l.0 == j => l.1 += c,
            _ => agg.push((j, c)),
        }
    }
    tails.sort();
    (m, agg, nflat, tails)
}
// U_e -> g_s U_e g_t^-1 for the link e from s to t
fn gauge(tab: &Tab, u: &[u8; NL], g: &[u8; V]) -> [u8; NL] {
    let mut o = [0u8; NL];
    for k in 0..NL {
        let (s, t) = if k < V {
            let (x, y) = ((k / 4) as i64, (k % 4) as i64);
            (k, pos(x + 1, y))
        } else {
            let q = k - V;
            let (x, y) = ((q / 4) as i64, (q % 4) as i64);
            (q, pos(x, y + 1))
        };
        o[k] = tab.mul[tab.mul[g[s] as usize][u[k] as usize] as usize][tab.inv[g[t] as usize] as usize];
    }
    o
}
// image i of the representative: a non-identity lattice map chosen from the key; image 1 also gets a vertex gauge
// transformation from a key-seeded generator (map 0 of tables() is the identity)
fn image_of(tab: &Tab, key: u64, i: usize, u: &[u8; NL]) -> [u8; NL] {
    let s = 1 + ((key + 17 * i as u64) % 47) as usize;
    let mut o = tab.apply(s, u);
    if i % 2 == 1 {
        let mut st = key.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        let mut g = [0u8; V];
        for x in g.iter_mut() {
            st = st.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            *x = ((st >> 33) % 6) as u8;
        }
        o = gauge(tab, &o, &g);
    }
    o
}

fn build_rows(tab: &Tab, keys: &[u64], index: &HashMap<u64, u32>, m0: i64, threads: usize, gates: bool, images: usize) -> (Vec<Row>, Gates) {
    let lv = AtomicUsize::new(0);
    let lm = AtomicUsize::new(0);
    let ni = AtomicUsize::new(0);
    let rows = par_map(keys.len(), threads, |i| {
        let key = keys[i];
        let (_, norb, wt, mag) = tab.info(key);
        let u = tab.links_of_key(key);
        let (m, core, nflat, tails) = row_at(tab, &u, index, m0, gates, &lv, &lm);
        assert_eq!(m, mag as i64);
        // FIX-1 item 6: the row rebuilt at symmetry images of the representative has identical core and tail multisets
        for im in 0..images {
            let ui = image_of(tab, key, im, &u);
            let (mi, ci, fi, ti) = row_at(tab, &ui, index, m0, false, &lv, &lm);
            assert!(mi == m && ci == core && fi == nflat && ti == tails, "symmetry image gate: class key {} image {} has a different row", key, im);
            ni.fetch_add(1, Ordering::Relaxed);
        }
        Row { key, mag, wt, norb, core, nflat, tails }
    });
    (rows, Gates { local_vs_full: lv.load(Ordering::Relaxed), link_multisets: lm.load(Ordering::Relaxed), images: ni.load(Ordering::Relaxed) })
}

// ---------------------------------------------------------------- analytic tail floor (Lemma 2): plaquette colourings
// signature = (M, counts of link types ee, et, ec, tt, tc, cc) over all 3^12 colourings of the 12 plaquettes
fn colour_signatures(tab: &Tab, even_t_only: bool) -> Vec<(i64, [i64; 6])> {
    let mut set: HashSet<(i64, [i64; 6])> = HashSet::new();
    let cost = [0i64, 2, 3];
    for code in 0..531441usize {
        let mut col = [0usize; V];
        let mut c = code;
        for cp in col.iter_mut() {
            *cp = c % 3;
            c /= 3;
        }
        let nt = col.iter().filter(|&&x| x == 1).count();
        if even_t_only && nt % 2 == 1 {
            continue;
        }
        let m: i64 = col.iter().map(|&x| cost[x]).sum();
        let mut n = [0i64; 6];
        for k in 0..NL {
            let [p1, p2] = tab.linkp[k];
            let (a, b) = (col[p1].min(col[p2]), col[p1].max(col[p2]));
            let ty = match (a, b) {
                (0, 0) => 0,
                (0, 1) => 1,
                (0, 2) => 2,
                (1, 1) => 3,
                (1, 2) => 4,
                (2, 2) => 5,
                _ => panic!(),
            };
            n[ty] += 1;
        }
        set.insert((m, n));
    }
    let mut v: Vec<(i64, [i64; 6])> = set.into_iter().collect();
    v.sort();
    v
}
// G(M) = max over colourings of sum over links of sum over tail-staying moves of f(M + Delta) (integer)
fn tail_g(sigs: &[(i64, [i64; 6])], f: &[i128], m0: i64) -> Vec<i128> {
    let gm = |m: i64, ty: usize| -> i128 {
        DELTAS[ty].iter().filter(|&&d| m + d > m0).map(|&d| f[(m + d) as usize]).sum()
    };
    let mut g = vec![-1i128; 37];
    for &(m, n) in sigs.iter() {
        if m <= m0 {
            continue;
        }
        let tt = gm(m, 3).max(gm(m, 4));
        let s = n[0] as i128 * gm(m, 0)
            + n[1] as i128 * gm(m, 1)
            + n[2] as i128 * gm(m, 2)
            + n[3] as i128 * tt
            + n[4] as i128 * gm(m, 5)
            + n[5] as i128 * gm(m, 6);
        if s > g[m as usize] {
            g[m as usize] = s;
        }
    }
    g
}

// ---------------------------------------------------------------- rationals and f
#[derive(Clone, Copy)]
struct Rat {
    n: i128,
    d: i128,
}
fn parse_rat(s: &str) -> Rat {
    let (n, d) = match s.split_once('/') {
        Some((a, b)) => (a.parse::<i128>().unwrap(), b.parse::<i128>().unwrap()),
        None => (s.parse::<i128>().unwrap(), 1),
    };
    assert!(d > 0);
    Rat { n, d }
}
fn dec(n: i128, d: i128, digits: u32) -> String {
    let neg = (n < 0) != (d < 0);
    let (n, d) = (n.abs(), d.abs());
    let p = 10i128.pow(digits);
    let q = n * p / d;
    format!("{}{}.{:0w$}", if neg { "-" } else { "" }, q / p, q % p, w = digits as usize)
}
// f(m0 + a) = vals[a - 1] for a <= len, constant beyond; f(M) for M <= m0 unused (set to 0)
fn make_f(spec: &str, m0: i64) -> Vec<i128> {
    let vals: Vec<i128> = spec.split(',').map(|s| s.trim().parse::<i128>().unwrap()).collect();
    let mut f = vec![0i128; 41];
    for m in (m0 + 1)..41 {
        let a = (m - m0) as usize;
        f[m as usize] = vals[(a - 1).min(vals.len() - 1)];
    }
    f
}
fn geom_spec(qn: i128, qd: i128, cap: usize) -> String {
    // f(m0+a) = qn^(a'-1) qd^(cap-a'), a' = min(a, cap)
    let mut v = Vec::new();
    for a in 1..=cap {
        v.push(qn.pow((a - 1) as u32) * qd.pow((cap - a) as u32));
    }
    v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")
}

// N_k = (rd td f_k)(delta_k - t) in integers: delta_k = 72 + r M_k - sum f(M_k + Delta)/f_k
#[inline(always)]
fn nk(t: &Tail, f: &[i128], r: Rat, tn: i128, td: i128) -> i128 {
    let m = t.m as usize;
    let fk = f[m];
    let mut sf = 0i128;
    for d in 0..9 {
        if t.hist[d] > 0 {
            sf += t.hist[d] as i128 * f[m + d - 4];
        }
    }
    td * r.d * (72 * fk - sf) + td * r.n * (m as i128) * fk - r.d * tn * fk
}
fn sumf(t: &Tail, f: &[i128]) -> i128 {
    let m = t.m as usize;
    let mut sf = 0i128;
    for d in 0..9 {
        sf += t.hist[d] as i128 * f[m + d - 4];
    }
    sf
}

// ---------------------------------------------------------------- exact integer row check
#[derive(Default, Clone, Copy)]
struct Opts {
    gates: bool, // Z-sign, completeness, positivity and tail-layer gates
    flip: bool,  // planted: Schur term enters with the wrong sign
    m0: i64,
    cap_n: i128, // min over tail layers of the analytic floor delta_min(M), as cap_n/cap_d
    cap_d: i128,
}
fn exact_check(rows: &[Row], v: &[i64], f: &[i128], r: Rat, tn: i128, td: i128, o: Opts) -> Result<(usize, i128), String> {
    let m0 = o.m0;
    // returns (number of rows, min over rows of lhs - rhs scaled) or the first refusal
    if o.gates {
        for (i, &x) in v.iter().enumerate() {
            if x < 1 {
                return Err(format!("REFUSE|gate=positivity_v|row={}|v={}", i, x));
            }
        }
        for m in (m0 + 1)..37 {
            if f[m as usize] < 1 {
                return Err(format!("REFUSE|gate=positivity_f|M={}|f={}", m, f[m as usize]));
            }
        }
        // integrity of the row data: Z-sign and completeness of every row and every tail target
        for (a, row) in rows.iter().enumerate() {
            for &(_, c) in row.core.iter() {
                if c < 1 {
                    return Err(format!("REFUSE|gate=zsign_core_count|row={}|count={}", a, c));
                }
            }
            let nc: i64 = row.core.iter().map(|x| x.1 as i64).sum();
            let tot = nc + row.nflat as i64 + row.tails.len() as i64;
            if tot != 72 {
                return Err(format!("REFUSE|gate=completeness_row|row={}|moves={}", a, tot));
            }
            for t in row.tails.iter() {
                let ns: i64 = t.hist.iter().map(|&x| x as i64).sum::<i64>() + t.back.len() as i64;
                if ns != 72 {
                    return Err(format!("REFUSE|gate=completeness_tail|row={}|moves={}", a, ns));
                }
            }
            // FIX-1: class detailed balance W'_A c(A->B) = W'_B c(B->A) on every core edge (a misrouted one-step move)
            for &(b, c) in row.core.iter() {
                let back = rows[b as usize].core.iter().find(|x| x.0 == a as u32).map(|x| x.1).unwrap_or(0);
                if row.wt as i64 * c as i64 != rows[b as usize].wt as i64 * back as i64 {
                    return Err(format!("REFUSE|gate=class_detailed_balance|row={}|target_row={}|counts={}/{}", a, b, c, back));
                }
            }
        }
        // the claimed t must lie below the analytic floor of every tail layer (Lemma 2)
        if tn * o.cap_d >= o.cap_n * td {
            return Err(format!("REFUSE|gate=tail_layer_floor|t={}|cap={}", dec(tn, td, 4), dec(o.cap_n, o.cap_d, 4)));
        }
    }
    let rdtd = r.d * td;
    let mut worst = i128::MAX;
    for (a, row) in rows.iter().enumerate() {
        let va = v[a] as i128;
        let mut lhs = (rdtd * 72 + td * r.n * row.mag as i128 - r.d * tn).checked_mul(va).unwrap();
        let mut s = 0i128;
        for &(j, c) in row.core.iter() {
            s += c as i128 * v[j as usize] as i128;
        }
        lhs -= rdtd * s;
        let mut rhs = 0i128;
        for t in row.tails.iter() {
            let n = nk(t, f, r, tn, td);
            if o.gates && n <= 0 {
                return Err(format!("REFUSE|gate=zsign_schur_denominator|row={}|N_k={}", a, n));
            }
            let mut sk = 0i128;
            for &j in t.back.iter() {
                sk += v[j as usize] as i128;
            }
            let num = sk.checked_mul(rdtd * rdtd).unwrap().checked_mul(f[t.m as usize]).unwrap();
            let term = if n > 0 { (num + n - 1) / n } else { -(num / (-n).max(1)) };
            rhs += if o.flip { -term } else { term };
        }
        let slack = lhs - rhs;
        if slack < 0 {
            return Err(format!("REFUSE|gate=row_check|row={}|key={}|M={}|slack={}", a, row.key, row.mag, slack));
        }
        worst = worst.min(slack);
    }
    Ok((rows.len(), worst))
}

// ---------------------------------------------------------------- fixed-point Gauss-Seidel eigen-iteration for F(t)
const E: i128 = 1 << 20;
struct FMat {
    diag: Vec<i128>,           // E (72 + r M - t)
    ent: Vec<Vec<(u32, i128)>>, // E c_AB + sum_k E/(delta_k - t) (two-step), aggregated
}
// t = tn/td is passed as one Rat (n = tn, d = td)
fn fmat_x(rows: &[Row], f: &[i128], r: Rat, t: Rat, threads: usize, flip: bool, strict: bool) -> FMat {
    let (tn, td) = (t.n, t.d);
    let rdtd = r.d * td;
    let ent = par_map(rows.len(), threads, |a| {
        let row = &rows[a];
        let mut e: Vec<(u32, i128)> = row.core.iter().map(|&(j, c)| (j, E * c as i128)).collect();
        if !strict {
            // faulted data may carry non-positive counts: keep the iteration well defined
            for x in e.iter_mut() {
                x.1 = x.1.max(0);
            }
        }
        for t in row.tails.iter() {
            let n = nk(t, f, r, tn, td);
            if strict {
                assert!(n > 0, "t at or above a tail floor");
            }
            let w0 = if n > 0 { E * rdtd * f[t.m as usize] / n } else { 0 };
            let w = if flip { -w0 } else { w0 };
            for &j in t.back.iter() {
                e.push((j, w));
            }
        }
        e.sort_unstable_by_key(|x| x.0);
        let mut agg: Vec<(u32, i128)> = Vec::new();
        for (j, w) in e {
            match agg.last_mut() {
                Some(l) if l.0 == j => l.1 += w,
                _ => agg.push((j, w)),
            }
        }
        agg
    });
    let diag = rows.iter().map(|row| E * (rdtd * 72 + td * r.n * row.mag as i128 - r.d * tn) / rdtd).collect();
    FMat { diag, ent }
}
const VMAX: i128 = 1 << 50;
fn cw_ratios(fm: &FMat, v: &[i128]) -> (i128, i128, usize) {
    let mut lo = i128::MAX;
    let mut hi = i128::MIN;
    let mut arg = 0;
    for a in 0..v.len() {
        let mut s = fm.diag[a] * v[a];
        for &(j, w) in fm.ent[a].iter() {
            s -= w * v[j as usize];
        }
        let q = s / v[a];
        if q < lo {
            lo = q;
            arg = a;
        }
        hi = hi.max(q);
    }
    (lo, hi, arg)
}
fn gs_eigen(fm: &FMat, v: &mut [i128], outer: usize, verbose: bool) -> i128 {
    // inexact inverse iteration: x solves (F - sigma) x = v by a few Gauss-Seidel sweeps, sigma below the CW lower bound
    let n = v.len();
    let inner = 8usize;
    let (mut lo, mut hi, a0) = cw_ratios(fm, v);
    if verbose {
        println!("GS|init|cw_lo={}|cw_hi={}|argmin={}", dec(lo, E, 4), dec(hi, E, 4), a0);
    }
    let mut selfw = vec![0i128; n];
    for (a, sw) in selfw.iter_mut().enumerate() {
        for &(j, w) in fm.ent[a].iter() {
            if j as usize == a {
                *sw += w;
            }
        }
    }
    let mut last = i128::MIN;
    for it in 0..outer {
        let margin = ((hi - lo) / 4).clamp(E / 50, 20 * E);
        let sigma = lo - margin;
        let mut x: Vec<i128> = v.iter().map(|&a| a * E / margin.max(1)).collect();
        for _ in 0..inner {
            for a in 0..n {
                let mut num = E * v[a];
                for &(j, w) in fm.ent[a].iter() {
                    if j as usize != a {
                        num += w * x[j as usize];
                    }
                }
                let den = fm.diag[a] - selfw[a] - sigma;
                x[a] = if den > 0 { num / den } else { x[a] };
            }
        }
        let mx = *x.iter().max().unwrap();
        // rescale so that max v = 2^50 exactly (up or down)
        for a in 0..n {
            v[a] = if mx >= VMAX { x[a] / (mx / VMAX).max(1) } else { x[a] * (VMAX / mx.max(1)) }.max(1);
        }
        let (l2, h2, _) = cw_ratios(fm, v);
        lo = l2;
        hi = h2;
        if verbose && (it % 20 == 0 || it + 1 == outer) {
            println!("GS|outer={}|sigma={}|cw_lo={}|cw_hi={}", it, dec(sigma, E, 6), dec(lo, E, 7), dec(hi, E, 7));
        }
        if it > 5 && ((lo - last).abs() <= 2 || hi - lo <= 4) {
            break;
        }
        last = lo;
    }
    lo
}

fn ritz(rows: &[Row], v: &[i64], r: Rat) -> (i128, i128) {
    // Rayleigh quotient of the zero-extended class vector: an upper bound on lambda_min(QHQ); v scaled by 2^-20
    let w: Vec<i128> = v.iter().map(|&x| ((x as i128) >> 20).max(1)).collect();
    let mut num = 0i128;
    let mut den = 0i128;
    for (a, row) in rows.iter().enumerate() {
        let mut s = (72 * r.d + r.n * row.mag as i128) * w[a];
        for &(j, c) in row.core.iter() {
            s -= r.d * c as i128 * w[j as usize];
        }
        num += row.wt as i128 * w[a] * s;
        den += row.wt as i128 * w[a] * w[a] * r.d;
    }
    (num, den)
}

// ---------------------------------------------------------------- I/O of class keys
fn keys_path(dir: &str, m0: i64) -> String {
    format!("{}/core_keys_m{}.bin", dir, m0)
}
fn load_or_enumerate(tab: &Tab, m0: i64, threads: usize, dir: &str) -> Vec<u64> {
    let p = keys_path(dir, m0);
    if let Ok(mut fh) = std::fs::File::open(&p) {
        let mut b = Vec::new();
        fh.read_to_end(&mut b).unwrap();
        let keys: Vec<u64> = b.chunks(8).map(|c| u64::from_le_bytes(c.try_into().unwrap())).collect();
        println!("KEYS|loaded={}|classes={}", p, keys.len());
        return keys;
    }
    let t0 = Instant::now();
    let keys = enumerate(tab, m0, threads);
    println!("ENUM|m0={}|classes={}|secs={}|hwm={}", m0, keys.len(), t0.elapsed().as_secs(), mem());
    let mut fh = std::fs::File::create(&p).unwrap();
    for k in keys.iter() {
        fh.write_all(&k.to_le_bytes()).unwrap();
    }
    keys
}

fn arg(args: &[String], key: &str, default: &str) -> String {
    for i in 0..args.len() {
        if args[i] == key && i + 1 < args.len() {
            return args[i + 1].clone();
        }
    }
    default.to_string()
}

fn census(args: &[String]) {
    let tab = tables();
    let m0: i64 = arg(args, "--m0", "8").parse().unwrap();
    let threads: usize = arg(args, "--threads", "4").parse().unwrap();
    let dir = arg(args, "--dir", ".");
    s3_table_gate(&tab);
    let keys = load_or_enumerate(&tab, m0, threads, &dir);
    let infos = par_map(keys.len(), threads, |i| tab.info(keys[i]));
    let (orb, wgt) = closed_form();
    let mut ok = true;
    for m in 1..=m0 {
        let cl = infos.iter().filter(|x| x.3 as i64 == m).count();
        let o: i128 = infos.iter().filter(|x| x.3 as i64 == m).map(|x| x.1 as i128).sum();
        let w: i128 = infos.iter().filter(|x| x.3 as i64 == m).map(|x| x.2 as i128).sum();
        let pass = o == orb[m as usize] && w == wgt[m as usize];
        ok &= pass;
        println!(
            "CENSUS|M={}|classes={}|orbits={}|closed_form_orbits={}|weight={}|closed_form_weight={}|{}",
            m,
            cl,
            o,
            orb[m as usize],
            w,
            wgt[m as usize],
            if pass { "PASS" } else { "FAIL" }
        );
    }
    let stabs: Vec<usize> = (1..=48).filter(|d| 48 % d == 0).collect();
    let mut hist = vec![0usize; 49];
    for x in infos.iter() {
        hist[x.1 as usize] += 1;
    }
    println!(
        "CENSUS|class_sizes(norb:count)={}",
        stabs.iter().filter(|&&d| hist[d] > 0).map(|&d| format!("{}:{}", d, hist[d])).collect::<Vec<_>>().join(",")
    );
    println!("GATE|census_vs_closed_form|{}|M=1..{}", if ok { "PASS" } else { "FAIL" }, m0);
    assert!(ok);
}

struct Built {
    rows: Vec<Row>,
    sigs_all: Vec<(i64, [i64; 6])>,
    rowhash: String,
    keyshash: String,
    images: usize,
}
fn build(args: &[String], tab: &Tab) -> (Built, i64) {
    let m0: i64 = arg(args, "--m0", "8").parse().unwrap();
    let threads: usize = arg(args, "--threads", "4").parse().unwrap();
    let dir = arg(args, "--dir", ".");
    let gates = arg(args, "--gates", "1") == "1";
    let images: usize = arg(args, "--images", "2").parse().unwrap();
    assert!(m0 >= 4, "m0 >= 4 keeps the tail one move away from the flats");
    sha_constants_gate();
    s3_table_gate(tab);
    let keys = load_or_enumerate(tab, m0, threads, &dir);
    for w in keys.windows(2) {
        assert!(w[0] < w[1], "class keys strictly increasing");
    }
    let keyshash = keys_hash(&keys);
    println!("KEYSHASH|m0={}|classes={}|sha256={}", m0, keys.len(), keyshash);
    let index: HashMap<u64, u32> = keys.iter().enumerate().map(|(i, &k)| (k, i as u32)).collect();
    let t0 = Instant::now();
    let (rows, g) = build_rows(tab, &keys, &index, m0, threads, gates, images);
    let ntail: usize = rows.iter().map(|x| x.tails.len()).sum();
    let nback: usize = rows.iter().map(|x| x.tails.iter().map(|t| t.back.len()).sum::<usize>()).sum();
    println!(
        "ROWS|m0={}|classes={}|tail_targets={}|two_step_back_moves={}|secs={}|hwm={}",
        m0,
        rows.len(),
        ntail,
        nback,
        t0.elapsed().as_secs(),
        mem()
    );
    if gates {
        println!("GATE|local_delta_vs_full_M|PASS|moves_checked={}", g.local_vs_full);
        println!("GATE|link_multiset_table|PASS|configurations_checked={}", g.link_multisets);
    }
    println!("GATE|symmetry_image_rows|{}|classes={}|images_per_class={}|rows_rebuilt={}", if images > 0 { "PASS" } else { "OFF" }, rows.len(), images, g.images);
    let th = Instant::now();
    let (rowhash, nt, nb, nbytes) = row_hash(&rows, m0);
    println!("ROWHASH|m0={}|sha256={}|classes={}|tail_moves={}|back_moves={}|bytes={}|secs={}", m0, rowhash, rows.len(), nt, nb, nbytes, th.elapsed().as_secs());
    // census of the enumerated core against the closed form
    let (orb, wgt) = closed_form();
    let mut ok = true;
    for m in 1..=m0 {
        let o: i128 = rows.iter().filter(|x| x.mag as i64 == m).map(|x| x.norb as i128).sum();
        let w: i128 = rows.iter().filter(|x| x.mag as i64 == m).map(|x| x.wt as i128).sum();
        ok &= o == orb[m as usize] && w == wgt[m as usize];
    }
    println!("GATE|core_census_vs_closed_form|{}|M=1..{}", if ok { "PASS" } else { "FAIL" }, m0);
    assert!(ok);
    // detailed balance on the class level: W'_A c(A->B) = W'_B c(B->A)
    let mut nb = 0usize;
    for (a, row) in rows.iter().enumerate() {
        for &(b, c) in row.core.iter() {
            let back = rows[b as usize].core.iter().find(|x| x.0 == a as u32).map(|x| x.1).unwrap_or(0);
            assert_eq!(row.wt as i64 * c as i64, rows[b as usize].wt as i64 * back as i64, "class detailed balance");
            nb += 1;
        }
    }
    println!("GATE|class_detailed_balance|PASS|edges={}", nb);
    // --even 1: use the proved parity constraint (the number of transposition plaquettes is even)
    let even = arg(args, "--even", "0") == "1";
    let sigs_all = colour_signatures(tab, even);
    println!("COLOURINGS|even_t_only={}|signatures={}", even, sigs_all.len());
    (Built { rows, sigs_all, rowhash, keyshash, images }, m0)
}

// min over the realised tail layers M > m0 of delta_min(M) = 72 + r M - G(M)/f(M), as (num, den) with den > 0 (f > 0)
fn cap_from_g(g: &[i128], f: &[i128], m0: i64, r: Rat, print: bool) -> (i128, i128) {
    let mut best: (i128, i128) = (0, 0);
    for m in (m0 + 1)..37 {
        if g[m as usize] < 0 {
            continue;
        }
        assert!(f[m as usize] > 0, "the cap needs f > 0");
        let num = (72 * r.d + r.n * m as i128) * f[m as usize] - r.d * g[m as usize];
        let den = r.d * f[m as usize];
        if print {
            println!("TAILFLOOR|M={}|f={}|G={}|delta_min={}|trivial_rM={}", m, f[m as usize], g[m as usize], dec(num, den, 4), dec(r.n * m as i128, r.d, 4));
        }
        if best.1 == 0 || num * best.1 < best.0 * den {
            best = (num, den);
        }
    }
    best
}
fn tail_floor_report(sigs: &[(i64, [i64; 6])], f: &[i128], m0: i64, r: Rat, print: bool) -> (Vec<i128>, i128, i128) {
    // returns G(M), and the min over M > m0 of delta_min(M) = 72 + r M - G(M)/f(M) as a rational (num, den)
    let g = tail_g(sigs, f, m0);
    let (n, d) = cap_from_g(&g, f, m0, r, print);
    (g, n, d)
}
// the full f on M = m0+1..36 with trailing repeats dropped (make_f keeps the last value beyond the list)
fn f_spec_of(f: &[i128], m0: i64) -> String {
    let vals: Vec<i128> = ((m0 + 1)..37).map(|m| f[m as usize]).collect();
    let mut n = vals.len();
    while n > 1 && vals[n - 1] == vals[n - 2] {
        n -= 1;
    }
    vals[..n].iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")
}


// the pipeline: outer t-iteration with inverse iteration for v, then exact bisection on t for that v
// the data of one certificate problem (rows, f, r and the t denominator td) and the solver settings of one certify call
#[derive(Clone, Copy)]
struct Problem<'a> {
    rows: &'a [Row],
    f: &'a [i128],
    r: Rat,
    td: i128,
}
#[derive(Clone, Copy)]
struct Solve<'a> {
    sweeps: usize,
    threads: usize,
    verbose: bool,
    tag: &'a str,
    strict: bool,
}
fn certify(pb: Problem, tcap: i128, o: Opts, sv: Solve) -> (i128, Vec<i64>) {
    let Problem { rows, f, r, td } = pb;
    let Solve { sweeps, threads, verbose, tag, strict } = sv;
    let strict = strict && o.gates && !o.flip;
    let mut v: Vec<i128> = rows.iter().map(|row| VMAX >> (3 * (row.mag as u32 - 3)).min(40)).collect();
    let mut tn: i128 = (r.n * 3 * td / r.d).min(tcap - td);
    for it in 0..10 {
        let fm = fmat_x(rows, f, r, Rat { n: tn, d: td }, threads, o.flip, strict);
        let mu = gs_eigen(&fm, &mut v, sweeps, verbose);
        let step = mu * td / E;
        println!("OUTER|{}|it={}|t={}|cw_lo(F(t))={}", tag, it, dec(tn, td, 4), dec(mu, E, 6));
        let nt = (tn + step).min(tcap - 1);
        if (nt - tn).abs() <= 1 {
            tn = nt;
            break;
        }
        tn = nt;
    }
    let vi: Vec<i64> = v.iter().map(|&x| x.max(1) as i64).collect();
    let mut lo = tn - 5 * td;
    let mut hi = tcap;
    let mut lo_ok = exact_check(rows, &vi, f, r, lo, td, o).is_ok();
    while !lo_ok && lo > -1000 * td {
        lo -= 10 * td;
        lo_ok = exact_check(rows, &vi, f, r, lo, td, o).is_ok();
    }
    if exact_check(rows, &vi, f, r, hi, td, o).is_ok() {
        lo = hi;
    } else {
        while hi - lo > 1 {
            let mid = (lo + hi) / 2;
            if exact_check(rows, &vi, f, r, mid, td, o).is_ok() {
                lo = mid;
            } else {
                hi = mid;
            }
        }
    }
    (lo, vi)
}

// ---------------------------------------------------------------- FIX-1: row hash, certificate file, r policy
// SHA-256 of the canonical serialization of the rows (r- and f-independent). Text, one line each:
//   "floorcert-rows-v1 m0=<m0>"; per class in increasing key order "C <key> <M> <flat moves>" + " <target key>:<count>"
//   per core target class (increasing target key); then per tail move "T <M_k> <h_0>,...,<h_8>" + " <back key>" per move
//   back into the core (sorted, with multiplicity), h_i = tail-staying moves with Delta M = i - 4, the tail lines sorted
//   by the integer tuple (M_k, h_0..h_8, back keys); last "END <classes> <tail moves> <back moves>".
fn row_hash(rows: &[Row], m0: i64) -> (String, usize, usize, u64) {
    let mut h = Sha256::new();
    let mut nbytes = 0u64;
    let (mut nt, mut nb) = (0usize, 0usize);
    let mut s = format!("floorcert-rows-v1 m0={}\n", m0);
    for (a, row) in rows.iter().enumerate() {
        if a > 0 {
            assert!(rows[a - 1].key < row.key, "rows must be in increasing key order");
        }
        write!(s, "C {} {} {}", row.key, row.mag, row.nflat).unwrap();
        let mut core = row.core.clone();
        core.sort_unstable();
        for w in core.windows(2) {
            assert!(w[0].0 < w[1].0, "core targets must be aggregated");
        }
        for &(j, c) in core.iter() {
            write!(s, " {}:{}", rows[j as usize].key, c).unwrap();
        }
        s.push('\n');
        let mut tails: Vec<Tail> = row
            .tails
            .iter()
            .map(|t| {
                let mut x = t.clone();
                x.back.sort_unstable();
                x
            })
            .collect();
        tails.sort();
        for t in tails.iter() {
            write!(s, "T {} {}", t.m, t.hist.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")).unwrap();
            for &j in t.back.iter() {
                write!(s, " {}", rows[j as usize].key).unwrap();
            }
            s.push('\n');
            nt += 1;
            nb += t.back.len();
        }
        if s.len() > 1 << 16 {
            h.update(s.as_bytes());
            nbytes += s.len() as u64;
            s.clear();
        }
    }
    writeln!(s, "END {} {} {}", rows.len(), nt, nb).unwrap();
    h.update(s.as_bytes());
    nbytes += s.len() as u64;
    (hex(&h.finish()), nt, nb, nbytes)
}
// sha256 of the class keys as 8-byte little-endian words in file order (= sha256sum of core_keys_m<m0>.bin)
fn keys_hash(keys: &[u64]) -> String {
    let mut h = Sha256::new();
    for k in keys.iter() {
        h.update(&k.to_le_bytes());
    }
    hex(&h.finish())
}
// one writer for honest and faulted certificates; the header carries the full f, the claimed cap and the row hash
struct CertOut<'a> {
    path: &'a str,
    m0: i64,
    r: Rat,
    tn: i128,
    td: i128,
    f: &'a [i128],
    cap: (i128, i128),
    rowhash: &'a str,
    keyshash: &'a str,
    freeze: &'a Option<(String, String)>,
    rows: &'a [Row],
    v: &'a [i64],
}
fn write_cert(c: &CertOut) -> String {
    let CertOut { path, m0, r, tn, td, f, cap, rowhash, keyshash, freeze, rows, v } = *c;
    let fs = f_spec_of(f, m0);
    let f2 = make_f(&fs, m0);
    for m in (m0 + 1)..37 {
        assert_eq!(f2[m as usize], f[m as usize], "the header f spec reproduces f on every tail layer");
    }
    assert!(cap.1 > 0);
    let mut s = String::new();
    write!(s, "# floorcert certificate: m0={} r={}/{} t={}/{} f={} cap={}/{} rowhash={} keyshash={} classes={}", m0, r.n, r.d, tn, td, fs, cap.0, cap.1, rowhash, keyshash, rows.len()).unwrap();
    if let Some((c, p)) = freeze {
        write!(s, " freeze={} pred={}", c, p).unwrap();
    }
    s.push('\n');
    for (row, x) in rows.iter().zip(v.iter()) {
        writeln!(s, "{} {} {}", row.key, row.mag, x).unwrap();
    }
    std::fs::write(path, s.as_bytes()).unwrap();
    sha256_hex(s.as_bytes())
}

// Prediction first. The excluded values are r in {21/2, 12, 14} and r >= 20 (nothing within 1 of r = 9); r = 9 itself
// runs only in the frozen binary; every other r is refused before any computation.
const FROZEN_COMMIT: Option<&str> = option_env!("FLOORCERT_FREEZE_COMMIT");
const FROZEN_PREDICTION_SHA256: Option<&str> = option_env!("FLOORCERT_PREDICTION_SHA256");
#[derive(PartialEq, Debug)]
enum RClass {
    Excluded,
    Nine,
    Refused,
}
fn r_class(r: Rat) -> RClass {
    assert!(r.d > 0);
    if 2 * r.n == 21 * r.d || r.n == 12 * r.d || r.n == 14 * r.d || r.n >= 20 * r.d {
        RClass::Excluded
    } else if r.n == 9 * r.d {
        RClass::Nine
    } else {
        RClass::Refused
    }
}
fn is_hex(s: &str, n: usize) -> bool {
    s.len() == n && s.bytes().all(|b| matches!(b, b'0'..=b'9' | b'a'..=b'f'))
}
fn refuse_exit(msg: &str) -> ! {
    println!("REFUSE|{}", msg);
    std::process::exit(3)
}
// None for an excluded r; Some((freeze commit, prediction sha256)) in the frozen r = 9 mode; refuses everything else
fn r_policy(r: Rat, args: &[String]) -> Option<(String, String)> {
    match r_class(r) {
        RClass::Excluded => None,
        RClass::Refused => refuse_exit(&format!("gate=r_policy|r={}/{}|allowed r: 21/2, 12, 14 and r >= 20 (nothing within 1 of r = 9); r = 9 only in the frozen binary", r.n, r.d)),
        RClass::Nine => {
            let (c, p) = match (FROZEN_COMMIT, FROZEN_PREDICTION_SHA256) {
                (Some(c), Some(p)) if is_hex(c, 40) && is_hex(p, 64) => (c, p),
                _ => refuse_exit("gate=r9_frozen_mode|not the frozen binary: built without FLOORCERT_FREEZE_COMMIT (40 hex) and FLOORCERT_PREDICTION_SHA256 (64 hex)"),
            };
            if arg(args, "--freeze-commit", "") != c || arg(args, "--prediction-sha256", "") != p {
                refuse_exit("gate=r9_frozen_mode|--freeze-commit or --prediction-sha256 differs from the pins compiled into this binary");
            }
            let bytes = match std::fs::read(arg(args, "--prediction", "")) {
                Ok(b) => b,
                Err(_) => refuse_exit("gate=r9_frozen_mode|--prediction file unreadable"),
            };
            if sha256_hex(&bytes) != p {
                refuse_exit("gate=r9_frozen_mode|the --prediction file does not hash to the frozen prediction sha256");
            }
            let exe = std::fs::read("/proc/self/exe").map(|b| sha256_hex(&b)).unwrap_or_default();
            println!("FREEZE|r=9|commit={}|prediction_sha256={}|binary_sha256={}", c, p, exe);
            Some((c.to_string(), p.to_string()))
        }
    }
}

fn cert(args: &[String]) {
    let tab = tables();
    let rs: Vec<Rat> = arg(args, "--r", "12").split(',').map(parse_rat).collect();
    // prediction first: every r is classified before any computation
    let mut freeze: Option<(String, String)> = None;
    for r in rs.iter() {
        if let Some(fz) = r_policy(*r, args) {
            freeze = Some(fz);
        }
    }
    let (b, m0) = build(args, &tab);
    let threads: usize = arg(args, "--threads", "4").parse().unwrap();
    let td: i128 = 10_000;
    let specs: Vec<String> = arg(args, "--f", "geom:1/2:6").split(';').map(|s| s.to_string()).collect();
    let sweeps: usize = arg(args, "--sweeps", "600").parse().unwrap();
    let plant = arg(args, "--plant", "none");
    let mut jobs: Vec<(Rat, String)> = Vec::new();
    for r in rs.iter() {
        for spec in specs.iter() {
            jobs.push((*r, spec.clone()));
        }
    }
    for (r, spec) in jobs.iter() {
        let r = *r;
        let fspec = if let Some(rest) = spec.strip_prefix("geom:") {
            let parts: Vec<&str> = rest.split(':').collect();
            let q = parse_rat(parts[0]);
            let cap: usize = parts[1].parse().unwrap();
            geom_spec(q.n, q.d, cap)
        } else {
            spec.clone()
        };
        let f = make_f(&fspec, m0);
        let t0 = Instant::now();
        let (g, dn, dd) = tail_floor_report(&b.sigs_all, &f, m0, r, args.iter().any(|a| a == "--print-tail"));
        // gate: every observed tail orbit's exact floor is >= the analytic layer floor (sum f <= G(M))
        let mut nobs = 0usize;
        let mut min_obs: (i128, i128) = (0, 0);
        for row in b.rows.iter() {
            for t in row.tails.iter() {
                let sf = sumf(t, &f);
                assert!(sf <= g[t.m as usize], "tail gate: observed f-sum above the colouring bound");
                let num = (72 * r.d + r.n * t.m as i128) * f[t.m as usize] - r.d * sf;
                let den = r.d * f[t.m as usize];
                if min_obs.1 == 0 || num * min_obs.1 < min_obs.0 * den {
                    min_obs = (num, den);
                }
                nobs += 1;
            }
        }
        // t must stay below the analytic floor of every tail layer: tcap = floor(td * min delta_min) - 1
        let tcap = (dn * td) / dd - 1;
        println!(
            "TAIL|f={}|min_layer_floor={}|min_observed_target_floor={}|observed_targets={}|gate_observed_ge_layer=PASS",
            fspec,
            dec(dn, dd, 4),
            dec(min_obs.0, min_obs.1, 4),
            nobs
        );
        let o = Opts { gates: true, flip: false, m0, cap_n: dn, cap_d: dd };
        let (lo, vi) = certify(Problem { rows: &b.rows, f: &f, r, td }, tcap, o, Solve { sweeps, threads, verbose: args.iter().any(|a| a == "--verbose"), tag: "honest", strict: true });
        let nfloor = vi.iter().filter(|&&x| x < 1 << 10).count();
        let vmin = *vi.iter().min().unwrap();
        println!("VEC|classes={}|v_max=2^50|v_min={}|entries_below_2^10={}", vi.len(), vmin, nfloor);
        let res = exact_check(&b.rows, &vi, &f, r, lo, td, o);
        let fail_next = exact_check(&b.rows, &vi, &f, r, lo + 1, td, o);
        let (rn_, rd_) = ritz(&b.rows, &vi, r);
        let trivial = r.n * (m0 as i128 + 1);
        let fs = f_spec_of(&f, m0);
        println!(
            "CERT|r={}/{}|m0={}|classes={}|f={}|gamma={}/{}={}|row_check={}|min_slack={}|next_t_refused={}|ritz_upper={}|trivial_r(m0+1)={}|tail_cap={}|rowhash={}|images={}|independent_gate=REQUIRED|secs={}",
            r.n,
            r.d,
            m0,
            b.rows.len(),
            fs,
            lo,
            td,
            dec(lo, td, 4),
            if res.is_ok() { "PASS" } else { "FAIL" },
            res.as_ref().map(|x| x.1.to_string()).unwrap_or("-".into()),
            fail_next.err().map(|e| e.split('|').nth(1).unwrap_or("").to_string()).unwrap_or("NONE".into()),
            dec(rn_, rd_, 6),
            dec(trivial, r.d, 4),
            dec(dn, dd, 4),
            b.rowhash,
            b.images,
            t0.elapsed().as_secs()
        );
        if args.iter().any(|a| a == "--write-cert") {
            let p = format!("{}/cert_m{}_r{}_{}_f{}.txt", arg(args, "--dir", "."), m0, r.n, r.d, fs.replace(',', "-"));
            let fsha = write_cert(&CertOut { path: &p, m0, r, tn: lo, td, f: &f, cap: (dn, dd), rowhash: &b.rowhash, keyshash: &b.keyshash, freeze: &freeze, rows: &b.rows, v: &vi });
            println!("WROTE|{}|sha256={}|independent_gate=REQUIRED: design/gate_required.sh {}", p, fsha, p);
        }
        if plant != "none" {
            let ub = {
                let u = arg(args, "--ub", "none");
                if u == "none" {
                    None
                } else {
                    let q = parse_rat(&u);
                    Some(q.n * td / q.d)
                }
            };
            let pdir = arg(args, "--plant-dir", &arg(args, "--dir", "."));
            // a faulted writer still solves below every observed tail floor (else F(t) is undefined)
            let tobs = if min_obs.1 > 0 { (min_obs.0 * td) / min_obs.1 - 1 } else { i128::MAX };
            let env = PlantEnv { b: &b, v: &vi, f: &f, r, tn: lo, td, m0, base: o, ub, sweeps, threads, dir: pdir, tobs };
            planted(&env, &plant);
        }
    }
}

// ---------------------------------------------------------------- planted faults
fn verdict(x: &Result<(usize, i128), String>) -> String {
    match x {
        Ok(_) => "PASS".to_string(),
        Err(e) => e.clone(),
    }
}
fn max_t(pb: Problem, v: &[i64], o: Opts, lo0: i128, hi0: i128) -> Option<i128> {
    let Problem { rows, f, r, td } = pb;
    // largest t in [lo0, hi0] (step 1/td) that the check accepts, assuming monotonicity in t
    let ok = |t: i128| exact_check(rows, v, f, r, t, td, o).is_ok();
    if !ok(lo0) {
        return None;
    }
    if ok(hi0) {
        return Some(hi0);
    }
    let (mut lo, mut hi) = (lo0, hi0);
    while hi - lo > 1 {
        let mid = (lo + hi) / 2;
        if ok(mid) {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    Some(lo)
}
struct PlantEnv<'a> {
    b: &'a Built,
    v: &'a [i64],
    f: &'a [i128],
    r: Rat,
    tn: i128,
    td: i128,
    m0: i64,
    base: Opts,
    ub: Option<i128>,
    sweeps: usize,
    threads: usize,
    dir: String,
    tobs: i128, // floor(td * min over observed tail targets of delta_k) - 1
}
// FIX-1 item 2: every planted fault writes its faulted certificate file, in the same format as an honest one and with
// no plant flag inside, for the independent verifier. A faulted writer keeps the honest tail cap unless the plant is in
// the cap (P4c, P4d). "writer_verdict" is the faulted writer's own gated check on the data and code it used;
// "honest_writer_rejudge" is the honest writer's gated check of the faulted (t, v) on its honest rows.
fn planted(e: &PlantEnv, which: &str) {
    let (b, v, f, r, tn, td, m0, base) = (e.b, e.v, e.f, e.r, e.tn, e.td, e.m0, e.base);
    let (sweeps, threads) = (e.sweeps, e.threads);
    let bare = Opts { gates: false, ..base };
    let gated = Opts { gates: true, ..base };
    let honest_cap = (base.cap_n, base.cap_d);
    let tcap = (base.cap_n * td) / base.cap_d - 1;
    let ubs = e.ub.map(|x| dec(x, td, 4)).unwrap_or("none".into());
    let emit = |name: &str, rows: &[Row], ff: &[i128], cap: (i128, i128), tf: i128, vf: &[i64], writer: String| {
        let (rh, _, _, _) = row_hash(rows, m0);
        let path = format!("{}/cert_m{}_r{}_{}_{}.txt", e.dir, m0, r.n, r.d, name);
        let fsha = write_cert(&CertOut { path: &path, m0, r, tn: tf, td, f: ff, cap, rowhash: &rh, keyshash: &b.keyshash, freeze: &None, rows: &b.rows, v: vf });
        let rejudge = verdict(&exact_check(&b.rows, vf, f, r, tf, td, gated));
        println!(
            "PLANT|{}|claimed_t={}|honest_gamma={}|claimed_t_above_honest={}|above_known_upper_bound({})={}|claimed_cap={}|rowhash_differs={}|writer_verdict={}|honest_writer_rejudge={}|file={}|file_sha256={}",
            name,
            dec(tf, td, 4),
            dec(tn, td, 4),
            tf > tn,
            ubs,
            e.ub.map(|u| tf > u).unwrap_or(false),
            dec(cap.0, cap.1, 4),
            rh != b.rowhash,
            writer.replace('|', ";"),
            rejudge.replace('|', ";"),
            path,
            fsha
        );
    };
    println!(
        "PLANT|baseline|t={}|gated={}|t+1e-4:gated={}",
        dec(tn, td, 4),
        verdict(&exact_check(&b.rows, v, f, r, tn, td, gated)),
        verdict(&exact_check(&b.rows, v, f, r, tn + 1, td, gated))
    );
    // the class with the smallest v: the wrong target of the misrouting plants
    let z = (0..v.len()).min_by_key(|&a| (v[a], a)).unwrap() as u32;
    // a faulted-row writer: honest cap, gates off while solving, then its own gated check
    let run_rows = |name: &str, rows: &[Row]| {
        let (tf, vf) = certify(Problem { rows, f, r, td }, tcap, bare, Solve { sweeps, threads, verbose: false, tag: name, strict: false });
        let w = verdict(&exact_check(rows, &vf, f, r, tf, td, gated));
        emit(name, rows, f, honest_cap, tf, &vf, w);
    };
    let all = ["P1a", "P1b", "P2a", "P2b", "P2c", "P3a", "P3b", "P4a", "P4b", "P4c", "P4d", "P5a", "P5b"];
    let list: Vec<&str> = if which == "all" { all.to_vec() } else { which.split(',').collect() };
    for w in list {
        match w {
            "P1a" => {
                // every core off-diagonal count negated (not a Z-matrix)
                let mut rows = b.rows.clone();
                for row in rows.iter_mut() {
                    for c in row.core.iter_mut() {
                        c.1 = -c.1;
                    }
                }
                run_rows("P1a_wrong_sign_offdiagonal", &rows);
            }
            "P1b" => {
                // code error: the Schur term added instead of subtracted; honest rows and v, the faulted code's largest t
                let o_flip = Opts { gates: false, flip: true, ..base };
                let tf = max_t(Problem { rows: &b.rows, f, r, td }, v, o_flip, tn - 20 * td, tcap).unwrap_or(tn);
                let wv = verdict(&exact_check(&b.rows, v, f, r, tf, td, Opts { gates: true, flip: true, ..base }));
                emit("P1b_wrong_sign_schur_term_code", &b.rows, f, honest_cap, tf, v, wv);
            }
            "P2a" => {
                let mut rows = b.rows.clone();
                for row in rows.iter_mut() {
                    row.tails.clear();
                }
                run_rows("P2a_all_tail_neighbours_missing", &rows);
            }
            "P2b" => {
                let mut rows = b.rows.clone();
                for row in rows.iter_mut() {
                    if !row.tails.is_empty() {
                        let mut best = 0;
                        let mut bs = -1i128;
                        for (i, t) in row.tails.iter().enumerate() {
                            let s: i128 = t.back.iter().map(|&j| v[j as usize] as i128).sum();
                            if s > bs {
                                bs = s;
                                best = i;
                            }
                        }
                        row.tails.remove(best);
                    }
                }
                run_rows("P2b_heaviest_tail_neighbour_missing", &rows);
            }
            "P2c" => {
                let mut rows = b.rows.clone();
                for row in rows.iter_mut() {
                    for t in row.tails.iter_mut() {
                        t.back.clear();
                    }
                }
                run_rows("P2c_two_step_paths_missing", &rows);
            }
            "P3a" => {
                let mut f2 = f.to_vec();
                f2[(m0 + 2) as usize] = -f2[(m0 + 2) as usize];
                let (tf, vf) = certify(Problem { rows: &b.rows, f: &f2, r, td }, tcap, bare, Solve { sweeps, threads, verbose: false, tag: "P3a", strict: false });
                let wv = verdict(&exact_check(&b.rows, &vf, &f2, r, tf, td, gated));
                emit("P3a_tail_f_not_positive", &b.rows, &f2, honest_cap, tf, &vf, wv);
            }
            "P3b" => {
                let mut v2 = v.to_vec();
                let a = v2.iter().enumerate().min_by_key(|x| x.1).unwrap().0;
                v2[a] = 0;
                let wv = verdict(&exact_check(&b.rows, &v2, f, r, tn, td, gated));
                emit("P3b_core_v_not_positive", &b.rows, f, honest_cap, tn, &v2, wv);
            }
            "P4a" => {
                let wv = verdict(&exact_check(&b.rows, v, f, r, tn + 1, td, gated));
                emit("P4a_gamma_overstated_by_1e-4", &b.rows, f, honest_cap, tn + 1, v, wv);
            }
            "P4b" => {
                // tail-staying decreasing moves forgotten (delta_k inflated)
                let mut rows = b.rows.clone();
                for row in rows.iter_mut() {
                    for t in row.tails.iter_mut() {
                        for d in 0..4 {
                            t.hist[d] = 0;
                        }
                    }
                }
                run_rows("P4b_tail_target_floors_overstated", &rows);
            }
            "P4c" => {
                // the analytic tail cap claimed 10 higher; the faulted writer trusts its claimed cap
                let over = Opts { gates: true, cap_n: base.cap_n + 10 * base.cap_d, ..base };
                let tcap_over = ((over.cap_n * td) / over.cap_d - 1).min(e.tobs);
                let (tf, vf) = certify(Problem { rows: &b.rows, f, r, td }, tcap_over, over, Solve { sweeps, threads, verbose: false, tag: "P4c", strict: false });
                let wv = verdict(&exact_check(&b.rows, &vf, f, r, tf, td, over));
                emit("P4c_tail_cap_overstated_by_10", &b.rows, f, (over.cap_n, over.cap_d), tf, &vf, wv);
            }
            "P4d" => {
                // the colouring bound G(M) understated by 10 %; the faulted writer derives its cap from it
                let g_true = tail_g(&b.sigs_all, f, m0);
                let g_low: Vec<i128> = g_true.iter().map(|&g| if g < 0 { g } else { g - g / 10 }).collect();
                let cap_low = cap_from_g(&g_low, f, m0, r, false);
                let under = Opts { gates: true, cap_n: cap_low.0, cap_d: cap_low.1, ..base };
                let tcap_low = ((cap_low.0 * td) / cap_low.1 - 1).min(e.tobs);
                let mut viol = 0usize;
                let mut seen = 0usize;
                for row in b.rows.iter() {
                    for t in row.tails.iter() {
                        seen += 1;
                        if sumf(t, f) > g_low[t.m as usize] {
                            viol += 1;
                        }
                    }
                }
                let (tf, vf) = certify(Problem { rows: &b.rows, f, r, td }, tcap_low, under, Solve { sweeps, threads, verbose: false, tag: "P4d", strict: false });
                let wv = if viol > 0 {
                    format!("REFUSE|gate=observed_tail_floor_below_claim|targets_above_claim={}|of={}", viol, seen)
                } else {
                    verdict(&exact_check(&b.rows, &vf, f, r, tf, td, under))
                };
                emit("P4d_colouring_bound_understated_10pct", &b.rows, f, cap_low, tf, &vf, wv);
            }
            "P5a" => {
                // NEW: in every row one one-step move goes to the wrong class with its count kept: one count of the
                // move to the core neighbour with the largest v is sent to the class with the smallest v
                let mut rows = b.rows.clone();
                let mut moved = 0usize;
                for row in rows.iter_mut() {
                    if row.core.is_empty() {
                        continue;
                    }
                    let bi = (0..row.core.len()).max_by_key(|&i| (v[row.core[i].0 as usize], row.core[i].0)).unwrap();
                    if row.core[bi].0 == z {
                        continue;
                    }
                    row.core[bi].1 -= 1;
                    if row.core[bi].1 == 0 {
                        row.core.remove(bi);
                    }
                    match row.core.binary_search_by_key(&z, |x| x.0) {
                        Ok(p) => row.core[p].1 += 1,
                        Err(p) => row.core.insert(p, (z, 1)),
                    }
                    moved += 1;
                }
                println!("PLANT|P5a_detail|rows_misrouted={}|wrong_target_row={}", moved, z);
                run_rows("P5a_misrouted_core_target", &rows);
            }
            "P5b" => {
                // NEW: in every tail move, the two-step move back to the core class with the largest v is sent to the
                // class with the smallest v (count kept)
                let mut rows = b.rows.clone();
                let mut moved = 0usize;
                for row in rows.iter_mut() {
                    for t in row.tails.iter_mut() {
                        if t.back.is_empty() {
                            continue;
                        }
                        let p = (0..t.back.len()).max_by_key(|&i| (v[t.back[i] as usize], t.back[i])).unwrap();
                        if t.back[p] == z {
                            continue;
                        }
                        t.back[p] = z;
                        t.back.sort_unstable();
                        moved += 1;
                    }
                }
                println!("PLANT|P5b_detail|tail_moves_misrouted={}|wrong_target_row={}", moved, z);
                run_rows("P5b_misrouted_two_step_target", &rows);
            }
            _ => panic!("unknown plant {}", w),
        }
    }
}

// r-independent: r_star = max over M > m0+1 of (G(M)/f(M) - 72)/(M - m0 - 1); for every r >= r_star the analytic tail
// cap is at least the trivial r (m0 + 1). gain1 = 72 - G(m0+1)/f(m0+1) >= 0 is the r-independent gain on layer m0+1.
fn rstar(args: &[String]) {
    let tab = tables();
    let sigs = colour_signatures(&tab, arg(args, "--even", "0") == "1");
    for m0 in arg(args, "--m0", "10").split(',').map(|x| x.parse::<i64>().unwrap()) {
        for spec in arg(args, "--f", "1").split(';') {
            let f = make_f(spec, m0);
            let g = tail_g(&sigs, &f, m0);
            let mut best: (i128, i128) = (-1_000_000, 1);
            let mut arg_m = 0;
            for m in (m0 + 2)..37 {
                if g[m as usize] < 0 {
                    continue;
                }
                let num = g[m as usize] - 72 * f[m as usize];
                let den = f[m as usize] * (m - m0 - 1) as i128;
                if num * best.1 > best.0 * den {
                    best = (num, den);
                    arg_m = m;
                }
            }
            let m1 = (m0 + 1) as usize;
            let gain = (72 * f[m1] - g[m1], f[m1]);
            println!(
                "RSTAR|m0={}|f={}|r_star={}|binding_M={}|gain_layer_m0+1={}|table(M:G/f)={}",
                m0,
                spec,
                dec(best.0, best.1, 4),
                arg_m,
                dec(gain.0, gain.1, 4),
                ((m0 + 1)..(m0 + 9).min(37)).map(|m| format!("{}:{}/{}", m, g[m as usize], f[m as usize])).collect::<Vec<_>>().join(",")
            );
        }
    }
}

fn tailonly(args: &[String]) {
    let tab = tables();
    let r = parse_rat(&arg(args, "--r", "12"));
    let _ = r_policy(r, args);
    let m0: i64 = arg(args, "--m0", "8").parse().unwrap();
    let even = arg(args, "--even", "0") == "1";
    let sigs = colour_signatures(&tab, even);
    println!("SIGS|count={}|even_t_only={}", sigs.len(), even);
    for spec in arg(args, "--f", "geom:1/2:6").split(';') {
        let fspec = if let Some(rest) = spec.strip_prefix("geom:") {
            let parts: Vec<&str> = rest.split(':').collect();
            let q = parse_rat(parts[0]);
            geom_spec(q.n, q.d, parts[1].parse().unwrap())
        } else {
            spec.to_string()
        };
        let f = make_f(&fspec, m0);
        let (_, dn, dd) = tail_floor_report(&sigs, &f, m0, r, true);
        println!("TAILONLY|m0={}|r={}/{}|f={}|min_delta_min={}", m0, r.n, r.d, fspec, dec(dn, dd, 4));
    }
}

// r-independent: the canonical row hash of the core at m0 (no certificate, no r)
// V2: an absent --dir is created here, before the keys file is written; `cert` creates no directory (it reuses the
// directory that `rowhash` wrote, or an existing one, as in FIX-1)
fn rowhash_only(args: &[String]) {
    std::fs::create_dir_all(arg(args, "--dir", ".")).unwrap();
    let tab = tables();
    let (b, m0) = build(args, &tab);
    println!("ROWHASH_ONLY|m0={}|sha256={}|keyshash={}|classes={}", m0, b.rowhash, b.keyshash, b.rows.len());
}

fn selftest() {
    sha_constants_gate();
    println!("SELFTEST|sha256_constants|PASS|H0 (8) and K (64) rederived from the first 64 primes equal the table");
    let million = vec![b'a'; 1_000_000];
    let cases: [(&str, &[u8], &str); 4] = [
        ("empty", b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        ("abc", b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        ("448bit", b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
        ("million_a", &million, "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"),
    ];
    for (name, m, want) in cases.iter() {
        let got = sha256_hex(m);
        assert_eq!(&got, want, "SHA-256 test vector {}", name);
        println!("SELFTEST|sha256_vector|{}|PASS|{}", name, got);
    }
    // streaming in uneven pieces equals one-shot hashing
    let data: Vec<u8> = (0..200_003u32).map(|i| (i.wrapping_mul(2654435761) >> 13) as u8).collect();
    let one = sha256_hex(&data);
    for piece in [1usize, 3, 55, 56, 63, 64, 65, 1000, 65536] {
        let mut h = Sha256::new();
        for c in data.chunks(piece) {
            h.update(c);
        }
        assert_eq!(hex(&h.finish()), one, "streaming piece {}", piece);
    }
    println!("SELFTEST|sha256_streaming|PASS|pieces 1,3,55,56,63,64,65,1000,65536 of 200003 bytes|{}", one);
    // r policy on excluded and refused values (no r-dependent computation; r = 9 itself is not exercised)
    let want: [(&str, RClass); 9] = [
        ("21/2", RClass::Excluded),
        ("12", RClass::Excluded),
        ("14", RClass::Excluded),
        ("20", RClass::Excluded),
        ("41/2", RClass::Excluded),
        ("10", RClass::Refused),
        ("19/2", RClass::Refused),
        ("90000001/10000000", RClass::Refused),
        ("8", RClass::Refused),
    ];
    for (s, c) in want.iter() {
        assert_eq!(r_class(parse_rat(s)), *c, "r policy at {}", s);
    }
    println!("SELFTEST|r_policy|PASS|excluded 21/2,12,14,20,41/2; refused 10,19/2,9+1e-7,8; frozen_binary={}", FROZEN_COMMIT.is_some() && FROZEN_PREDICTION_SHA256.is_some());
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(|s| s.as_str()) {
        Some("census") => census(&args),
        Some("cert") => cert(&args),
        Some("tail") => tailonly(&args),
        Some("rstar") => rstar(&args),
        Some("rowhash") => rowhash_only(&args),
        Some("selftest") => selftest(),
        Some("sha256") => {
            let b = std::fs::read(&args[2]).unwrap();
            println!("{}  {}", sha256_hex(&b), args[2]);
        }
        _ => {
            eprintln!("usage: floorcert census --m0 N | rowhash --m0 N | selftest | sha256 FILE | cert --m0 N --r 21/2 --f '8,7,6,5,4;1' [--write-cert] [--images 2] [--plant all|P1a,..,P5b --plant-dir D --ub 993765/10000] | tail --m0 N --r R --f ...");
            std::process::exit(2);
        }
    }
}
