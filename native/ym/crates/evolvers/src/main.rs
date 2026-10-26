//! Integer-only Euclidean evolution for the finite S3 2x2-torus operator
//! H = JE*E + JB*M (HEB-C rule: no floating point anywhere).
//!
//! A = 24*H is an exact integer matrix (all orbit weights divide 24).
//! Evolution v <- (c - H) v, c just above (E0 + Emax)/2: the smallest shift
//! for which the lowest state still dominates (about half the steps of a
//! Gershgorin shift). Emax is estimated by power iteration on A.
//!
//! Run 1 (ground): v converges to the lowest state of the matrix; its
//!   Rayleigh quotient E0 = <v,Hv>_W/<v,v>_W is an upper estimate of E0 whose
//!   error is quadratic in the remaining excited amplitude.
//! Run 2 (deflated): same evolution with the converged ground vector
//!   projected out (W inner product) every step; the Rayleigh quotient
//!   converges to E1 of the matrix. gap = E1 - E0, no ratio fitting.
//!
//! Energies reported in micro-units of JE (integer floor). The change over
//! the last 10% of steps is reported as dE (settledness).
//! Output: one line, json=0, kind=MEASUREMENT_NOT_CERTIFICATE.
#![deny(clippy::float_arithmetic)]

use std::collections::BTreeMap;
use std::time::Instant;

const VBITS: u32 = 40;
const DEFL_FP: u32 = 28;

struct Op {
    n: usize,
    w: Vec<i128>,
    rows: Vec<Vec<(usize, i128)>>,
}

fn load(path: &str, je: i128, jb: i128) -> Result<Op, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
    let toks: Result<Vec<i128>, String> =
        text.split_ascii_whitespace().map(|s| s.parse::<i128>().map_err(|_| format!("bad token {s}"))).collect();
    let toks = toks?;
    let n = usize::try_from(*toks.first().ok_or("empty")?).map_err(|_| "bad n")?;
    if toks.len() < 1 + 2 * n || (toks.len() - 1 - 2 * n) % 3 != 0 {
        return Err("bad layout".to_string());
    }
    let w = toks[1..1 + n].to_vec();
    let mag = &toks[1 + n..1 + 2 * n];
    let mut dense: Vec<BTreeMap<usize, i128>> = vec![BTreeMap::new(); n];
    for t in toks[1 + 2 * n..].chunks(3) {
        let (i, j, z) = (usize::try_from(t[0]).map_err(|_| "bad i")?, usize::try_from(t[1]).map_err(|_| "bad j")?, t[2]);
        if i >= n || j >= n {
            return Err("index out of range".to_string());
        }
        if z == 0 {
            continue;
        }
        *dense[i].entry(j).or_insert(0) += 24 * je * z;
        if i != j {
            let num = 24 * je * w[i] * z;
            if num % w[j] != 0 {
                return Err("non-integer 24H entry".to_string());
            }
            *dense[j].entry(i).or_insert(0) += num / w[j];
        }
    }
    let rows = dense
        .into_iter()
        .enumerate()
        .map(|(i, mut d)| {
            *d.entry(i).or_insert(0) += 24 * jb * mag[i];
            d.into_iter().filter(|&(_, v)| v != 0).collect()
        })
        .collect();
    Ok(Op { n, w, rows })
}

fn apply(op: &Op, v: &[i128], out: &mut [i128]) {
    for (o, row) in out.iter_mut().zip(op.rows.iter()) {
        let mut s = 0i128;
        for &(j, a) in row {
            s += a * v[j];
        }
        *o = s;
    }
}

fn wdot(op: &Op, a: &[i128], b: &[i128]) -> i128 {
    let mut s = 0i128;
    for i in 0..op.n {
        s += op.w[i] * a[i] * b[i];
    }
    s
}

fn renorm(v: &mut [i128]) {
    let top = v.iter().map(|x| x.unsigned_abs()).max().unwrap_or(0);
    let bits = 128 - top.leading_zeros();
    if bits > VBITS {
        let sh = bits - VBITS;
        for x in v.iter_mut() {
            *x >>= sh;
        }
    }
}

fn lcg_start(n: usize, seed0: u64) -> Vec<i128> {
    let mut seed = seed0;
    (0..n)
        .map(|_| {
            seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            i128::from(seed >> 24) - (1i128 << 39)
        })
        .collect()
}

