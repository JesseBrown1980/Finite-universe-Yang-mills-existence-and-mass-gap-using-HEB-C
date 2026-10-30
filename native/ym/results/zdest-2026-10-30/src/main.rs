//! Destination-pull test: "No quantum data can leave at c without having z pulled instantly
//! from its destination ... Anything in the matrix ... should not be affected."
//!
//! Same lattice as zlight (64x64 torus of canonical trits, local linear GF(3) rule, c = 1).
//! RULE (operator): z(t) = sha256(global_root(t) || dest_token(t)); the destination token is
//! pulled at step 0, before emission, and re-pulled when the destination is switched. The pull
//! writes no cell. BOOKKEEPING (control): z(t) = global_root(t). HBP out, json=0, integer only.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

#[allow(dead_code)]
#[path = "C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/crates/torusl/src/sha.rs"]
mod sha;

use tribit::Zero;

const N: usize = 64;
const STEPS: usize = 40;
const SRC: (usize, usize) = (20, 32);
const D1: (usize, usize) = (40, 32);
const D2: (usize, usize) = (20, 52);
const SWITCH: usize = 5;

type Grid = Vec<Zero>;
type H = [u8; 32];

fn idx(x: usize, y: usize) -> usize {
    y * N + x
}

fn bal3(v: i32) -> Zero {
    Zero::from_digit(((v.rem_euclid(3) as u8) + 1) % 3)
}

fn background() -> Grid {
    let mut s: u64 = 0x5A1A_C0DE;
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
            out.push(bal3(d(0, 0) + d(1, 0) + d(N - 1, 0) + d(0, 1) + d(0, N - 1)));
        }
    }
    out
}

