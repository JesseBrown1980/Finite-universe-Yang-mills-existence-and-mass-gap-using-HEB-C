//! Per-level test: "Instant is not always instant, it is instant PER LEVEL, three per level."
//!
//! A ring of 3^N sites; each address is N base-3 digits (canonical `tribit::Zero` digits), and
//! digit l is level l. Two operators, from the operator's dictionary:
//!   r  "the radius, goes straight there bidirectionally"   -> one step to both ring neighbours
//!   j  "the reverse of the radius ... the tridirectional curve has to come back"
//!      -> at level l, all three values of digit l mixed at once (all-ones 3x3), other digits kept
//! Reach = first tick at which a site is nonzero, starting from one source. Nonnegative integers
//! only, so nothing can cancel. Output: HBP rows, json=0.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

use tribit::Zero;

const NMAX: u32 = 5;

/// Base-3 address of site x on 3^n sites, least significant digit first, as canonical trits.
fn digits(x: usize, n: u32) -> Vec<Zero> {
    let mut v = Vec::with_capacity(n as usize);
    let mut y = x;
    for _ in 0..n {
        v.push(Zero::from_digit((y % 3) as u8));
        y /= 3;
    }
    v
}

fn site(d: &[Zero]) -> usize {
    d.iter().rev().fold(0usize, |acc, z| acc * 3 + z.digit() as usize)
}

/// One j tick at level l (1-based): each site's value is spread over the three sites that
/// differ from it only in digit l.
fn j_level(v: &[u64], n: u32, l: u32) -> Vec<u64> {
    let mut out = vec![0u64; v.len()];
    for (x, &a) in v.iter().enumerate() {
        if a == 0 {
            continue;
        }
        let mut d = digits(x, n);
        for t in 0..3u8 {
            d[(l - 1) as usize] = Zero::from_digit(t);
            out[site(&d)] += a;
        }
    }
    out
}

/// One r tick: reach the two ring neighbours (straight out, both ways).
fn r_step(s: &[bool]) -> Vec<bool> {
    let m = s.len();
    (0..m).map(|y| s[(y + m - 1) % m] || s[(y + 1) % m]).collect()
}

/// First tick each site is reached by r from `src` (u32::MAX if never).
fn r_first(m: usize, src: usize) -> Vec<u32> {
    let mut first = vec![u32::MAX; m];
    let mut s = vec![false; m];
    s[src] = true;
    first[src] = 0;
    let mut t = 0u32;
    while first.iter().any(|&f| f == u32::MAX) && t < 2 * m as u32 {
        t += 1;
        s = r_step(&s);
        for (y, &on) in s.iter().enumerate() {
            if on && first[y] == u32::MAX {
                first[y] = t;
            }
        }
    }
    first
}

/// First tick each site is reached by j from `src`, ticking levels 1..n in order; also the
/// value vector after all n levels, and whether after levels 1..l the reached set is exactly
/// the source's block of 3^l sites, for every l.
fn j_first(n: u32, src: usize) -> (Vec<u32>, Vec<u64>, bool) {
    let m = 3usize.pow(n);
    let mut v = vec![0u64; m];
    v[src] = 1;
    let mut first = vec![u32::MAX; m];
    first[src] = 0;
    let mut blocks_exact = true;
    for l in 1..=n {
        v = j_level(&v, n, l);
        let size = 3usize.pow(l);
        for (y, &a) in v.iter().enumerate() {
            let same_block = y / size == src / size;
            if (a > 0) != same_block {
                blocks_exact = false;
            }
            if a > 0 && first[y] == u32::MAX {
                first[y] = l;
            }
        }
    }
    (first, v, blocks_exact)
}

/// Index (1-based) of the highest base-3 digit where x and y differ; 0 if equal.
fn top_diff(x: usize, y: usize, n: u32) -> u32 {
    let (a, b) = (digits(x, n), digits(y, n));
    (0..n).rev().find(|&i| a[i as usize] != b[i as usize]).map_or(0, |i| i + 1)
}

fn main() {
    let (mut q1, mut q2, mut q3, mut q4, mut q5, mut q6) = (1u8, 1u8, 1u8, 1u8, 1u8, 1u8);
    for n in 1..=NMAX {
        let m = 3usize.pow(n);
        // Q2 / Q1: r from source 0 (the ring is symmetric, so one source suffices)
        let rf = r_first(m, 0);
        let r_all = *rf.iter().max().unwrap_or(&u32::MAX);
        let r_pred = ((m - 1) / 2) as u32;
        q2 &= u8::from(r_all == r_pred);
        // Q3, Q5: j from every source
        let (mut j_all_max, mut per_site_ok, mut blocks_ok, mut product_ok) = (0u32, true, true, true);
        for src in 0..m {
            let (jf, v, blocks) = j_first(n, src);
            j_all_max = j_all_max.max(*jf.iter().max().unwrap_or(&u32::MAX));
            per_site_ok &= (0..m).all(|y| jf[y] == top_diff(src, y, n));
            blocks_ok &= blocks;
            product_ok &= v.iter().all(|&a| a == 1);
        }
        q3 &= u8::from(j_all_max == n && per_site_ok && blocks_ok);
        q5 &= u8::from(product_ok);
        // Q4: every column (= row, the level matrix is symmetric) of every level has exactly 3 nonzeros
        let mut three = true;
        for l in 1..=n {
            for x in 0..m {
                let mut e = vec![0u64; m];
                e[x] = 1;
                three &= j_level(&e, n, l).iter().filter(|&&a| a > 0).count() == 3;
            }
        }
        q4 &= u8::from(three);
        if n == 1 {
            q1 &= u8::from(r_all == 1 && j_all_max == 1);
        }
        // Q6: ring neighbours across the top-level boundary
        let (q6_line, q6_ok) = if n >= 2 {
            let (s, t) = (3usize.pow(n - 1) - 1, 3usize.pow(n - 1));
            let (rt, jt) = (r_first(m, s)[t], j_first(n, s).0[t]);
            (format!("|q6_source={s}|q6_target={t}|q6_r_ticks={rt}|q6_j_ticks={jt}"), rt == 1 && jt == n)
        } else {
            (String::new(), true)
        };
        q6 &= u8::from(q6_ok);
        println!(
            "PERLEVEL_N|N={n}|sites={m}|r_ticks_to_reach_all={r_all}|r_predicted={r_pred}|j_ticks_to_reach_all={j_all_max}|j_per_site_eq_top_digit={}|j_blocks_exact_each_level={}|j_three_per_level={}|j_all_levels_product_all_ones={}{q6_line}|json=0",
            u8::from(per_site_ok),
            u8::from(blocks_ok),
            u8::from(three),
            u8::from(product_ok)
        );
    }
    println!("PERLEVEL_PREDICTIONS|Q1_one_level_both_instant={q1}|Q2_r_is_c1={q2}|Q3_j_one_tick_per_level={q3}|Q4_three_per_level={q4}|Q5_all_levels_is_J={q5}|Q6_boundary_r1_jN={q6}|json=0");
}