fn deflate(op: &Op, v: &mut [i128], g: &[i128], gg: i128) {
    let c = (wdot(op, g, v) << DEFL_FP) / gg;
    for (x, gi) in v.iter_mut().zip(g.iter()) {
        *x -= (c * gi) >> DEFL_FP;
    }
}

/// energy in micro-units of JE, floor: 10^6 * num / (24 * je * den)
fn micro(num: i128, den: i128, je: i128) -> i128 {
    // num < 2^115, so split to avoid overflow in num * 10^6
    let d = 24 * je * den;
    let q = num / d;
    let r = num % d;
    q * 1_000_000 + (r * 1000 / d) * 1000 + ((r * 1000 % d) * 1000) / d
}

struct Run {
    e_end: i128,
    e_90: i128,
    v: Vec<i128>,
}

fn evolve(op: &Op, je: i128, c24: i128, steps: usize, defl: Option<&[i128]>) -> Run {
    let mut v = lcg_start(op.n, 12345);
    let mut av = vec![0i128; op.n];
    let gg = defl.map(|g| wdot(op, g, g));
    let mark = steps - steps / 10;
    let (mut e_90, mut e_end) = (0, 0);
    for k in 0..steps {
        if let (Some(g), Some(gg)) = (defl, gg) {
            deflate(op, &mut v, g, gg);
        }
        apply(op, &v, &mut av);
        if k == mark || k + 1 == steps {
            let e = micro(wdot(op, &v, &av), wdot(op, &v, &v), je);
            if k == mark {
                e_90 = e;
            }
            e_end = e;
        }
        for (x, a) in v.iter_mut().zip(av.iter()) {
            *x = c24 * *x - a;
        }
        renorm(&mut v);
    }
    if let (Some(g), Some(gg)) = (defl, gg) {
        deflate(op, &mut v, g, gg);
    }
    Run { e_end, e_90, v }
}

fn emax24(op: &Op, steps: usize) -> i128 {
    let mut v = lcg_start(op.n, 999);
    let mut av = vec![0i128; op.n];
    let mut est = 0i128;
    for _ in 0..steps {
        apply(op, &v, &mut av);
        est = wdot(op, &v, &av) / wdot(op, &v, &v);
        v.copy_from_slice(&av);
        renorm(&mut v);
    }
    est
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 5 {
        eprintln!("usage: evolvers MATRIX JE JB STEPS [DEFLATE=1]");
        std::process::exit(1);
    }
    let t0 = Instant::now();
    let p = |i: usize| {
        a[i].parse::<i128>().unwrap_or_else(|_| {
            eprintln!("bad arg {}", a[i]);
            std::process::exit(1)
        })
    };
    let (je, jb) = (p(2), p(3));
    let steps = usize::try_from(p(4)).unwrap_or(1000).max(10);
    let defl = a.get(5).map_or(true, |s| s != "0");
    let op = match load(&a[1], je, jb) {
        Ok(o) => o,
        Err(e) => {
            println!("EVOLVE-RS|error={e}|json=0");
            std::process::exit(1);
        }
    };
    // Gershgorin: all eigenvalues of 24H lie in [0, gersh] (H >= 0), so
    // c = gersh + 1 (x24) is rigorously above the spectrum on any lattice.
    let gersh = op.rows.iter().map(|r| r.iter().map(|&(_, v)| v.abs()).sum::<i128>()).max().unwrap_or(0);
    let c24 = gersh + 24;
    let _ = emax24;
    let g = evolve(&op, je, c24, steps, None);
    let mut line = format!(
        "EVOLVE-RS|matrix={}|n={}|JE={je}|JB={jb}|steps={steps}|c=({c24})/24|E0={}/1000000|dE0={}",
        a[1].rsplit('/').next().unwrap_or(""),
        op.n,
        g.e_end,
        g.e_90 - g.e_end
    );
    if defl {
        let mut gv = g.v.clone();
        renorm(&mut gv);
        let s = evolve(&op, je, c24, steps, Some(&gv));
        line.push_str(&format!("|E1={}/1000000|dE1={}|gap={}/1000000", s.e_end, s.e_90 - s.e_end, s.e_end - g.e_end));
    }
    println!("{line}|ms={}|kind=MEASUREMENT_NOT_CERTIFICATE|json=0", t0.elapsed().as_millis());
}
