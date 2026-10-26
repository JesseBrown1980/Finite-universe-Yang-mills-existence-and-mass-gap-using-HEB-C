//! Streaming zero-momentum sector pass (Host8 / SG-RAM method): one sequential
//! pass over one residue class of the gauge-fixed configuration space, with no
//! tables in RAM. Integer-only, Rust 1.81, json=0.
//!
//! The non-tree links of a spanning-tree gauge form a tuple q in S3^k, indexed
//! 0..6^k. The pass streams the ids id = RESIDUE (mod MODULUS), constant
//! memory, and for each id:
//!   1. gauge orbit: q is kept only if it is the least member of its global
//!      conjugation class (one tuple per gauge orbit);
//!   2. Burnside / character data: for every symmetry op g of
//!      G = translations x C2v (|G| = 4 Lx Ly) it records whether g fixes the
//!      gauge orbit, so  sum over g of chi_s(g) Fix(g) / |G|  gives every
//!      sector's dimension independently of the representative count;
//!   3. sector row: if q is the least key of its G-orbit, it is the sector
//!      representative. Sector s keeps it when chi_s is trivial on its
//!      stabiliser. Its row is generated on the fly: 3 transpositions on each
//!      link, each target canonicalised under G and signed by chi_s of the
//!      minimising op (a target with two minimising ops of different sign is
//!      outside the sector);
//!   4. diagonal-dominance core: the row is a core row at threshold t when
//!      1000(JE E_ii + JB M_ii) - t - 1000 JE sum_{j != i} |E_ij| <= 0
//!      (the `ddcore` test, row scaled by its weight).
//!
//! Residue classes are independent and evenly loaded (representatives are least
//! keys, so contiguous ranges would not be), so the space splits into GitRAM
//! cells, one class each, and the per-class records add up.
//!
//! WORKERS=n splits the range over n threads (records identical for any n).
//!
//! usage: ymstream LX LY JE JB T1[,T2,...] RESIDUE MODULUS
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use torusl::{Lat, G, TRANS};

struct Ops {
    /// per op: destination link and inversion flag for every source link
    dest: Vec<Vec<(usize, bool)>>,
    /// per op: (Sx, Sy) reflection content: p = 0 e, 1 sx, 2 sy, 3 c2
    point: Vec<u8>,
}

fn build_ops(lat: &Lat) -> Ops {
    let (lx, ly, n) = (lat.lx, lat.ly, lat.n);
    let mut dest = Vec::new();
    let mut point = Vec::new();
    for p in 0..4u8 {
        for tx in 0..lx {
            for ty in 0..ly {
                let fx = p == 1 || p == 3;
                let fy = p == 2 || p == 3;
                let mut d = vec![(0usize, false); 2 * n];
                for x in 0..lx {
                    for y in 0..ly {
                        let s = lat.site(x, y);
                        let px = if fx { (lx - x) % lx } else { x };
                        let py = if fy { (ly - y) % ly } else { y };
                        let dxx = if fx { (px + lx - 1) % lx } else { px };
                        let dyy = if fy { (py + ly - 1) % ly } else { py };
                        d[s] = (lat.site((dxx + tx) % lx, (py + ty) % ly), fx);
                        d[n + s] = (n + lat.site((px + tx) % lx, (dyy + ty) % ly), fy);
                    }
                }
                dest.push(d);
                point.push(p);
            }
        }
    }
    Ops { dest, point }
}

struct Ctx<'a> {
    g: &'a G,
    lat: &'a Lat,
    ops: Ops,
    pow6: Vec<u64>,
    conj: [[u8; 6]; 6], // conj[c][x] = c x c^-1
}

impl Ctx<'_> {
    fn key(&self, links: &[u8], h: &mut [u8], q: &mut [u8]) -> u64 {
        // gauge fix along the tree, then least conjugate
        let g = self.g;
        let lat = self.lat;
        h[0] = 0;
        for &e in &lat.tree {
            let (t, hd) = lat.edges[e];
            h[hd] = g.m(h[t], links[e]);
        }
        for (i, &e) in lat.free.iter().enumerate() {
            let (t, hd) = lat.edges[e];
            q[i] = g.m(g.m(h[t], links[e]), g.i(h[hd]));
        }
        let mut best = u64::MAX;
        for c in 0..6 {
            let row = &self.conj[c];
            let mut id = 0u64;
            for (i, &v) in q.iter().enumerate() {
                id += u64::from(row[v as usize]) * self.pow6[i];
            }
            best = best.min(id);
        }
        best
    }
    fn apply(&self, op: usize, u: &[u8], out: &mut [u8]) {
        for (l, &(d, inv)) in self.ops.dest[op].iter().enumerate() {
            out[d] = if inv { self.g.i(u[l]) } else { u[l] };
        }
    }
}

#[derive(Clone)]
struct Acc {
    gauge_orbits: u64,
    fix: Vec<i64>,
    reps: [u64; 4],
    flat: [u64; 4],
    core: Vec<[u64; 4]>,
    nonpos: Vec<[u64; 4]>,
    row_hash: [u64; 4],
}

