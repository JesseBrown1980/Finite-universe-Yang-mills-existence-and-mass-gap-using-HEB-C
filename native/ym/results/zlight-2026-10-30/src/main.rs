//! z versus light: does a hash layer change instantly while light travels at c = 1 per step?
//!
//! A 64x64 torus of canonical balanced trits (`tribit::Zero`). One update rule, local and
//! linear over GF(3): each cell becomes the balanced sum of itself and its four von Neumann
//! neighbours. Nothing can move faster than one cell per step (c = 1).
//!
//! A "laser" adds a trit message at a source cell at step 0. We record, against the
//! no-laser control, when three hashes change:
//!   global root          Merkle root over every cell              (the z layer)
//!   target local         the target cell alone                    (what a local observer sees)
//!   target with global   target local || global root              (a target that can read z)
//! Output: HBP rows, json=0. Integer only.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

#[allow(dead_code)]
#[path = "C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/crates/torusl/src/sha.rs"]
mod sha;

use tribit::Zero;

const N: usize = 64;
const STEPS: usize = 40;
const TARGET: (usize, usize) = (40, 32);

type Grid = Vec<Zero>;
/// A laser pulse: source cell and the trit message added there at step 0.
type Laser = Option<(usize, usize, i32)>;
/// (variant name, laser, light distance from source to target on the torus)
type Variant = (&'static str, Laser, usize);

fn idx(x: usize, y: usize) -> usize {
    y * N + x
}

/// Balanced residue of an integer as a canonical trit: 0 -> Nil, 1 -> Pos, 2 -> Neg.
fn bal3(v: i32) -> Zero {
    let r = v.rem_euclid(3) as u8;
    Zero::from_digit((r + 1) % 3)
}

/// Deterministic background: a 64-bit linear congruential sequence, integer only.
fn background(seed: u64) -> Grid {
    let mut s = seed;
    (0..N * N)
        .map(|_| {
            s = s.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407);
            Zero::from_digit(((s >> 33) % 3) as u8)
        })
        .collect()
}

fn step(g: &Grid) -> Grid {
    let mut out = Vec::with_capacity(N * N);
    for y in 0..N {
        for x in 0..N {
            let d = |dx: usize, dy: usize| g[idx((x + dx) % N, (y + dy) % N)].direction() as i32;
            let sum = d(0, 0) + d(1, 0) + d(N - 1, 0) + d(0, 1) + d(0, N - 1);
            out.push(bal3(sum));
        }
    }
    out
}

fn leaf(x: usize, y: usize, z: Zero) -> [u8; 32] {
    sha::sha256(&[x as u8, y as u8, z.digit()])
}

fn root(g: &Grid) -> [u8; 32] {
    let mut level: Vec<[u8; 32]> = (0..N * N).map(|i| leaf(i % N, i / N, g[i])).collect();
    while level.len() > 1 {
        level = level
            .chunks(2)
            .map(|p| {
                if p.len() == 2 {
                    let mut b = [0u8; 64];
                    b[..32].copy_from_slice(&p[0]);
                    b[32..].copy_from_slice(&p[1]);
                    sha::sha256(&b)
                } else {
                    p[0]
                }
            })
            .collect();
    }
    level[0]
}

fn hex(h: &[u8; 32]) -> String {
    use std::fmt::Write;
    h.iter().fold(String::with_capacity(64), |mut s, b| {
        let _ = write!(s, "{b:02x}");
        s
    })
}

struct Trace {
    root: Vec<[u8; 32]>,
    local: Vec<[u8; 32]>,
    with_global: Vec<[u8; 32]>,
}

