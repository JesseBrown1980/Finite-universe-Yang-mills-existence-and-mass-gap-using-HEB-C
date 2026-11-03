//! Exhaustive walk over every assignment of a class (e, t, c) to each plaquette of an Lx x Ly torus, with a even: 3^P assignments.
//! Each real configuration induces one of these, with each t-t link either same or different in its frame. So the minimum over assignments, with each t-t link taken
//! at the worse of the two, is a rigorous lower bound on the real minimum at each lump, tighter than the table's isoperimetric constraint.
//! It also checks the table's constraints on every assignment.
//!
//!   classes LX LY R_NUM R_DEN GFILE CLAIM_MICRO
//!
//! Single thread. Integer only, json=0.
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use review::{adj_limit, ceil_two_root, micro, Torus, Vector, NPAT, P_CC, P_EC, P_EE, P_ET, P_TC, P_TTD, P_TTS, RULE};
use std::collections::HashSet;

struct Walk<'a> {
    nb: &'a [Vec<usize>],
    cls: Vec<u8>,
    a: u32,
    b: u32,
    ee: i32,
    et: i32,
    ec: i32,
    tt: i32,
    tc: i32,
    cc: i32,
    seen: HashSet<u64>,
    visited: u64,
}

impl Walk<'_> {
    fn go(&mut self, p: usize) {
        if p == self.cls.len() {
            self.visited += 1;
            if self.a % 2 == 0 {
                // Links to plaquettes not yet assigned are all counted when their later end is assigned, so all counts are complete here.
                let key = u64::from(self.a) | (u64::from(self.b) << 6) | ((self.tt as u64) << 12) | ((self.tc as u64) << 18) | ((self.cc as u64) << 24) | ((self.et as u64) << 30) | ((self.ec as u64) << 36) | ((self.ee as u64) << 42);
                self.seen.insert(key);
            }
            return;
        }
        let nb = self.nb;
        for c in 0..3u8 {
            let (mut de, mut dt, mut dc) = (0i32, 0i32, 0i32);
            for &q in &nb[p] {
                if q < p {
                    match self.cls[q] {
                        0 => de += 1,
                        1 => dt += 1,
                        _ => dc += 1,
                    }
                }
            }
            match c {
                0 => {
                    self.ee += de;
                    self.et += dt;
                    self.ec += dc;
                }
                1 => {
                    self.et += de;
                    self.tt += dt;
                    self.tc += dc;
                    self.a += 1;
                }
                _ => {
                    self.ec += de;
                    self.tc += dt;
                    self.cc += dc;
                    self.b += 1;
                }
            }
            self.cls[p] = c;
            self.go(p + 1);
            match c {
                0 => {
                    self.ee -= de;
                    self.et -= dt;
                    self.ec -= dc;
                }
                1 => {
                    self.et -= de;
                    self.tt -= dt;
                    self.tc -= dc;
                    self.a -= 1;
                }
                _ => {
                    self.ec -= de;
                    self.tc -= dt;
                    self.cc -= dc;
                    self.b -= 1;
                }
            }
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (lx, ly): (usize, usize) = (args[1].parse().expect("lx"), args[2].parse().expect("ly"));
    let (r_num, r_den): (i128, i128) = (args[3].parse().expect("r"), args[4].parse().expect("r"));
    let v = Vector::load(&args[5]);
    let claim: i128 = args[6].parse().expect("claim");
    let t = Torus::new(lx, ly);
    let mut nb = vec![Vec::new(); t.sites];
    for l in 0..t.nl {
        let [a, b] = t.link_plaq[l];
        nb[a].push(b);
        nb[b].push(a);
    }
    let mut w = Walk { nb: &nb, cls: vec![0; t.sites], a: 0, b: 0, ee: 0, et: 0, ec: 0, tt: 0, tc: 0, cc: 0, seen: HashSet::new(), visited: 0 };
    w.go(0);
    let (ul, uy) = (lx as u32, ly as u32);
    let planar = args.iter().any(|x| x == "planar");
    let limit = |s: u32| if planar { 2 * s - ceil_two_root(s) } else { adj_limit(s, ul, uy) };
    let mut outside = 0u64;
    let mut low: Option<(i128, u32, u32, [i32; NPAT])> = None;
    let mut per: std::collections::BTreeMap<(u32, u32), (i128, [i32; NPAT])> = std::collections::BTreeMap::new();
    for key in &w.seen {
        let a = (key & 63) as u32;
        let b = ((key >> 6) & 63) as u32;
        let tt = ((key >> 12) & 63) as i32;
        let tc = ((key >> 18) & 63) as i32;
        let cc = ((key >> 24) & 63) as i32;
        let et = ((key >> 30) & 63) as i32;
        let ec = ((key >> 36) & 63) as i32;
        let ee = ((key >> 42) & 63) as i32;
        let good = 4 * a as i32 == et + tc + 2 * tt && 4 * b as i32 == ec + tc + 2 * cc && ee + et + ec + tt + tc + cc == t.nl as i32 && tt as u32 <= limit(a) && cc as u32 <= limit(b) && (tt + tc + cc) as u32 <= limit(a + b);
        if !good {
            outside += 1;
        }
        if a == 0 && b == 0 {
            continue;
        }
        let d0 = v.d(a, b);
        // Each t-t link at the worse of same and different.
        let mut best: Option<(i128, [i32; NPAT])> = None;
        for choice in [P_TTS, P_TTD] {
            let mut n = [0i32; NPAT];
            n[P_EE] = ee;
            n[P_ET] = et;
            n[P_EC] = ec;
            n[choice] = tt;
            n[P_TC] = tc;
            n[P_CC] = cc;
            let mut sum: i128 = 0;
            for (pat, moves) in RULE.iter().enumerate() {
                if n[pat] == 0 {
                    continue;
                }
                for &(da, db, c) in *moves {
                    let (ta, tb) = (a.wrapping_add_signed(da), b.wrapping_add_signed(db));
                    sum += i128::from(n[pat]) * i128::from(c) * (d0 - v.d(ta, tb));
                }
            }
            let num = r_num * i128::from(2 * a + 3 * b) * d0 + r_den * sum;
            let m = micro(num, r_den * d0);
            if best.as_ref().map_or(true, |x| m < x.0) {
                best = Some((m, n));
            }
            if tt == 0 {
                break;
            }
        }
        let (m, n) = best.expect("one choice");
        let e = per.entry((a, b)).or_insert((i128::MAX, n));
        if m < e.0 {
            *e = (m, n);
        }
        if low.as_ref().map_or(true, |x| m < x.0) {
            low = Some((m, a, b, n));
        }
    }
    for ((a, b), (m, n)) in &per {
        println!("CLASSMIN|a={a}|b={b}|micro={m}|n={n:?}|json=0");
    }
    if args.iter().any(|x| x == "dump") {
        for key in &w.seen {
            println!("CSIG|{key}|json=0");
        }
    }
    let (m, a, b, n) = low.expect("a non-flat assignment");
    println!("CLASSES|Lx={lx}|Ly={ly}|assignments={}|signatures_a_even={}|outside_constraints={outside}|lumps={}|class_min_micro={m}|at_a={a}|at_b={b}|n={n:?}|claim_micro={claim}|below_claim={}|json=0", w.visited, w.seen.len(), per.len(), i32::from(m < claim));
    if outside != 0 || m < claim {
        std::process::exit(2);
    }
}
