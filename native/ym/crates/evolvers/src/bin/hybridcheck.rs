//! hybridcheck: an attack on a hybrid Barta certificate from results/3x4_stream/perron/vector/review-opus55, from the definition of H.
//!
//!   hybridcheck check LX LY R CUT HYBRID TABLE CLAIM_MICRO THREADS [sabotage=NAME]
//!     d is the file's value on each gauge orbit with 0 < M <= CUT, given once per class under the lattice symmetries, one value per lump above CUT, and 0 on the flats.
//!     1. Classes: every representative is decoded and its class counted image by image. The counts per lump must equal C(P; a, b) N(a, b), the Frobenius count on a torus,
//!        with N = 12 3^a 2^b for even a >= 2 and N = 12 2^b + 6 (-1)^b for a = 0. Distinct classes whose counts reach the total hold every configuration of the lump.
//!     2. Rows at M <= CUT: all 3 nl moves of each representative, each recomputed from all plaquettes, each target looked up by its canonical form. A sample of images
//!        under a random symmetry and gauge must give the same row.
//!     3. Rows above CUT: every row of TABLE, written by local_table.py, with a move into a lump at M <= CUT taken at the largest d in that lump.
//!     4. The upper side: the Rayleigh quotient of d cut off at CUT, and the 9-dimensional space it spans with the 8 flats. Any integer vector gives a valid bound.
//!     Exits 2 if any count differs, any target is missing, or the minimum differs from CLAIM_MICRO.
//!     Sabotages for its controls: lower_one, drop_one, wrong_m, nonzero_flat.
//!
//!   hybridcheck write PASSA LX LY CUT HYBRID D_OUT
//!     The same d over every row of a store, as little-endian i64, for the pinned perroncert check.
//!
//!   hybridcheck upper LX LY R CUT HYBRID SWEEPS THREADS PSI_OUT
//!     A trial vector on the file's orbits, fitted from d, then its A, B and C recomputed from all plaquettes. Any integer vector gives a valid bound, so the fit is untrusted.
//!     Writes the vector as key|M|weight|value.
//!
//! Its group, lattice, gauge and canonical form are its own. From the reader it takes the file's format. Integer only, Rust 1.81, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use num_bigint::BigInt;
use std::collections::{BTreeMap, HashMap};
use std::io::{BufRead, BufReader, BufWriter, Read, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;

const PERMS: [[u8; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];
const MICRO: u128 = 1_000_000;
const CHUNK: usize = 64;
const SAMPLE_EVERY: usize = 97;
const TRIAL_BITS: u32 = 40;
const MAX_VALUE_BITS: u32 = 96;

fn num<T: std::str::FromStr>(s: &str) -> Result<T, String> {
    s.parse().map_err(|_| format!("bad number {s}"))
}

fn field<'a>(line: &'a str, k: &str) -> Option<&'a str> {
    line.split('|').find_map(|kv| kv.strip_prefix(k))
}

struct Sym {
    link: Vec<u16>,
    flip: Vec<bool>,
    plaq: Vec<u8>,
}

struct Lattice {
    p: usize,
    nl: usize,
    mul: [[u8; 6]; 6],
    inv: [u8; 6],
    kind: [u8; 6],
    trans: [u8; 3],
    conj: [[u8; 6]; 6],
    plaq: Vec<[usize; 4]>,
    tree: Vec<(usize, usize, usize)>,
    src: Vec<usize>,
    dst: Vec<usize>,
    free: Vec<usize>,
    syms: Vec<Sym>,
    reader_free: Vec<usize>,
    reader_el: [u8; 6],
}

/// What one thread reuses from call to call.
struct Scratch {
    p: Vec<u8>,
    img: Vec<u8>,
    digits: Vec<u8>,
    best: Vec<u8>,
    mins: Vec<u16>,
    defects: Vec<(u8, u8)>,
    keys: Vec<u128>,
}

