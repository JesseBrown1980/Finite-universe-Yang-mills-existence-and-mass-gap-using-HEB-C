//! Frustrated-orientation benchmark. The three prism orientations are spins with frozen frustrated
//! couplings J12 = +1, J23 = +1, J13 = -1 and fields h. Route part: does frustration change
//! delivery versus hash and classical selection? Bell part: the selected orientations through the
//! prism-Bell stations; local bound when the settings are hidden, measured values when seen.
//! Integer only, HBP out, json=0.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

#[allow(dead_code)]
#[path = "C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/crates/torusl/src/sha.rs"]
mod sha;

use tribit::Zero;

type H = [u8; 32];

const J: [i32; 3] = [1, 1, -1]; // J12, J23, J13
const TRIALS: u64 = 131_072;
const W_PLUS: [i32; 3] = [1, 1, -1];
const W_MINUS: [i32; 3] = [1, -1, 1];
const A_BRANCH: [usize; 2] = [0, 4];
const B_BRANCH: [usize; 2] = [18, 22];
const SIGNS: [[i64; 2]; 2] = [[1, 1], [1, -1]];

fn bal(v: i32) -> i32 {
    Zero::from_digit(((v.rem_euclid(3) as u8) + 1) % 3).direction() as i32
}

fn sha_cat(parts: &[&[u8]]) -> H {
    let mut b = Vec::new();
    for p in parts {
        b.extend_from_slice(p);
    }
    sha::sha256(&b)
}

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
        leaves = leaves.chunks(2).map(|p| if p.len() == 2 { sha_cat(&[&p[0], &p[1]]) } else { p[0] }).collect();
    }
    leaves[0]
}

