//! Vacuum-ball compression of the Lx x Ly S3 gauge-orbit Hamiltonian.
//!
//! The 8 flat vacua (from the 18 commuting holonomy pairs) are the seeds; a
//! breadth-first search over single-link electric moves collects every gauge
//! orbit within K moves. H = JE E + JB M is then compressed onto the span of
//! those orbit states: since distinct orbit states are W-orthogonal, the
//! compression is H restricted to the ball's index set, still W-self-adjoint
//! (diagonal kept in full, off-diagonals kept only inside the ball).
//! Cauchy interlacing: its k-th eigenvalue is >= the k-th eigenvalue of H, so
//! ball energies are rigorous UPPER bounds on E0, E1, ... and decrease
//! monotonically as K grows. Their difference (the gap) is a measurement.
//!
//! Writes the standard exchange format (n / weights / magnetic / "i j z" for
//! j >= i, z = electric entry) so `cheb`, `jump` and `sturmrs` run unchanged.
//!
//! usage: ball LX LY K OUT_MATRIX
//! Output: one BALL line with the shell sizes, json=0. Integer-only, Rust 1.81.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::collections::{BTreeMap, HashMap};
use std::io::Write;
use torusl::{Lat, G, TRANS};

fn moves(g: &G, lat: &Lat, key: usize) -> Vec<usize> {
    let raw = lat.representative(&lat.decode(key));
    let nl = 2 * lat.n;
    let mut out = Vec::with_capacity(3 * nl);
    for e in 0..nl {
        for &t in &TRANS {
            let mut next = raw.clone();
            next[e] = g.m(t, next[e]);
            out.push(lat.canonical(g, &lat.gauge_fix(g, &next)));
        }
    }
    out
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 5 {
        eprintln!("usage: ball LX LY K OUT_MATRIX");
        std::process::exit(1);
    }
    let lx: usize = a[1].parse().unwrap_or(0);
    let ly: usize = a[2].parse().unwrap_or(0);
    let kmax: usize = a[3].parse().unwrap_or(0);
    if !(2..=4).contains(&lx) || !(2..=4).contains(&ly) || lx * ly > 9 || kmax > 8 {
        println!("BALL|error=bad_arguments|json=0");
        std::process::exit(1);
    }
    let t0 = std::time::Instant::now();
    let g = G::new();
    let lat = Lat::new(lx, ly);
    let nl = 2 * lat.n;
    // seeds: flat vacua from commuting holonomy pairs (seam links = A, B)
    let mut dist: HashMap<usize, usize> = HashMap::new();
    let mut order: Vec<usize> = Vec::new();
    for a_ in 0..6u8 {
        for b_ in 0..6u8 {
            if g.m(a_, b_) != g.m(b_, a_) {
                continue;
            }
            let mut links = vec![0u8; nl];
            for y in 0..ly {
                links[lat.site(lx - 1, y)] = a_;
            }
            for x in 0..lx {
                links[lat.n + lat.site(x, ly - 1)] = b_;
            }
            if lat.magnetic(&g, &links) != 0 {
                println!("BALL|error=seed_not_flat|json=0");
                std::process::exit(1);
            }
            let key = lat.canonical(&g, &lat.gauge_fix(&g, &links));
            if let std::collections::hash_map::Entry::Vacant(e) = dist.entry(key) {
                e.insert(0);
                order.push(key);
            }
        }
    }
    let seeds = order.len();
    let mut shells = vec![seeds];
    let mut frontier = order.clone();
    let mut rows: HashMap<usize, Vec<usize>> = HashMap::new();
    for d in 1..=kmax {
        let mut next = Vec::new();
        for &k in &frontier {
            let mv = moves(&g, &lat, k);
            for &j in &mv {
                if let std::collections::hash_map::Entry::Vacant(e) = dist.entry(j) {
                    e.insert(d);
                    next.push(j);
                }
            }
            rows.insert(k, mv);
        }
        shells.push(next.len());
        order.extend(next.iter().copied());
        frontier = next;
    }
    for &k in &frontier {
        rows.insert(k, moves(&g, &lat, k));
    }
    // index in a canonical order (sorted keys) so the file is deterministic
    let mut keys = order.clone();
    keys.sort_unstable();
    let idx: HashMap<usize, usize> = keys.iter().enumerate().map(|(i, &k)| (k, i)).collect();
    let n = keys.len();
    let mut weights = Vec::with_capacity(n);
    let mut mag = Vec::with_capacity(n);
    let mut erows: Vec<BTreeMap<usize, i64>> = Vec::with_capacity(n);
    let diag = 3 * i64::try_from(nl).unwrap_or(0);
    let mut dropped: u64 = 0;
    for &k in &keys {
        let q = lat.decode(k);
        weights.push(lat.weight(&g, &q));
        mag.push(lat.magnetic(&g, &lat.representative(&q)));
        let i = idx[&k];
        let mut row = BTreeMap::new();
        row.insert(i, diag);
        for j in &rows[&k] {
            match idx.get(j) {
                Some(&jj) => *row.entry(jj).or_insert(0) -= 1,
                None => dropped += 1,
            }
        }
        erows.push(row);
    }
    // W-self-adjointness of the compression (exact integers)
    let mut sym_ok = true;
    for (i, row) in erows.iter().enumerate() {
        for (&j, &v) in row {
            let back = erows[j].get(&i).copied().unwrap_or(0);
            if weights[i] * v != weights[j] * back {
                sym_ok = false;
            }
        }
    }
    let file = std::fs::File::create(&a[4]).unwrap_or_else(|e| {
        println!("BALL|error=write:{e}|json=0");
        std::process::exit(1)
    });
    let mut out = std::io::BufWriter::new(file);
    let join = |v: &[i64]| v.iter().map(i64::to_string).collect::<Vec<_>>().join(" ");
    let mut ok = writeln!(out, "{n}").is_ok();
    ok &= writeln!(out, "{}", join(&weights)).is_ok();
    ok &= writeln!(out, "{}", join(&mag)).is_ok();
    for (i, row) in erows.iter().enumerate() {
        for (&j, &v) in row {
            if j >= i && v != 0 {
                ok &= writeln!(out, "{i} {j} {v}").is_ok();
            }
        }
    }
    ok &= out.flush().is_ok();
    let nnz: usize = erows.iter().map(BTreeMap::len).sum();
    println!(
        "BALL|L={lx}x{ly}|K={kmax}|seeds={seeds}|shells={}|states={n}|nnz={nnz}|moves_leaving_ball={dropped}|w_self_adjoint={}|write={}|ms={}|kind=COMPRESSION_UPPER_BOUNDS|json=0",
        shells.iter().map(usize::to_string).collect::<Vec<_>>().join(","),
        if sym_ok { "PASS" } else { "FAIL" },
        if ok { "ok" } else { "failed" },
        t0.elapsed().as_millis()
    );
    if !sym_ok || !ok {
        std::process::exit(2);
    }
}
