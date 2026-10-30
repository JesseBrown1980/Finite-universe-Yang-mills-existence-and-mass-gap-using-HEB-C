//! Bell/CHSH on the actual three-prism mechanism, with two separated measurement stations.
//!
//! The world is prism3's 40-cell propagation (curved j+/j- per prism, c = 1). Station A reads a
//! final branch in subtree 0, station B one in subtree 2; each station's setting picks which
//! branch, chosen per trial after emission by an independent station hash. Outcome = sign of the
//! amplitude. Raw outcomes (t, x, y, a, b) are written per model. Integer only, HBP, json=0.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

#[allow(dead_code)]
#[path = "C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/crates/torusl/src/sha.rs"]
mod sha;

use std::fmt::Write as _;
use tribit::Zero;

type H = [u8; 32];

const TRIALS: u64 = 131_072;
const W_PLUS: [i32; 3] = [1, 1, -1];
const W_MINUS: [i32; 3] = [1, -1, 1];
const A_BRANCH: [usize; 2] = [0, 4];
const B_BRANCH: [usize; 2] = [18, 22];

fn bal(v: i32) -> i32 {
    Zero::from_digit(((v.rem_euclid(3) as u8) + 1) % 3).direction() as i32
}

fn weights(bit: u8) -> [i32; 3] {
    if bit == 0 {
        W_PLUS
    } else {
        W_MINUS
    }
}

fn sha_cat(parts: &[&[u8]]) -> H {
    let mut b = Vec::new();
    for p in parts {
        b.extend_from_slice(p);
    }
    sha::sha256(&b)
}

/// Merkle root of the 40-cell world at step 0 (only the source cell carries the laser).
fn root0(laser: i32) -> H {
    let mut leaves: Vec<H> = Vec::new();
    for (s, n) in [1usize, 3, 9, 27].iter().enumerate() {
        for i in 0..*n {
            let a = if s == 0 { laser } else { 0 };
            let z = Zero::from_digit(((a.rem_euclid(3) as u8) + 1) % 3);
            leaves.push(sha::sha256(&[s as u8, i as u8, z.digit()]));
        }
    }
    while leaves.len() > 1 {
        leaves = leaves
            .chunks(2)
            .map(|p| if p.len() == 2 { sha_cat(&[&p[0], &p[1]]) } else { p[0] })
            .collect();
    }
    leaves[0]
}

/// Full three-prism propagation (as prism3): returns the 27 final amplitudes.
fn propagate(laser: i32, o: [u8; 3]) -> Vec<i32> {
    let mut stage = vec![laser];
    for &bit in o.iter() {
        let w = weights(bit);
        let mut next = vec![0i32; stage.len() * 3];
        for (c, &a) in stage.iter().enumerate() {
            for (b, &wb) in w.iter().enumerate() {
                next[c * 3 + b] = bal(a * wb);
            }
        }
        stage = next;
    }
    stage
}

fn bits(z: &H) -> [u8; 3] {
    [z[0] & 1, (z[0] >> 1) & 1, (z[0] >> 2) & 1]
}

#[derive(Clone, Copy, PartialEq)]
enum Model {
    Locked,
    Pull,
    PullNoLambda,
    Tuned,
}

