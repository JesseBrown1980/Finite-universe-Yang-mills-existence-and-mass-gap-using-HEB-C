//! Independent leading-minor sign kernel (separate from the production
//! shellschur / Schur path). Reads an integer symmetric matrix B and prints the
//! sign of every leading principal minor D_1..D_n, from which the caller
//! counts negative eigenvalues (Sylvester / Jacobi: sign changes of
//! 1, D_1, ..., D_n when no minor is zero).
//!
//! Each D_k is computed modulo distinct primes p < 2^62 (Montgomery arithmetic,
//! elimination without pivoting) until the product of the moduli exceeds twice
//! the Hadamard bound of every leading minor. Its sign is read from balanced
//! mixed-radix (Garner) digits: with every digit in (-p_i/2, p_i/2], the sign of
//! the value is the sign of its last nonzero digit. A zero pivot modulo a prime
//! drops that prime; an exactly zero minor is reported as sign 0.
//!
//! Input (text): n, then n lines of n integers (row-major).
//! Output: INDEP_MINORS|n=..|primes=..|hadamard_bits=..|signs=<string of + - 0>|json=0
//! Integer-only, Rust 1.81, no external crates.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use std::io::Read;

fn is_prime(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    for p in [2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        if n % p == 0 {
            return n == p;
        }
    }
    let (mut d, mut s) = (n - 1, 0);
    while d % 2 == 0 {
        d /= 2;
        s += 1;
    }
    let mulm = |a: u64, b: u64| ((a as u128 * b as u128) % n as u128) as u64;
    'w: for a in [2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        let (mut x, mut e, mut b) = (1u64, d, a);
        while e > 0 {
            if e & 1 == 1 {
                x = mulm(x, b);
            }
            b = mulm(b, b);
            e >>= 1;
        }
        if x == 1 || x == n - 1 {
            continue;
        }
        for _ in 1..s {
            x = mulm(x, x);
            if x == n - 1 {
                continue 'w;
            }
        }
        return false;
    }
    true
}

/// Montgomery arithmetic modulo an odd p < 2^62, R = 2^64.
struct Mont {
    p: u64,
    pinv: u64, // -p^-1 mod 2^64
    r2: u64,   // R^2 mod p
}

impl Mont {
    fn new(p: u64) -> Mont {
        let mut inv = 1u64;
        for _ in 0..6 {
            inv = inv.wrapping_mul(2u64.wrapping_sub(p.wrapping_mul(inv)));
        }
        let r = (u128::from(u64::MAX) % u128::from(p) + 1) % u128::from(p);
        let r2 = (r * r % u128::from(p)) as u64;
        Mont { p, pinv: inv.wrapping_neg(), r2 }
    }
    #[inline]
    fn redc(&self, t: u128) -> u64 {
        let m = (t as u64).wrapping_mul(self.pinv);
        let u = ((t + u128::from(m) * u128::from(self.p)) >> 64) as u64;
        if u >= self.p {
            u - self.p
        } else {
            u
        }
    }
    #[inline]
    fn mul(&self, a: u64, b: u64) -> u64 {
        self.redc(u128::from(a) * u128::from(b))
    }
    fn to_m(&self, a: u64) -> u64 {
        self.mul(a % self.p, self.r2)
    }
    fn out_m(&self, a: u64) -> u64 {
        self.redc(u128::from(a))
    }
    fn pow(&self, mut b: u64, mut e: u64) -> u64 {
        let mut acc = self.to_m(1);
        while e > 0 {
            if e & 1 == 1 {
                acc = self.mul(acc, b);
            }
            b = self.mul(b, b);
            e >>= 1;
        }
        acc
    }
}

/// D_1..D_n mod p (plain residues), or None on a zero pivot.
fn minors_mod(n: usize, b: &[i128], p: u64) -> Option<Vec<u64>> {
    let mt = Mont::new(p);
    let pi = i128::from(p);
    let mut m: Vec<u64> = b.iter().map(|&v| mt.to_m(v.rem_euclid(pi) as u64)).collect();
    let mut det = mt.to_m(1);
    let mut out = Vec::with_capacity(n);
    for k in 0..n {
        let piv = m[k * n + k];
        if piv == 0 {
            return None;
        }
        det = mt.mul(det, piv);
        out.push(mt.out_m(det));
        let inv = mt.pow(piv, p - 2);
        let (head, tail) = m.split_at_mut((k + 1) * n);
        let prow = &head[k * n + k..k * n + n];
        for r in 0..n - k - 1 {
            let row = &mut tail[r * n + k..r * n + n];
            let f = mt.mul(row[0], inv);
            if f == 0 {
                continue;
            }
            for (cell, &pv) in row.iter_mut().zip(prow.iter()).skip(1) {
                let s = mt.mul(f, pv);
                *cell = if *cell >= s { *cell - s } else { *cell + p - s };
            }
        }
    }
    Some(out)
}

