//! cantorint: the Cantor-27 drive on the finite S3 sector, again, in integers only.
//!
//!   cantorint run MATRIX R THREADS [P=256] [K=auto] [sabotage=NAME]
//!
//! The same experiment as the floating-point run kept in results/cantor-integer-2026-11-03/float-run-2026-10-31: H_t = E + (r + f(c_t)/27) M,
//! U_t = exp(-i H_t / 27), 729 slots of the Cantor signal, from basis state 0, with the controls cantor, zero, inverted and rotated_one.
//!
//! No square roots: in orbit-function form H has integer entries z_ij, with w_i z_ij = w_j z_ji, and it is self-adjoint in the weighted inner product
//! <f, g>_W = sum w_i conj(f_i) g_i. Starting from e_b, the probabilities are |Phi_b|^2, and sum w_i m_i |Phi_i|^2 / w_b for the magnetic expectation.
//!
//! No growth of error: with X = -i (27 H - 27 c) / 729, anti-self-adjoint in the weighted norm, each slot is the Taylor sum of exp(X) in fixed point with 2^-P as its unit.
//! The exact step is unitary in that norm, so the slots' errors add. A slot's error is at most
//!   K e^x sqrt(2 sum w) units from rounding, and x^(K+1)/(K+1)! (sqrt(w_b) + 1) from truncation, where x >= ||X||,
//! and x comes from the largest row sum of 27 H - 27 c, since the spectrum is real and the row sum bounds the spectral radius.
//! Every bound is computed here in integers, and each printed value is an enclosure at scale 10^30.
//!
//! Sabotages for its controls: short_taylor, low_precision, break_symmetry, wrong_pulse. Exits 2 if a bound or a check fails. Integer only, Rust 1.81, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use num_bigint::BigInt;
use num_traits::{Signed, Zero};

#[path = "../../../torusl/src/sha.rs"]
mod sha;

const SIGNAL_SHA256: &str = "1f48fa5083237cd4bdadc3f6c4f9094b864ca1386d7d09b5b27c19b5f27f6913";
const LIMBS: usize = 6;
const HEADROOM_BITS: u32 = 360;
const SCALE_DIGITS: u32 = 30;

/// A two's-complement integer of 384 bits. Additions and products wrap, and `bits` is checked on every term, so none does.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
struct Fx([u64; LIMBS]);

impl Fx {
    const ZERO: Fx = Fx([0; LIMBS]);

    fn shifted_one(p: u32) -> Fx {
        let mut v = [0u64; LIMBS];
        v[(p / 64) as usize] = 1u64 << (p % 64);
        Fx(v)
    }

    fn is_negative(&self) -> bool {
        self.0[LIMBS - 1] >> 63 == 1
    }

    fn add(&mut self, o: &Fx) {
        let mut carry = 0u64;
        for (a, b) in self.0.iter_mut().zip(o.0.iter()) {
            let (s1, c1) = a.overflowing_add(*b);
            let (s2, c2) = s1.overflowing_add(carry);
            *a = s2;
            carry = u64::from(c1) + u64::from(c2);
        }
    }

    fn neg(&self) -> Fx {
        let mut out = [0u64; LIMBS];
        let mut carry = 1u64;
        for (a, b) in out.iter_mut().zip(self.0.iter()) {
            let (s, c) = (!*b).overflowing_add(carry);
            *a = s;
            carry = u64::from(c);
        }
        Fx(out)
    }

    /// self += o * m.
    fn add_mul(&mut self, o: &Fx, m: i64) {
        let (mag, negative) = (m.unsigned_abs(), m < 0);
        let mut product = [0u64; LIMBS];
        let mut carry = 0u128;
        for (a, b) in product.iter_mut().zip(o.0.iter()) {
            let wide = u128::from(*b) * u128::from(mag) + carry;
            *a = wide as u64;
            carry = wide >> 64;
        }
        let p = Fx(product);
        if negative {
            self.add(&p.neg());
        } else {
            self.add(&p);
        }
    }

