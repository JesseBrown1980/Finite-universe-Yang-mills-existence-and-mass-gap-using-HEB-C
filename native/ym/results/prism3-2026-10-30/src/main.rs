//! Three-prism test: "j curves based on universal hash and particles that approximate before
//! travel based on laser." Independent Rust 1.81 integer replication beside PR #43 (Python).
//!
//! World: source + 3 prism stages = 1 + 3 + 9 + 27 = 40 balanced-trit cells (tribit::Zero).
//! Prism k splits each beam cell into (stay, forward, back) with the curved j: j+ = (+1,+1,-1)
//! or j- = (+1,-1,+1), chosen by bit k of z = sha256(laser || destination || world root at step 0).
//! The beam moves one stage per step (c = 1); a stage it has left goes back to zero.
//! LOCKED: orientations fixed from z at emission. LIVE: prism t reads the z in force before step t.
//! HBP out, json=0, integer only.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

#[allow(dead_code)]
#[path = "C:/Users/acer/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/native/ym/crates/torusl/src/sha.rs"]
mod sha;

use tribit::Zero;

type World = [Vec<i32>; 4];
type H = [u8; 32];
/// Destination in force at step t, for a run.
type DestFn = dyn Fn(usize) -> u8;

const W_PLUS: [i32; 3] = [1, 1, -1];
const W_MINUS: [i32; 3] = [1, -1, 1];

fn bal(v: i32) -> i32 {
    // balanced residue mod 3, through the canonical trit
    Zero::from_digit(((v.rem_euclid(3) as u8) + 1) % 3).direction() as i32
}

fn weights(bit: u8) -> [i32; 3] {
    if bit == 0 {
        W_PLUS
    } else {
        W_MINUS
    }
}

fn fresh(laser: i32) -> World {
    let mut w: World = [vec![0; 1], vec![0; 3], vec![0; 9], vec![0; 27]];
    w[0][0] = laser;
    w
}