impl Lattice {
    fn new(lx: usize, ly: usize) -> Result<Lattice, String> {
        if lx < 3 || ly < 3 || lx * ly > 32 {
            return Err("each side at least 3, at most 32 plaquettes".into());
        }
        let p = lx * ly;
        let nl = 2 * p;
        let site = |x: usize, y: usize| (x % lx) * ly + y % ly;
        let xl = |x: usize, y: usize| site(x, y);
        let yl = |x: usize, y: usize| p + site(x, y);
        let mut mul = [[0u8; 6]; 6];
        let mut inv = [0u8; 6];
        let mut kind = [0u8; 6];
        for (a, pa) in PERMS.iter().enumerate() {
            for (b, pb) in PERMS.iter().enumerate() {
                let t = [pa[pb[0] as usize], pa[pb[1] as usize], pa[pb[2] as usize]];
                mul[a][b] = PERMS.iter().position(|q| *q == t).map_or(255, |i| i as u8);
                if mul[a][b] == 0 {
                    inv[a] = b as u8;
                }
            }
            kind[a] = match (0..3).filter(|&k| pa[k] == k as u8).count() {
                3 => 0,
                1 => 1,
                _ => 2,
            };
        }
        let t: Vec<u8> = (0..6u8).filter(|&g| kind[g as usize] == 1).collect();
        let mut conj = [[0u8; 6]; 6];
        for c in 0..6 {
            for e in 0..6 {
                conj[c][e] = mul[mul[c][e] as usize][inv[c] as usize];
            }
        }
        let mut plaq = Vec::with_capacity(p);
        let (mut src, mut dst) = (vec![0usize; nl], vec![0usize; nl]);
        for x in 0..lx {
            for y in 0..ly {
                plaq.push([xl(x, y), yl(x + 1, y), xl(x, y + 1), yl(x, y)]);
                src[xl(x, y)] = site(x, y);
                dst[xl(x, y)] = site(x + 1, y);
                src[yl(x, y)] = site(x, y);
                dst[yl(x, y)] = site(x, y + 1);
            }
        }
        // The comb gauge: these links are the identity after gauge fixing, and the free links stay in ascending order, each a base-6 digit, lowest first.
        let mut tree = Vec::with_capacity(p - 1);
        let mut in_tree = vec![false; nl];
        for y in 1..ly {
            tree.push((yl(0, y - 1), site(0, y - 1), site(0, y)));
            in_tree[yl(0, y - 1)] = true;
        }
        for x in 1..lx {
            for y in 0..ly {
                tree.push((xl(x - 1, y), site(x - 1, y), site(x, y)));
                in_tree[xl(x - 1, y)] = true;
            }
        }
        let free: Vec<usize> = (0..nl).filter(|&l| !in_tree[l]).collect();
        // The file's format: its own numbering of links, its own tree, and its own numbering of the group, read into this program's.
        let r_index = |x: usize, y: usize, d: usize| 2 * (x + lx * y) + d;
        let mut r_tree = vec![false; nl];
        let mut r_to_mine = vec![0usize; nl];
        for y in 0..ly {
            for x in 0..lx {
                r_to_mine[r_index(x, y, 0)] = xl(x, y);
                r_to_mine[r_index(x, y, 1)] = yl(x, y);
                if x + 1 < lx {
                    r_tree[r_index(x, y, 0)] = true;
                }
            }
        }
        for y in 0..ly - 1 {
            r_tree[r_index(0, y, 1)] = true;
        }
        let reader_free: Vec<usize> = (0..nl).filter(|&l| !r_tree[l]).map(|l| r_to_mine[l]).collect();
        let mut reader_el = [0u8; 6];
        for (e, slot) in reader_el.iter_mut().enumerate() {
            let (k, f) = (e % 3, e / 3);
            let image = |x: usize| ((k + if f == 0 { x } else { 3 - x }) % 3) as u8;
            let t = [image(0), image(1), image(2)];
            *slot = PERMS.iter().position(|q| *q == t).ok_or("the file's element is outside the group")? as u8;
        }
        // Lattice symmetries: translations, the two reflections, and the swap when the sides are equal.
        let mut by_links: HashMap<[usize; 4], usize> = HashMap::new();
        for (i, q) in plaq.iter().enumerate() {
            let mut s = *q;
            s.sort_unstable();
            by_links.insert(s, i);
        }
        let swaps: &[bool] = if lx == ly { &[false, true] } else { &[false] };
        let mut syms = Vec::new();
        for &sw in swaps {
            for sx in [false, true] {
                for sy in [false, true] {
                    for tx in 0..lx {
                        for ty in 0..ly {
                            let phi = |x: usize, y: usize| {
                                let a = if sx { (lx - x) % lx } else { x };
                                let b = if sy { (ly - y) % ly } else { y };
                                let (a, b) = if sw { (b, a) } else { (a, b) };
                                ((a + tx) % lx, (b + ty) % ly)
                            };
                            let mut link = vec![0u16; nl];
                            let mut flip = vec![false; nl];
                            for x in 0..lx {
                                for y in 0..ly {
                                    for d in 0..2 {
                                        let from = phi(x, y);
                                        let to = if d == 0 { phi((x + 1) % lx, y) } else { phi(x, (y + 1) % ly) };
                                        let me = if d == 0 { xl(x, y) } else { yl(x, y) };
                                        let (target, inverted) = if to == ((from.0 + 1) % lx, from.1) {
                                            (xl(from.0, from.1), false)
                                        } else if to == (from.0, (from.1 + 1) % ly) {
                                            (yl(from.0, from.1), false)
                                        } else if from == ((to.0 + 1) % lx, to.1) {
                                            (xl(to.0, to.1), true)
                                        } else if from == (to.0, (to.1 + 1) % ly) {
                                            (yl(to.0, to.1), true)
                                        } else {
                                            return Err("a symmetry sends a link off the lattice".into());
                                        };
                                        link[me] = target as u16;
                                        flip[me] = inverted;
                                    }
                                }
                            }
                            let mut pl = vec![0u8; p];
                            for (i, q) in plaq.iter().enumerate() {
                                let mut s = [link[q[0]] as usize, link[q[1]] as usize, link[q[2]] as usize, link[q[3]] as usize];
                                s.sort_unstable();
                                pl[i] = *by_links.get(&s).ok_or("a symmetry sends a plaquette off the lattice")? as u8;
                            }
                            syms.push(Sym { link, flip, plaq: pl });
                        }
                    }
                }
            }
        }
        Ok(Lattice { p, nl, mul, inv, kind, trans: [t[0], t[1], t[2]], conj, plaq, tree, src, dst, free, syms, reader_free, reader_el })
    }

    fn scratch(&self) -> Scratch {
        Scratch {
            p: vec![0; self.p],
            img: vec![0; self.nl],
            digits: vec![0; self.free.len()],
            best: vec![0; self.free.len()],
            mins: Vec::with_capacity(self.syms.len()),
            defects: Vec::with_capacity(self.p),
            keys: Vec::with_capacity(self.syms.len() * 6),
        }
    }

    fn holonomy(&self, u: &[u8], p: usize) -> u8 {
        let q = &self.plaq[p];
        self.mul[self.mul[self.mul[u[q[0]] as usize][u[q[1]] as usize] as usize][self.inv[u[q[2]] as usize] as usize] as usize][self.inv[u[q[3]] as usize] as usize]
    }

    /// (a, b) from every plaquette.
    fn lump(&self, u: &[u8]) -> (usize, usize) {
        let (mut a, mut b) = (0usize, 0usize);
        for p in 0..self.p {
            match self.kind[self.holonomy(u, p) as usize] {
                1 => a += 1,
                2 => b += 1,
                _ => {}
            }
        }
        (a, b)
    }

    fn image(&self, u: &[u8], s: &Sym, out: &mut [u8]) {
        for (l, &v) in u.iter().enumerate() {
            out[s.link[l] as usize] = if s.flip[l] { self.inv[v as usize] } else { v };
        }
    }

    fn gauge_fix(&self, u: &[u8], p: &mut [u8], out: &mut [u8]) {
        p[0] = 0;
        for &(l, a, b) in &self.tree {
            p[b] = self.mul[p[a] as usize][u[l] as usize];
        }
        for (o, &l) in out.iter_mut().zip(&self.free) {
            *o = self.mul[self.mul[p[self.src[l]] as usize][u[l] as usize] as usize][self.inv[p[self.dst[l]] as usize] as usize];
        }
    }

    /// One key per class under gauge, global conjugation and lattice symmetries. The symmetries that give the least pattern of defects are the only ones that need the links.
    fn canon(&self, u: &[u8], w: &mut Scratch) -> u128 {
        let Scratch { p, img, digits, best, mins, defects, .. } = w;
        defects.clear();
        for q in 0..self.p {
            let k = self.kind[self.holonomy(u, q) as usize];
            if k != 0 {
                defects.push((q as u8, k));
            }
        }
        let mut top = u64::MAX;
        mins.clear();
        for (i, s) in self.syms.iter().enumerate() {
            let mut pattern = 0u64;
            for &(q, k) in defects.iter() {
                pattern |= u64::from(k) << (2 * u32::from(s.plaq[q as usize]));
            }
            match pattern.cmp(&top) {
                std::cmp::Ordering::Less => {
                    top = pattern;
                    mins.clear();
                    mins.push(i as u16);
                }
                std::cmp::Ordering::Equal => mins.push(i as u16),
                std::cmp::Ordering::Greater => {}
            }
        }
        let mut have = false;
        for &i in mins.iter() {
            self.image(u, &self.syms[i as usize], img);
            self.gauge_fix(img, p, digits);
            for c in &self.conj {
                let mut smaller = !have;
                if have {
                    for (d, b) in digits.iter().zip(best.iter()) {
                        let x = c[*d as usize];
                        if x != *b {
                            smaller = x < *b;
                            break;
                        }
                    }
                }
                if smaller {
                    for (b, d) in best.iter_mut().zip(digits.iter()) {
                        *b = c[*d as usize];
                    }
                    have = true;
                }
            }
        }
        best.iter().rev().fold(0u128, |k, &d| k * 6 + u128::from(d))
    }