    /// floor(self / d), for d > 0.
    fn floor_div(&self, d: u64) -> Fx {
        let negative = self.is_negative();
        let mag = if negative { self.neg() } else { *self };
        let mut q = [0u64; LIMBS];
        let mut rem = 0u128;
        for i in (0..LIMBS).rev() {
            let cur = (rem << 64) | u128::from(mag.0[i]);
            q[i] = (cur / u128::from(d)) as u64;
            rem = cur % u128::from(d);
        }
        let mut out = Fx(q);
        if negative {
            if rem != 0 {
                out.add(&Fx::shifted_one(0));
            }
            out = out.neg();
        }
        out
    }

    fn bits(&self) -> u32 {
        let mag = if self.is_negative() { self.neg() } else { *self };
        for i in (0..LIMBS).rev() {
            if mag.0[i] != 0 {
                return 64 * i as u32 + 64 - mag.0[i].leading_zeros();
            }
        }
        0
    }

    fn big(&self) -> BigInt {
        let negative = self.is_negative();
        let mag = if negative { self.neg() } else { *self };
        let mut out = BigInt::from(0);
        for i in (0..LIMBS).rev() {
            out = (out << 64u32) + BigInt::from(mag.0[i]);
        }
        if negative {
            -out
        } else {
            out
        }
    }
}

fn num<T: std::str::FromStr>(s: &str) -> Result<T, String> {
    s.parse().map_err(|_| format!("bad number {s}"))
}

struct Sector {
    n: usize,
    w: Vec<i64>,
    m: Vec<i64>,
    /// Off-diagonal entries of each row, and the electric diagonal.
    rows: Vec<Vec<(usize, i64)>>,
    diag: Vec<i64>,
    sha: String,
    nnz: usize,
}

fn read_sector(path: &str, break_symmetry: bool) -> Result<Sector, String> {
    let raw = std::fs::read(path).map_err(|e| format!("{path}: {e}"))?;
    let sha_text = sha::sha256_hex(&raw);
    let text = std::str::from_utf8(&raw).map_err(|e| e.to_string())?;
    let mut tokens = Vec::new();
    for t in text.split_ascii_whitespace() {
        tokens.push(num::<i64>(t)?);
    }
    let n = *tokens.first().ok_or("an empty sector")? as usize;
    if tokens.len() < 1 + 2 * n || (tokens.len() - 1 - 2 * n) % 3 != 0 {
        return Err("a sector of another layout".into());
    }
    let w: Vec<i64> = tokens[1..1 + n].to_vec();
    let m: Vec<i64> = tokens[1 + n..1 + 2 * n].to_vec();
    if w.iter().any(|x| *x <= 0) || m.iter().any(|x| *x < 0) {
        return Err("a weight at or below 0, or a negative magnetic entry".into());
    }
    let mut rows = vec![Vec::new(); n];
    let mut diag = vec![0i64; n];
    let mut seen = std::collections::HashSet::new();
    let mut nnz = 0usize;
    for t in tokens[1 + 2 * n..].chunks_exact(3) {
        let (i, j, z) = (t[0] as usize, t[1] as usize, t[2]);
        if i > j || j >= n || !seen.insert((i, j)) {
            return Err("an entry outside the upper triangle, or repeated".into());
        }
        if i == j {
            diag[i] = z;
            nnz += 1;
            continue;
        }
        let top = w[i] * z;
        if top % w[j] != 0 {
            return Err(format!("the reverse of ({i},{j}) is not an integer"));
        }
        rows[i].push((j, z));
        rows[j].push((i, top / w[j]));
        nnz += 2;
    }
    if break_symmetry {
        rows[0][0].1 += 1;
    }
    // The defining identity, entry by entry, from the rows as they will be used.
    let lookup: std::collections::HashMap<(usize, usize), i64> = rows.iter().enumerate().flat_map(|(i, r)| r.iter().map(move |&(j, z)| ((i, j), z))).collect();
    for (&(i, j), &z) in &lookup {
        if w[i] * z != w[j] * lookup.get(&(j, i)).copied().unwrap_or(0) {
            return Err("WEIGHTED_SELF_ADJOINT|result=FAIL|json=0".into());
        }
    }
    Ok(Sector { n, w, m, rows, diag, sha: sha_text, nnz })
}