/// One universe. `laser` = Some((src_x, src_y, message)) adds the message trit at step 0.
fn run(laser: Laser) -> Trace {
    let mut g = background(0x5A1A_C0DE);
    if let Some((sx, sy, m)) = laser {
        let i = idx(sx, sy);
        g[i] = bal3(g[i].direction() as i32 + m);
    }
    let mut t = Trace { root: vec![], local: vec![], with_global: vec![] };
    for s in 0..=STEPS {
        if s > 0 {
            g = step(&g);
        }
        let r = root(&g);
        let l = leaf(TARGET.0, TARGET.1, g[idx(TARGET.0, TARGET.1)]);
        let mut b = [0u8; 64];
        b[..32].copy_from_slice(&l);
        b[32..].copy_from_slice(&r);
        t.root.push(r);
        t.local.push(l);
        t.with_global.push(sha::sha256(&b));
    }
    t
}

fn first_diff(a: &[[u8; 32]], b: &[[u8; 32]]) -> String {
    a.iter().zip(b).position(|(x, y)| x != y).map_or("never".into(), |p| p.to_string())
}

fn distinct(traces: &[Trace], f: fn(&Trace) -> &Vec<[u8; 32]>, s: usize) -> usize {
    let mut v: Vec<[u8; 32]> = traces.iter().map(|t| f(t)[s]).collect();
    v.sort();
    v.dedup();
    v.len()
}

fn main() {
    let (tx, ty) = TARGET;
    // (name, laser, light distance to target on the torus)
    let variants: [Variant; 6] = [
        ("V0", None, 0),
        ("V1", Some((tx - 20, ty, 1)), 20),
        ("V2", Some((tx - 20, ty, -1)), 20),
        ("V3", Some((tx - 24, ty, 1)), 24),
        ("V4", Some((tx - 24, ty, -1)), 24),
        ("V5", Some((tx, ty - 28, 1)), 28),
    ];
    let traces: Vec<Trace> = variants.iter().map(|v| run(v.1)).collect();
    let c = &traces[0];
    println!("ZLIGHT_RUN|steps={STEPS}|grid={N}x{N}|target=({tx},{ty})|control_root_step0={}|json=0", hex(&c.root[0]));
    let (mut p1, mut p2, mut p5) = (1, 1, 1);
    for (k, (name, _, d)) in variants.iter().enumerate().skip(1) {
        let t = &traces[k];
        let g = first_diff(&t.root, &c.root);
        let l = first_diff(&t.local, &c.local);
        let w = first_diff(&t.with_global, &c.with_global);
        p1 &= u8::from(g == "0");
        p2 &= u8::from(l == d.to_string());
        p5 &= u8::from(w == "0");
        println!("ZLIGHT_VARIANT|v={name}|light_distance={d}|global_root_first_diff={g}|target_local_first_diff={l}|target_with_global_first_diff={w}|json=0");
    }
    let mut p3 = 1;
    for s in 0..20 {
        let n = distinct(&traces, |t| &t.local, s);
        if n != 1 {
            p3 = 0;
        }
        if s == 0 || s == 19 {
            println!("ZLIGHT_LOCAL_INFO|step={s}|distinct_target_local_across_6_variants={n}|json=0");
        }
    }
    for s in [20usize, 24, 28] {
        println!("ZLIGHT_LOCAL_INFO|step={s}|distinct_target_local_across_6_variants={}|json=0", distinct(&traces, |t| &t.local, s));
    }
    let r0 = distinct(&traces, |t| &t.root, 0);
    let w0 = distinct(&traces, |t| &t.with_global, 0);
    let p4 = u8::from(r0 == 6);
    p5 &= u8::from(w0 == 6);
    println!("ZLIGHT_GLOBAL_INFO|step=0|distinct_global_roots_across_6_variants={r0}|distinct_target_with_global_across_6_variants={w0}|json=0");
    println!("ZLIGHT_PREDICTIONS|P1_global_instant={p1}|P2_local_at_exactly_d={p2}|P3_no_local_info_before_arrival={p3}|P4_global_encodes_aim_and_message_at_step0={p4}|P5_target_reading_global_learns_instantly={p5}|json=0");
}
