//! Chebyshev-accelerated Euclidean evolution (integer-only, HEB-C rule).
//!
//! Same measurement as `evolvers` (Rayleigh energies, ground run then a
//! deflated run, gap = E1 - E0), but the filter is the Chebyshev polynomial
//! T_k(x) of x = ((a+b) - 2H)/(b-a): states inside [a, b] stay bounded while
//! those below a grow like cosh(k*acosh(x)), roughly the square root of the
//! steps plain v <- (c-H)v needs. b = Gershgorin bound (rigorous top of the
//! spectrum); a is restarted every block at  E_R + GUESS/2,  E_R the current
//! Rayleigh quotient (always >= the target level), GUESS a gap estimate. Any
//! a above the target works; a near mid-gap is fastest.
//!
//! Integer recurrence (A = 24H, alpha = 24a, beta = 24b):
//!   y_{k+1} = ( 2((alpha+beta) y_k - 2 A y_k) - (beta-alpha) y_{k-1} ) / (beta-alpha)
//! floor division, common right-shift renormalisation of (y_{k-1}, y_k).
//!
//! usage: cheb MATRIX JE JB STEPS GUESS_MICRO [BLOCK=200]
//! Output: one line, micro-units of JE, json=0, kind=MEASUREMENT_NOT_CERTIFICATE.
#![deny(clippy::float_arithmetic)]

use std::collections::BTreeMap;
use std::time::Instant;

const VBITS: u32 = 40;

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

fn top_bits(v: &[i128]) -> u32 {
    128 - v.iter().map(|x| x.unsigned_abs()).max().unwrap_or(0).leading_zeros()
}

fn shift_all(v: &mut [i128], sh: u32) {
    for x in v.iter_mut() {
        *x >>= sh;
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
    let c = (wdot(op, g, v) << 28) / gg;
    for (x, gi) in v.iter_mut().zip(g.iter()) {
        *x -= (c * gi) >> 28;
    }
}

fn micro(num: i128, den: i128, je: i128) -> i128 {
    let d = 24 * je * den;
    let (q, r) = (num / d, num % d);
    q * 1_000_000 + (r * 1000 / d) * 1000 + ((r * 1000 % d) * 1000) / d
}

/// Rayleigh quotient of v as (24E as num/den) and micro-units
fn rq(op: &Op, v: &[i128], av: &mut [i128], je: i128) -> (i128, i128, i128) {
    let mut u = v.to_vec();
    let b = top_bits(&u);
    if b > 36 {
        shift_all(&mut u, b - 36);
    }
    apply(op, &u, av);
    let (num, den) = (wdot(op, &u, av), wdot(op, &u, &u));
    (num, den, micro(num, den, je))
}

struct Out {
    e_end: i128,
    e_prev_block: i128,
    v: Vec<i128>,
}

#[allow(clippy::too_many_arguments)]
fn run(op: &Op, je: i128, beta: i128, guess24: i128, steps: usize, block: usize, defl: Option<&[i128]>) -> Out {
    let n = op.n;
    let gg = defl.map(|g| wdot(op, g, g));
    let mut av = vec![0i128; n];
    let mut v = lcg_start(n, 12345);
    if let (Some(g), Some(gg)) = (defl, gg) {
        deflate(op, &mut v, g, gg);
    }
    // warm-up: a few plain steps with c = beta + 24 (removes the top of the spectrum)
    for _ in 0..20 {
        apply(op, &v, &mut av);
        for (x, a) in v.iter_mut().zip(av.iter()) {
            *x = (beta + 24) * *x - a;
        }
        let b = top_bits(&v);
        if b > VBITS {
            shift_all(&mut v, b - VBITS);
        }
        if let (Some(g), Some(gg)) = (defl, gg) {
            deflate(op, &mut v, g, gg);
        }
    }
    let (mut e_prev, mut e_end) = (0, 0);
    let mut done = 0;
    let mut block = block;
    while done < steps {
        // doubling blocks: Chebyshev growth compounds only within one
        // polynomial, so the final (longest) block carries the filtering
        block = block.min(steps - done).max(2);
        let (num, den, e) = rq(op, &v, &mut av, je);
        e_prev = e_end;
        e_end = e;
        let alpha = (num / den + guess24 / 2).min(beta - 1);
        let width = beta - alpha;
        // y0 = v, y1 = T y0
        let mut y0 = v.clone();
        apply(op, &y0, &mut av);
        let mut y1: Vec<i128> = y0.iter().zip(av.iter()).map(|(y, a)| ((alpha + beta) * y - 2 * a) / width).collect();
        for _ in 1..block {
            if let (Some(g), Some(gg)) = (defl, gg) {
                deflate(op, &mut y1, g, gg);
                deflate(op, &mut y0, g, gg);
            }
            apply(op, &y1, &mut av);
            let y2: Vec<i128> = (0..n)
                .map(|i| (2 * ((alpha + beta) * y1[i] - 2 * av[i]) - width * y0[i]) / width)
                .collect();
            y0 = y1;
            y1 = y2;
            let b = top_bits(&y1);
            if b > VBITS {
                shift_all(&mut y0, b - VBITS);
                shift_all(&mut y1, b - VBITS);
            }
        }
        v = y1;
        if let (Some(g), Some(gg)) = (defl, gg) {
            deflate(op, &mut v, g, gg);
        }
        done += block;
        block *= 2;
    }
    let (_, _, e) = rq(op, &v, &mut av, je);
    e_prev = if done > 0 { e_end } else { e_prev };
    Out { e_end: e, e_prev_block: e_prev, v }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 6 {
        eprintln!("usage: cheb MATRIX JE JB STEPS GUESS_MICRO [BLOCK=200]");
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
    let steps = usize::try_from(p(4)).unwrap_or(1000).max(1);
    let guess24 = (p(5) * 24 * je) / 1_000_000;
    let block = a.get(6).and_then(|s| s.parse::<usize>().ok()).unwrap_or(200).max(2);
    let op = match load(&a[1], je, jb) {
        Ok(o) => o,
        Err(e) => {
            println!("CHEB|error={e}|json=0");
            std::process::exit(1);
        }
    };
    let beta = op.rows.iter().map(|r| r.iter().map(|&(_, v)| v.abs()).sum::<i128>()).max().unwrap_or(0) + 24;
    let g = run(&op, je, beta, guess24.max(1), steps, block, None);
    let mut gv = g.v.clone();
    let b = top_bits(&gv);
    if b > VBITS {
        shift_all(&mut gv, b - VBITS);
    }
    let s = run(&op, je, beta, guess24.max(1), steps, block, Some(&gv));
    println!(
        "CHEB|matrix={}|n={}|JE={je}|JB={jb}|steps={steps}|block={block}|b=({beta})/24|guess={}/1000000|E0={}/1000000|dE0={}|E1={}/1000000|dE1={}|gap={}/1000000|ms={}|kind=MEASUREMENT_NOT_CERTIFICATE|json=0",
        a[1].rsplit('/').next().unwrap_or(""),
        op.n,
        p(5),
        g.e_end,
        g.e_prev_block - g.e_end,
        s.e_end,
        s.e_prev_block - s.e_end,
        s.e_end - g.e_end,
        t0.elapsed().as_millis()
    );
}