/// The Cantor signal, from its digits: 0 when a base-3 digit is 1, else 1 or 2 by the parity of the digits equal to 2.
fn cantor_signal() -> Result<Vec<i64>, String> {
    let mut raw = Vec::with_capacity(729);
    for index in 0..729u32 {
        let (mut v, mut twos, mut hit) = (index, 0u32, false);
        for _ in 0..6 {
            let d = v % 3;
            v /= 3;
            if d == 1 {
                hit = true;
                break;
            }
            twos += d / 2;
        }
        raw.push(if hit {
            0u8
        } else if twos % 2 == 0 {
            1u8
        } else {
            2u8
        });
    }
    if sha::sha256_hex(&raw) != SIGNAL_SHA256 {
        return Err("the Cantor signal differs".into());
    }
    Ok(raw.iter().map(|c| [0i64, 1, -1][*c as usize]).collect())
}

/// 27 H - 27 c, for one pulse value.
struct Step {
    rows: Vec<Vec<(usize, i64)>>,
    diag: [Vec<i64>; 3],
    row_sum: i64,
}

fn step_matrix(s: &Sector, r: i64, c: i64) -> Step {
    let rows: Vec<Vec<(usize, i64)>> = s.rows.iter().map(|row| row.iter().map(|&(j, z)| (j, 27 * z)).collect()).collect();
    let make = |f: i64| -> Vec<i64> { (0..s.n).map(|i| 27 * s.diag[i] + (27 * r + f) * s.m[i] - 27 * c).collect() };
    let diag = [make(0), make(1), make(-1)];
    let mut row_sum = 0i64;
    for i in 0..s.n {
        let off: i64 = rows[i].iter().map(|e| e.1.abs()).sum();
        for d in &diag {
            row_sum = row_sum.max(off + d[i].abs());
        }
    }
    Step { rows, diag, row_sum }
}

fn big_pow(base: i64, e: u32) -> BigInt {
    let mut out = BigInt::from(1);
    for _ in 0..e {
        out *= base;
    }
    out
}

fn isqrt_up(v: &BigInt) -> BigInt {
    // The smallest integer whose square is at least v.
    let mut low = BigInt::from(0);
    let mut high = BigInt::from(1);
    while &high * &high < *v {
        high *= 2;
    }
    while &high - &low > BigInt::from(1) {
        let mid: BigInt = (&low + &high) / 2;
        if &mid * &mid >= *v {
            high = mid;
        } else {
            low = mid;
        }
    }
    high
}

/// The least K with x^(K+1) / (K+1)! <= 2^-P, for x = R / 729.
fn least_k(row_sum: i64, p: u32) -> u32 {
    let mut k = 0u32;
    let mut top = BigInt::from(row_sum) << p;
    let mut bottom = BigInt::from(729);
    while top > bottom {
        k += 1;
        top *= row_sum;
        bottom *= 729i64 * (i64::from(k) + 1);
    }
    k
}

fn remainder_holds(row_sum: i64, p: u32, k: u32) -> bool {
    let mut top = BigInt::from(1) << p;
    let mut bottom = BigInt::from(1);
    for i in 1..=(i64::from(k) + 1) {
        top *= row_sum;
        bottom *= 729i64 * i;
    }
    top <= bottom
}

struct Bound {
    k: u32,
    delta: BigInt,
    delta_bits: u64,
}

/// In units of 2^-P, and in the weighted norm: 729 slots of K 3^ceil(x) ceil(sqrt(2 sum w)) from rounding, and of ceil(sqrt(w_b)) + 1 from truncation.
fn error_bound(s: &Sector, st: &Step, k: u32, basis: usize) -> Bound {
    let x_ceil = (st.row_sum + 728) / 729;
    let exp_up = big_pow(3, x_ceil as u32);
    let sum_w: i64 = s.w.iter().sum();
    let d = isqrt_up(&BigInt::from(2 * sum_w));
    let per_slot = BigInt::from(k) * exp_up * d + isqrt_up(&BigInt::from(s.w[basis])) + BigInt::from(1);
    let delta = per_slot * 729i64;
    let delta_bits = delta.bits();
    Bound { k, delta, delta_bits }
}

struct Run {
    re: Vec<Fx>,
    im: Vec<Fx>,
    start: usize,
    /// The largest bit length seen in a term.
    top_bits: u32,
}