    /// The number of gauge-fixed configurations in the class of u, image by image.
    fn class_size(&self, u: &[u8], w: &mut Scratch) -> u64 {
        let Scratch { p, img, digits, keys, .. } = w;
        keys.clear();
        for s in &self.syms {
            self.image(u, s, img);
            self.gauge_fix(img, p, digits);
            for c in &self.conj {
                keys.push(digits.iter().rev().fold(0u128, |k, &d| k * 6 + u128::from(c[d as usize])));
            }
        }
        keys.sort_unstable();
        keys.dedup();
        keys.len() as u64
    }

    fn decode_reader(&self, mut key: u128, u: &mut [u8]) {
        u.iter_mut().for_each(|v| *v = 0);
        for &l in self.reader_free.iter().rev() {
            u[l] = self.reader_el[(key % 6) as usize];
            key /= 6;
        }
    }

    /// One representative of each flat orbit, with its number of gauge-fixed configurations.
    fn flats(&self, lx: usize, ly: usize, w: &mut Scratch) -> Vec<(Vec<u8>, u64)> {
        let mut orbits: BTreeMap<u128, (Vec<u8>, u64)> = BTreeMap::new();
        for hx in 0..6u8 {
            for hy in 0..6u8 {
                if self.mul[hx as usize][hy as usize] != self.mul[hy as usize][hx as usize] {
                    continue;
                }
                let mut u = vec![0u8; self.nl];
                for y in 0..ly {
                    u[(lx - 1) * ly + y] = hx;
                }
                for x in 0..lx {
                    u[self.p + x * ly + ly - 1] = hy;
                }
                self.gauge_fix(&u, &mut w.p, &mut w.digits);
                let key = self.conj.iter().map(|c| w.digits.iter().rev().fold(0u128, |k, &d| k * 6 + u128::from(c[d as usize]))).min().unwrap_or(0);
                orbits.entry(key).or_insert((u, 0)).1 += 1;
            }
        }
        orbits.into_values().collect()
    }
}

fn binomial(n: usize, k: usize) -> u128 {
    let mut out = 1u128;
    for i in 0..k {
        out = out * (n - i) as u128 / (i + 1) as u128;
    }
    out
}

/// The number of gauge-fixed configurations in a lump: C(P; a, b) N(a, b), the Frobenius count on a torus with one puncture per defect.
fn expected(p: usize, a: usize, b: usize) -> u128 {
    if a % 2 == 1 || a + b > p {
        return 0;
    }
    let n = if a == 0 {
        let base = 12 * (1u128 << b);
        if b % 2 == 0 {
            base + 6
        } else {
            base - 6
        }
    } else {
        12 * 3u128.pow(a as u32) * (1u128 << b)
    };
    binomial(p, a) * binomial(p - a, b) * n
}

struct Rep {
    key: u128,
    value: u128,
    canon: u128,
    weight: u64,
    a: u8,
    b: u8,
}

struct Hybrid {
    reps: Vec<Rep>,
    above: HashMap<(usize, usize), u128>,
    bits: u32,
}

fn read_hybrid(path: &str) -> Result<Hybrid, String> {
    let file = std::fs::File::open(path).map_err(|e| format!("{path}: {e}"))?;
    let mut reps = Vec::new();
    let mut above = HashMap::new();
    let mut top = 0u128;
    for line in BufReader::new(file).lines() {
        let line = line.map_err(|e| e.to_string())?;
        let f: Vec<&str> = line.split('|').collect();
        match f[0] {
            "P" if f.len() == 3 => {
                let value: u128 = num(f[2])?;
                top = top.max(value);
                reps.push(Rep { key: num(f[1])?, value, canon: 0, weight: 0, a: 0, b: 0 });
            }
            "G" if f.len() == 4 => {
                let value: u128 = num(f[3])?;
                top = top.max(value);
                above.insert((num(f[1])?, num(f[2])?), value);
            }
            _ => return Err(format!("a row of another kind: {line}")),
        }
    }
    let bits = 128 - top.leading_zeros();
    if bits > MAX_VALUE_BITS {
        return Err(format!("a value of {bits} bits"));
    }
    Ok(Hybrid { reps, above, bits })
}

/// Canonical form, lump and class size of each representative.
fn classify(lat: &Lattice, reps: &mut [Rep], threads: usize) {
    let size = reps.len().div_ceil(threads.max(1)).max(1);
    std::thread::scope(|sc| {
        for part in reps.chunks_mut(size) {
            sc.spawn(move || {
                let mut w = lat.scratch();
                let mut u = vec![0u8; lat.nl];
                for r in part.iter_mut() {
                    lat.decode_reader(r.key, &mut u);
                    let (a, b) = lat.lump(&u);
                    r.a = a as u8;
                    r.b = b as u8;
                    r.canon = lat.canon(&u, &mut w);
                    r.weight = lat.class_size(&u, &mut w);
                }
            });
        }
    });
}

struct Ctx<'a> {
    lat: &'a Lattice,
    map: &'a HashMap<u128, u128>,
    above: &'a [u128],
    side: usize,
    cut: usize,
    shift: u32,
    flat_d: u128,
}

#[derive(Default)]
struct Row {
    s: u128,
    trial: u128,
    to_flat: u64,
    missing: u64,
}

fn row(ctx: &Ctx, u: &mut [u8], w: &mut Scratch) -> Row {
    let lat = ctx.lat;
    let mut r = Row::default();
    for l in 0..lat.nl {
        let keep = u[l];
        for &t in &lat.trans {
            u[l] = lat.mul[t as usize][keep as usize];
            let (a, b) = lat.lump(u);
            let m = 2 * a + 3 * b;
            if m == 0 {
                r.to_flat += 1;
                r.s += ctx.flat_d;
            } else if m <= ctx.cut {
                match ctx.map.get(&lat.canon(u, w)) {
                    Some(v) => {
                        r.s += *v;
                        r.trial += *v >> ctx.shift;
                    }
                    None => r.missing += 1,
                }
            } else {
                let v = ctx.above[a * ctx.side + b];
                if v == 0 {
                    r.missing += 1;
                }
                r.s += v;
            }
        }
        u[l] = keep;
    }
    r
}

fn ratio_micro(diag: u128, s: u128, own: u128) -> i128 {
    (diag * MICRO) as i128 - (s * MICRO).div_ceil(own) as i128
}