#[allow(clippy::too_many_arguments)]
fn scan(ctx: &Ctx, residue: u64, modulus: u64, total: u64, ts: &[i64], je: i64, jb: i64) -> Acc {
    let (g, lat) = (ctx.g, ctx.lat);
    let k = lat.free.len();
    let nl = 2 * lat.n;
    let nops = ctx.ops.dest.len();
    let mut h = vec![0u8; lat.n];
    let mut qb = vec![0u8; k];
    let mut buf = vec![0u8; nl];
    let mut buf2 = vec![0u8; nl];
    let mut move_links = vec![0u8; nl];
    let mut q = vec![0u8; k];
    let mut stab_chi = [true; 4];
    let mut keys = vec![0u64; nops];
    let mut acc = Acc { gauge_orbits: 0, fix: vec![0i64; nops], reps: [0; 4], flat: [0; 4], core: vec![[0; 4]; ts.len()], nonpos: vec![[0; 4]; ts.len()], row_hash: [0; 4] };
    for id in (residue..total).step_by(usize::try_from(modulus).unwrap_or(1)) {
        let mut rest = id;
        for v in q.iter_mut() {
            *v = (rest % 6) as u8;
            rest /= 6;
        }
        // 1. least member of its conjugation class
        let mut is_min = true;
        for c in 1..6 {
            let row = &ctx.conj[c];
            let mut cid = 0u64;
            for (i, &v) in q.iter().enumerate() {
                cid += u64::from(row[v as usize]) * ctx.pow6[i];
            }
            if cid < id {
                is_min = false;
                break;
            }
        }
        if !is_min {
            continue;
        }
        acc.gauge_orbits += 1;
        let raw = lat.representative(&q);
        // 2. images under every op
        let mut is_rep = true;
        for (o, slot) in keys.iter_mut().enumerate() {
            ctx.apply(o, &raw, &mut buf);
            *slot = ctx.key(&buf, &mut h, &mut qb);
            match (*slot).cmp(&id) {
                std::cmp::Ordering::Equal => acc.fix[o] += 1,
                std::cmp::Ordering::Less => is_rep = false,
                std::cmp::Ordering::Greater => {}
            }
        }
        if !is_rep {
            continue;
        }
        // 3. sector membership: chi trivial on the stabiliser
        for (s, &(sx, sy)) in SECTORS.iter().enumerate() {
            stab_chi[s] = (0..nops).all(|o| keys[o] != id || chi(ctx.ops.point[o], sx, sy) == 1);
        }
        if !stab_chi.iter().any(|&b| b) {
            continue;
        }
        let mag = lat.magnetic(g, &raw);
        // row: for each move, the target's least key and the chi of its minimising ops
        // entries[s] accumulates (target key, signed coefficient)
        let mut entries: [Vec<(u64, i64)>; 4] = [Vec::new(), Vec::new(), Vec::new(), Vec::new()];
        for l in 0..nl {
            for &t in &TRANS {
                move_links.copy_from_slice(&raw);
                move_links[l] = g.m(t, move_links[l]);
                let mut best = u64::MAX;
                let mut sgn = [0i64; 4]; // 0 unset, +-1, 2 conflict
                for o in 0..nops {
                    ctx.apply(o, &move_links, &mut buf2);
                    let kk = ctx.key(&buf2, &mut h, &mut qb);
                    match kk.cmp(&best) {
                        std::cmp::Ordering::Less => {
                            best = kk;
                            for (s, &(sx, sy)) in SECTORS.iter().enumerate() {
                                sgn[s] = chi(ctx.ops.point[o], sx, sy);
                            }
                        }
                        std::cmp::Ordering::Equal => {
                            for (s, &(sx, sy)) in SECTORS.iter().enumerate() {
                                if sgn[s] != chi(ctx.ops.point[o], sx, sy) {
                                    sgn[s] = 2;
                                }
                            }
                        }
                        std::cmp::Ordering::Greater => {}
                    }
                }
                for s in 0..4 {
                    if stab_chi[s] && sgn[s] != 2 {
                        entries[s].push((best, sgn[s]));
                    }
                }
            }
        }
        for s in 0..4 {
            if !stab_chi[s] {
                continue;
            }
            acc.reps[s] += 1;
            if mag == 0 {
                acc.flat[s] += 1;
            }
            let e = &mut entries[s];
            e.sort_unstable();
            // E row: diagonal 3 nl minus moves into self; off-diagonal minus signed moves
            let mut diag_e = i64::try_from(3 * nl).unwrap_or(0);
            let mut off_abs = 0i64;
            let mut i = 0;
            let mut hsh = id.wrapping_mul(0x9E37_79B9_7F4A_7C15);
            while i < e.len() {
                let kk = e[i].0;
                let mut c = 0i64;
                while i < e.len() && e[i].0 == kk {
                    c += e[i].1;
                    i += 1;
                }
                if kk == id {
                    diag_e -= c;
                } else {
                    off_abs += c.abs();
                }
                hsh = hsh.rotate_left(7) ^ kk.wrapping_mul(31).wrapping_add(c.unsigned_abs());
            }
            acc.row_hash[s] ^= hsh;
            for (ti, &t) in ts.iter().enumerate() {
                let d = 1000 * (je * diag_e + jb * mag) - t;
                if d <= 0 {
                    acc.nonpos[ti][s] += 1;
                }
                if d - 1000 * je * off_abs <= 0 {
                    acc.core[ti][s] += 1;
                }
            }
        }
    }
    acc
}