fn root(g: &Grid) -> H {
    let mut level: Vec<H> = (0..N * N).map(|i| sha::sha256(&[(i % N) as u8, (i / N) as u8, g[i].digit()])).collect();
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

fn token(d: (usize, usize)) -> H {
    sha::sha256(&[d.0 as u8, d.1 as u8, 1])
}

fn cat(a: &H, b: &H) -> H {
    let mut buf = [0u8; 64];
    buf[..32].copy_from_slice(a);
    buf[32..].copy_from_slice(b);
    sha::sha256(&buf)
}

struct Run {
    z: Vec<H>,
    grids: Vec<Grid>,
}

/// laser: fire at SRC at step 0. rule: true = operator RULE, false = BOOKKEEPING.
/// dest(t): the destination in force at step t (None = no pull).
fn run(laser: bool, rule: bool, dest: fn(usize) -> Option<(usize, usize)>) -> Run {
    let mut g = background();
    if laser {
        let i = idx(SRC.0, SRC.1);
        g[i] = bal3(g[i].direction() as i32 + 1);
    }
    let mut r = Run { z: vec![], grids: vec![] };
    for t in 0..=STEPS {
        if t > 0 {
            g = step(&g);
        }
        let gr = root(&g);
        let z = match (rule, dest(t)) {
            (true, Some(d)) => cat(&gr, &token(d)),
            _ => gr,
        };
        r.z.push(z);
        r.grids.push(g.clone());
    }
    r
}

fn first_diff(a: &[H], b: &[H]) -> String {
    a.iter().zip(b).position(|(x, y)| x != y).map_or("never".into(), |p| p.to_string())
}

fn tdist(a: (usize, usize), b: (usize, usize)) -> usize {
    let d = |p: usize, q: usize| {
        let e = p.abs_diff(q);
        e.min(N - e)
    };
    d(a.0, b.0) + d(a.1, b.1)
}

fn det3(m: [[i64; 3]; 3]) -> i64 {
    m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
}

/// circulant a*I + b*R + c*R^2 with R the forward shift
fn circ(a: i64, b: i64, c: i64) -> [[i64; 3]; 3] {
    let mut m = [[0i64; 3]; 3];
    for (i, row) in m.iter_mut().enumerate() {
        row[i] += a;
        row[(i + 1) % 3] += b;
        row[(i + 2) % 3] += c;
    }
    m
}

fn rank_mod3(m: [[i64; 3]; 3]) -> usize {
    let mut a: Vec<Vec<i64>> = m.iter().map(|r| r.iter().map(|v| v.rem_euclid(3)).collect()).collect();
    let mut rank = 0;
    for col in 0..3 {
        if let Some(p) = (rank..3).find(|&r| a[r][col] != 0) {
            a.swap(rank, p);
            let inv = if a[rank][col] == 1 { 1 } else { 2 };
            for v in a[rank].iter_mut() {
                *v = (*v * inv) % 3;
            }
            for r in 0..3 {
                if r != rank && a[r][col] != 0 {
                    let f = a[r][col];
                    for c in 0..3 {
                        a[r][c] = (a[r][c] - f * a[rank][c]).rem_euclid(3);
                    }
                }
            }
            rank += 1;
        }
    }
    rank
}

fn main() {
    let c0 = run(false, false, |_| None);
    let l1 = run(true, true, |_| Some(D1));
    let l2 = run(true, true, |t| Some(if t < SWITCH { D1 } else { D2 }));
    let k1 = run(true, false, |_| Some(D1));
    let k2 = run(true, false, |t| Some(if t < SWITCH { D1 } else { D2 }));
    // M1
    let l1_vs_c0 = first_diff(&l1.z, &c0.z);
    let l2_vs_l1 = first_diff(&l2.z, &l1.z);
    let m1 = u8::from(l1_vs_c0 == "0" && l2_vs_l1 == SWITCH.to_string());
    // M2
    let k1_vs_k2 = first_diff(&k1.z, &k2.z);
    let m2 = u8::from(k1_vs_k2 == "never");
    // M3: the pull and the switch change no cell
    let grids_equal = (0..=STEPS).all(|t| l1.grids[t] == l2.grids[t] && l1.grids[t] == k1.grids[t] && k1.grids[t] == k2.grids[t]);
    let m3 = u8::from(grids_equal);
    // M4: locality against the no-laser control
    let mut violations = 0usize;
    for t in 0..=STEPS {
        for y in 0..N {
            for x in 0..N {
                if tdist((x, y), SRC) > t && l2.grids[t][idx(x, y)] != c0.grids[t][idx(x, y)] {
                    violations += 1;
                }
            }
        }
    }
    let m4 = u8::from(violations == 0);
    // M5: the destinations' own cells change only when light arrives
    let cell_first = |r: &Run, d: (usize, usize)| {
        (0..=STEPS).find(|&t| r.grids[t][idx(d.0, d.1)] != c0.grids[t][idx(d.0, d.1)]).map_or("never".into(), |t| t.to_string())
    };
    let (d1_first, d2_first) = (cell_first(&l2, D1), cell_first(&l2, D2));
    let m5 = u8::from(d1_first == "20" && d2_first == "20");
    // M6: rank / determinant check of the other seat's claim
    let j = circ(1, 1, 1);
    let jc = circ(1, 1, -1);
    let jr = circ(1, -1, 1);
    let (dj, djc, djr) = (det3(j), det3(jc), det3(jr));
    let m6 = u8::from(rank_mod3(j) == 1 && djc == 4 && djc.rem_euclid(3) == 1 && djr == 4 && djr.rem_euclid(3) == 1 && rank_mod3(jc) == 3);
    println!("ZDEST_RUN|grid={N}x{N}|src=({},{})|D1=({},{})|D2=({},{})|switch_step={SWITCH}|steps={STEPS}|json=0", SRC.0, SRC.1, D1.0, D1.1, D2.0, D2.1);
    println!("ZDEST_M1|rule_z_L1_vs_C0_first_diff={l1_vs_c0}|rule_z_L2_vs_L1_first_diff={l2_vs_l1}|json=0");
    println!("ZDEST_M2|bookkeeping_z_K1_vs_K2_first_diff={k1_vs_k2}|json=0");
    println!("ZDEST_M3|cell_grids_L1_L2_K1_K2_identical_all_steps={}|json=0", u8::from(grids_equal));
    println!("ZDEST_M4|locality_violations={violations}|json=0");
    println!("ZDEST_M5|D1_own_cell_first_diff={d1_first}|D2_own_cell_first_diff={d2_first}|json=0");
    println!("ZDEST_M6|J_rank_mod3={}|det_J={dj}|det_I+R-R2={djc}|mod3={}|rank_mod3={}|det_I-R+R2={djr}|mod3={}|json=0", rank_mod3(j), djc.rem_euclid(3), rank_mod3(jc), djr.rem_euclid(3));
    println!("ZDEST_PREDICTIONS|M1_z_pulled_instantly_and_follows_switch={m1}|M2_bookkeeping_blind_to_switch={m2}|M3_pull_changes_no_cell={m3}|M4_locality_intact={m4}|M5_destination_untouched_until_light={m5}|M6_rank_claim={m6}|json=0");
}
