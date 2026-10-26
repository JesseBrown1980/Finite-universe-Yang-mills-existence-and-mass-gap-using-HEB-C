//! Matrix-free application of the Lx x Ly S3 gauge-orbit Hamiltonian
//! H = JE*E + JB*M (same construction as `torusl`), for lattices whose full
//! matrix is too large to store (3x3: 10,097,891 states). Rows are generated
//! on demand from the orbit representatives; no matrix is allocated.
//! Exact integers (i128, overflow-checked), Rust 1.81, no floating point.
//!
//! Starting from the trivial flat vacuum (all links = identity, amplitude 1),
//! applies H STEPS times and reports per step, in encoding-independent form:
//!   support   number of nonzero gauge-orbit amplitudes
//!   norm_w    sum_i w_i v_i^2        (w_i = conjugation-orbit size)
//!   sum_w     sum_i w_i v_i
//!   sa_check  <v_{k+1}, v_{k-1}>_W == <v_k, v_k>_W  (exact W-self-adjointness)
//!
//! usage: onfly LX LY JE JB STEPS
//! Output: one line per step, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::collections::{BTreeSet, HashMap};
use torusl::{Lat, G, TRANS};

struct Ctx {
    g: G,
    lat: Lat,
    je: i128,
    jb: i128,
    nl: usize,
}

impl Ctx {
    /// row i of H: (column key, coefficient), from the representative of key
    fn row(&self, key: usize) -> Vec<(usize, i128)> {
        let q = self.lat.decode(key);
        let raw = self.lat.representative(&q);
        let mut out: HashMap<usize, i128> = HashMap::new();
        let diag = self.je * i128::try_from(3 * self.nl).unwrap_or(0) + self.jb * i128::from(self.lat.magnetic(&self.g, &raw));
        *out.entry(key).or_insert(0) += diag;
        for e in 0..self.nl {
            for &t in &TRANS {
                let mut next = raw.clone();
                next[e] = self.g.m(t, next[e]);
                let j = self.lat.canonical(&self.g, &self.lat.gauge_fix(&self.g, &next));
                *out.entry(j).or_insert(0) -= self.je;
            }
        }
        out.into_iter().filter(|&(_, c)| c != 0).collect()
    }
    fn neighbours(&self, key: usize) -> Vec<usize> {
        self.row(key).into_iter().map(|(j, _)| j).collect()
    }
    fn weight(&self, key: usize) -> i128 {
        i128::from(self.lat.weight(&self.g, &self.lat.decode(key)))
    }
}

fn wdot(ctx: &Ctx, wcache: &mut HashMap<usize, i128>, a: &HashMap<usize, i128>, b: &HashMap<usize, i128>) -> Option<i128> {
    let mut s = 0i128;
    for (k, x) in a {
        if let Some(y) = b.get(k) {
            let w = *wcache.entry(*k).or_insert_with(|| ctx.weight(*k));
            s = s.checked_add(w.checked_mul(*x)?.checked_mul(*y)?)?;
        }
    }
    Some(s)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 6 {
        eprintln!("usage: onfly LX LY JE JB STEPS");
        std::process::exit(1);
    }
    let p = |i: usize| a[i].parse::<i128>().unwrap_or(-1);
    let (lx, ly, je, jb, steps) = (p(1), p(2), p(3), p(4), p(5));
    if !(2..=4).contains(&lx) || !(2..=4).contains(&ly) || lx * ly > 9 || je < 0 || jb < 0 || !(1..=8).contains(&steps) {
        println!("ONFLY|error=bad_arguments|json=0");
        std::process::exit(1);
    }
    let t0 = std::time::Instant::now();
    let lat = Lat::new(usize::try_from(lx).unwrap_or(2), usize::try_from(ly).unwrap_or(2));
    let nl = 2 * lat.n;
    let ctx = Ctx { g: G::new(), lat, je, jb, nl };
    let mut wcache: HashMap<usize, i128> = HashMap::new();
    let zero_links = vec![0u8; nl];
    let k0 = ctx.lat.canonical(&ctx.g, &ctx.lat.gauge_fix(&ctx.g, &zero_links));
    let mut prev: HashMap<usize, i128> = HashMap::new();
    let mut v: HashMap<usize, i128> = HashMap::from([(k0, 1i128)]);
    for step in 1..=steps {
        // candidates: support of v and its one-move neighbours (H is local)
        let mut cand: BTreeSet<usize> = v.keys().copied().collect();
        for &k in v.keys() {
            cand.extend(ctx.neighbours(k));
        }
        let mut nv: HashMap<usize, i128> = HashMap::new();
        for &i in &cand {
            let mut s = 0i128;
            for (j, c) in ctx.row(i) {
                if let Some(x) = v.get(&j) {
                    s = match c.checked_mul(*x).and_then(|t| s.checked_add(t)) {
                        Some(z) => z,
                        None => {
                            println!("ONFLY|error=overflow|step={step}|json=0");
                            std::process::exit(1);
                        }
                    };
                }
            }
            if s != 0 {
                nv.insert(i, s);
            }
        }
        let norm = wdot(&ctx, &mut wcache, &nv, &nv);
        let sumw = nv.iter().try_fold(0i128, |acc, (k, x)| {
            let w = *wcache.entry(*k).or_insert_with(|| ctx.weight(*k));
            acc.checked_add(w.checked_mul(*x)?)
        });
        // exact self-adjointness: <v_{k+1}, v_{k-1}>_W == <v_k, v_k>_W  (k >= 1)
        let sa = if step >= 2 {
            match (wdot(&ctx, &mut wcache, &nv, &prev), wdot(&ctx, &mut wcache, &v, &v)) {
                (Some(x), Some(y)) => if x == y { "PASS" } else { "FAIL" },
                _ => "OVERFLOW",
            }
        } else {
            "n/a"
        };
        println!(
            "ONFLY|L={lx}x{ly}|JE={je}|JB={jb}|step={step}|candidates={}|support={}|norm_w={}|sum_w={}|sa_check={sa}|ms={}|json=0",
            cand.len(),
            nv.len(),
            norm.map_or("overflow".to_string(), |x| x.to_string()),
            sumw.map_or("overflow".to_string(), |x| x.to_string()),
            t0.elapsed().as_millis()
        );
        if sa == "FAIL" {
            std::process::exit(2);
        }
        prev = v;
        v = nv;
    }
}