fn chi(p: u8, sx: i64, sy: i64) -> i64 {
    match p {
        0 => 1,
        1 => sx,
        2 => sy,
        _ => sx * sy,
    }
}

const SECTORS: [(i64, i64); 4] = [(1, 1), (1, -1), (-1, 1), (-1, -1)];

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 8 {
        eprintln!("usage: ymstream LX LY JE JB T1[,T2,...] RESIDUE MODULUS");
        std::process::exit(1);
    }
    let lx: usize = a[1].parse().unwrap_or(0);
    let ly: usize = a[2].parse().unwrap_or(0);
    let je: i64 = a[3].parse().unwrap_or(0);
    let jb: i64 = a[4].parse().unwrap_or(0);
    let ts: Vec<i64> = a[5].split(',').filter_map(|v| v.parse().ok()).collect();
    if !(2..=4).contains(&lx) || !(2..=4).contains(&ly) || lx * ly > 12 || ts.is_empty() {
        println!("YMSTREAM|error=bad_arguments|json=0");
        std::process::exit(1);
    }
    let t0 = std::time::Instant::now();
    let g = G::new();
    let lat = Lat::new(lx, ly);
    let k = lat.free.len();
    let total = 6u64.pow(u32::try_from(k).unwrap_or(0));
    let residue: u64 = a[6].parse().unwrap_or(0);
    let modulus: u64 = a[7].parse().unwrap_or(0);
    if modulus == 0 || residue >= modulus {
        println!("YMSTREAM|error=bad_residue_class|json=0");
        std::process::exit(1);
    }
    let mut conj = [[0u8; 6]; 6];
    for c in 0..6u8 {
        for x in 0..6u8 {
            conj[c as usize][x as usize] = g.m(g.m(c, x), g.i(c));
        }
    }
    let ctx = Ctx { g: &g, lat: &lat, ops: build_ops(&lat), pow6: (0..k).map(|i| 6u64.pow(u32::try_from(i).unwrap_or(0))).collect(), conj };
    let nops = ctx.ops.dest.len();
    let workers: u64 = std::env::var("WORKERS").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
    let parts: Vec<Acc> = std::thread::scope(|sc| {
        let hs: Vec<_> = (0..workers)
            .map(|w| {
                // thread w: ids = residue + w*modulus  (mod modulus*workers)
                let (ctx, ts) = (&ctx, &ts);
                sc.spawn(move || scan(ctx, residue + w * modulus, modulus * workers, total, ts, je, jb))
            })
            .collect();
        hs.into_iter().map(|h| h.join().unwrap_or_else(|_| std::process::exit(2))).collect()
    });
    let mut gauge_orbits = 0u64;
    let mut fix = vec![0i64; nops];
    let mut reps = [0u64; 4];
    let mut flat = [0u64; 4];
    let mut core = vec![[0u64; 4]; ts.len()];
    let mut nonpos = vec![[0u64; 4]; ts.len()];
    let mut row_hash = [0u64; 4];
    for p in &parts {
        gauge_orbits += p.gauge_orbits;
        for (f, pf) in fix.iter_mut().zip(p.fix.iter()) {
            *f += pf;
        }
        for s in 0..4 {
            reps[s] += p.reps[s];
            flat[s] += p.flat[s];
            row_hash[s] ^= p.row_hash[s];
            for ti in 0..ts.len() {
                core[ti][s] += p.core[ti][s];
                nonpos[ti][s] += p.nonpos[ti][s];
            }
        }
    }
    let gsize = i64::try_from(nops).unwrap_or(1);
    let fix_join = fix.iter().map(i64::to_string).collect::<Vec<_>>().join(",");
    println!(
        "YMSTREAM|L={lx}x{ly}|JE={je}|JB={jb}|class={residue}/{modulus}|space={total}|gauge_orbits={gauge_orbits}|group={gsize}|fix={fix_join}|ms={}|json=0",
        t0.elapsed().as_millis()
    );
    for (s, &(sx, sy)) in SECTORS.iter().enumerate() {
        let cf: i64 = (0..nops).map(|o| chi(ctx.ops.point[o], sx, sy) * fix[o]).sum();
        let cores = ts.iter().enumerate().map(|(ti, t)| format!("{t}:{}:{}", core[ti][s], nonpos[ti][s])).collect::<Vec<_>>().join(",");
        println!(
            "YMSTREAM_SECTOR|L={lx}x{ly}|sector=Sx{}Sy{}|class={residue}/{modulus}|reps={}|flat_states={}|character_sum={cf}|core_t:rows:nonpos={cores}|row_hash={:016x}|json=0",
            if sx > 0 { "+" } else { "-" },
            if sy > 0 { "+" } else { "-" },
            reps[s],
            flat[s],
            row_hash[s]
        );
    }
}
