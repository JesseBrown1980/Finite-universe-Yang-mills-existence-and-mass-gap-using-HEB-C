//! Integer-only block eigensolver for the low-energy CLUSTER of a
//! W-self-adjoint operator (the 8 near-degenerate vacuum levels of a torus or
//! vacuum ball), with rigorous residual intervals.
//!
//! Method (Chebyshev-filtered subspace iteration):
//!   * block of P integer vectors (P = 8 + guards), LCG start;
//!   * each outer step: Chebyshev filter of degree M on [a, b] (b = Gershgorin,
//!     rigorous top of the spectrum; a = largest current Ritz value of the
//!     block), W-orthonormalisation by modified Gram-Schmidt in fixed point,
//!     Rayleigh-Ritz: P x P projected matrix diagonalised by integer Jacobi
//!     rotations (fixed point 2^50, integer square roots), block rotated;
//!   * stop when every wanted Ritz value moves by <= 1 micro-unit.
//!
//! Verification (exact big integers, independent of the fixed-point steps):
//!   for each wanted Ritz vector x (integer), theta = <x,Hx>_W/<x,x>_W exactly,
//!   eps = ||Hx - theta x||_W / ||x||_W rounded UP.  For W-self-adjoint H there
//!   is an eigenvalue in [theta - eps, theta + eps] (Krylov-Bogoliubov).
//!   Which eigenvalue it is (the ordering) is NOT established here: that needs
//!   an inertia count (sturmrs) between the intervals.
//!
//! usage: cluster MATRIX JE JB [WANT=8] [GUARD=4] [DEGREE=12] [MAXOUTER=200]
//! Output: one line per wanted level plus a summary, micro-units of JE, json=0.
#![deny(clippy::float_arithmetic)]

use num_bigint::BigInt;
use num_traits::{Signed, Zero};
use std::collections::BTreeMap;

const VB: u32 = 40; // vector magnitude bits
const FX: u32 = 50; // fixed point of the small eigenproblem

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

fn top_bits(v: &[i128]) -> u32 {
    128 - v.iter().map(|x| x.unsigned_abs()).max().unwrap_or(0).leading_zeros()
}

fn shr_all(v: &mut [i128], s: u32) {
    if s > 0 {
        for x in v.iter_mut() {
            *x >>= s;
        }
    }
}

fn isqrt(n: u128) -> u128 {
    if n < 2 {
        return n;
    }
    let mut x = 1u128 << ((128 - n.leading_zeros()).div_ceil(2));
    loop {
        let y = (x + n / x) / 2;
        if y >= x {
            return x;
        }
        x = y;
    }
}

/// W inner product of vectors pre-shifted to `bits` (keeps i128 sums safe)
fn wdot_s(op: &Op, a: &[i128], b: &[i128], sa: u32, sb: u32) -> i128 {
    let mut s = 0i128;
    for i in 0..op.n {
        s += op.w[i] * (a[i] >> sa) * (b[i] >> sb);
    }
    s
}

fn lcg(n: usize, seed0: u64) -> Vec<i128> {
    let mut seed = seed0;
    (0..n)
        .map(|_| {
            seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            i128::from(seed >> 24) - (1i128 << 39)
        })
        .collect()
}

/// shift so that inner products of two vectors stay below 2^120
fn safe_shift(op: &Op, v: &[i128]) -> u32 {
    let nb = 128 - (op.n as u128).leading_zeros() + 3; // n * max weight (<= 8)
    let b = top_bits(v);
    // 2*(b - s) + nb <= 118
    let lim = (118u32.saturating_sub(nb)) / 2;
    b.saturating_sub(lim)
}

fn project_out(op: &Op, q: &mut [Vec<i128>], i: usize) {
    for j in 0..i {
        let (a, b) = q.split_at_mut(i);
        let qj = &a[j];
        let qi = &mut b[0];
        let sj = safe_shift(op, qj);
        let si = safe_shift(op, qi);
        let num = wdot_s(op, qj, qi, sj, si);
        let den = wdot_s(op, qj, qj, sj, sj);
        if den == 0 {
            continue;
        }
        // coefficient num/den in fixed point 2^30 (big integers: num may be ~2^118)
        let c = i128::try_from((BigInt::from(num) << 30u32) / BigInt::from(den.max(1))).unwrap_or(0);
        for (x, y) in qi.iter_mut().zip(qj.iter()) {
            let t = (c * (y >> sj)) >> 30;
            *x -= t << si;
        }
    }
}

fn rescale(v: &mut [i128]) {
    let b = top_bits(v);
    if b > VB {
        shr_all(v, b - VB);
    } else if b > 0 && b < VB {
        for x in v.iter_mut() {
            *x <<= VB - b;
        }
    }
}

