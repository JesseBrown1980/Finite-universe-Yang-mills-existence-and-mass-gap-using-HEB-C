//! Cantor all-band laser test. Bands = Cantor set at depth 4 (base-3 addresses with no digit 1).
//! C1: every band travels its own c = 1 ring channel; all must arrive together (dispersion control
//! must not). C2: Cantor counts and structure. C3: prism3 mechanism per band, two separated
//! stations, outcome = product over all bands; does carrying all bands change the Bell trade-off?
//! Integer only, HBP out, json=0.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

#[allow(dead_code)]
#[path = "C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/crates/torusl/src/sha.rs"]
mod sha;

use tribit::Zero;

type H = [u8; 32];

const DEPTH: u32 = 4;
const RING: usize = 64;
const TARGET: usize = 20;
const STEPS: usize = 120;
const TRIALS: u64 = 131_072;
const W_PLUS: [i32; 3] = [1, 1, -1];
const W_MINUS: [i32; 3] = [1, -1, 1];
const A_BRANCH: [usize; 2] = [0, 4];
const B_BRANCH: [usize; 2] = [18, 22];
const SIGNS: [[i64; 2]; 2] = [[1, 1], [1, -1]];

fn bal(v: i32) -> i32 {
    Zero::from_digit(((v.rem_euclid(3) as u8) + 1) % 3).direction() as i32
}

fn digits(mut v: u32, n: u32) -> Vec<u8> {
    (0..n)
        .map(|_| {
            let d = (v % 3) as u8;
            v /= 3;
            d
        })
        .collect()
}

/// Cantor addresses at depth n: base-3 digit strings with no digit 1.
fn cantor(n: u32) -> Vec<Vec<u8>> {
    (0..3u32.pow(n)).map(|v| digits(v, n)).filter(|d| !d.contains(&1)).collect()
}

/// First step the target cell is nonzero; the band updates only on steps divisible by `every`.
fn arrival(amp: i32, every: usize) -> usize {
    let mut s = vec![0i32; RING];
    s[0] = amp;
    for t in 1..=STEPS {
        if t % every == 0 {
            s = (0..RING).map(|x| bal(s[(x + RING - 1) % RING] + s[x] + s[(x + 1) % RING])).collect();
        }
        if s[TARGET] != 0 {
            return t;
        }
    }
    usize::MAX
}

fn sha_cat(parts: &[&[u8]]) -> H {
    let mut b = Vec::new();
    for p in parts {
        b.extend_from_slice(p);
    }
    sha::sha256(&b)
}

