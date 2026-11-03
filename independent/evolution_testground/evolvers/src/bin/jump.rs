//! Matrix-jump Euclidean evolution (integer-only, HEB-C rule).
//!
//! T = c - H (as 24T, exact integers). Repeated squaring gives
//! P = T^(2^J): ONE multiply by P advances the evolution 2^J steps.
//! Entries are renormalised by right shifts after every squaring (max near
//! 2^40); rounding noise is relative 2^-40 to the dominant (ground) part.
//!
//! Ground: v = P^REPS v0, E0 = Rayleigh quotient with the exact sparse H.
//! First excited: Hotelling deflation H' = H + s*Pi_g, Pi_g the W-orthogonal
//! projector on the measured ground vector g, s = 24*JE (pushes E0 above
//! E1; E1 - E0 <= 6*JE). The error in g enters E1 only at second order.
//! The jumped evolution of H' converges to the E1 state; after a final exact
//! projection against g its Rayleigh quotient with the TRUE H gives E1.
//!
//! usage: jump MATRIX JE JB J [REPS=4]
//! Output: one line, energies in micro-units of JE, json=0,
//! kind=MEASUREMENT_NOT_CERTIFICATE.
#![deny(clippy::float_arithmetic)]

use std::collections::BTreeMap;
use std::time::Instant;

const VBITS: u32 = 40;

struct Sys {
    n: usize,
    w: Vec<i128>,
    a: Vec<i128>, // dense 24*H, row-major
    sparse: Vec<Vec<(usize, i128)>>,
}

fn load(path: &str, je: i128, jb: i128) -> Result<Sys, String> {
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
    let mut a = vec![0i128; n * n];
    for t in toks[1 + 2 * n..].chunks(3) {
        let (i, j, z) = (usize::try_from(t[0]).map_err(|_| "bad i")?, usize::try_from(t[1]).map_err(|_| "bad j")?, t[2]);
        if i >= n || j >= n {
            return Err("index out of range".to_string());
        }
        a[i * n + j] += 24 * je * z;
        if i != j {
            let num = 24 * je * w[i] * z;
            if num % w[j] != 0 {
                return Err("non-integer 24H entry".to_string());
            }
            a[j * n + i] += num / w[j];
        }
    }
    for (i, m) in mag.iter().enumerate() {
        a[i * n + i] += 24 * jb * m;
    }
    let sparse = (0..n)
        .map(|i| {
            let row: BTreeMap<usize, i128> = (0..n).filter(|&j| a[i * n + j] != 0).map(|j| (j, a[i * n + j])).collect();
            row.into_iter().collect()
        })
        .collect();
    Ok(Sys { n, w, a, sparse })
}

fn renorm_to(v: &mut [i128], bits_target: u32) {
    let top = v.iter().map(|x| x.unsigned_abs()).max().unwrap_or(0);
    let bits = 128 - top.leading_zeros();
    if bits > bits_target {
        let sh = bits - bits_target;
        for x in v.iter_mut() {
            *x >>= sh;
        }
    }
}

fn matmul(n: usize, x: &[i128], y: &[i128]) -> Vec<i128> {
    let mut out = vec![0i128; n * n];
    for i in 0..n {
        let xi = &x[i * n..(i + 1) * n];
        let oi = &mut out[i * n..(i + 1) * n];
        for (k, &xik) in xi.iter().enumerate() {
            if xik == 0 {
                continue;
            }
            let yk = &y[k * n..(k + 1) * n];
            for (o, &ykj) in oi.iter_mut().zip(yk.iter()) {
                *o += xik * ykj;
            }
        }
    }
    out
}

fn matvec(n: usize, m: &[i128], v: &[i128]) -> Vec<i128> {
    (0..n).map(|i| m[i * n..(i + 1) * n].iter().zip(v.iter()).map(|(a, b)| a * b).sum()).collect()
}

fn sparse_apply(s: &Sys, v: &[i128]) -> Vec<i128> {
    s.sparse.iter().map(|row| row.iter().map(|&(j, a)| a * v[j]).sum()).collect()
}

fn wdot(s: &Sys, a: &[i128], b: &[i128]) -> i128 {
    (0..s.n).map(|i| s.w[i] * a[i] * b[i]).sum()
}

fn micro(num: i128, den: i128, je: i128) -> i128 {
    let d = 24 * je * den;
    let (q, r) = (num / d, num % d);
    q * 1_000_000 + (r * 1000 / d) * 1000 + ((r * 1000 % d) * 1000) / d
}