/// W-orthonormalise (up to scale) by modified Gram-Schmidt applied twice;
/// a vector that collapses below 12 bits after projection (its direction was
/// lost to integer resolution) is replaced by a fresh pseudo-random vector.
/// Returns the number of replacements.
fn orthonormalise(op: &Op, q: &mut [Vec<i128>], seed: &mut u64) -> usize {
    let mut replaced = 0;
    for i in 0..q.len() {
        let mut tries = 0;
        loop {
            let before = top_bits(&q[i]);
            project_out(op, q, i);
            project_out(op, q, i);
            let after = top_bits(&q[i]);
            if after >= 12 && after + 28 >= before {
                rescale(&mut q[i]);
                break;
            }
            if after >= 12 && tries > 0 {
                rescale(&mut q[i]);
                break;
            }
            // direction lost or nearly so: restart this vector
            *seed = seed.wrapping_add(104729);
            q[i] = lcg(op.n, *seed);
            replaced += 1;
            tries += 1;
            if tries > 4 {
                rescale(&mut q[i]);
                break;
            }
        }
    }
    replaced
}

/// Jacobi diagonalisation of a symmetric matrix in fixed point FX.
/// Returns (eigenvalues, U columns = eigenvectors) in fixed point.
fn jacobi(mut s: Vec<Vec<i128>>) -> (Vec<i128>, Vec<Vec<i128>>) {
    let p = s.len();
    let one = 1i128 << FX;
    let mut u = vec![vec![0i128; p]; p];
    for (i, r) in u.iter_mut().enumerate() {
        r[i] = one;
    }
    for _sweep in 0..60 {
        let mut off = 0i128;
        for (i, row) in s.iter().enumerate() {
            for (j, &v) in row.iter().enumerate() {
                if i != j {
                    off = off.max(v.abs());
                }
            }
        }
        if off <= 2 {
            break;
        }
        for pi in 0..p {
            for qi in pi + 1..p {
                let spq = s[pi][qi];
                if spq.abs() <= 1 {
                    continue;
                }
                let d = s[qi][qi] - s[pi][pi];
                let e = 2 * spq;
                // t = e / (|d| + sqrt(d^2 + e^2)) * sign(d), |t| <= 1 (fixed point)
                let rt = i128::try_from(isqrt((d.unsigned_abs()).pow(2) + (e.unsigned_abs()).pow(2))).unwrap_or(i128::MAX);
                let mut t = (e << FX) / (d.abs() + rt).max(1);
                if d < 0 {
                    t = -t;
                }
                // c = 1/sqrt(1+t^2), s = t c   (fixed point)
                let root = isqrt((one.unsigned_abs()).pow(2) + (t.unsigned_abs()).pow(2)).max(1);
                let cfx = i128::try_from((one.unsigned_abs()).pow(2) / root).unwrap_or(one);
                let sfx = (t * cfx) >> FX;
                // rotate rows/cols pi, qi
                for row in s.iter_mut() {
                    let skp = row[pi];
                    let skq = row[qi];
                    row[pi] = (cfx * skp - sfx * skq) >> FX;
                    row[qi] = (sfx * skp + cfx * skq) >> FX;
                }
                for k in 0..p {
                    let spk = s[pi][k];
                    let sqk = s[qi][k];
                    s[pi][k] = (cfx * spk - sfx * sqk) >> FX;
                    s[qi][k] = (sfx * spk + cfx * sqk) >> FX;
                }
                for row in u.iter_mut() {
                    let ukp = row[pi];
                    let ukq = row[qi];
                    row[pi] = (cfx * ukp - sfx * ukq) >> FX;
                    row[qi] = (sfx * ukp + cfx * ukq) >> FX;
                }
            }
        }
    }
    ((0..p).map(|i| s[i][i]).collect(), u)
}