impl Run {
    fn new(n: usize, basis: usize, p: u32) -> Run {
        let mut re = vec![Fx::ZERO; n];
        re[basis] = Fx::shifted_one(p);
        Run { re, im: vec![Fx::ZERO; n], start: basis, top_bits: 0 }
    }

    /// One slot of exp(-i A / 729) when forward, of exp(+i A / 729) when not.
    fn slot(&mut self, st: &Step, pulse: i64, k: u32, forward: bool, tre: &mut [Fx], tim: &mut [Fx]) -> Result<(), String> {
        let d = &st.diag[match pulse {
            0 => 0,
            1 => 1,
            _ => 2,
        }];
        tre.copy_from_slice(&self.re);
        tim.copy_from_slice(&self.im);
        let n = self.re.len();
        let mut yre = vec![Fx::ZERO; n];
        let mut yim = vec![Fx::ZERO; n];
        for term in 1..=k {
            for i in 0..n {
                let (mut a, mut b) = (Fx::ZERO, Fx::ZERO);
                a.add_mul(&tre[i], d[i]);
                b.add_mul(&tim[i], d[i]);
                for &(j, z) in &st.rows[i] {
                    a.add_mul(&tre[j], z);
                    b.add_mul(&tim[j], z);
                }
                yre[i] = a;
                yim[i] = b;
            }
            let den = 729u64 * u64::from(term);
            for i in 0..n {
                // -i (a + i b) = b - i a; +i (a + i b) = -b + i a.
                let (nr, ni) = if forward { (yim[i], yre[i].neg()) } else { (yim[i].neg(), yre[i]) };
                tre[i] = nr.floor_div(den);
                tim[i] = ni.floor_div(den);
                self.top_bits = self.top_bits.max(tre[i].bits()).max(tim[i].bits());
                self.re[i].add(&tre[i]);
                self.im[i].add(&tim[i]);
            }
            if self.top_bits > HEADROOM_BITS {
                return Err(format!("a term of {} bits, past the headroom", self.top_bits));
            }
        }
        Ok(())
    }

    /// sum w_i weight_i |Phi_i|^2, in units of 2^-2P.
    fn quadratic(&self, s: &Sector, weight: impl Fn(usize) -> i64) -> BigInt {
        let mut out = BigInt::from(0);
        for i in 0..s.n {
            let (a, b) = (self.re[i].big(), self.im[i].big());
            out += (&a * &a + &b * &b) * (s.w[i] * weight(i));
        }
        out
    }
}

/// The floor and ceiling of value * 10^30, for value = top / bottom, widened by err, which is in units of 1 / err_den.
fn enclosure(top: &BigInt, bottom: &BigInt, err: &BigInt, err_den: &BigInt) -> (BigInt, BigInt) {
    let scale = BigInt::from(10).pow(SCALE_DIGITS);
    let low_top = top * err_den - err * bottom;
    let high_top = top * err_den + err * bottom;
    let den = bottom * err_den;
    let lo = floor_div(&(&low_top * &scale), &den);
    let hi = -floor_div(&(-(&high_top * &scale)), &den);
    (lo, hi)
}

fn floor_div(a: &BigInt, b: &BigInt) -> BigInt {
    let q = a / b;
    let r = a - &q * b;
    if !r.is_zero() && (r.is_negative() != b.is_negative()) {
        q - 1
    } else {
        q
    }
}

struct Outcome {
    name: &'static str,
    run: Run,
    magnetic: (BigInt, BigInt),
    ret: (BigInt, BigInt),
    norm_dev_max: BigInt,
    norm_ok: bool,
    inverse_dev2: BigInt,
    inverse_ok: bool,
    secs: u64,
}

struct Params<'a> {
    s: &'a Sector,
    st: &'a Step,
    k: u32,
    p: u32,
    basis: usize,
    delta: &'a BigInt,
}