fn rayleigh(s: &Sys, v: &[i128], je: i128) -> i128 {
    let mut v = v.to_vec();
    renorm_to(&mut v, 36);
    let av = sparse_apply(s, &v);
    micro(wdot(s, &v, &av), wdot(s, &v, &v), je)
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

/// P = T^(2^J), renormalised after every squaring
fn jump_power(n: usize, mut t: Vec<i128>, j: u32) -> Vec<i128> {
    renorm_to(&mut t, VBITS);
    for _ in 0..j {
        t = matmul(n, &t, &t);
        renorm_to(&mut t, VBITS);
    }
    t
}

/// returns (energies after each rep, final vector)
fn run(s: &Sys, p: &[i128], reps: usize, je: i128, project: Option<&[i128]>) -> (Vec<i128>, Vec<i128>) {
    let mut v = lcg_start(s.n, 12345);
    let mut es = Vec::new();
    for _ in 0..reps {
        v = matvec(s.n, p, &v);
        renorm_to(&mut v, VBITS);
        if let Some(g) = project {
            project_out(s, &mut v, g);
        }
        es.push(rayleigh(s, &v, je));
    }
    (es, v)
}

fn project_out(s: &Sys, v: &mut [i128], g: &[i128]) {
    renorm_to(v, 36);
    let (gv, gg) = (wdot(s, g, v), wdot(s, g, g));
    let c = (gv << 40) / gg;
    for (x, gi) in v.iter_mut().zip(g.iter()) {
        *x -= (c * gi) >> 40;
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 5 {
        eprintln!("usage: jump MATRIX JE JB J [REPS=4]");
        std::process::exit(1);
    }
    let t0 = Instant::now();
    let num = |i: usize| {
        a[i].parse::<i128>().unwrap_or_else(|_| {
            eprintln!("bad arg {}", a[i]);
            std::process::exit(1)
        })
    };
    let (je, jb) = (num(2), num(3));
    let jexp = u32::try_from(num(4)).unwrap_or(20).min(60);
    let reps = a.get(5).and_then(|x| x.parse::<usize>().ok()).unwrap_or(4).max(2);
    let s = match load(&a[1], je, jb) {
        Ok(x) => x,
        Err(e) => {
            println!("JUMP|error={e}|json=0");
            std::process::exit(1);
        }
    };
    let n = s.n;
    // Gershgorin: every eigenvalue of 24H lies in [0, gersh] (H >= 0), so
    // c = gersh + 24 is rigorously above the spectrum and the lowest state of
    // the sector dominates T = c - H, whatever that sector's E0 is.
    let gersh = (0..n).map(|i| s.a[i * n..(i + 1) * n].iter().map(|x| x.abs()).sum::<i128>()).max().unwrap_or(0);
    let c24 = gersh + 24;
    // ground: T = c - H  (scaled by 24)
    let mut t = s.a.iter().map(|x| -x).collect::<Vec<_>>();
    for i in 0..n {
        t[i * n + i] += c24;
    }
    let p = jump_power(n, t, jexp);
    let (e0s, mut g) = run(&s, &p, reps, je, None);
    renorm_to(&mut g, 30);
    // deflated operator in fixed point 2^F:  24H' = 24H + 24*sigma*Pi_g,  sigma = 24*JE
    const F: u32 = 40;
    let sig24 = 24 * 24 * je;
    let gg = wdot(&s, &g, &g);
    // H' = H + sigma*Pi_g adds at most sigma to the top of the spectrum
    let c24b = gersh + sig24 + 24;
    let mut tb = vec![0i128; n * n];
    for i in 0..n {
        for j in 0..n {
            let pij = (g[i] * s.w[j] * g[j]) * sig24 / gg; // integer part
            let prem = (((g[i] * s.w[j] * g[j]) * sig24 % gg) << F) / gg; // fraction, 2^F
            let hij = (s.a[i * n + j] + pij) << F;
            let mut v = -(hij + prem);
            if i == j {
                v += c24b << F;
            }
            tb[i * n + j] = v;
        }
    }
    let pb = jump_power(n, tb, jexp);
    let (e1s, _) = run(&s, &pb, reps, je, Some(&g));
    let last = |v: &Vec<i128>| *v.last().unwrap_or(&0);
    let prev = |v: &Vec<i128>| v[v.len() - 2];
    println!(
        "JUMP|matrix={}|n={n}|JE={je}|JB={jb}|J={jexp}|reps={reps}|steps_equiv=2^{jexp}x{reps}|c=({c24})/24|E0={}/1000000|dE0={}|E1={}/1000000|dE1={}|gap={}/1000000|E1_trace={}|ms={}|kind=MEASUREMENT_NOT_CERTIFICATE|json=0",
        a[1].rsplit('/').next().unwrap_or(""),
        last(&e0s),
        prev(&e0s) - last(&e0s),
        last(&e1s),
        prev(&e1s) - last(&e1s),
        last(&e1s) - last(&e0s),
        e1s.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","),
        t0.elapsed().as_millis()
    );
}
