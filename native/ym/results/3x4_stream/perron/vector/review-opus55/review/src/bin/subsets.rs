//! Exhaustive test of the adjacency inequality over every subset of plaquettes of an Lx x Ly torus, by a Gray-code walk.
//!
//!   subsets LX LY [planar]
//!
//! For each size s it prints the true maximum of internal links, against the limit. With `planar` the limit is the planar one, 2s - ceil(2 sqrt s),
//! which must go red on tori because stripes and complements beat it. Integer only, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use review::{adj_limit, ceil_two_root, Torus};

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (lx, ly): (usize, usize) = (args[1].parse().expect("lx"), args[2].parse().expect("ly"));
    let planar = args.get(3).is_some_and(|x| x == "planar");
    let t = Torus::new(lx, ly);
    let p = t.sites;
    assert!(p <= 30);
    // Plaquette neighbours through links: one entry per link.
    let mut nb = vec![Vec::new(); p];
    for l in 0..t.nl {
        let [a, b] = t.link_plaq[l];
        assert_ne!(a, b, "a link's two plaquettes must differ for L>=2");
        nb[a].push(b);
        nb[b].push(a);
    }
    for row in &nb {
        assert_eq!(row.len(), 4);
    }
    let mut max_e = vec![0i32; p + 1];
    let mut mask: u32 = 0;
    let mut size: usize = 0;
    let mut e: i32 = 0;
    let total: u64 = 1u64 << p;
    for k in 1..total {
        let bit = k.trailing_zeros() as usize;
        let m = 1u32 << bit;
        let mut inside = 0;
        for &q in &nb[bit] {
            if mask & (1u32 << q) != 0 {
                inside += 1;
            }
        }
        if mask & m == 0 {
            e += inside;
            size += 1;
        } else {
            e -= inside;
            size -= 1;
        }
        mask ^= m;
        if e > max_e[size] {
            max_e[size] = e;
        }
    }
    let mut violations = 0;
    let mut tight = 0;
    for (s, m) in max_e.iter().enumerate() {
        let su = s as u32;
        let limit = if planar { 2 * su - ceil_two_root(su) } else { adj_limit(su, lx as u32, ly as u32) };
        let lim = limit as i32;
        if *m > lim {
            violations += 1;
        }
        if *m == lim {
            tight += 1;
        }
        println!("ADJ|Lx={lx}|Ly={ly}|s={s}|true_max={m}|limit={lim}|json=0");
    }
    println!("ADJ_VERDICT|Lx={lx}|Ly={ly}|subsets={total}|sizes={}|violations={violations}|tight_sizes={tight}|mode={}|json=0", p + 1, if planar { "planar_sabotage" } else { "torus" });
    if violations != 0 {
        std::process::exit(2);
    }
}