fn propagate(laser: i32, o: [u8; 3]) -> Vec<i32> {
    let mut stage = vec![laser];
    for &bit in o.iter() {
        let w = if bit == 0 { W_PLUS } else { W_MINUS };
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

#[derive(Clone, Copy)]
enum Model {
    Local,
    Pull,
    Det,
}

struct Stats {
    n: [[i64; 2]; 2],
    c: [[i64; 2]; 2],
    a_plus: [[i64; 2]; 2],
    b_plus: [[i64; 2]; 2],
}

fn run(m: Model, bands: usize) -> Stats {
    let mut st = Stats { n: [[0; 2]; 2], c: [[0; 2]; 2], a_plus: [[0; 2]; 2], b_plus: [[0; 2]; 2] };
    for t in 0..TRIALS {
        let tb = t.to_le_bytes();
        let x = sha_cat(&[&tb, b"A"])[0] & 1;
        let y = sha_cat(&[&tb, b"B"])[0] & 1;
        let amps: Vec<u8> = (0..bands)
            .map(|b| match m {
                Model::Det => 2u8,
                _ => {
                    if sha_cat(&[&tb, b"amp", &[b as u8]])[0] & 1 == 0 {
                        2
                    } else {
                        0
                    }
                }
            })
            .collect();
        let z = match m {
            Model::Local => sha_cat(&[&amps, &tb]),
            Model::Pull => sha_cat(&[&amps, &tb, &[x, y]]),
            Model::Det => sha_cat(&[&[x, y]]),
        };
        let (mut a, mut b) = (1i32, 1i32);
        for (band, &am) in amps.iter().enumerate() {
            let zb = sha_cat(&[&z, &[band as u8]]);
            let o = [zb[0] & 1, (zb[0] >> 1) & 1, (zb[0] >> 2) & 1];
            let fin = propagate(if am == 2 { 1 } else { -1 }, o);
            a *= fin[A_BRANCH[x as usize]];
            b *= fin[B_BRANCH[y as usize]];
        }
        let (xi, yi) = (x as usize, y as usize);
        st.n[xi][yi] += 1;
        st.c[xi][yi] += i64::from(a * b);
        st.a_plus[xi][yi] += i64::from(a == 1);
        st.b_plus[xi][yi] += i64::from(b == 1);
    }
    st
}

fn isqrt(n: u64) -> u64 {
    let mut r = 0u64;
    while (r + 1) * (r + 1) <= n {
        r += 1;
    }
    r
}

/// (S in micro-units, conservative 5 sigma in micro-units, no-signalling within 5 sigma)
fn analyse(st: &Stats) -> (i64, i64, bool) {
    let mut s = 0i64;
    let mut nmin = i64::MAX;
    for ((sign_row, c_row), n_row) in SIGNS.iter().zip(st.c.iter()).zip(st.n.iter()) {
        for ((&sg, &c), &n) in sign_row.iter().zip(c_row.iter()).zip(n_row.iter()) {
            s += sg * (c * 1_000_000).div_euclid(n);
            nmin = nmin.min(n);
        }
    }
    let r = isqrt(nmin as u64) as i64;
    let five = (10_000_000 + r - 1) / r;
    let tol = (5_000_000 + r - 1) / r;
    let p = |num: i64, den: i64| (num * 1_000_000).div_euclid(den);
    let mut ns = true;
    for i in 0..2 {
        ns &= (p(st.a_plus[i][0], st.n[i][0]) - p(st.a_plus[i][1], st.n[i][1])).abs() <= tol;
        ns &= (p(st.b_plus[0][i], st.n[0][i]) - p(st.b_plus[1][i], st.n[1][i])).abs() <= tol;
    }
    (s, five, ns)
}

fn main() {
    // C2
    let counts: Vec<usize> = (1..=6).map(|n| cantor(n).len()).collect();
    let no_one = (1..=6).all(|n| cantor(n).iter().all(|d| !d.contains(&1)));
    let self_similar = (2..=6).all(|n| {
        let prev = cantor(n - 1);
        let cur = cantor(n);
        cur.len() == 2 * prev.len() && cur.iter().all(|d| prev.contains(&d[..(n - 1) as usize].to_vec()))
    });
    let c2 = counts == vec![2, 4, 8, 16, 32, 64] && no_one && self_similar;
    println!("CANTOR_C2|counts_depth1..6={:?}|no_digit_1={}|self_similar={}|json=0", counts, u8::from(no_one), u8::from(self_similar));
    // C1
    let bands = cantor(DEPTH);
    let arrivals: Vec<usize> = bands.iter().map(|_| arrival(1, 1)).collect();
    let c1 = arrivals.iter().all(|&a| a == TARGET);
    let ctrl: Vec<usize> = bands.iter().map(|d| arrival(1, 1 + d.iter().filter(|&&v| v == 2).count())).collect();
    let ctrl_ok = ctrl.iter().any(|&a| a != ctrl[0])
        && bands.iter().zip(ctrl.iter()).all(|(d, &a)| a == TARGET * (1 + d.iter().filter(|&&v| v == 2).count()));
    println!("CANTOR_C1|bands={}|arrivals_all={}|all_equal_{TARGET}={}|json=0", bands.len(), arrivals.iter().map(|a| a.to_string()).collect::<Vec<_>>().join(","), u8::from(c1));
    println!("CANTOR_C1_CONTROL|arrivals={}|dispersion_detected_and_exact={}|json=0", ctrl.iter().map(|a| a.to_string()).collect::<Vec<_>>().join(","), u8::from(ctrl_ok));
    // C3
    let mut c3 = Vec::new();
    for (m, name) in [(Model::Local, "LOCAL"), (Model::Pull, "PULL"), (Model::Det, "DET")] {
        let st = run(m, bands.len());
        let (s, five, ns) = analyse(&st);
        println!("CANTOR_C3|m={name}|bands={}|S_micro={s}|five_sigma_micro={five}|no_signalling={}|E00={}/{}|E01={}/{}|E10={}/{}|E11={}/{}|json=0",
            bands.len(), u8::from(ns), st.c[0][0], st.n[0][0], st.c[0][1], st.n[0][1], st.c[1][0], st.n[1][0], st.c[1][1], st.n[1][1]);
        match m {
            Model::Local | Model::Pull => c3.push(format!("{name}={}", u8::from(s.abs() <= five && ns))),
            Model::Det => c3.push(format!("DET_theorem_holds={}|DET_case={}", u8::from(!(ns && s.abs() > 2_000_000 + five)),
                if ns { "no_signalling_and_|S|<=2" } else { "signalling" })),
        }
    }
    println!("CANTOR_PREDICTIONS|C1_all_bands_arrive_together={}|C1_control_detects_dispersion={}|C2_cantor_structure={}|C3_{}|json=0",
        u8::from(c1), u8::from(ctrl_ok), u8::from(c2), c3.join("|C3_"));
}
