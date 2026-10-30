//! Dictionary tests B and A (the human-based understanding). Integer only, HBP out, json=0.
//!
//! B  "Straight out, curved back ... a straight line is symmetric; a curve is not."
//!    r = R + R^-1 on a ring of 3^N; per level, jJ = all-ones on digit l (the PR #40 model) and
//!    jc = I + R - R^2 on digit l (balanced-trit weights +1, +1, -1).
//! A  "Three inversions, three brakes: every turn has to be held at its own level, or the three
//!    collapse into one and the direction is lost." 27 states = three levels of canonical trits.

#[allow(dead_code)]
#[path = "C:/asolaria-acer/asolaria-os/kernel/core/src/tribit/mod.rs"]
mod tribit;

use tribit::Zero;

type Mat = Vec<Vec<i64>>;

fn digit_of(x: usize, l: u32) -> usize {
    (x / 3usize.pow(l - 1)) % 3
}

fn with_digit(x: usize, l: u32, d: usize) -> usize {
    let p = 3usize.pow(l - 1);
    x - digit_of(x, l) * p + d * p
}

/// Level-l operator as a matrix M[y][x]: column x sends weight w[k] to the site whose digit l
/// is turned forward k times (k = 0 stay, 1 = R, 2 = R^2).
fn level_mat(n: u32, l: u32, w: [i64; 3]) -> Mat {
    let m = 3usize.pow(n);
    let mut a = vec![vec![0i64; m]; m];
    for x in 0..m {
        let d = digit_of(x, l);
        for (k, &wk) in w.iter().enumerate() {
            a[with_digit(x, l, (d + k) % 3)][x] += wk;
        }
    }
    a
}

fn r_mat(n: u32) -> Mat {
    let m = 3usize.pow(n);
    let mut a = vec![vec![0i64; m]; m];
    for x in 0..m {
        a[(x + 1) % m][x] += 1;
        a[(x + m - 1) % m][x] += 1;
    }
    a
}

fn transpose(a: &Mat) -> Mat {
    let m = a.len();
    (0..m).map(|i| (0..m).map(|j| a[j][i]).collect()).collect()
}

fn apply(a: &Mat, v: &[i64]) -> Vec<i64> {
    a.iter().map(|row| row.iter().zip(v).map(|(p, q)| p * q).sum()).collect()
}

fn top_diff(x: usize, y: usize, n: u32) -> u32 {
    (1..=n).rev().find(|&l| digit_of(x, l) != digit_of(y, l)).unwrap_or(0)
}

/// Reach under levels 1..n of the given weights, from src: (first tick per site, final vector,
/// blocks exact after each level).
fn reach(levels: &[Mat], src: usize, n: u32) -> (Vec<u32>, Vec<i64>, bool) {
    let m = 3usize.pow(n);
    let mut v = vec![0i64; m];
    v[src] = 1;
    let mut first = vec![u32::MAX; m];
    first[src] = 0;
    let mut blocks = true;
    for (i, a) in levels.iter().enumerate() {
        let l = i as u32 + 1;
        v = apply(a, &v);
        let size = 3usize.pow(l);
        for (y, &val) in v.iter().enumerate() {
            if (val != 0) != (y / size == src / size) {
                blocks = false;
            }
            if val != 0 && first[y] == u32::MAX {
                first[y] = l;
            }
        }
    }
    (first, v, blocks)
}

fn test_b() -> [u8; 5] {
    let (mut b1, mut b2, mut b3, mut b4, mut b5) = (1u8, 1u8, 1u8, 1u8, 1u8);
    for n in 1..=5u32 {
        let m = 3usize.pow(n);
        let r = r_mat(n);
        let r_sym = transpose(&r) == r;
        b1 &= u8::from(r_sym);
        let (mut jj_sym, mut jc_asym, mut jc_three, mut jc_t_is_return) = (true, true, true, true);
        let mut jcs = Vec::new();
        for l in 1..=n {
            let jj = level_mat(n, l, [1, 1, 1]);
            let jc = level_mat(n, l, [1, 1, -1]);
            jj_sym &= transpose(&jj) == jj;
            jc_asym &= transpose(&jc) != jc;
            jc_three &= jc.iter().all(|row| row.iter().filter(|&&a| a != 0).count() == 3);
            jc_t_is_return &= transpose(&jc) == level_mat(n, l, [1, -1, 1]);
            jcs.push(jc);
        }
        b2 &= u8::from(jj_sym);
        b3 &= u8::from(jc_asym && jc_three && jc_t_is_return);
        // B4 / B5 with the curved j, from every source
        let (mut per_site, mut blocks_ok, mut pm_only, mut counts_ok, mut ticks_max) = (true, true, true, true, 0u32);
        let (want_pos, want_neg) = ((m + 1) / 2, (m - 1) / 2);
        for src in 0..m {
            let (first, v, blocks) = reach(&jcs, src, n);
            ticks_max = ticks_max.max(*first.iter().max().unwrap_or(&u32::MAX));
            per_site &= (0..m).all(|y| first[y] == top_diff(src, y, n));
            blocks_ok &= blocks;
            pm_only &= v.iter().all(|&a| a == 1 || a == -1);
            let pos = v.iter().filter(|&&a| a == 1).count();
            let neg = v.iter().filter(|&&a| a == -1).count();
            counts_ok &= pos == want_pos && neg == want_neg && v.iter().sum::<i64>() == 1;
        }
        let q6 = if n >= 2 {
            let (s, t) = (3usize.pow(n - 1) - 1, 3usize.pow(n - 1));
            reach(&jcs, s, n).0[t] == n
        } else {
            true
        };
        b4 &= u8::from(ticks_max == n && per_site && blocks_ok && pm_only && q6);
        b5 &= u8::from(counts_ok);
        println!(
            "B_N|N={n}|sites={m}|r_symmetric={}|jJ_symmetric={}|jc_asymmetric={}|jc_three_per_row={}|jc_transpose_is_I-R+R2={}|jc_ticks_to_reach_all={ticks_max}|jc_per_site_eq_top_digit={}|jc_blocks_exact={}|jc_boundary_jN={}|jc_product_entries_pm1={}|jc_column_pos={want_pos}_neg={want_neg}_sum1={}|json=0",
            u8::from(r_sym), u8::from(jj_sym), u8::from(jc_asym), u8::from(jc_three), u8::from(jc_t_is_return),
            u8::from(per_site), u8::from(blocks_ok), u8::from(q6), u8::from(pm_only), u8::from(counts_ok)
        );
    }
    [b1, b2, b3, b4, b5]
}