#[derive(Default)]
struct Sum {
    min: Option<(i128, u128, u8, u8)>,
    moves: u64,
    to_flat: u64,
    missing: u64,
    samples: u64,
    sample_bad: u64,
    a: i128,
    b: i128,
}

/// Every move out of a random image of u under a random symmetry and gauge, against the row of u itself.
fn sample(ctx: &Ctx, i: usize, u: &[u8], canon: u128, s: u128, w: &mut Scratch) -> bool {
    let lat = ctx.lat;
    let mut st = (i as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15) ^ 0xD1B5_4A32_D192_ED03;
    let mut draw = |n: usize| {
        st = st.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407);
        ((st >> 33) as usize) % n
    };
    let sym = &lat.syms[draw(lat.syms.len())];
    let mut image = vec![0u8; lat.nl];
    lat.image(u, sym, &mut image);
    let g: Vec<u8> = (0..lat.p).map(|_| draw(6) as u8).collect();
    let mut v: Vec<u8> = (0..lat.nl).map(|l| lat.mul[lat.mul[g[lat.src[l]] as usize][image[l] as usize] as usize][lat.inv[g[lat.dst[l]] as usize] as usize]).collect();
    lat.canon(&v, w) == canon && row(ctx, &mut v, w).s == s
}

fn check(a: &[String]) -> Result<i32, String> {
    let (lx, ly, r, cut) = (num::<usize>(&a[2])?, num::<usize>(&a[3])?, num::<u128>(&a[4])?, num::<usize>(&a[5])?);
    let (hybrid_path, table_path, claim, threads) = (&a[6], &a[7], num::<i128>(&a[8])?, num::<usize>(&a[9])?);
    let sabotage = a.get(10).and_then(|s| s.strip_prefix("sabotage=")).unwrap_or("none");
    if a.len() > 11 || (a.len() == 11 && sabotage == "none") {
        return Err("an argument too many".into());
    }
    let t0 = std::time::Instant::now();
    let lat = Lattice::new(lx, ly)?;
    let mut h = read_hybrid(hybrid_path)?;
    if sabotage == "lower_one" {
        h.reps[0].value /= 2;
    } else if sabotage == "drop_one" {
        h.reps.remove(0);
    }
    let shift = h.bits.saturating_sub(TRIAL_BITS);
    let side = lat.p + 1;
    println!("HYBRIDCHECK_INPUT|Lx={lx}|Ly={ly}|r={r}|cut={cut}|reps={}|lumps_above={}|value_bits={}|symmetries={}|threads={threads}|sabotage={sabotage}|json=0", h.reps.len(), h.above.len(), h.bits, lat.syms.len());
    classify(&lat, &mut h.reps, threads);
    // 1. Classes.
    let mut map: HashMap<u128, u128> = HashMap::with_capacity(h.reps.len());
    let mut same_class = 0u64;
    let mut outside_the_cut = 0u64;
    let mut not_positive = 0u64;
    let mut found: BTreeMap<(usize, usize), u128> = BTreeMap::new();
    let mut dmax = vec![0u128; side * side];
    for rep in &h.reps {
        let (x, y) = (rep.a as usize, rep.b as usize);
        let m = 2 * x + 3 * y;
        outside_the_cut += u64::from(m == 0 || m > cut);
        not_positive += u64::from(rep.value == 0);
        same_class += u64::from(map.insert(rep.canon, rep.value).is_some());
        *found.entry((x, y)).or_insert(0) += u128::from(rep.weight);
        dmax[x * side + y] = dmax[x * side + y].max(rep.value);
    }
    let (mut total_expected, mut total_found, mut wrong) = (0u128, 0u128, Vec::new());
    for x in 0..=lat.p {
        for y in 0..=lat.p - x {
            let m = 2 * x + 3 * y;
            if m == 0 || m > cut {
                continue;
            }
            let (want, got) = (expected(lat.p, x, y), found.get(&(x, y)).copied().unwrap_or(0));
            total_expected += want;
            total_found += got;
            if want != got {
                wrong.push(format!("{x},{y}:{got}/{want}"));
            }
        }
    }
    println!(
        "HYBRIDCHECK_CLASSES|reps={}|classes_in_one_rep={same_class}|outside_the_cut={outside_the_cut}|not_positive={not_positive}|configs_in_model={total_found}|configs_expected={total_expected}|configs_missing={}|lumps_with_a_wrong_count={}|wrong={}|secs={}|json=0",
        h.reps.len(),
        total_expected.saturating_sub(total_found),
        wrong.len(),
        if wrong.is_empty() { "-".to_string() } else { wrong.join(";") },
        t0.elapsed().as_secs()
    );
    // 2. Rows at M <= CUT.
    let mut above = vec![0u128; side * side];
    for (&(x, y), &v) in &h.above {
        if x > lat.p || y > lat.p {
            return Err("a lump above the cut lies outside the lattice".into());
        }
        above[x * side + y] = v;
    }
    let flat_d = if sabotage == "nonzero_flat" { 1u128 << h.bits } else { 0 };
    let ctx = Ctx { lat: &lat, map: &map, above: &above, side, cut, shift, flat_d };
    let m_of = |x: usize, y: usize| if sabotage == "wrong_m" { 2 * x + 2 * y } else { 2 * x + 3 * y };
    let nl3 = 3 * lat.nl;
    let next = AtomicUsize::new(0);
    let total = Mutex::new(Sum::default());
    std::thread::scope(|sc| {
        for _ in 0..threads {
            sc.spawn(|| {
                let mut w = lat.scratch();
                let mut u = vec![0u8; lat.nl];
                let mut sum = Sum::default();
                loop {
                    let start = next.fetch_add(CHUNK, Ordering::Relaxed);
                    if start >= h.reps.len() {
                        break;
                    }
                    for (i, rep) in h.reps.iter().enumerate().skip(start).take(CHUNK) {
                        lat.decode_reader(rep.key, &mut u);
                        let got = row(&ctx, &mut u, &mut w);
                        let diag = (r * m_of(rep.a as usize, rep.b as usize) as u128 + nl3 as u128) as i128;
                        let ratio = ratio_micro(diag as u128, got.s, rep.value.max(1));
                        if sum.min.map_or(true, |m| ratio < m.0) {
                            sum.min = Some((ratio, rep.key, rep.a, rep.b));
                        }
                        sum.moves += nl3 as u64;
                        sum.to_flat += got.to_flat;
                        sum.missing += got.missing;
                        // The trial vector of the upper side: d >> shift on the orbits at M <= CUT, 0 elsewhere. Any integer vector is valid there.
                        let t = (rep.value >> shift) as i128;
                        sum.a += i128::from(rep.weight) * t * (diag * t - got.trial as i128);
                        sum.b += i128::from(rep.weight) * t * t;
                        if i % SAMPLE_EVERY == 0 {
                            sum.samples += 1;
                            sum.sample_bad += u64::from(!sample(&ctx, i, &u, rep.canon, got.s, &mut w));
                        }
                    }
                }
                let mut all = total.lock().unwrap_or_else(|e| e.into_inner());
                if let Some(m) = sum.min {
                    if all.min.map_or(true, |o| m.0 < o.0) {
                        all.min = Some(m);
                    }
                }
                all.moves += sum.moves;
                all.to_flat += sum.to_flat;
                all.missing += sum.missing;
                all.samples += sum.samples;
                all.sample_bad += sum.sample_bad;
                all.a += sum.a;
                all.b += sum.b;
            });
        }
    });
    let sum = total.into_inner().unwrap_or_else(|e| e.into_inner());
    let (min_exact, min_key, min_a, min_b) = sum.min.ok_or("no representatives")?;
    println!(
        "HYBRIDCHECK_ROWS|min_exact_micro={min_exact}|at_key={min_key}|at_lump={min_a},{min_b}|moves={}|moves_to_flats={}|missing_moves={}|symmetry_samples={}|symmetry_mismatches={}|secs={}|json=0",
        sum.moves,
        sum.to_flat,
        sum.missing,
        sum.samples,
        sum.sample_bad,
        t0.elapsed().as_secs()
    );
    // 3. Rows above CUT, from the table.
    let table = std::fs::File::open(table_path).map_err(|e| format!("{table_path}: {e}"))?;
    let mut names: Vec<(usize, usize)> = Vec::new();
    let (mut rows_total, mut rows_past, mut bad_rows) = (0u64, 0u64, 0u64);
    let mut lumps_past: BTreeMap<(usize, usize), u64> = BTreeMap::new();
    let mut min_table: Option<(i128, usize, usize)> = None;
    for line in BufReader::new(table).lines() {
        let line = line.map_err(|e| e.to_string())?;
        let need = |k: &str| field(&line, k).ok_or_else(|| format!("no {k}"));
        if line.starts_with("LUMP|") {
            names.push((num(need("a=")?)?, num(need("b=")?)?));
        } else if line.starts_with("SIG|") {
            rows_total += 1;
            let own = *names.get(num::<usize>(need("lump=")?)?).ok_or("a row outside the lumps")?;
            if 2 * own.0 + 3 * own.1 <= cut {
                continue;
            }
            rows_past += 1;
            *lumps_past.entry(own).or_insert(0) += 1;
            let flat: u128 = num(need("flat=")?)?;
            let diag_field: usize = num(need("diag=")?)?;
            let own_d = above[own.0 * side + own.1];
            if own_d == 0 || diag_field != nl3 {
                bad_rows += 1;
                continue;
            }
            let mut s = flat * flat_d;
            let mut count = flat;
            let list = need("n=")?;
            if !list.is_empty() {
                for p in list.split(',') {
                    let (i, c) = p.split_once(':').ok_or("bad neighbour")?;
                    let (id, c) = (num::<usize>(i)?, num::<u128>(c)?);
                    let (x, y) = *names.get(id).ok_or("a move outside the lumps")?;
                    count += c;
                    let v = if 2 * x + 3 * y <= cut { dmax[x * side + y] } else { above[x * side + y] };
                    if v == 0 {
                        bad_rows += 1;
                    }
                    s += c * v;
                }
            }
            bad_rows += u64::from(count != nl3 as u128);
            let d = r * m_of(own.0, own.1) as u128 + nl3 as u128;
            let ratio = ratio_micro(d, s, own_d);
            if min_table.map_or(true, |m| ratio < m.0) {
                min_table = Some((ratio, own.0, own.1));
            }
        }
    }
    let (min_table_v, ta, tb) = min_table.map_or((i128::MAX, 0, 0), |m| m);
    let table_text = if rows_past == 0 { "-".to_string() } else { min_table_v.to_string() };
    println!("HYBRIDCHECK_TABLE|rows={rows_total}|rows_past_cut={rows_past}|lumps_past_cut={}|bad_rows={bad_rows}|min_table_micro={table_text}|at_lump={ta},{tb}|secs={}|json=0", lumps_past.len(), t0.elapsed().as_secs());
    // 4. The upper side: the Rayleigh quotient of the trial vector, then the 9-dimensional space with the flats.
    let mut w = lat.scratch();
    let flats = lat.flats(lx, ly, &mut w);
    let mut c_sum = BigInt::from(0);
    let mut weights = Vec::new();
    for (u, size) in &flats {
        let mut v = u.clone();
        let got = row(&ctx, &mut v, &mut w);
        let t = BigInt::from(got.trial);
        c_sum += &t * &t * BigInt::from(*size);
        weights.push(size.to_string());
    }
    let flat_weight: u64 = flats.iter().map(|f| f.1).sum();
    let (rho, e9) = upper(&BigInt::from(sum.a), &BigInt::from(sum.b), &c_sum, nl3 as u128)?;
    println!("HYBRIDCHECK_UPPER|shift={shift}|A={}|B={}|C={c_sum}|flat_orbits={}|flat_weights={}|flat_sum={flat_weight}|lambda1_upper_micro={rho}|E9_upper_micro={e9}|json=0", sum.a, sum.b, flats.len(), weights.join(","));
    let cert = min_exact.min(min_table_v);
    let clean = same_class == 0 && outside_the_cut == 0 && not_positive == 0 && wrong.is_empty() && sum.missing == 0 && sum.sample_bad == 0 && bad_rows == 0 && flats.len() == 8 && flat_weight == 18;
    let above_cert = e9 >= BigInt::from(cert);
    let pass = clean && above_cert && cert == claim;
    println!(
        "HYBRIDCHECK|Lx={lx}|Ly={ly}|r={r}|cut={cut}|cert_micro={cert}|claim_micro={claim}|same={}|counts_and_rows_clean={}|upper_at_or_above_cert={}|sabotage={sabotage}|secs={}|verdict={}|json=0",
        u8::from(cert == claim),
        u8::from(clean),
        u8::from(above_cert),
        t0.elapsed().as_secs(),
        if pass { "PASS" } else { "FAIL" }
    );
    Ok(if pass { 0 } else { 2 })
}

