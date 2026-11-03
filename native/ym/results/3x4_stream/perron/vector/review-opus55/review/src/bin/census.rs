//! Exhaustive census of every gauge-fixed configuration of an Lx x Ly torus: 6^(P+1) configurations, one or more for each gauge orbit.
//! It collects the signature (a, b, n vector) of each, checks each against my constraints, and gives the exact minimum ratio over real orbits for a vector.
//!
//!   census LX LY R_NUM R_DEN GFILE THREADS [conj]
//! With `conj`, the first free link runs only over one element of each conjugacy class, with its class size as a multiplicity. Conjugation is a bijection that keeps every signature.
//!
//! Integer only, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use review::{adj_limit, ceil_two_root, micro, El, Group, Torus, Vector, NPAT, P_CC, P_EC, P_ET, P_TC, P_TTD, P_TTS, RULE};
use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

const TABLE_BITS: u32 = 20;

type WorkerOut = (Table, Vec<Vec<El>>, u64, u64, u64, u64);

struct Table {
    keys: Vec<u64>,
    vals: Vec<u64>,
    used: usize,
}

impl Table {
    fn new() -> Table {
        Table { keys: vec![0; 1 << TABLE_BITS], vals: vec![0; 1 << TABLE_BITS], used: 0 }
    }

    #[inline]
    fn add(&mut self, key: u64, mult: u64) {
        let mask = (1usize << TABLE_BITS) - 1;
        let mut i = (key.wrapping_mul(0x9E37_79B9_7F4A_7C15) >> (64 - TABLE_BITS)) as usize;
        loop {
            let k = self.keys[i];
            if k == key {
                self.vals[i] += mult;
                return;
            }
            if k == 0 {
                self.keys[i] = key;
                self.vals[i] = mult;
                self.used += 1;
                assert!(self.used * 2 < (1 << TABLE_BITS), "signature table is full");
                return;
            }
            i = (i + 1) & mask;
        }
    }
}

struct Work<'a> {
    t: &'a Torus,
    g: &'a Group,
    free: &'a [usize],
    near: &'a [Vec<usize>],
    u: Vec<El>,
    cls: Vec<u8>,
    pat: Vec<u8>,
    n: [i32; NPAT],
    a: i32,
    b: i32,
    table: Table,
    flats: Vec<Vec<El>>,
    leaves: u64,
    mult: u64,
    flat_weighted: u64,
    tick: u64,
    frame_checks: u64,
    frame_bad: u64,
}