type State = [Zero; 3];

fn all_states() -> Vec<State> {
    (0..27u8).map(|i| [Zero::from_digit(i % 3), Zero::from_digit((i / 3) % 3), Zero::from_digit(i / 9)]).collect()
}

fn rot_k(z: Zero, k: u8) -> Zero {
    (0..k).fold(z, |a, _| a.rotate())
}

fn test_a() -> [u8; 5] {
    let vals = [Zero::Neg, Zero::Nil, Zero::Pos];
    // mirror = negation: Neg <-> Pos; its involution and fixed point are checked below
    let neg = |z: Zero| match z {
        Zero::Neg => Zero::Pos,
        Zero::Pos => Zero::Neg,
        Zero::Nil => Zero::Nil,
    };
    let a1 = vals.iter().all(|&z| rot_k(z, 3) == z)
        && vals.iter().all(|&z| z.rotate() != z.anti_rotate())
        && vals.iter().all(|&z| neg(neg(z)) == z)
        && neg(Zero::Nil) == Zero::Nil;
    let states = all_states();
    let held = |s: State| [s[0].rotate(), s[1].rotate(), s[2].rotate()];
    let collapsed = |s: State| [rot_k(s[0], 3), s[1], s[2]];
    let held_moved = states.iter().filter(|&&s| held(s) != s).count();
    let held_order = (1..=6).find(|&k| states.iter().all(|&s| (0..k).fold(s, |a, _| held(a)) == s)).unwrap_or(0);
    let collapsed_moved = states.iter().filter(|&&s| collapsed(s) != s).count();
    let table = |a: u8, b: u8, c: u8| -> Vec<State> {
        states.iter().map(|s| [rot_k(s[0], a), rot_k(s[1], b), rot_k(s[2], c)]).collect()
    };
    let mut per_level: Vec<Vec<State>> = Vec::new();
    for a in 0..3 {
        for b in 0..3 {
            for c in 0..3 {
                let t = table(a, b, c);
                if !per_level.contains(&t) {
                    per_level.push(t);
                }
            }
        }
    }
    let mut one_level: Vec<Vec<State>> = Vec::new();
    for k in 0..9u8 {
        let t = table(k % 3 + 3 * (k / 3), 0, 0);
        if !one_level.contains(&t) {
            one_level.push(t);
        }
    }
    let sum = |s: State| s.iter().map(|z| z.digit() as u32).sum::<u32>() % 3;
    let level_changed = states.iter().filter(|&&s| held(s) != s).count();
    let sum_changed = states.iter().filter(|&&s| sum(held(s)) != sum(s)).count();
    println!("A_TRIT|rotate_cubed_is_identity=1|rotate_ne_anti_rotate_all3={}|mirror_is_involution_with_fixed_Nil={}|json=0",
        u8::from(vals.iter().all(|&z| z.rotate() != z.anti_rotate())), u8::from(a1));
    println!("A_HELD|states_moved={held_moved}/27|order={held_order}|json=0");
    println!("A_COLLAPSED|states_moved={collapsed_moved}/27|json=0");
    println!("A_DISTINCT|per_level_turns={}|one_level_turns={}|json=0", per_level.len(), one_level.len());
    println!("A_OBSERVE|per_level_changed={level_changed}/27|summed_changed={sum_changed}/27|json=0");
    [
        u8::from(a1),
        u8::from(held_moved == 27 && held_order == 3),
        u8::from(collapsed_moved == 0),
        u8::from(per_level.len() == 27 && one_level.len() == 3),
        u8::from(level_changed == 27 && sum_changed == 0),
    ]
}

fn main() {
    let b = test_b();
    println!("B_PREDICTIONS|B1_r_symmetric={}|B2_jJ_symmetric={}|B3_jc_curved_tridirectional={}|B4_reach_unchanged_with_jc={}|B5_jc_all_levels_not_J={}|json=0", b[0], b[1], b[2], b[3], b[4]);
    let a = test_a();
    println!("A_PREDICTIONS|A1_turn_not_mirror={}|A2_held_moves_all_order3={}|A3_collapsed_identity={}|A4_27_vs_3={}|A5_sum_hides_held_turn={}|json=0", a[0], a[1], a[2], a[3], a[4]);
}