/// lambda_1(H') <= A/B, and E_9 <= the top eigenvalue of [[f I_8, c], [c^T, A/B]], f = 3 nl, |c|^2 = C/B, both as the smallest micro value at or above the bound.
fn upper(a: &BigInt, b: &BigInt, c: &BigInt, nl3: u128) -> Result<(BigInt, BigInt), String> {
    let zero = BigInt::from(0);
    if *b <= zero {
        return Err("the trial vector is zero".into());
    }
    let micro = BigInt::from(MICRO);
    let rho = -((-(a * &micro)).div_floor_big(b));
    let flat = BigInt::from(nl3) * &micro;
    let holds = |u: &BigInt| *u >= rho && *u >= flat && (u - &flat) * (u * b - a * &micro) >= c * &micro * &micro;
    let low = if rho > flat { rho.clone() } else { flat.clone() };
    if holds(&low) {
        return Ok((rho, low));
    }
    let mut step = BigInt::from(1);
    while !holds(&(&low + &step)) {
        step *= 2;
    }
    let (mut no, mut yes) = (low.clone(), &low + &step);
    while &yes - &no > BigInt::from(1) {
        let mid: BigInt = (&yes + &no) / 2;
        if holds(&mid) {
            yes = mid;
        } else {
            no = mid;
        }
    }
    Ok((rho, yes))
}