/// One trial: returns (x, y, a, b, laser).
fn trial(m: Model, t: u64) -> (u8, u8, i32, i32, i32) {
    let tb = t.to_le_bytes();
    let laser = if sha_cat(&[&tb, b"L"])[0] & 1 == 0 { 1 } else { -1 };
    // settings: independent station hashes, chosen after emission
    let x = sha_cat(&[&tb, b"A"])[0] & 1;
    let y = sha_cat(&[&tb, b"B"])[0] & 1;
    let r0 = root0(laser);
    let lb = [if laser > 0 { 2u8 } else { 0u8 }];
    let (a, b) = match m {
        Model::Locked | Model::Pull | Model::PullNoLambda => {
            let z = match m {
                Model::Locked => sha_cat(&[&lb, &r0, &tb]),
                Model::Pull => sha_cat(&[&lb, &r0, &tb, &[x, y]]),
                _ => sha_cat(&[&lb, &r0, &[x, y]]),
            };
            let fin = propagate(laser, bits(&z));
            (fin[A_BRANCH[x as usize]], fin[B_BRANCH[y as usize]])
        }
        Model::Tuned => {
            // positive control: the CHSH quantum-matching z, E = +-70/99
            let s: i64 = if x == 1 && y == 1 { -1 } else { 1 };
            let lam = u64::from_le_bytes(sha_cat(&[&tb, b"Z"])[..8].try_into().unwrap_or([0; 8]));
            let a = if lam % 396 < 198 { 1 } else { -1 };
            let mu = (lam % 198) as i64;
            let b = if mu < 99 + s * 70 { a } else { -a };
            (a, b)
        }
    };
    (x, y, a, b, laser)
}

fn isqrt(n: u64) -> u64 {
    let mut r = 0u64;
    while (r + 1) * (r + 1) <= n {
        r += 1;
    }
    r
}

struct Stats {
    n: [[i64; 2]; 2],
    c: [[i64; 2]; 2],
    a_plus: [[i64; 2]; 2],
    b_plus: [[i64; 2]; 2],
    // per laser sign (index 0 = +1, 1 = -1)
    nl: [[[i64; 2]; 2]; 2],
    cl: [[[i64; 2]; 2]; 2],
    nonzero: bool,
}

fn run(m: Model, name: &str) -> (Stats, String) {
    let mut st = Stats {
        n: [[0; 2]; 2],
        c: [[0; 2]; 2],
        a_plus: [[0; 2]; 2],
        b_plus: [[0; 2]; 2],
        nl: [[[0; 2]; 2]; 2],
        cl: [[[0; 2]; 2]; 2],
        nonzero: true,
    };
    let mut raw = String::with_capacity(TRIALS as usize * 24);
    for t in 0..TRIALS {
        let (x, y, a, b, laser) = trial(m, t);
        let (xi, yi, li) = (x as usize, y as usize, usize::from(laser < 0));
        st.nonzero &= a != 0 && b != 0;
        st.n[xi][yi] += 1;
        st.c[xi][yi] += i64::from(a * b);
        st.a_plus[xi][yi] += i64::from(a == 1);
        st.b_plus[xi][yi] += i64::from(b == 1);
        st.nl[li][xi][yi] += 1;
        st.cl[li][xi][yi] += i64::from(a * b);
        let _ = writeln!(raw, "R|m={name}|t={t}|x={x}|y={y}|a={a}|b={b}|json=0");
    }
    (st, raw)
}

const SIGNS: [[i64; 2]; 2] = [[1, 1], [1, -1]];

/// S in micro-units (floor of each term), and the conservative 5-sigma in micro-units.
fn s_micro(st: &Stats) -> (i64, i64, i64) {
    let mut s = 0i64;
    let mut nmin = i64::MAX;
    for ((sign_row, c_row), n_row) in SIGNS.iter().zip(st.c.iter()).zip(st.n.iter()) {
        for ((&sg, &c), &n) in sign_row.iter().zip(c_row.iter()).zip(n_row.iter()) {
            s += sg * (c * 1_000_000).div_euclid(n);
            nmin = nmin.min(n);
        }
    }
    let r = isqrt(nmin as u64) as i64;
    let five_sigma = (10_000_000 + r - 1) / r; // 5 * 2e6 / sqrt(Nmin), rounded up
    (s, five_sigma, nmin)
}