fn run_control(par: &Params, name: &'static str, seq: &[i64]) -> Result<Outcome, String> {
    let t0 = std::time::Instant::now();
    let (s, st, k, p, basis) = (par.s, par.st, par.k, par.p, par.basis);
    let n = s.n;
    let (mut tre, mut tim) = (vec![Fx::ZERO; n], vec![Fx::ZERO; n]);
    let mut run = Run::new(n, basis, p);
    let w_b = BigInt::from(s.w[basis]);
    let unit2 = BigInt::from(1) << (2 * p);
    // The norm of the exact state is w_b. Each row below compares with (2 delta sqrt(w_b) + delta^2), the allowed distance of the computed square norm, in units of 2^-2P.
    let root_up = isqrt_up(&w_b);
    let allowed = BigInt::from(2) * par.delta * &root_up * (BigInt::from(1) << p) + par.delta * par.delta;
    let mut norm_dev_max = BigInt::from(0);
    let mut norm_ok = true;
    for &pulse in seq {
        run.slot(st, pulse, k, true, &mut tre, &mut tim)?;
        let dev = (run.quadratic(s, |_| 1) - &w_b * &unit2).abs();
        norm_ok &= dev <= allowed;
        if dev > norm_dev_max {
            norm_dev_max = dev;
        }
    }
    // Observables of the state at the end of the forward run.
    let m_max = s.m.iter().copied().max().unwrap_or(0).max(1);
    // |q~ - q| <= ||A|| (2 Delta + Delta^2) for a normalised state, with Delta = delta 2^-P >= delta 2^-P / sqrt(w_b).
    let err_top = par.delta * BigInt::from(2) * (BigInt::from(1) << p) + par.delta * par.delta;
    let err_den = unit2.clone();
    let magnetic_top = run.quadratic(s, |i| s.m[i]);
    let bottom_m = &w_b * &unit2;
    let magnetic = enclosure(&magnetic_top, &bottom_m, &(&err_top * m_max), &err_den);
    let (a, b) = (run.re[basis].big(), run.im[basis].big());
    let ret_top = &a * &a + &b * &b;
    let ret = enclosure(&ret_top, &unit2, &err_top, &err_den);
    // The way back.
    let end = Run { re: run.re.clone(), im: run.im.clone(), start: basis, top_bits: run.top_bits };
    for &pulse in seq.iter().rev() {
        run.slot(st, pulse, k, false, &mut tre, &mut tim)?;
    }
    let one = Fx::shifted_one(p).big();
    let mut inverse_dev2 = BigInt::from(0);
    for i in 0..n {
        let mut x = run.re[i].big();
        if i == run.start {
            x -= &one;
        }
        let y = run.im[i].big();
        inverse_dev2 += (&x * &x + &y * &y) * s.w[i];
    }
    // Forward and back each add at most delta to the weighted distance from e_b.
    let limit = BigInt::from(2) * par.delta;
    let inverse_ok = inverse_dev2 <= &limit * &limit;
    Ok(Outcome { name, run: end, magnetic, ret, norm_dev_max, norm_ok, inverse_dev2, inverse_ok, secs: t0.elapsed().as_secs() })
}

fn fidelity(s: &Sector, a: &Run, b: &Run, basis: usize, p: u32, delta: &BigInt) -> (BigInt, BigInt) {
    let (mut cr, mut ci) = (BigInt::from(0), BigInt::from(0));
    for i in 0..s.n {
        let (ar, ai, br, bi) = (a.re[i].big(), a.im[i].big(), b.re[i].big(), b.im[i].big());
        cr += (&ar * &br + &ai * &bi) * s.w[i];
        ci += (&ar * &bi - &ai * &br) * s.w[i];
    }
    let w_b = BigInt::from(s.w[basis]);
    let bottom = (&w_b * &w_b) << (4 * p);
    let top = &cr * &cr + &ci * &ci;
    // eta = 2 Delta + Delta^2 on the overlap, and eta (2 + eta) on its square, with Delta = delta 2^-P.
    let unit = BigInt::from(1) << p;
    let eta_top = BigInt::from(2) * delta * &unit + delta * delta;
    let eta_den = &unit * &unit;
    let err_top = &eta_top * BigInt::from(2) * &eta_den + &eta_top * &eta_top;
    let err_den = &eta_den * &eta_den;
    enclosure(&top, &bottom, &err_top, &err_den)
}

