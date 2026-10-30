//! Bell/CHSH test of the z model. Outcomes are canonical balanced trits (Pos = +1, Neg = -1).
//! S = E00 + E01 + E10 - E11. Exact integer/rational arithmetic only; sqrt(2) appears only as
//! the exact check S^2 <= 8. N = 102400 = 320^2 trials per setting pair, so sqrt(N) = 320 and the
//! 5-sigma margin (sigma <= 2/sqrt(N)) is exactly N/32 in S-numerator units. HBP out, json=0.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

#[allow(dead_code)]
#[path = "C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/crates/torusl/src/sha.rs"]
mod sha;

use tribit::Zero;

const N: i64 = 102_400;
const SQRT_N: i64 = 320;
const R_NUM: i64 = 70; // r = 70/99 ~ 1/sqrt(2)
const R_DEN: i64 = 99;

fn out(z: Zero) -> i64 {
    z.direction() as i64
}

fn trit(plus: bool) -> Zero {
    if plus {
        Zero::Pos
    } else {
        Zero::Neg
    }
}

fn sign(x: u8, y: u8) -> i64 {
    if x == 1 && y == 1 {
        -1
    } else {
        1
    }
}

fn h64(parts: &[&[u8]]) -> u64 {
    let mut buf = Vec::new();
    for p in parts {
        buf.extend_from_slice(p);
    }
    let d = sha::sha256(&buf);
    u64::from_le_bytes([d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7]])
}

const PAIRS: [(u8, u8); 4] = [(0, 0), (0, 1), (1, 0), (1, 1)];

/// Q1: all 16 local deterministic strategies a(x), b(y) in {+1,-1}.
fn q1() -> (bool, i64) {
    let fs: [[i64; 2]; 4] = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
    let mut all_two = true;
    let mut max = 0i64;
    for a in fs.iter() {
        for b in fs.iter() {
            let s: i64 = PAIRS.iter().map(|&(x, y)| sign(x, y) * a[x as usize] * b[y as usize]).sum();
            all_two &= s.abs() == 2;
            max = max.max(s.abs());
        }
    }
    (all_two, max)
}

/// Q2: local hashed model, shared lambda = trial index, each side reads only its own setting.
fn q2() -> i64 {
    let mut s_num = 0i64;
    for &(x, y) in PAIRS.iter() {
        let mut corr = 0i64;
        for t in 0..N {
            let lam = t.to_le_bytes();
            let a = out(trit(h64(&[&lam, b"A", &[x]]) & 1 == 1));
            let b = out(trit(h64(&[&lam, b"B", &[y]]) & 1 == 1));
            corr += a * b;
        }
        s_num += sign(x, y) * corr;
    }
    s_num
}

/// Q3: PR box. Global z reads both settings: a uniform, b = a * (-1)^(x*y). Exact over a.
fn q3() -> (i64, bool) {
    let mut s = 0i64;
    let mut a_plus = Vec::new();
    let mut b_plus = Vec::new();
    for &(x, y) in PAIRS.iter() {
        let (mut corr, mut ap, mut bp) = (0i64, 0i64, 0i64);
        for &a in [1i64, -1].iter() {
            let b = a * if x == 1 && y == 1 { -1 } else { 1 };
            corr += a * b;
            ap += i64::from(a == 1);
            bp += i64::from(b == 1);
        }
        s += sign(x, y) * corr; // over 2 cases: corr = +-2
        a_plus.push(ap);
        b_plus.push(bp);
    }
    let no_signal = a_plus.iter().all(|&v| v == a_plus[0]) && b_plus.iter().all(|&v| v == b_plus[0]);
    (s / 2, no_signal)
}

/// Quantum-matching z: global z reads both settings; outcome pair from lam in 0..396.
fn zq_outcome(lam: u64, x: u8, y: u8) -> (i64, i64) {
    let s = sign(x, y);
    let a = if lam % 396 < 198 { 1 } else { -1 };
    let mu = (lam % 198) as i64;
    let b = if mu < R_DEN + s * R_NUM { a } else { -a };
    (a, b)
}