trait FloorDiv {
    fn div_floor_big(&self, b: &BigInt) -> BigInt;
}

impl FloorDiv for BigInt {
    /// Floor division for a positive divisor.
    fn div_floor_big(&self, b: &BigInt) -> BigInt {
        let q: BigInt = self / b;
        let rem: BigInt = self - &q * b;
        if rem < BigInt::from(0) {
            q - 1
        } else {
            q
        }
    }
}

fn write_d(a: &[String]) -> Result<i32, String> {
    let (passa, lx, ly, cut, hybrid_path, out) = (&a[2], num::<usize>(&a[3])?, num::<usize>(&a[4])?, num::<usize>(&a[5])?, &a[6], &a[7]);
    let lat = Lattice::new(lx, ly)?;
    let h = read_hybrid(hybrid_path)?;
    let mut w = lat.scratch();
    let mut u = vec![0u8; lat.nl];
    let mut map: HashMap<u128, u128> = HashMap::with_capacity(h.reps.len());
    for rep in &h.reps {
        lat.decode_reader(rep.key, &mut u);
        map.insert(lat.canon(&u, &mut w), rep.value);
    }
    let shift = h.bits.saturating_sub(62);
    let mut input = BufReader::with_capacity(1 << 20, std::fs::File::open(passa).map_err(|e| format!("{passa}: {e}"))?);
    let mut output = BufWriter::with_capacity(1 << 20, std::fs::File::create(out).map_err(|e| format!("{out}: {e}"))?);
    let mut buf = [0u8; 16];
    let (mut rows, mut flats, mut low, mut high, mut missing, mut m_differs, mut floored) = (0u64, 0u64, 0u64, 0u64, 0u64, 0u64, 0u64);
    loop {
        match input.read_exact(&mut buf) {
            Ok(()) => {}
            Err(e) if e.kind() == std::io::ErrorKind::UnexpectedEof => break,
            Err(e) => return Err(e.to_string()),
        }
        let mut key = u64::from_le_bytes([buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7]]);
        let stored_m = u32::from_le_bytes([buf[12], buf[13], buf[14], buf[15]]) as usize;
        u.iter_mut().for_each(|v| *v = 0);
        for &l in &lat.free {
            u[l] = (key % 6) as u8;
            key /= 6;
        }
        let (x, y) = lat.lump(&u);
        let m = 2 * x + 3 * y;
        rows += 1;
        m_differs += u64::from(m != stored_m);
        let value = if m == 0 {
            flats += 1;
            0
        } else if m <= cut {
            low += 1;
            match map.get(&lat.canon(&u, &mut w)) {
                Some(v) => *v,
                None => {
                    missing += 1;
                    0
                }
            }
        } else {
            high += 1;
            match h.above.get(&(x, y)) {
                Some(v) => *v,
                None => {
                    missing += 1;
                    0
                }
            }
        };
        let mut d = (value >> shift) as i64;
        if m != 0 && d == 0 {
            floored += 1;
            d = 1;
        }
        output.write_all(&d.to_le_bytes()).map_err(|e| e.to_string())?;
    }
    output.flush().map_err(|e| e.to_string())?;
    let ok = missing == 0 && m_differs == 0;
    println!("HYBRIDCHECK_WRITE|Lx={lx}|Ly={ly}|cut={cut}|rows={rows}|flats={flats}|at_most_cut={low}|above_cut={high}|missing={missing}|m_differs={m_differs}|raised_to_1={floored}|shift={shift}|verdict={}|json=0", if ok { "PASS" } else { "FAIL" });
    Ok(if ok { 0 } else { 2 })
}

/// The moves of each representative that stay at 0 < M <= CUT, as indices into the representatives.
fn adjacency(lat: &Lattice, reps: &[Rep], index: &HashMap<u128, u32>, cut: usize, threads: usize) -> Result<(Vec<usize>, Vec<u32>), String> {
    let size = reps.len().div_ceil(threads.max(1)).max(1);
    let parts: Vec<Option<(Vec<u32>, Vec<u32>)>> = std::thread::scope(|sc| {
        let handles: Vec<_> = reps
            .chunks(size)
            .map(|part| {
                sc.spawn(move || {
                    let mut w = lat.scratch();
                    let mut u = vec![0u8; lat.nl];
                    let (mut counts, mut list) = (Vec::with_capacity(part.len()), Vec::new());
                    for rep in part {
                        lat.decode_reader(rep.key, &mut u);
                        let start = list.len();
                        for l in 0..lat.nl {
                            let keep = u[l];
                            for &t in &lat.trans {
                                u[l] = lat.mul[t as usize][keep as usize];
                                let (x, y) = lat.lump(&u);
                                let m = 2 * x + 3 * y;
                                if m > 0 && m <= cut {
                                    if let Some(j) = index.get(&lat.canon(&u, &mut w)) {
                                        list.push(*j);
                                    }
                                }
                            }
                            u[l] = keep;
                        }
                        counts.push((list.len() - start) as u32);
                    }
                    (counts, list)
                })
            })
            .collect();
        handles.into_iter().map(|j| j.join().ok()).collect()
    });
    let mut offs = Vec::with_capacity(reps.len() + 1);
    offs.push(0usize);
    let mut list = Vec::new();
    for part in parts {
        let (counts, chunk) = part.ok_or("a thread stopped")?;
        for c in counts {
            offs.push(offs[offs.len() - 1] + c as usize);
        }
        list.extend_from_slice(&chunk);
    }
    if offs.len() != reps.len() + 1 {
        return Err("the adjacency lost rows".into());
    }
    Ok((offs, list))
}

/// The smallest micro value at or above A/B for the vector t, from the adjacency.
fn rayleigh_micro(reps: &[Rep], diag: &[u128], offs: &[usize], list: &[u32], t: &[i128]) -> u128 {
    let (mut a, mut b) = (0i128, 0i128);
    for (i, rep) in reps.iter().enumerate() {
        let moved: i128 = list[offs[i]..offs[i + 1]].iter().map(|&j| t[j as usize]).sum();
        let w = i128::from(rep.weight);
        a += w * t[i] * (diag[i] as i128 * t[i] - moved);
        b += w * t[i] * t[i];
    }
    let big = BigInt::from(a) * BigInt::from(MICRO);
    let q: BigInt = big / BigInt::from(b);
    q.to_string().parse::<u128>().unwrap_or(0) + 1
}