fn micro_of(num: &BigInt, den: &BigInt, je: i128) -> BigInt {
    // floor(10^6 * num / (24 je den))
    let d = den * BigInt::from(24 * je);
    let q = num * BigInt::from(1_000_000) / &d;
    if num.is_negative() && !(num * BigInt::from(1_000_000) % &d).is_zero() {
        q - 1
    } else {
        q
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 4 {
        eprintln!("usage: cluster MATRIX JE JB [WANT=8] [GUARD=4] [DEGREE=12] [MAXOUTER=200]");
        std::process::exit(1);
    }
    let t0 = std::time::Instant::now();
    let num = |i: usize, d: i128| a.get(i).and_then(|s| s.parse::<i128>().ok()).unwrap_or(d);
    let (je, jb) = (num(2, 1), num(3, 0));
    let want = usize::try_from(num(4, 8)).unwrap_or(8);
    let guard = usize::try_from(num(5, 4)).unwrap_or(4);
    let degree = usize::try_from(num(6, 12)).unwrap_or(12).max(2);
    let maxouter = usize::try_from(num(7, 200)).unwrap_or(200);
    let op = match load(&a[1], je, jb) {
        Ok(o) => o,
        Err(e) => {
            println!("CLUSTER|error={e}|json=0");
            std::process::exit(1);
        }
    };
    let n = op.n;
    let p = (want + guard).min(n);
    let beta = op.rows.iter().map(|r| r.iter().map(|&(_, v)| v.abs()).sum::<i128>()).max().unwrap_or(0) + 24;
    let mut q: Vec<Vec<i128>> = (0..p).map(|k| lcg(n, 12345 + 7919 * k as u64)).collect();
    let mut seed = 999_983u64;
    let mut replaced_total = orthonormalise(&op, &mut q, &mut seed);
    let mut av = vec![0i128; n];
    let mut theta_prev: Vec<i128> = vec![i128::MAX; p];
    let mut alpha = beta / 2;
    let mut outer = 0;
    let mut converged = false;
    while outer < maxouter {
        outer += 1;
        // Chebyshev filter each vector: damp [alpha, beta], amplify below alpha
        let width = (beta - alpha).max(1);
        for v in q.iter_mut() {
            let mut y0 = v.clone();
            apply(&op, &y0, &mut av);
            let mut y1: Vec<i128> = y0.iter().zip(av.iter()).map(|(y, x)| ((alpha + beta) * y - 2 * x) / width).collect();
            for _ in 1..degree {
                apply(&op, &y1, &mut av);
                let y2: Vec<i128> = (0..n).map(|i| (2 * ((alpha + beta) * y1[i] - 2 * av[i]) - width * y0[i]) / width).collect();
                y0 = y1;
                y1 = y2;
                let b = top_bits(&y1);
                if b > VB {
                    shr_all(&mut y0, b - VB);
                    shr_all(&mut y1, b - VB);
                }
            }
            *v = y1;
        }
        replaced_total += orthonormalise(&op, &mut q, &mut seed);
        // Rayleigh-Ritz. Common shift s0 for all block vectors; the small
        // P x P projection C_ij = <q_i, A q_j>_W / sqrt(n_i n_j) is formed in
        // exact big integers (cheap), then rounded to fixed point FX.
        let s0 = q.iter().map(|v| safe_shift(&op, v)).max().unwrap_or(0);
        let norms: Vec<i128> = (0..p).map(|i| wdot_s(&op, &q[i], &q[i], s0, s0)).collect();
        let roots: Vec<i128> = norms.iter().map(|&x| i128::try_from(isqrt(x.unsigned_abs())).unwrap_or(1).max(1)).collect();
        let mut s = vec![vec![0i128; p]; p];
        for j in 0..p {
            let mut vv = q[j].clone();
            shr_all(&mut vv, 6); // headroom for A
            let mut o = vec![0i128; n];
            apply(&op, &vv, &mut o);
            let sa = safe_shift(&op, &o);
            for i in 0..p {
                let ip = BigInt::from(wdot_s(&op, &q[i], &o, s0, sa));
                // raw <q_i, A q_j> = ip * 2^(s0 + sa + 6); raw sqrt(n_i n_j) = r_i r_j 2^(2 s0)
                let e = i64::from(sa) + 6 - i64::from(s0) + i64::from(FX);
                let numb = if e >= 0 { ip << u32::try_from(e).unwrap_or(0) } else { ip >> u32::try_from(-e).unwrap_or(0) };
                let val = numb / (BigInt::from(roots[i]) * BigInt::from(roots[j]));
                s[i][j] = i128::try_from(val).unwrap_or(0);
            }
        }
        for i in 0..p {
            for j in i + 1..p {
                let m = (s[i][j] + s[j][i]) / 2;
                s[i][j] = m;
                s[j][i] = m;
            }
        }
        let (ev, u) = jacobi(s);
        let mut order: Vec<usize> = (0..p).collect();
        order.sort_by_key(|&k| ev[k]);
        // normalised block y_j = q_j * 2^50 / r_j (all on one scale), then x_k = sum_j U_jk y_j
        let ys: Vec<Vec<i128>> = (0..p)
            .map(|j| {
                let f = (1i128 << 100) / roots[j];
                q[j].iter().map(|&x| ((x >> s0) * f) >> 50).collect()
            })
            .collect();
        let newq: Vec<Vec<i128>> = order
            .iter()
            .map(|&k| {
                let mut x = vec![0i128; n];
                for (j, y) in ys.iter().enumerate() {
                    let c = u[j][k];
                    for (xi, yi) in x.iter_mut().zip(y.iter()) {
                        *xi += (c * yi) >> FX;
                    }
                }
                let b = top_bits(&x);
                if b > VB {
                    shr_all(&mut x, b - VB);
                }
                x
            })
            .collect();
        q = newq;
        let theta: Vec<i128> = order.iter().map(|&k| ev[k]).collect(); // 24H units, fixed point FX
        if std::env::var("CLUSTER_TRACE").is_ok() && (outer <= 5 || outer % 50 == 0) {
            let tm: Vec<String> = theta.iter().map(|t| ((t >> FX) * 1000 / (24 * je)).to_string()).collect();
            eprintln!("trace outer={outer} alpha24={alpha} s0={s0} theta_milli={}", tm.join(","));
        }
        // alpha: just above the largest Ritz value of the block (in 24H units)
        alpha = ((theta[p - 1] >> FX) + 1).min(beta - 1);
        let tol = ((24 * je) << FX) / 1_000_000; // 1 micro-unit
        let moved = (0..want).map(|k| (theta[k] - theta_prev[k]).abs()).max().unwrap_or(i128::MAX);
        theta_prev = theta;
        if moved <= tol && outer > 3 {
            converged = true;
            break;
        }
    }
    // exact verification of each wanted Ritz vector
    let mut lines = Vec::new();
    let mut ivals = Vec::new();
    for (k, x) in q.iter().take(want).enumerate() {
        let mut xs = x.clone();
        let b = top_bits(&xs);
        if b > 36 {
            shr_all(&mut xs, b - 36);
        }
        apply(&op, &xs, &mut av);
        let bx: Vec<BigInt> = xs.iter().map(|&v| BigInt::from(v)).collect();
        let bav: Vec<BigInt> = av.iter().map(|&v| BigInt::from(v)).collect();
        let bw: Vec<BigInt> = op.w.iter().map(|&v| BigInt::from(v)).collect();
        let mut nm = BigInt::zero();
        let mut dn = BigInt::zero();
        for i in 0..n {
            nm += &bw[i] * &bx[i] * &bav[i];
            dn += &bw[i] * &bx[i] * &bx[i];
        }
        // r = dn*Ax - nm*x  =  24*dn*(Hx - theta x)
        let mut rr = BigInt::zero();
        for i in 0..n {
            let r = &dn * &bav[i] - &nm * &bx[i];
            rr += &bw[i] * &r * &r;
        }
        // eps^2 = rr / (576 dn^2 * dn)   [||x||_W^2 = dn];  eps_micro = ceil(10^6 sqrt(eps^2))
        let denom = BigInt::from(576) * &dn * &dn * &dn * BigInt::from(je * je);
        let num12 = rr * BigInt::from(1_000_000_000_000u64);
        let qv = (&num12 + &denom - BigInt::from(1)) / &denom; // ceil
        let mut e = qv.sqrt();
        if &e * &e < qv {
            e += 1;
        }
        let th = micro_of(&nm, &dn, je);
        lines.push(format!(
            "CLUSTER_LEVEL|k={k}|theta={th}/1000000|eps_up={e}/1000000|interval=[{},{}]/1000000|json=0",
            &th - &e,
            &th + &e + 1
        ));
        ivals.push((th.clone() - e.clone(), th + e + 1));
    }
    for l in &lines {
        println!("{l}");
    }
    let disjoint01 = ivals.len() >= 2 && ivals[0].1 < ivals[1].0;
    let disjoint12 = ivals.len() >= 3 && ivals[1].1 < ivals[2].0;
    let (glo, ghi) = if ivals.len() >= 2 {
        (&ivals[1].0 - &ivals[0].1, &ivals[1].1 - &ivals[0].0)
    } else {
        (BigInt::zero(), BigInt::zero())
    };
    println!(
        "CLUSTER|matrix={}|n={n}|JE={je}|JB={jb}|block={p}|degree={degree}|outer={outer}|replaced_vectors={replaced_total}|converged={}|interval0_disjoint_from_1={}|interval1_disjoint_from_2={}|gap_if_ordered_in=[{glo},{ghi}]/1000000|ordering=UNVERIFIED_needs_inertia|ms={}|json=0",
        a[1].rsplit('/').next().unwrap_or(""),
        u8::from(converged),
        u8::from(disjoint01),
        u8::from(disjoint12),
        t0.elapsed().as_millis()
    );
}