fn run_all(a: &[String]) -> Result<i32, String> {
    let (matrix, r, threads) = (&a[2], num::<i64>(&a[3])?, num::<usize>(&a[4])?);
    let mut p = 256u32;
    let mut k_arg: Option<u32> = None;
    let mut sabotage = "none";
    for extra in &a[5..] {
        if let Some(v) = extra.strip_prefix("P=") {
            p = num(v)?;
        } else if let Some(v) = extra.strip_prefix("K=") {
            k_arg = Some(num(v)?);
        } else if let Some(v) = extra.strip_prefix("sabotage=") {
            sabotage = v;
        } else {
            return Err(format!("an argument of another kind: {extra}"));
        }
    }
    if sabotage == "low_precision" {
        p = 48;
    }
    let t0 = std::time::Instant::now();
    let s = read_sector(matrix, sabotage == "break_symmetry")?;
    let signal = cantor_signal()?;
    let basis = 0usize;
    let c = 6 * r + 24;
    let st = step_matrix(&s, r, c);
    let auto_k = least_k(st.row_sum, p);
    let k = if sabotage == "short_taylor" { auto_k / 2 } else { k_arg.unwrap_or(auto_k) };
    let remainder_ok = remainder_holds(st.row_sum, p, k);
    let bound = error_bound(&s, &st, k, basis);
    // The whole method asks for an error far below the printed scale: delta 2^-P < 2^-110.
    let bound_ok = bound.delta_bits + 110 <= u64::from(p);
    let positive = signal.iter().filter(|x| **x == 1).count();
    let negative = signal.iter().filter(|x| **x == -1).count();
    println!("CANTOR_INT|schema=CANTOR-S3-INTEGER-V1|arithmetic=integers_only|matrix_sha256={}|signal_sha256={SIGNAL_SHA256}|states={}|nnz={}|basis={basis}|samples={}|positive={positive}|negative={negative}|zero={}|r={r}|lambda=1/27|dt=1/27|c={c}|P={p}|K={}|auto_K={auto_k}|R={}|sabotage={sabotage}|json=0", s.sha, s.n, s.nnz, signal.len(), signal.len() - positive - negative, bound.k, st.row_sum);
    println!("CANTOR_INT_BOUND|x_upper={}/729|remainder_at_most_one_unit={}|delta_units_bits={}|delta_below_2^-110={}|weighted_self_adjoint=PASS|json=0", st.row_sum, u8::from(remainder_ok), bound.delta_bits, u8::from(bound_ok));
    if !remainder_ok || !bound_ok {
        println!("CANTOR_INT_VERDICT|result=FAIL|reason=the_error_bound_does_not_hold_at_these_settings|json=0");
        return Ok(2);
    }
    let mut seq_cantor = signal.clone();
    if sabotage == "wrong_pulse" {
        let at = seq_cantor.iter().position(|x| *x == -1).ok_or("no negative pulse")?;
        seq_cantor[at] = 1;
    }
    let zero = vec![0i64; signal.len()];
    let inverted: Vec<i64> = seq_cantor.iter().map(|x| -*x).collect();
    let mut rotated = seq_cantor.clone();
    rotated.rotate_left(1);
    let jobs: Vec<(&'static str, Vec<i64>)> = vec![("cantor", seq_cantor), ("zero", zero), ("inverted", inverted), ("rotated_one", rotated)];
    let par = Params { s: &s, st: &st, k, p, basis, delta: &bound.delta };
    let threads = threads.max(1);
    let mut outcomes: Vec<Outcome> = Vec::new();
    for group in jobs.chunks(threads) {
        let done: Vec<Result<Outcome, String>> = std::thread::scope(|sc| {
            let hs: Vec<_> = group
                .iter()
                .map(|(name, seq)| {
                    let par = &par;
                    sc.spawn(move || run_control(par, name, seq))
                })
                .collect();
            hs.into_iter().map(|h| h.join().unwrap_or_else(|_| Err("a thread stopped".into()))).collect()
        });
        for d in done {
            outcomes.push(d?);
        }
    }
    let mut clean = true;
    for o in &outcomes {
        clean &= o.norm_ok && o.inverse_ok;
        println!(
            "RUN|control={}|magnetic_expectation_lo_e30={}|magnetic_expectation_hi_e30={}|return_probability_lo_e30={}|return_probability_hi_e30={}|norm_within_bound={}|norm_dev_bits={}|inverse_within_bound={}|inverse_dev2_bits={}|top_bits={}|secs={}|json=0",
            o.name,
            o.magnetic.0,
            o.magnetic.1,
            o.ret.0,
            o.ret.1,
            u8::from(o.norm_ok),
            o.norm_dev_max.bits(),
            u8::from(o.inverse_ok),
            o.inverse_dev2.bits(),
            o.run.top_bits,
            o.secs
        );
    }
    let f = fidelity(&s, &outcomes[0].run, &outcomes[1].run, basis, p, &bound.delta);
    println!("COMPARE|driven_vs_zero_fidelity_lo_e30={}|driven_vs_zero_fidelity_hi_e30={}|json=0", f.0, f.1);
    println!("CANTOR_INT_VERDICT|result={}|scope=finite_sector_exact_enclosure|secs={}|json=0", if clean { "PASS" } else { "FAIL" }, t0.elapsed().as_secs());
    Ok(if clean { 0 } else { 2 })
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let r = match a.get(1).map(String::as_str) {
        Some("run") if a.len() >= 5 => run_all(&a),
        _ => Err("usage: cantorint run MATRIX R THREADS [P=256] [K=auto] [sabotage=NAME]".into()),
    };
    match r {
        Ok(code) => std::process::exit(code),
        Err(e) => {
            println!("CANTOR_INT_ERROR|{e}|json=0");
            std::process::exit(2);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn draw(st: &mut u64) -> u64 {
        *st = st.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407);
        *st
    }

    fn sample(st: &mut u64) -> Fx {
        // A value of a few hundred bits with a random sign.
        let mut v = [0u64; LIMBS];
        let top = (draw(st) % 5) as usize + 1;
        for limb in v.iter_mut().take(top) {
            *limb = draw(st);
        }
        let f = Fx(v);
        if draw(st) >> 63 == 1 {
            f.neg()
        } else {
            f
        }
    }

    #[test]
    fn fixed_width_arithmetic_agrees_with_big_integers() {
        let mut st = 42u64;
        for _ in 0..20_000 {
            let (a, b) = (sample(&mut st), sample(&mut st));
            let (ba, bb) = (a.big(), b.big());
            let m = (draw(&mut st) % 200_001) as i64 - 100_000;
            let d = draw(&mut st) % 400_000 + 1;
            let mut sum = a;
            sum.add(&b);
            assert_eq!(sum.big(), &ba + &bb);
            let mut x = a;
            x.add_mul(&b, m);
            assert_eq!(x.big(), &ba + &bb * m);
            assert_eq!(a.floor_div(d).big(), floor_div(&ba, &BigInt::from(d)));
            assert_eq!(a.neg().big(), -&ba);
            assert_eq!(u64::from(a.bits()), ba.bits());
        }
    }

    #[test]
    fn floor_rounds_down_on_both_sides() {
        let seven = Fx([7, 0, 0, 0, 0, 0]);
        assert_eq!(seven.floor_div(2).big(), BigInt::from(3));
        assert_eq!(seven.neg().floor_div(2).big(), BigInt::from(-4));
        assert_eq!(Fx::ZERO.floor_div(5).big(), BigInt::from(0));
        assert_eq!(seven.neg().floor_div(7).big(), BigInt::from(-1));
    }

    #[test]
    fn the_signal_has_its_counts_and_hash() {
        let s = cantor_signal().unwrap();
        assert_eq!(s.len(), 729);
        assert_eq!(s.iter().filter(|x| **x == 1).count(), 32);
        assert_eq!(s.iter().filter(|x| **x == -1).count(), 32);
    }

    fn two_state() -> Sector {
        // w = (1, 3), and E with z_01 = -3, z_10 = -1, diagonal 3 and 1: its eigenvalues are 0 and 4. M = diag(0, 1).
        Sector { n: 2, w: vec![1, 3], m: vec![0, 1], rows: vec![vec![(1, -3)], vec![(0, -1)]], diag: vec![3, 1], sha: String::new(), nnz: 4 }
    }

    fn evolve(s: &Sector, st: &Step, seq: &[i64], k: u32, p: u32) -> Run {
        let (mut tre, mut tim) = (vec![Fx::ZERO; s.n], vec![Fx::ZERO; s.n]);
        let mut run = Run::new(s.n, 0, p);
        for &q in seq {
            run.slot(st, q, k, true, &mut tre, &mut tim).unwrap();
        }
        run
    }

    #[test]
    fn a_step_conserves_the_weighted_norm_and_forward_then_back_returns() {
        let s = two_state();
        let st = step_matrix(&s, 2, 3);
        let p = 200;
        let k = least_k(st.row_sum, p);
        assert!(remainder_holds(st.row_sum, p, k));
        assert!(!remainder_holds(st.row_sum, p, k / 2));
        let seq = [0i64, 1, -1, 0, 1, 1, -1];
        let mut run = evolve(&s, &st, &seq, k, p);
        let unit2 = BigInt::from(1) << (2 * p);
        let dev = (run.quadratic(&s, |_| 1) - &unit2).abs();
        assert!(dev.bits() < u64::from(p) + 40, "norm drift of {} bits", dev.bits());
        let (mut tre, mut tim) = (vec![Fx::ZERO; 2], vec![Fx::ZERO; 2]);
        for &q in seq.iter().rev() {
            run.slot(&st, q, k, false, &mut tre, &mut tim).unwrap();
        }
        let back = (run.re[0].big() - Fx::shifted_one(p).big()).abs();
        assert!(back.bits() < 40, "the way back is off by {} bits", back.bits());
    }

    #[test]
    fn two_half_steps_agree_with_one_step() {
        // exp(-i A / 729) from exp(-i (A/2) / 729) twice, on a matrix with even entries.
        let s = two_state();
        let st = step_matrix(&s, 2, 4);
        let halved = Step { rows: st.rows.iter().map(|r| r.iter().map(|&(j, z)| (j, 2 * z)).collect()).collect(), diag: [st.diag[0].iter().map(|x| 2 * x).collect(), st.diag[1].iter().map(|x| 2 * x).collect(), st.diag[2].iter().map(|x| 2 * x).collect()], row_sum: 2 * st.row_sum };
        let p = 200;
        let whole = evolve(&s, &halved, &[0], least_k(halved.row_sum, p), p);
        let parts = evolve(&s, &st, &[0, 0], least_k(st.row_sum, p), p);
        for i in 0..2 {
            assert!((whole.re[i].big() - parts.re[i].big()).abs().bits() < 40);
            assert!((whole.im[i].big() - parts.im[i].big()).abs().bits() < 40);
        }
    }

    #[test]
    fn the_exact_two_level_answer() {
        // With M dropped (r = 0, pulse 0) H has eigenvalues 0 and 4 and A/729 = (27 H - 27 c)/729. From e_0 the return probability after n slots is
        // 1 - 2 * a * b * (1 - cos(4 n / 27)) with a, b the weights 1/4, 3/4. At n = 27 pi k this would be exact, so test the identity with the norm alone and the spectrum of 2 x 2:
        // the computed amplitude at e_0 must equal 1/4 + (3/4) exp(-4 i n / 27) up to the phase of c, and its modulus squared is 5/8 + (3/8) cos(4 n / 27).
        let s = Sector { n: 2, w: vec![1, 3], m: vec![0, 0], rows: vec![vec![(1, -3)], vec![(0, -1)]], diag: vec![3, 1], sha: String::new(), nnz: 4 };
        let st = step_matrix(&s, 0, 0);
        let p = 200;
        let k = least_k(st.row_sum, p);
        let run = evolve(&s, &st, &[0], k, p);
        let (a, b) = (run.re[0].big(), run.im[0].big());
        let ret = &a * &a + &b * &b;
        // cos(4/27) from its series in integers, at the same unit.
        let unit = BigInt::from(1) << p;
        let mut term = unit.clone();
        let mut cos = unit.clone();
        for j in 1..40i64 {
            term = -(term * 16i64) / (729i64 * (2 * j - 1) * (2 * j));
            cos += &term;
        }
        let want = (BigInt::from(5) * &unit * &unit + BigInt::from(3) * &cos * &unit) / 8i64;
        assert!((ret - want).abs().bits() < u64::from(p) + 20);
    }
}