fn upper_mode(a: &[String]) -> Result<i32, String> {
    let (lx, ly, r, cut) = (num::<usize>(&a[2])?, num::<usize>(&a[3])?, num::<u128>(&a[4])?, num::<usize>(&a[5])?);
    let (hybrid_path, sweeps, threads, psi_out) = (&a[6], num::<usize>(&a[7])?, num::<usize>(&a[8])?, &a[9]);
    let t0 = std::time::Instant::now();
    let lat = Lattice::new(lx, ly)?;
    let mut h = read_hybrid(hybrid_path)?;
    classify(&lat, &mut h.reps, threads);
    let reps = &h.reps;
    let mut index: HashMap<u128, u32> = HashMap::with_capacity(reps.len());
    for (i, rep) in reps.iter().enumerate() {
        index.insert(rep.canon, i as u32);
    }
    let (offs, list) = adjacency(&lat, reps, &index, cut, threads)?;
    let nl3 = (3 * lat.nl) as u128;
    let diag: Vec<u128> = reps.iter().map(|x| r * (2 * x.a as u128 + 3 * x.b as u128) + nl3).collect();
    let least_diag = diag.iter().copied().min().ok_or("no representatives")?;
    let start_shift = h.bits.saturating_sub(60);
    let mut cur: Vec<u128> = reps.iter().map(|x| (x.value >> start_shift).max(1)).collect();
    let mut next = cur.clone();
    let size = reps.len().div_ceil(threads.max(1)).max(1);
    let mut lambda = 0u128;
    println!("HYBRIDCHECK_FIT_START|Lx={lx}|Ly={ly}|r={r}|cut={cut}|reps={}|moves_kept={}|sweeps={sweeps}|secs={}|json=0", reps.len(), list.len(), t0.elapsed().as_secs());
    for sweep in 0..sweeps {
        if sweep % 5 == 0 {
            let t: Vec<i128> = cur.iter().map(|v| (*v >> 20) as i128).collect();
            lambda = rayleigh_micro(reps, &diag, &offs, &list, &t).min((least_diag - 1) * MICRO);
        }
        std::thread::scope(|sc| {
            for (n, part) in next.chunks_mut(size).enumerate() {
                let (cur, offs, list, diag) = (&cur, &offs, &list, &diag);
                sc.spawn(move || {
                    for (k, slot) in part.iter_mut().enumerate() {
                        let i = n * size + k;
                        let moved: u128 = list[offs[i]..offs[i + 1]].iter().map(|&j| cur[j as usize]).sum();
                        *slot = (cur[i] + moved * MICRO / (diag[i] * MICRO - lambda)) / 2;
                    }
                });
            }
        });
        std::mem::swap(&mut cur, &mut next);
        let top = cur.iter().copied().max().unwrap_or(1).max(1);
        let bits = 128 - top.leading_zeros();
        match bits.cmp(&60) {
            std::cmp::Ordering::Greater => cur.iter_mut().for_each(|v| *v >>= bits - 60),
            std::cmp::Ordering::Less => cur.iter_mut().for_each(|v| *v <<= 60 - bits),
            std::cmp::Ordering::Equal => {}
        }
    }
    // The vector is now fixed, as 40-bit integers, and A, B and C come from the definition of H.
    let t: Vec<u128> = cur.iter().map(|v| (*v >> 20).max(1)).collect();
    let mut map: HashMap<u128, u128> = HashMap::with_capacity(reps.len());
    for (rep, v) in reps.iter().zip(&t) {
        map.insert(rep.canon, *v);
    }
    let side = lat.p + 1;
    let above = vec![1u128; side * side];
    let ctx = Ctx { lat: &lat, map: &map, above: &above, side, cut, shift: 0, flat_d: 0 };
    let next_i = AtomicUsize::new(0);
    let total = Mutex::new((0i128, 0i128, 0u64));
    std::thread::scope(|sc| {
        for _ in 0..threads {
            sc.spawn(|| {
                let mut w = lat.scratch();
                let mut u = vec![0u8; lat.nl];
                let (mut sa, mut sb, mut missing) = (0i128, 0i128, 0u64);
                loop {
                    let start = next_i.fetch_add(CHUNK, Ordering::Relaxed);
                    if start >= reps.len() {
                        break;
                    }
                    for (rep, tv) in reps.iter().zip(&t).skip(start).take(CHUNK) {
                        lat.decode_reader(rep.key, &mut u);
                        let got = row(&ctx, &mut u, &mut w);
                        let d = (r * (2 * rep.a as u128 + 3 * rep.b as u128) + nl3) as i128;
                        let (ti, wi) = (*tv as i128, i128::from(rep.weight));
                        sa += wi * ti * (d * ti - got.trial as i128);
                        sb += wi * ti * ti;
                        missing += got.missing;
                    }
                }
                let mut all = total.lock().unwrap_or_else(|e| e.into_inner());
                all.0 += sa;
                all.1 += sb;
                all.2 += missing;
            });
        }
    });
    let (sa, sb, missing) = total.into_inner().unwrap_or_else(|e| e.into_inner());
    let mut w = lat.scratch();
    let flats = lat.flats(lx, ly, &mut w);
    let mut c_sum = BigInt::from(0);
    for (u, size) in &flats {
        let mut v = u.clone();
        let got = row(&ctx, &mut v, &mut w);
        let s = BigInt::from(got.trial);
        c_sum += &s * &s * BigInt::from(*size);
    }
    let (rho, e9) = upper(&BigInt::from(sa), &BigInt::from(sb), &c_sum, nl3)?;
    let mut out = BufWriter::with_capacity(1 << 20, std::fs::File::create(psi_out).map_err(|e| format!("{psi_out}: {e}"))?);
    for (rep, v) in reps.iter().zip(&t) {
        writeln!(out, "{}|{}|{}|{}", rep.key, 2 * u32::from(rep.a) + 3 * u32::from(rep.b), rep.weight, v).map_err(|e| e.to_string())?;
    }
    out.flush().map_err(|e| e.to_string())?;
    let ok = missing == 0 && flats.len() == 8;
    println!("HYBRIDCHECK_FIT|Lx={lx}|Ly={ly}|r={r}|cut={cut}|reps={}|sweeps={sweeps}|last_lambda_micro={lambda}|A={sa}|B={sb}|C={c_sum}|missing_moves={missing}|lambda1_upper_micro={rho}|E9_upper_micro={e9}|secs={}|verdict={}|json=0", reps.len(), t0.elapsed().as_secs(), if ok { "PASS" } else { "FAIL" });
    Ok(if ok { 0 } else { 2 })
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let r = match (a.get(1).map(String::as_str), a.len()) {
        (Some("check"), 10 | 11) => check(&a),
        (Some("write"), 8) => write_d(&a),
        (Some("upper"), 10) => upper_mode(&a),
        _ => Err("usage: hybridcheck check LX LY R CUT HYBRID TABLE CLAIM_MICRO THREADS [sabotage=NAME] | hybridcheck write PASSA LX LY CUT HYBRID D_OUT | hybridcheck upper LX LY R CUT HYBRID SWEEPS THREADS PSI_OUT".into()),
    };
    match r {
        Ok(code) => std::process::exit(code),
        Err(e) => {
            eprintln!("HYBRIDCHECK_ERROR|{e}|json=0");
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn shuffled(lat: &Lattice, seed: u64) -> Vec<u8> {
        let mut st = seed;
        (0..lat.nl)
            .map(|_| {
                st = st.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407);
                ((st >> 33) % 6) as u8
            })
            .collect()
    }

    #[test]
    fn the_counts_of_all_lumps_fill_the_whole_space() {
        for (lx, ly) in [(3, 3), (3, 4), (4, 4), (4, 5), (5, 5)] {
            let p: usize = lx * ly;
            let mut total = 0u128;
            for a in 0..=p {
                for b in 0..=p - a {
                    total += expected(p, a, b);
                }
            }
            assert_eq!(total, 6u128.pow(p as u32 + 1), "{lx}x{ly}");
            assert_eq!(expected(p, 0, 0), 18);
            assert_eq!(expected(p, 1, 0), 0);
        }
    }

    #[test]
    fn eight_flat_orbits_with_weights_summing_to_18() {
        for (lx, ly) in [(3, 3), (3, 4), (4, 4), (5, 5)] {
            let lat = Lattice::new(lx, ly).unwrap();
            let mut w = lat.scratch();
            let flats = lat.flats(lx, ly, &mut w);
            assert_eq!(flats.len(), 8);
            assert_eq!(flats.iter().map(|f| f.1).sum::<u64>(), 18);
            for (u, _) in &flats {
                assert_eq!(lat.lump(u), (0, 0));
            }
        }
    }

    #[test]
    fn symmetries_keep_every_plaquette_class_and_the_canonical_form() {
        for (lx, ly) in [(3, 4), (4, 4), (4, 5)] {
            let lat = Lattice::new(lx, ly).unwrap();
            let want = if lx == ly { 8 * lx * ly } else { 4 * lx * ly };
            assert_eq!(lat.syms.len(), want);
            let mut w = lat.scratch();
            for seed in 1..6u64 {
                let u = shuffled(&lat, seed);
                let key = lat.canon(&u, &mut w);
                let mut v = vec![0u8; lat.nl];
                for s in &lat.syms {
                    lat.image(&u, s, &mut v);
                    for q in 0..lat.p {
                        assert_eq!(lat.kind[lat.holonomy(&u, q) as usize], lat.kind[lat.holonomy(&v, s.plaq[q] as usize) as usize]);
                    }
                    assert_eq!(lat.canon(&v, &mut w), key);
                }
            }
        }
    }

    #[test]
    fn a_gauge_transformation_keeps_the_canonical_form() {
        let lat = Lattice::new(4, 4).unwrap();
        let mut w = lat.scratch();
        for seed in 1..40u64 {
            let u = shuffled(&lat, seed);
            let g = shuffled(&lat, seed + 1000);
            let v: Vec<u8> = (0..lat.nl).map(|l| lat.mul[lat.mul[g[lat.src[l]] as usize][u[l] as usize] as usize][lat.inv[g[lat.dst[l]] as usize] as usize]).collect();
            assert_eq!(lat.canon(&u, &mut w), lat.canon(&v, &mut w));
        }
    }

    #[test]
    fn gauge_fixing_leaves_the_tree_at_the_identity_and_keeps_the_lump() {
        let lat = Lattice::new(4, 5).unwrap();
        let mut w = lat.scratch();
        for seed in 1..20u64 {
            let u = shuffled(&lat, seed);
            lat.gauge_fix(&u, &mut w.p, &mut w.digits);
            let mut v = vec![0u8; lat.nl];
            for (d, &l) in w.digits.iter().zip(&lat.free) {
                v[l] = *d;
            }
            assert_eq!(lat.lump(&u), lat.lump(&v));
        }
    }

    #[test]
    fn the_classes_of_one_defect_on_4x4_hold_the_count_of_its_lump() {
        // One 3-cycle sits where two cuts cross, holding a pair that does not commute, and the 18 such pairs with their translates are all of the lump (0, 1).
        let lat = Lattice::new(4, 4).unwrap();
        let mut w = lat.scratch();
        let mut seen: HashMap<u128, u64> = HashMap::new();
        for hx in 0..6u8 {
            for hy in 0..6u8 {
                if lat.mul[hx as usize][hy as usize] == lat.mul[hy as usize][hx as usize] {
                    continue;
                }
                let mut u = vec![0u8; lat.nl];
                for y in 0..4 {
                    u[3 * 4 + y] = hx;
                }
                for x in 0..4 {
                    u[lat.p + x * 4 + 3] = hy;
                }
                assert_eq!(lat.lump(&u), (0, 1));
                let key = lat.canon(&u, &mut w);
                let size = lat.class_size(&u, &mut w);
                seen.insert(key, size);
            }
        }
        assert_eq!(u128::from(seen.values().sum::<u64>()), expected(16, 0, 1));
    }

    #[test]
    fn the_upper_bound_of_the_small_matrix() {
        // A/B = 5, f = 3, C/B = 8: (U - 3)(U - 5) = 8 has its top root at 7.
        let (rho, e9) = upper(&BigInt::from(50), &BigInt::from(10), &BigInt::from(80), 3).unwrap();
        assert_eq!(rho, BigInt::from(5_000_000));
        assert_eq!(e9, BigInt::from(7_000_000));
        // With no coupling the top is the larger of the two.
        let (_, e9) = upper(&BigInt::from(20), &BigInt::from(10), &BigInt::from(0), 3).unwrap();
        assert_eq!(e9, BigInt::from(3_000_000));
    }

    #[test]
    fn a_row_of_the_reader_decodes_into_its_cut() {
        let lat = Lattice::new(4, 4).unwrap();
        let mut u = vec![0u8; lat.nl];
        // The first row of tmp/hyb_4x4_r9_m10.hybrid.
        lat.decode_reader(3_461_144_431_725, &mut u);
        let (a, b) = lat.lump(&u);
        let m = 2 * a + 3 * b;
        assert!(m > 0 && m <= 10, "M = {m}");
    }
}
