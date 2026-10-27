//! Direct count of S3^k orbits under simultaneous conjugation, without any CNF:
//! a configuration is counted iff it is the lexicographic minimum of its orbit.
//! Integer-only. Build: rustc +1.81.0 -O direct_orbits.rs. Usage: direct_orbits K
#![deny(clippy::float_arithmetic)]

fn perms() -> Vec<[usize; 3]> {
    let mut v = Vec::new();
    for a in 0..3 {
        for b in 0..3 {
            for c in 0..3 {
                if a != b && b != c && a != c {
                    v.push([a, b, c]);
                }
            }
        }
    }
    v // lexicographic order, the same element order as orbit_cnf.py
}

fn main() {
    let k: u32 = std::env::args().nth(1).expect("K").parse().expect("K");
    let els = perms();
    let idx = |p: [usize; 3]| els.iter().position(|q| *q == p).unwrap();
    let mul = |a: usize, b: usize| idx([els[a][els[b][0]], els[a][els[b][1]], els[a][els[b][2]]]);
    let inv = |a: usize| {
        let mut r = [0usize; 3];
        for (i, &x) in els[a].iter().enumerate() {
            r[x] = i;
        }
        idx(r)
    };
    let conj: Vec<Vec<usize>> = (0..6).map(|g| (0..6).map(|v| mul(mul(g, v), inv(g))).collect()).collect();
    let total: u64 = 6u64.pow(k);
    let mut cfg = vec![0usize; k as usize];
    let mut count: u64 = 0;
    for code in 0..total {
        let mut c = code;
        for l in (0..k as usize).rev() {
            cfg[l] = (c % 6) as usize;
            c /= 6;
        }
        let mut minimal = true;
        for row in conj.iter().skip(1) {
            for &v in cfg.iter() {
                let w = row[v];
                if w < v {
                    minimal = false;
                    break;
                }
                if w > v {
                    break;
                }
            }
            if !minimal {
                break;
            }
        }
        count += minimal as u64;
    }
    let burnside = (6u64.pow(k) + 3 * 2u64.pow(k) + 2 * 3u64.pow(k)) / 6;
    println!("DIRECT|K={k}|configurations={total}|lexmin_count={count}|burnside={burnside}|json=0");
}
