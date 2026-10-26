//! Long jumps of the full evolution operator T = c - H, then play forward.
//!
//! Binary powering: P_j = T^(2^j) by repeated squaring (j = 0..J); a jump to
//! step N applies P_j for every set bit j of N. One cache of squarings serves
//! every target N <= 2^(J+1) - 1, so any stage can be reached and played from.
//!
//! mode exact P : all arithmetic modulo the prime P (< 2^31) on the full state.
//!   This keeps EVERY component exactly (no rounding, no renormalisation).
//!   Checks: (1) jump to 1024 == 1024 sequential steps; (2) jump(N/2) applied
//!   twice == jump(N); (3) 27 sequential frames from jump(N) == jump(N+27).
//!   Prints sha256-free fingerprints (sum and weighted sum mod P) and the
//!   first components of the state. Exact algebra, not physical amplitudes.
//! mode fixed   : integer fixed point (matrix powers and vector renormalised
//!   by right shifts to ~2^40), so directions are kept to ~2^-40 and the
//!   physical energy E(N) = <v,Hv>_W/<v,v>_W can be measured at every stage
//!   N = 10^0 .. 10^k, then FRAMES steps are played one by one from N_max.
//!   Error control: for the vector at N_max an exact big-integer residual
//!   radius eps = ||Hv - E v||_W / ||v||_W (rounded up) is reported; some
//!   eigenvalue lies in [E - eps, E + eps] (Krylov-Bogoliubov). Which
//!   eigenvalue is not decided here (use cluster + inertia for ordering).
//!
//! Clock: one step is v <- (c - H) v, i.e. (after dividing by c) the
//! forward-Euler imaginary-time step 1 - H/c. Mode k decays per step by
//! (c - E_k)/c exactly; this is NOT the propagator exp(-tau H), and steps
//! are not physical time. A single relaxed vector suppresses the excited
//! levels, so level splittings are measured with the block solver.
//!
//! usage: jumpto MATRIX JE JB exact P N
//!        jumpto MATRIX JE JB fixed KMAX FRAMES
//! Output json=0. Integer-only, Rust 1.81.
#![deny(clippy::float_arithmetic)]

use std::collections::BTreeMap;