fn root(w: &World) -> H {
    let mut leaves: Vec<H> = Vec::new();
    for (s, stage) in w.iter().enumerate() {
        for (i, &a) in stage.iter().enumerate() {
            let z = Zero::from_digit(((a.rem_euclid(3) as u8) + 1) % 3);
            leaves.push(sha::sha256(&[s as u8, i as u8, z.digit()]));
        }
    }
    while leaves.len() > 1 {
        leaves = leaves
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
    leaves[0]
}

fn zhash(laser: i32, dest: u8, root0: &H) -> H {
    let mut b = vec![if laser > 0 { 2u8 } else { 0u8 }, dest];
    b.extend_from_slice(root0);
    sha::sha256(&b)
}

fn bits(z: &H) -> [u8; 3] {
    [z[0] & 1, (z[0] >> 1) & 1, (z[0] >> 2) & 1]
}

/// Propagate 3 steps. `orient(t)` gives the bit used by prism t (1-based). Returns the world
/// after each step 0..3.
fn propagate(laser: i32, orient: &dyn Fn(usize) -> u8) -> Vec<World> {
    let mut w = fresh(laser);
    let mut hist = vec![w.clone()];
    for t in 1..=3usize {
        let wt = weights(orient(t));
        let mut next = vec![0i32; w[t].len()];
        for (c, &a) in w[t - 1].iter().enumerate() {
            for (b, &wb) in wt.iter().enumerate() {
                next[c * 3 + b] = bal(a * wb);
            }
        }
        w[t] = next;
        w[t - 1] = vec![0; w[t - 1].len()];
        hist.push(w.clone());
    }
    hist
}

fn forecast(laser: i32, o: [u8; 3]) -> Vec<i32> {
    (0..27)
        .map(|i| {
            let (b1, b2, b3) = (i / 9, (i / 3) % 3, i % 3);
            bal(laser * weights(o[0])[b1] * weights(o[1])[b2] * weights(o[2])[b3])
        })
        .collect()
}

fn main() {
    let configs: Vec<(i32, u8)> = [1, -1].iter().flat_map(|&l| (0..27u8).map(move |d| (l, d))).collect();
    let (mut p1, mut p2, mut p4, mut p5l, mut p5v, mut p7) = (true, true, true, true, true, true);
    let mut combos: Vec<[u8; 3]> = Vec::new();
    let mut forecasts: Vec<Vec<i32>> = Vec::new();
    let mut zs: Vec<H> = Vec::new();
    let mut local_states: Vec<Vec<i32>> = Vec::new();
    let mut live_changed_cfgs = 0usize;
    let mut live_violations = 0usize;
    // P7: classical controller = a stored 3-bit table built in a separate pass
    let table: Vec<[u8; 3]> = configs
        .iter()
        .map(|&(l, d)| bits(&zhash(l, d, &root(&fresh(l)))))
        .collect();
    for (ci, &(laser, dest)) in configs.iter().enumerate() {
        let root0 = root(&fresh(laser));
        let z0 = zhash(laser, dest, &root0);
        let o = bits(&z0);
        let hist = propagate(laser, &|t| o[t - 1]);
        // P1: occupancy 1,3,9,27 and nothing early
        for (t, w) in hist.iter().enumerate() {
            let occ: usize = w.iter().map(|s| s.iter().filter(|&&a| a != 0).count()).sum();
            p1 &= occ == 3usize.pow(t as u32);
            for (s, stage) in w.iter().enumerate() {
                if s > t {
                    p1 &= stage.iter().all(|&a| a == 0);
                }
            }
        }
        // P2, P4
        let fc = forecast(laser, o);
        p2 &= fc == hist[3][3];
        p4 &= hist[3][3].iter().all(|&a| a != 0);
        if !combos.contains(&o) {
            combos.push(o);
        }
        if !forecasts.contains(&fc) {
            forecasts.push(fc);
        }
        if !zs.contains(&z0) {
            zs.push(z0);
        }
        // P6: the destination branch's own cell, steps 0..2
        local_states.push((0..3).map(|t| hist[t][3][dest as usize]).collect());
        // P7
        let o_table = table[ci];
        p7 &= propagate(laser, &|t| o_table[t - 1]) == hist;
        // P5: switch the destination at step 1
        let dest2 = (dest + 13) % 27;
        let dest_at: Box<DestFn> = Box::new(move |t| if t >= 1 { dest2 } else { dest });
        let z_at = |t: usize| zhash(laser, dest_at(t), &root0);
        let z_noswitch = |_t: usize| z0;
        let z_first_diff = (0..=3).find(|&t| z_at(t) != z_noswitch(t));
        // LOCKED: orientations from z at emission, so the beam is the same with or without the switch
        let locked_switch = propagate(laser, &|t| o[t - 1]);
        p5l &= z_first_diff == Some(1) && locked_switch == hist;
        // LIVE: prism t uses the z in force before step t
        let live_noswitch = propagate(laser, &|t| bits(&z_noswitch(t - 1))[t - 1]);
        let live_switch = propagate(laser, &|t| bits(&z_at(t - 1))[t - 1]);
        let mut changed = false;
        for t in 0..=3usize {
            for s in 0..4usize {
                if live_switch[t][s] != live_noswitch[t][s] {
                    changed = true;
                    if s < 2 || t < 2 {
                        live_violations += 1;
                    }
                }
            }
        }
        let new_bits = bits(&z_at(1));
        let flips_later = new_bits[1] != o[1] || bits(&z_at(2))[2] != o[2];
        p5v &= changed == flips_later;
        if changed {
            live_changed_cfgs += 1;
        }
    }
    p5v &= live_violations == 0;
    local_states.sort();
    local_states.dedup();
    let p3 = combos.len() == 8;
    let p6_local = local_states.len() == 1;
    let p6_orig = forecasts.len() == 54;
    println!("PRISM3_RUN|configs={}|cells=40|stages=1,3,9,27|json=0", configs.len());
    println!("PRISM3_P1|occupancy_1_3_9_27_and_nothing_early={}|json=0", u8::from(p1));
    println!("PRISM3_P2|forecast_at_step0_equals_propagated={}|json=0", u8::from(p2));
    println!("PRISM3_P3|distinct_orientation_combos={}|json=0", combos.len());
    println!("PRISM3_P4|final_amplitudes_all_nonzero={}|json=0", u8::from(p4));
    println!("PRISM3_P5_LOCKED|z_follows_switch_at_step1_and_beam_unchanged={}|json=0", u8::from(p5l));
    println!("PRISM3_P5_LIVE|configs_redirected={live_changed_cfgs}|redirect_iff_switched_z_flips_a_later_prism={}|locality_violations={live_violations}|json=0", u8::from(p5v));
    println!("PRISM3_P6|local_distinct_states_before_step3={}|distinct_forecasts={}|distinct_z={}|json=0", local_states.len(), forecasts.len(), zs.len());
    println!("PRISM3_P7|classical_3bit_table_equals_hash_selected={}|json=0", u8::from(p7));
    println!(
        "PRISM3_PREDICTIONS|P1={}|P2={}|P3={}|P4={}|P5_LOCKED={}|P5_LIVE={}|P6_local_zero_info={}|P6_original_forecasts_54={}|P6_addendum_z_54={}|P7={}|json=0",
        u8::from(p1), u8::from(p2), u8::from(p3), u8::from(p4), u8::from(p5l), u8::from(p5v),
        u8::from(p6_local), u8::from(p6_orig), u8::from(zs.len() == 54), u8::from(p7)
    );
}