fn no_signalling(st: &Stats, nmin: i64) -> bool {
    let r = isqrt(nmin as u64) as i64;
    let tol = (5_000_000 + r - 1) / r; // 5 / sqrt(Nmin) in micro, conservative
    let p = |num: i64, den: i64| (num * 1_000_000).div_euclid(den);
    let mut ok = true;
    for x in 0..2 {
        ok &= (p(st.a_plus[x][0], st.n[x][0]) - p(st.a_plus[x][1], st.n[x][1])).abs() <= tol;
    }
    for y in 0..2 {
        ok &= (p(st.b_plus[0][y], st.n[0][y]) - p(st.b_plus[1][y], st.n[1][y])).abs() <= tol;
    }
    ok
}

fn main() {
    let out_dir = std::env::args().nth(1).unwrap_or_else(|| ".".into());
    let models = [
        (Model::Locked, "LOCKED"),
        (Model::Pull, "PULL"),
        (Model::PullNoLambda, "PULL_NOLAMBDA"),
        (Model::Tuned, "TUNED"),
    ];
    let mut verdict: Vec<String> = Vec::new();
    let (mut p5, mut p6) = (true, true);
    for (m, name) in models {
        let (st, raw) = run(m, name);
        let path = format!("{out_dir}/RAW-{name}.hbp");
        if std::fs::write(&path, raw.as_bytes()).is_err() {
            println!("PBELL_FAIL|reason=raw_write_failed|model={name}|json=0");
        }
        let (s, five, nmin) = s_micro(&st);
        let ns = no_signalling(&st, nmin);
        p5 &= ns;
        p6 &= st.nonzero && st.n.iter().flatten().sum::<i64>() == TRIALS as i64;
        let e = |x: usize, y: usize| format!("{}/{}", st.c[x][y], st.n[x][y]);
        println!(
            "PBELL_MODEL|m={name}|S_micro={s}|five_sigma_micro={five}|N_min={nmin}|E00={}|E01={}|E10={}|E11={}|no_signalling={}|all_outcomes_pm1={}|json=0",
            e(0, 0), e(0, 1), e(1, 0), e(1, 1), u8::from(ns), u8::from(st.nonzero)
        );
        match m {
            Model::Locked => verdict.push(format!("P1_LOCKED={}", u8::from(s.abs() <= 2_000_000 + five && s.abs() <= five))),
            Model::Pull => verdict.push(format!("P2_PULL={}", u8::from(s.abs() <= five))),
            Model::PullNoLambda => {
                let pm1 = (0..2).all(|x| (0..2).all(|y| st.c[x][y].abs() == st.n[x][y]));
                let s_int_ok = pm1 && s % 2_000_000 == 0;
                verdict.push(format!("P3_original={}", u8::from(s_int_ok)));
                let mut per_laser_ok = true;
                for (li, sign) in [(0usize, "+1"), (1usize, "-1")] {
                    let pm = (0..2).all(|x| (0..2).all(|y| st.nl[li][x][y] > 0 && st.cl[li][x][y].abs() == st.nl[li][x][y]));
                    let sl: i64 = (0..2).map(|x| (0..2).map(|y| SIGNS[x][y] * st.cl[li][x][y].signum()).sum::<i64>()).sum();
                    per_laser_ok &= pm && [-4, -2, 0, 2, 4].contains(&sl);
                    println!("PBELL_NOLAMBDA_LASER|laser={sign}|E_each_pm1={}|S={sl}|json=0", u8::from(pm));
                }
                verdict.push(format!("P3_addendum_per_laser={}", u8::from(per_laser_ok)));
            }
            Model::Tuned => verdict.push(format!(
                "P4_TUNED={}",
                u8::from(s > 2_000_000 + five && {
                    let lo = s - five;
                    lo <= 0 || (lo as i128) * (lo as i128) <= 8_000_000_000_000
                })
            )),
        }
    }
    println!("PBELL_PREDICTIONS|{}|P5_no_signalling_all={}|P6_outcomes_pm1_and_counts={}|json=0", verdict.join("|"), u8::from(p5), u8::from(p6));
}