struct Op {
    n: usize,
    w: Vec<i128>,
    a: Vec<i128>, // dense 24H
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
    let mut a = vec![0i128; n * n];
    let mut seen: BTreeMap<(usize, usize), ()> = BTreeMap::new();
    for t in toks[1 + 2 * n..].chunks(3) {
        let (i, j, z) = (usize::try_from(t[0]).map_err(|_| "bad i")?, usize::try_from(t[1]).map_err(|_| "bad j")?, t[2]);
        if i >= n || j >= n || seen.insert((i, j), ()).is_some() {
            return Err("bad or duplicate entry".to_string());
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
    Ok(Op { n, w, a })
}

fn gersh(op: &Op) -> i128 {
    let n = op.n;
    (0..n).map(|i| op.a[i * n..(i + 1) * n].iter().map(|x| x.abs()).sum::<i128>()).max().unwrap_or(0)
}

fn lcg(n: usize) -> Vec<i128> {
    let mut seed = 12345u64;
    (0..n)
        .map(|_| {
            seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            i128::from(seed >> 24) - (1i128 << 39)
        })
        .collect()
}

// ---------------- exact modular mode ----------------

fn mm_mod(n: usize, x: &[u64], y: &[u64], p: u64) -> Vec<u64> {
    let mut out = vec![0u64; n * n];
    for i in 0..n {
        let xi = &x[i * n..(i + 1) * n];
        let oi = &mut out[i * n..(i + 1) * n];
        let mut acc = vec![0u128; n];
        for (k, &xik) in xi.iter().enumerate() {
            if xik == 0 {
                continue;
            }
            let yk = &y[k * n..(k + 1) * n];
            for (s, &ykj) in acc.iter_mut().zip(yk.iter()) {
                *s += u128::from(xik) * u128::from(ykj);
            }
        }
        for (o, s) in oi.iter_mut().zip(acc.iter()) {
            *o = u64::try_from(s % u128::from(p)).unwrap_or(0);
        }
    }
    out
}

fn mv_mod(n: usize, m: &[u64], v: &[u64], p: u64) -> Vec<u64> {
    (0..n)
        .map(|i| {
            let s: u128 = m[i * n..(i + 1) * n].iter().zip(v.iter()).map(|(a, b)| u128::from(*a) * u128::from(*b)).sum();
            u64::try_from(s % u128::from(p)).unwrap_or(0)
        })
        .collect()
}

fn jump_mod(n: usize, powers: &[Vec<u64>], v: &[u64], steps: u64, p: u64) -> Vec<u64> {
    let mut out = v.to_vec();
    for (j, pj) in powers.iter().enumerate() {
        if (steps >> j) & 1 == 1 {
            out = mv_mod(n, pj, &out, p);
        }
    }
    out
}

fn fingerprint(v: &[u64], p: u64) -> (u64, u64) {
    let mut s = 0u128;
    let mut ws = 0u128;
    for (i, &x) in v.iter().enumerate() {
        s += u128::from(x);
        ws += u128::from(x) * (i as u128 + 1);
    }
    (u64::try_from(s % u128::from(p)).unwrap_or(0), u64::try_from(ws % u128::from(p)).unwrap_or(0))
}

fn exact_mode(op: &Op, je: i128, jb: i128, p: u64, target: u64, name: &str) {
    let t0 = std::time::Instant::now();
    let n = op.n;
    let c24 = gersh(op) + 24;
    let pi = i128::from(p);
    let tmod: Vec<u64> = (0..n * n)
        .map(|k| {
            let (i, j) = (k / n, k % n);
            let v = if i == j { c24 - op.a[k] } else { -op.a[k] };
            u64::try_from(v.rem_euclid(pi)).unwrap_or(0)
        })
        .collect();
    let need = 64 - (target + 64).leading_zeros(); // bits for target + 27 and composition
    let mut powers = vec![tmod.clone()];
    for _ in 1..need {
        let last = powers.last().cloned().unwrap_or_default();
        powers.push(mm_mod(n, &last, &last, p));
    }
    let v0: Vec<u64> = lcg(n).iter().map(|x| u64::try_from(x.rem_euclid(pi)).unwrap_or(0)).collect();
    // (1) jump to 1024 vs sequential
    let mut seq = v0.clone();
    for _ in 0..1024 {
        seq = mv_mod(n, &tmod, &seq, p);
    }
    let ok1 = jump_mod(n, &powers, &v0, 1024, p) == seq;
    // (2) composition
    let half = target / 2;
    let rest = target - half;
    let direct = jump_mod(n, &powers, &v0, target, p);
    let composed = jump_mod(n, &powers, &jump_mod(n, &powers, &v0, half, p), rest, p);
    let ok2 = direct == composed;
    // (3) play 27 frames from the jump spot vs direct jump to target + 27
    let mut play = direct.clone();
    let mut frames = Vec::new();
    for f in 1..=27u64 {
        play = mv_mod(n, &tmod, &play, p);
        if f == 1 || f == 9 || f == 27 {
            frames.push(format!("f{f}:{}", play[0]));
        }
    }
    let ok3 = play == jump_mod(n, &powers, &v0, target + 27, p);
    let (fs, fw) = fingerprint(&direct, p);
    println!(
        "JUMPTO|mode=exact|matrix={name}|n={n}|JE={je}|JB={jb}|c=({c24})/24|modulus={p}|target={target}|squarings={}|seq1024_equal={}|composition_{half}+{rest}_equal={}|replay27_equal={}|state_sum_mod={fs}|state_weighted_mod={fw}|v0_component0={}|frames={}|rounding=NONE|ms={}|json=0",
        need - 1,
        u8::from(ok1),
        u8::from(ok2),
        u8::from(ok3),
        direct[0],
        frames.join(","),
        t0.elapsed().as_millis()
    );
    if !(ok1 && ok2 && ok3) {
        std::process::exit(2);
    }
}

// ---------------- fixed-point physical mode ----------------

fn top_bits(v: &[i128]) -> u32 {
    128 - v.iter().map(|x| x.unsigned_abs()).max().unwrap_or(0).leading_zeros()
}

fn renorm(v: &mut [i128], bits: u32) {
    let b = top_bits(v);
    if b > bits {
        for x in v.iter_mut() {
            *x >>= b - bits;
        }
    }
}

fn mm_fx(n: usize, x: &[i128], y: &[i128]) -> Vec<i128> {
    let mut out = vec![0i128; n * n];
    for i in 0..n {
        let xi = &x[i * n..(i + 1) * n];
        let oi = &mut out[i * n..(i + 1) * n];
        for (k, &xik) in xi.iter().enumerate() {
            if xik == 0 {
                continue;
            }
            for (o, &ykj) in oi.iter_mut().zip(y[k * n..(k + 1) * n].iter()) {
                *o += xik * ykj;
            }
        }
    }
    out
}

fn mv_fx(n: usize, m: &[i128], v: &[i128]) -> Vec<i128> {
    (0..n).map(|i| m[i * n..(i + 1) * n].iter().zip(v.iter()).map(|(a, b)| a * b).sum()).collect()
}

fn energy_micro(op: &Op, v: &[i128], je: i128) -> i128 {
    let mut u = v.to_vec();
    renorm(&mut u, 36);
    let av = mv_fx(op.n, &op.a, &u);
    let num: i128 = (0..op.n).map(|i| op.w[i] * u[i] * av[i]).sum();
    let den: i128 = (0..op.n).map(|i| op.w[i] * u[i] * u[i]).sum();
    let d = 24 * je * den;
    let (q, r) = (num / d, num % d);
    q * 1_000_000 + (r * 1000 / d) * 1000 + ((r * 1000 % d) * 1000) / d
}

/// exact residual radius of v in micro-units, rounded up (big integers)
fn eps_micro(op: &Op, v: &[i128], je: i128) -> (num_bigint::BigInt, num_bigint::BigInt) {
    use num_bigint::BigInt;
    let mut u = v.to_vec();
    renorm(&mut u, 36);
    let av = mv_fx(op.n, &op.a, &u);
    let bu: Vec<BigInt> = u.iter().map(|&x| BigInt::from(x)).collect();
    let ba: Vec<BigInt> = av.iter().map(|&x| BigInt::from(x)).collect();
    let mut nm = BigInt::from(0);
    let mut dn = BigInt::from(0);
    for i in 0..op.n {
        let w = BigInt::from(op.w[i]);
        nm += &w * &bu[i] * &ba[i];
        dn += &w * &bu[i] * &bu[i];
    }
    let mut rr = BigInt::from(0);
    for i in 0..op.n {
        let r = &dn * &ba[i] - &nm * &bu[i];
        rr += BigInt::from(op.w[i]) * &r * &r;
    }
    let denom = BigInt::from(576 * je * je) * &dn * &dn * &dn;
    let q = (rr * BigInt::from(1_000_000_000_000u64) + &denom - BigInt::from(1)) / &denom;
    let mut e = q.sqrt();
    if &e * &e < q {
        e += 1;
    }
    let th = nm * BigInt::from(1_000_000) / (dn * BigInt::from(24 * je));
    (th, e)
}

fn fixed_mode(op: &Op, je: i128, jb: i128, kmax: u32, frames: usize, name: &str) {
    let t0 = std::time::Instant::now();
    let n = op.n;
    let c24 = gersh(op) + 24;
    let mut t: Vec<i128> = (0..n * n).map(|k| if k / n == k % n { c24 - op.a[k] } else { -op.a[k] }).collect();
    renorm(&mut t, 40);
    let target = 10u64.pow(kmax);
    let need = 64 - target.leading_zeros();
    let mut powers = vec![t];
    for _ in 1..need {
        let last = powers.last().cloned().unwrap_or_default();
        let mut sq = mm_fx(n, &last, &last);
        renorm(&mut sq, 40);
        powers.push(sq);
    }
    let v0 = lcg(n);
    let jump = |steps: u64| {
        let mut v = v0.clone();
        for (j, pj) in powers.iter().enumerate() {
            if (steps >> j) & 1 == 1 {
                v = mv_fx(n, pj, &v);
                renorm(&mut v, 40);
            }
        }
        v
    };
    let mut stages = Vec::new();
    for k in 0..=kmax {
        let v = jump(10u64.pow(k));
        stages.push(format!("1e{k}:{}", energy_micro(op, &v, je)));
    }
    // play frames from the far jump spot
    let mut v = jump(target);
    let (th, eps) = eps_micro(op, &v, je);
    let mut played = Vec::new();
    for f in 1..=frames {
        v = mv_fx(n, &powers[0], &v);
        renorm(&mut v, 40);
        if f <= 3 || f == frames {
            played.push(format!("+{f}:{}", energy_micro(op, &v, je)));
        }
    }
    println!(
        "JUMPTO|mode=fixed|matrix={name}|n={n}|JE={je}|JB={jb}|c=({c24})/24|squarings={}|E_micro_at_step={}|play_from_1e{kmax}={}|E_at_1e{kmax}={th}/1000000|eps_up={eps}/1000000|eigenvalue_in=[{},{}]/1000000|ms={}|kind=MEASUREMENT_WITH_RESIDUAL_BOUND|json=0",
        need - 1,
        stages.join(","),
        played.join(","),
        &th - &eps,
        &th + &eps + 1,
        t0.elapsed().as_millis()
    );
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 7 {
        eprintln!("usage: jumpto MATRIX JE JB exact P N | jumpto MATRIX JE JB fixed KMAX FRAMES");
        std::process::exit(1);
    }
    let p = |i: usize| a[i].parse::<i128>().unwrap_or(-1);
    let (je, jb) = (p(2), p(3));
    let op = match load(&a[1], je, jb) {
        Ok(o) => o,
        Err(e) => {
            println!("JUMPTO|error={e}|json=0");
            std::process::exit(1);
        }
    };
    let name = a[1].rsplit('/').next().unwrap_or("");
    match a[4].as_str() {
        "exact" => {
            let modulus = u64::try_from(p(5)).unwrap_or(0);
            let target = u64::try_from(p(6)).unwrap_or(0);
            if !(3..(1u64 << 31)).contains(&modulus) || !(2..=(1u64 << 40)).contains(&target) {
                println!("JUMPTO|error=bad_modulus_or_target|json=0");
                std::process::exit(1);
            }
            exact_mode(&op, je, jb, modulus, target, name);
        }
        "fixed" => {
            let kmax = u32::try_from(p(5)).unwrap_or(0).min(12);
            let frames = usize::try_from(p(6)).unwrap_or(27);
            fixed_mode(&op, je, jb, kmax, frames, name);
        }
        _ => {
            println!("JUMPTO|error=mode_must_be_exact_or_fixed|json=0");
            std::process::exit(1);
        }
    }
}