/// Q4: exact enumeration of lam in 0..396 per pair.
fn q4() -> (i64, bool) {
    let mut s_num = 0i64; // S = s_num / 396
    let mut a_plus = Vec::new();
    let mut b_plus = Vec::new();
    for &(x, y) in PAIRS.iter() {
        let (mut corr, mut ap, mut bp) = (0i64, 0i64, 0i64);
        for lam in 0..396u64 {
            let (a, b) = zq_outcome(lam, x, y);
            corr += a * b;
            ap += i64::from(a == 1);
            bp += i64::from(b == 1);
        }
        s_num += sign(x, y) * corr;
        a_plus.push(ap);
        b_plus.push(bp);
    }
    let no_signal = a_plus.iter().all(|&v| v == a_plus[0]) && b_plus.iter().all(|&v| v == b_plus[0]);
    (s_num, no_signal)
}

/// Q5: quantum-matching z sampled with hash randomness, N per pair.
fn q5() -> i64 {
    let mut s_num = 0i64;
    for &(x, y) in PAIRS.iter() {
        let mut corr = 0i64;
        for t in 0..N {
            let lam = h64(&[&t.to_le_bytes(), b"Z", &[x, y]]);
            let (a, b) = zq_outcome(lam, x, y);
            corr += a * b;
        }
        s_num += sign(x, y) * corr;
    }
    s_num
}

/// Q6: signalling control. A's outcome copies y; check A's marginal against y.
fn q6() -> bool {
    // a = (-1)^y, b uniform over two cases; count A's +1 outcomes for y = 0 and y = 1
    let a_plus = |y: u8| -> i64 {
        let a: i64 = if y == 0 { 1 } else { -1 };
        let mut n = 0i64;
        for _b in [1i64, -1] {
            if a == 1 {
                n += 1;
            }
        }
        n
    };
    a_plus(0) != a_plus(1)
}

fn main() {
    let (q1_all2, q1_max) = q1();
    let q2_s = q2();
    let (q3_s, q3_ns) = q3();
    let (q4_num, q4_ns) = q4();
    let q5_s = q5();
    let q6_sig = q6();
    // Q2: S_hat <= 2 + 5 sigma  <=>  s_num <= 2N + N/32
    let q2_ok = q2_s <= 2 * N + N / 32;
    // Q4: S = q4_num / 396 = 280/99 exactly; S > 2; S^2 <= 8
    let q4_ok = q4_num * 99 == 280 * 396 && q4_num > 2 * 396 && q4_num * q4_num <= 8 * 396 * 396 && q4_ns;
    // Q5: S_hat > 2 + 5 sigma  <=>  s_num > 2N + N/32 ; and S_hat - 1/32 <= sqrt(8)
    let lower = 32 * q5_s - N; // = 32N * (S_hat - 1/32)
    let q5_ok = q5_s > 2 * N + N / 32 && (lower <= 0 || (lower as i128) * (lower as i128) <= 8 * (32 * N as i128) * (32 * N as i128));
    println!("CHSH_RUN|N_per_pair={N}|sqrt_N={SQRT_N}|five_sigma_in_S_numerator={}|r={R_NUM}/{R_DEN}|json=0", N / 32);
    println!("CHSH_Q1|local_deterministic_strategies=16|all_abs_S_eq_2={}|max_abs_S={q1_max}|json=0", u8::from(q1_all2));
    println!("CHSH_Q2|local_hash|S_numerator={q2_s}|N={N}|S_hat={q2_s}/{N}|bound_2N_plus_5sigma={}|json=0", 2 * N + N / 32);
    println!("CHSH_Q3|PR_box_exact|S={q3_s}|no_signalling={}|json=0", u8::from(q3_ns));
    println!("CHSH_Q4|quantum_matching_exact|S={q4_num}/396|equals_280/99={}|S_sq_le_8={}|no_signalling={}|json=0",
        u8::from(q4_num * 99 == 280 * 396), u8::from(q4_num * q4_num <= 8 * 396 * 396), u8::from(q4_ns));
    println!("CHSH_Q5|quantum_matching_sampled|S_numerator={q5_s}|N={N}|S_hat={q5_s}/{N}|lower_5sigma={}|json=0", 2 * N + N / 32);
    println!("CHSH_Q6|signalling_control_detected={}|json=0", u8::from(q6_sig));
    println!(
        "CHSH_PREDICTIONS|Q1_local_max_2={}|Q2_local_hash_le_2={}|Q3_PR_box_4_no_signal={}|Q4_quantum_exact_280_99={}|Q5_quantum_sampled_gt_2={}|Q6_signalling_seen={}|json=0",
        u8::from(q1_all2 && q1_max == 2), u8::from(q2_ok), u8::from(q3_s == 4 && q3_ns), u8::from(q4_ok), u8::from(q5_ok), u8::from(q6_sig)
    );
}