/// Spins (+1 = j+, -1 = j-) to the 27 final amplitudes.
fn propagate(laser: i32, s: [i32; 3]) -> Vec<i32> {
    let mut stage = vec![laser];
    for &sk in s.iter() {
        let w = if sk >= 0 { W_PLUS } else { W_MINUS };
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

fn energy(s: [i32; 3], h: [i32; 3], j: [i32; 3]) -> i32 {
    -(j[0] * s[0] * s[1] + j[1] * s[1] * s[2] + j[2] * s[0] * s[2]) - (h[0] * s[0] + h[1] * s[1] + h[2] * s[2])
}

/// Exact minimum over the 8 binary states (ties: first in enumeration order).
fn exact(h: [i32; 3], j: [i32; 3]) -> ([i32; 3], i32) {
    let mut best = ([1, 1, 1], i32::MAX);
    for i in 0..8u32 {
        let s = [1 - 2 * (i & 1) as i32, 1 - 2 * ((i >> 1) & 1) as i32, 1 - 2 * ((i >> 2) & 1) as i32];
        let e = energy(s, h, j);
        if e < best.1 {
            best = (s, e);
        }
    }
    best
}

/// Minimum over the 27 ternary states (0 = neutral); returns (state, energy).
fn ternary(h: [i32; 3], j: [i32; 3]) -> ([i32; 3], i32) {
    let mut best = ([0, 0, 0], i32::MAX);
    for i in 0..27u32 {
        let s = [(i % 3) as i32 - 1, ((i / 3) % 3) as i32 - 1, (i / 9) as i32 - 1];
        let e = energy(s, h, j);
        if e < best.1 {
            best = (s, e);
        }
    }
    best
}

fn route() -> String {
    let root = root0(1);
    let (mut d_hash, mut d_exact, mut d_tern, mut d_field) = (0, 0, 0, 0);
    let (mut e_le, mut t_le, mut t_lower) = (0, 0, 0);
    let (mut e_hash_sum, mut e_exact_sum, mut e_tern_sum) = (0i64, 0i64, 0i64);
    for dest in 0..27usize {
        let digits = [dest / 9, (dest / 3) % 3, dest % 3];
        let h = digits.map(|b| match b {
            0 => 0,
            1 => 1,
            _ => -1,
        });
        let z = sha_cat(&[&[2u8, dest as u8], &root]);
        let s_hash = [0, 1, 2].map(|k| if (z[0] >> k) & 1 == 0 { 1 } else { -1 });
        let e_hash = energy(s_hash, h, J);
        let (s_exact, e_exact) = exact(h, J);
        let (s_tern_raw, e_tern) = ternary(h, J);
        let s_tern = s_tern_raw.map(|v| if v == 0 { 1 } else { v });
        let (s_field, _) = exact(h, [0, 0, 0]);
        let deliver = |s: [i32; 3]| i32::from(propagate(1, s)[dest] == 1);
        d_hash += deliver(s_hash);
        d_exact += deliver(s_exact);
        d_tern += deliver(s_tern);
        d_field += deliver(s_field);
        e_le += i32::from(e_exact <= e_hash);
        t_le += i32::from(e_tern <= e_exact);
        t_lower += i32::from(e_tern < e_exact);
        e_hash_sum += i64::from(e_hash);
        e_exact_sum += i64::from(e_exact);
        e_tern_sum += i64::from(e_tern);
    }
    println!("FRUST_ROUTE|destinations=27|delivery_HASH={d_hash}/27|delivery_EXACT={d_exact}/27|delivery_TERNARY={d_tern}/27|delivery_FIELD_ONLY={d_field}/27|energy_sum_HASH={e_hash_sum}|energy_sum_EXACT={e_exact_sum}|energy_sum_TERNARY={e_tern_sum}|json=0");
    println!("FRUST_ROUTE_CHECKS|EXACT_le_HASH={e_le}/27|TERNARY_le_EXACT={t_le}/27|TERNARY_strictly_lower={t_lower}/27|json=0");
    format!("R1_FIELD_ONLY_27={}|R2_EXACT_le_HASH_27={}|R3_TERNARY_le_EXACT_27={}", u8::from(d_field == 27), u8::from(e_le == 27), u8::from(t_le == 27))
}

fn isqrt(n: u64) -> u64 {
    let mut r = 0u64;
    while (r + 1) * (r + 1) <= n {
        r += 1;
    }
    r
}

/// Bell part; joint = the controller sees both settings. Returns (S micro, 5 sigma micro, max
/// marginal difference micro for A, for B, tolerance micro).
fn bell(joint: bool) -> (i64, i64, i64, i64, i64) {
    let (mut n, mut c, mut ap, mut bp) = ([[0i64; 2]; 2], [[0i64; 2]; 2], [[0i64; 2]; 2], [[0i64; 2]; 2]);
    for t in 0..TRIALS {
        let tb = t.to_le_bytes();
        let laser = if sha_cat(&[&tb, b"L"])[0] & 1 == 0 { 1 } else { -1 };
        let x = sha_cat(&[&tb, b"A"])[0] & 1;
        let y = sha_cat(&[&tb, b"B"])[0] & 1;
        let lb = [if laser > 0 { 2u8 } else { 0u8 }];
        let r0 = root0(laser);
        let z = if joint { sha_cat(&[&lb, &r0, &tb, &[x, y]]) } else { sha_cat(&[&lb, &r0, &tb]) };
        let h = [0usize, 1, 2].map(|k| i32::from(z[k] % 3) - 1);
        let (s, _) = exact(h, J);
        let fin = propagate(laser, s);
        let (a, b) = (fin[A_BRANCH[x as usize]], fin[B_BRANCH[y as usize]]);
        let (xi, yi) = (x as usize, y as usize);
        n[xi][yi] += 1;
        c[xi][yi] += i64::from(a * b);
        ap[xi][yi] += i64::from(a == 1);
        bp[xi][yi] += i64::from(b == 1);
    }
    let mut s_micro = 0i64;
    let mut nmin = i64::MAX;
    for ((sr, cr), nr) in SIGNS.iter().zip(c.iter()).zip(n.iter()) {
        for ((&sg, &cv), &nv) in sr.iter().zip(cr.iter()).zip(nr.iter()) {
            s_micro += sg * (cv * 1_000_000).div_euclid(nv);
            nmin = nmin.min(nv);
        }
    }
    let r = isqrt(nmin as u64) as i64;
    let five = (10_000_000 + r - 1) / r;
    let tol = (5_000_000 + r - 1) / r;
    let p = |num: i64, den: i64| (num * 1_000_000).div_euclid(den);
    let mut a_max = 0i64;
    let mut b_max = 0i64;
    for i in 0..2 {
        a_max = a_max.max((p(ap[i][0], n[i][0]) - p(ap[i][1], n[i][1])).abs());
        b_max = b_max.max((p(bp[0][i], n[0][i]) - p(bp[1][i], n[1][i])).abs());
    }
    (s_micro, five, a_max, b_max, tol)
}

fn main() {
    let r = route();
    let (sl, fl, al, bl, tl) = bell(false);
    println!("FRUST_BELL|m=FROZEN-LOCAL|S_micro={sl}|five_sigma_micro={fl}|A_max_marginal_diff_micro={al}|B_max_marginal_diff_micro={bl}|tolerance_micro={tl}|json=0");
    let (sj, fj, aj, bj, tj) = bell(true);
    println!("FRUST_BELL|m=FROZEN-JOINT|S_micro={sj}|five_sigma_micro={fj}|A_max_marginal_diff_micro={aj}|B_max_marginal_diff_micro={bj}|tolerance_micro={tj}|signalling_detected={}|json=0", u8::from(aj > tj || bj > tj));
    println!("FRUST_PREDICTIONS|{r}|B1_LOCAL_bound={}|B2_JOINT=measured(S_micro={sj},signalling={})|json=0",
        u8::from(sl <= 2_000_000 + fl), u8::from(aj > tj || bj > tj));
}