impl Work<'_> {
    #[inline]
    fn pattern_quick(&self, l: usize) -> u8 {
        let [p0, p1] = self.t.link_plaq[l];
        let (c0, c1) = (self.cls[p0], self.cls[p1]);
        match (c0.min(c1), c0.max(c1)) {
            (0, 0) => 0,
            (0, 1) => P_ET as u8,
            (0, 2) => P_EC as u8,
            (1, 1) => {
                let (x, y) = self.t.frame(self.g, &self.u, l);
                if x == y {
                    P_TTS as u8
                } else {
                    P_TTD as u8
                }
            }
            (1, 2) => P_TC as u8,
            _ => P_CC as u8,
        }
    }

    #[inline]
    fn set(&mut self, l: usize, e: El) {
        self.u[l] = e;
        let t = self.t;
        for &p in &t.link_plaq[l] {
            let c = self.g.class[t.hol(self.g, &self.u, p) as usize];
            let o = self.cls[p];
            if c != o {
                match o {
                    1 => self.a -= 1,
                    2 => self.b -= 1,
                    _ => {}
                }
                match c {
                    1 => self.a += 1,
                    2 => self.b += 1,
                    _ => {}
                }
                self.cls[p] = c;
            }
        }
        let near = self.near;
        for &k in &near[l] {
            let z = self.pattern_quick(k);
            let o = self.pat[k];
            if z != o {
                self.n[o as usize] -= 1;
                self.n[z as usize] += 1;
                self.pat[k] = z;
            }
        }
    }

    fn leaf(&mut self) {
        self.leaves += self.mult;
        let mut key: u64 = (self.a as u64) | ((self.b as u64) << 6);
        for (i, c) in self.n.iter().enumerate() {
            key |= (*c as u64) << (12 + 6 * i);
        }
        self.table.add(key + 1, self.mult);
        if self.a == 0 && self.b == 0 {
            self.flat_weighted += self.mult;
            self.flats.push(self.u.clone());
        }
        self.tick += 1;
        if self.tick & 0xF_FFFF == 0 {
            self.frame_checks += 1;
            if self.t.counts(self.g, &self.u).iter().zip(self.n.iter()).any(|(x, y)| *x as i32 != *y) || self.t.lump_full(self.g, &self.u) != (self.a as u32, self.b as u32) {
                self.frame_bad += 1;
            }
        }
    }

    fn dfs(&mut self, depth: usize) {
        if depth == self.free.len() {
            self.leaf();
            return;
        }
        let l = self.free[depth];
        for e in 0..6u8 {
            self.set(l, e);
            self.dfs(depth + 1);
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (lx, ly): (usize, usize) = (args[1].parse().expect("lx"), args[2].parse().expect("ly"));
    let (r_num, r_den): (i128, i128) = (args[3].parse().expect("r"), args[4].parse().expect("r"));
    let v = Vector::load(&args[5]);
    let threads: usize = args[6].parse().expect("threads");
    let conj_mode = args.iter().any(|x| x == "conj");
    let planar = args.iter().any(|x| x == "planar");
    assert!(threads <= 3, "at most 3 threads by the brief");
    let t = Torus::new(lx, ly);
    let g = Group::new();
    // Comb tree: x-links in every row but the last column, y-links on column 0 but the last row. The rest are free.
    let mut is_tree = vec![false; t.nl];
    for y in 0..ly {
        for x in 0..lx - 1 {
            is_tree[2 * (x + lx * y)] = true;
        }
    }
    for y in 0..ly - 1 {
        is_tree[2 * (lx * y) + 1] = true;
    }
    assert_eq!(is_tree.iter().filter(|x| **x).count(), t.sites - 1);
    let free: Vec<usize> = (0..t.nl).filter(|l| !is_tree[*l]).collect();
    assert_eq!(free.len(), t.sites + 1);
    // Neighbours of each link.
    let mut plaq_links = vec![Vec::new(); t.sites];
    for l in 0..t.nl {
        for &p in &t.link_plaq[l] {
            plaq_links[p].push(l);
        }
    }
    let mut near: Vec<Vec<usize>> = Vec::with_capacity(t.nl);
    for l in 0..t.nl {
        let mut w: Vec<usize> = Vec::new();
        for &p in &t.link_plaq[l] {
            for &k in &plaq_links[p] {
                if !w.contains(&k) {
                    w.push(k);
                }
            }
        }
        near.push(w);
    }
    let start = Instant::now();
    let prefix_len = 2usize;
    let tasks = if conj_mode { 18usize } else { 36usize };
    let next = AtomicUsize::new(0);
    let mut results: Vec<WorkerOut> = Vec::new();
    std::thread::scope(|sc| {
        let mut hs = Vec::new();
        for _ in 0..threads {
            let (t, g, free, near, next) = (&t, &g, &free, &near, &next);
            hs.push(sc.spawn(move || {
                let mut w = Work {
                    t,
                    g,
                    free,
                    near,
                    u: vec![0; t.nl],
                    cls: vec![0; t.sites],
                    pat: vec![0; t.nl],
                    n: {
                        let mut n = [0; NPAT];
                        n[0] = t.nl as i32;
                        n
                    },
                    a: 0,
                    b: 0,
                    table: Table::new(),
                    flats: Vec::new(),
                    leaves: 0,
                    mult: 1,
                    flat_weighted: 0,
                    tick: 0,
                    frame_checks: 0,
                    frame_bad: 0,
                };
                loop {
                    let task = next.fetch_add(1, Ordering::Relaxed);
                    if task >= tasks {
                        break;
                    }
                    if conj_mode {
                        // Identity, a 3-cycle, a transposition, each standing for its class.
                        let (first, mult) = [(0u8, 1u64), (1, 2), (3, 3)][task / 6];
                        assert_eq!(g.class[first as usize], [0u8, 2, 1][task / 6]);
                        w.mult = mult;
                        w.set(free[0], first);
                    } else {
                        w.set(free[0], (task / 6) as u8);
                    }
                    w.set(free[1], (task % 6) as u8);
                    w.dfs(prefix_len);
                }
                (w.table, w.flats, w.leaves, w.frame_checks, w.frame_bad, w.flat_weighted)
            }));
        }
        for h in hs {
            results.push(h.join().expect("worker"));
        }
    });
    let mut merged: HashMap<u64, u64> = HashMap::new();
    let mut flats: Vec<Vec<El>> = Vec::new();
    let (mut leaves, mut fc, mut fb, mut fw) = (0u64, 0u64, 0u64, 0u64);
    for (table, fl, lv, c, b, w) in results {
        for (k, val) in table.keys.iter().zip(table.vals.iter()) {
            if *k != 0 {
                *merged.entry(*k - 1).or_insert(0) += *val;
            }
        }
        flats.extend(fl);
        leaves += lv;
        fc += c;
        fb += b;
        fw += w;
    }
    let expected = 6u64.pow(free.len() as u32);
    assert_eq!(leaves, expected);
    // Flat classes.
    let mut classes: Vec<Vec<El>> = Vec::new();
    for f in &flats {
        let image: Vec<Vec<El>> = (0..6).map(|c| f.iter().map(|e| g.conj[c][*e as usize]).collect()).collect();
        let m = image.iter().min().expect("six").clone();
        if !classes.contains(&m) {
            classes.push(m);
        }
    }
    println!("CENSUS|Lx={lx}|Ly={ly}|configs={leaves}|expected={expected}|signatures={}|flat_gauge_fixed={fw}|flat_classes={}|frame_audits={fc}|frame_bad={fb}|seconds={}|json=0", merged.len(), classes.len(), start.elapsed().as_secs());
    // Each signature: inside my constraints, and its exact ratio.
    let (ul, uy) = (lx as u32, ly as u32);
    let p = (lx * ly) as u32;
    let limit = |s: u32| if planar { 2 * s - ceil_two_root(s) } else { adj_limit(s, ul, uy) };
    let mut outside = 0u64;
    let mut odd_a = 0u64;
    let mut below_m3 = 0u64;
    let mut best: Option<(i128, i128, u32, u32, [i32; NPAT])> = None;
    let mut per_lump: HashMap<(u32, u32), (i128, u64, u64)> = HashMap::new();
    for (key, count) in &merged {
        let a = (key & 63) as u32;
        let b = ((key >> 6) & 63) as u32;
        let mut n = [0i32; NPAT];
        for (i, c) in n.iter_mut().enumerate() {
            *c = ((key >> (12 + 6 * i)) & 63) as i32;
        }
        let (tt, cc, tc) = ((n[P_TTS] + n[P_TTD]) as u32, n[P_CC] as u32, n[P_TC] as u32);
        let ok = 4 * a as i32 == n[P_ET] + n[P_TC] + 2 * (n[P_TTS] + n[P_TTD])
            && 4 * b as i32 == n[P_EC] + n[P_TC] + 2 * n[P_CC]
            && n.iter().sum::<i32>() == t.nl as i32
            && tt <= limit(a)
            && cc <= limit(b)
            && tt + tc + cc <= limit(a + b);
        if !ok {
            outside += 1;
            println!("OUTSIDE|a={a}|b={b}|n={n:?}|count={count}|json=0");
        }
        if a % 2 != 0 {
            odd_a += 1;
        }
        let e = per_lump.entry((a, b)).or_insert((i128::MAX, 0, 0));
        e.1 += *count;
        e.2 += 1;
        if a == 0 && b == 0 {
            continue;
        }
        if 2 * a + 3 * b < 3 {
            below_m3 += 1;
        }
        let d0 = v.d(a, b);
        let mut sum: i128 = 0;
        for (pat, moves) in RULE.iter().enumerate() {
            if n[pat] == 0 {
                continue;
            }
            for &(da, db, c) in *moves {
                let (ta, tb) = (a.wrapping_add_signed(da), b.wrapping_add_signed(db));
                sum += i128::from(n[pat]) * i128::from(c) * (d0 - v.d(ta, tb));
            }
        }
        let num = r_num * i128::from(2 * a + 3 * b) * d0 + r_den * sum;
        let den = r_den * d0;
        let m = micro(num, den);
        if m < e.0 {
            e.0 = m;
        }
        let better = match &best {
            None => true,
            Some(x) => m < micro(x.0, x.1),
        };
        if better {
            best = Some((num, den, a, b, n));
        }
    }
    let mut lumps: Vec<_> = per_lump.iter().collect();
    lumps.sort();
    for ((a, b), (m, cnt, sigs)) in lumps {
        println!("LUMP|a={a}|b={b}|configs={cnt}|signatures={sigs}|min_ratio_micro={}|json=0", if *m == i128::MAX { -1 } else { *m });
    }
    let total_lumps = (0..=p).step_by(2).map(|a| p - a + 1).sum::<u32>();
    let (num, den, a, b, n) = best.expect("a non-flat orbit exists");
    println!("CENSUS_RESULT|outside_my_constraints={outside}|odd_a={odd_a}|nonflat_below_M3={below_m3}|lumps_realized={}/{total_lumps}|real_min_micro={}|at_a={a}|at_b={b}|n={n:?}|json=0", per_lump.len(), micro(num, den));
    if outside != 0 || odd_a != 0 || below_m3 != 0 || fb != 0 {
        std::process::exit(2);
    }
}