fn main() {
    let mut text = String::new();
    if std::io::stdin().read_to_string(&mut text).is_err() {
        println!("INDEP_MINORS|error=read|json=0");
        std::process::exit(2);
    }
    let mut it = text.split_ascii_whitespace();
    let n: usize = it.next().and_then(|v| v.parse().ok()).unwrap_or(0);
    let b: Vec<i128> = it.filter_map(|v| v.parse().ok()).collect();
    if n == 0 || b.len() != n * n {
        println!("INDEP_MINORS|error=bad_matrix|json=0");
        std::process::exit(2);
    }
    // Hadamard: |D_k| <= prod_{i<k} ||row_i|| <= (max row norm)^k
    let mut bits = 0u32;
    for i in 0..n {
        let s: u128 = b[i * n..(i + 1) * n].iter().map(|&v| (v.unsigned_abs()) * (v.unsigned_abs())).sum();
        bits = bits.max((128 - s.leading_zeros()).div_ceil(2) + 1);
    }
    let total_bits = u64::from(bits) * n as u64 + 2;
    let need = usize::try_from(total_bits.div_ceil(61) + 1).unwrap_or(usize::MAX);
    let workers: usize = std::env::var("WORKERS").ok().and_then(|v| v.parse().ok()).unwrap_or(1).max(1);
    // primes below 2^62, descending
    let mut cand = (1u64 << 62) - 1;
    let mut mods: Vec<u64> = Vec::new();
    let mut res: Vec<Vec<u64>> = Vec::new();
    let mut dropped = 0usize;
    while mods.len() < need {
        let mut batch = Vec::new();
        while batch.len() < workers.max(need - mods.len()).min(need - mods.len()) {
            if is_prime(cand) {
                batch.push(cand);
            }
            cand -= 2;
        }
        let results: Vec<(u64, Option<Vec<u64>>)> = std::thread::scope(|sc| {
            let chunks: Vec<Vec<u64>> = (0..workers).map(|w| batch.iter().skip(w).step_by(workers).copied().collect()).collect();
            let hs: Vec<_> = chunks
                .into_iter()
                .map(|ch| {
                    let b = &b;
                    sc.spawn(move || ch.into_iter().map(|p| (p, minors_mod(n, b, p))).collect::<Vec<_>>())
                })
                .collect();
            hs.into_iter().flat_map(|h| h.join().unwrap_or_default()).collect()
        });
        for (p, r) in results {
            match r {
                Some(v) => {
                    mods.push(p);
                    res.push(v);
                }
                None => dropped += 1,
            }
            if dropped > 64 {
                println!("INDEP_MINORS|error=too_many_zero_pivots|json=0");
                std::process::exit(2);
            }
        }
    }
    // Garner with balanced digits per minor
    let r = mods.len();
    let mut radix = vec![vec![0u64; r]; r];
    let mut inv = vec![0u64; r];
    for i in 0..r {
        let mi = mods[i];
        let mut acc = 1u64;
        for (slot, &mt_) in radix[i].iter_mut().zip(mods.iter()).take(i) {
            *slot = acc;
            acc = ((u128::from(acc) * u128::from(mt_ % mi)) % u128::from(mi)) as u64;
        }
        let mt = Mont::new(mi);
        inv[i] = mt.out_m(mt.pow(mt.to_m(acc), mi - 2));
    }
    let mut signs = String::with_capacity(n);
    let mut digits = vec![0i128; r];
    for k in 0..n {
        for i in 0..r {
            let mi = mods[i];
            let mut acc = 0u128;
            for (dg, &rd) in digits.iter().zip(radix[i].iter()).take(i) {
                let d = dg.rem_euclid(i128::from(mi)) as u128;
                acc = (acc + d * u128::from(rd)) % u128::from(mi);
            }
            let x = u128::from(res[i][k]);
            let v = ((x + u128::from(mi) - acc) % u128::from(mi) * u128::from(inv[i]) % u128::from(mi)) as i128;
            digits[i] = if v > i128::from(mi) / 2 { v - i128::from(mi) } else { v };
        }
        signs.push(match digits.iter().rev().find(|&&d| d != 0) {
            None => '0',
            Some(&d) if d > 0 => '+',
            _ => '-',
        });
    }
    println!("INDEP_MINORS|n={n}|primes={r}|dropped_primes={dropped}|hadamard_bits={total_bits}|signs={signs}|json=0");
}
