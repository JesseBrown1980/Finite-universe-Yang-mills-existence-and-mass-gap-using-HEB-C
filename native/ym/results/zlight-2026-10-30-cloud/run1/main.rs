//! z-versus-light cross-check. Integer-only, json=0. See PREREG.md.
use sha2::{Digest, Sha256};

const W: usize = 33;
const H: usize = 33;
const STEPS: usize = 48;
const S: (usize, usize) = (0, 16);
const T: (usize, usize) = (32, 16);

#[derive(Clone, Copy, PartialEq)]
enum Aim {
    East,
    North,
}

fn h(b: &[u8]) -> [u8; 32] {
    Sha256::digest(b).into()
}

fn root(g: &[u32]) -> [u8; 32] {
    let mut lv: Vec<[u8; 32]> = g.iter().map(|v| h(&v.to_le_bytes())).collect();
    while lv.len() > 1 {
        if lv.len() % 2 == 1 {
            let l = *lv.last().unwrap();
            lv.push(l);
        }
        lv = lv
            .chunks(2)
            .map(|p| {
                let mut b = [0u8; 64];
                b[..32].copy_from_slice(&p[0]);
                b[32..].copy_from_slice(&p[1]);
                h(&b)
            })
            .collect();
    }
    lv[0]
}

fn hex(d: &[u8; 32]) -> String {
    d.iter().map(|b| format!("{b:02x}")).collect()
}

/// Per step: (global root, local hash at T).
fn run(laser: Option<(Aim, u32)>) -> Vec<([u8; 32], [u8; 32])> {
    let mut g = vec![0u32; W * H];
    let mut out = Vec::with_capacity(STEPS + 1);
    for t in 0..=STEPS {
        if let Some((aim, p)) = laser {
            // the front is t cells from S at step t (c = 1); the trail keeps the payload
            let (x, y) = match aim {
                Aim::East => (S.0 + t, S.1),
                Aim::North => (S.0, S.1 + t),
            };
            if x < W && y < H {
                g[y * W + x] = p;
            }
        }
        out.push((root(&g), h(&g[T.1 * W + T.0].to_le_bytes())));
    }
    out
}

fn main() {
    let base = run(None);
    let mut runs = vec![("baseline".to_string(), base.clone())];
    for aim in [Aim::East, Aim::North] {
        for p in 1..=3u32 {
            let n = format!("{}_p{}", if aim == Aim::East { "east" } else { "north" }, p);
            runs.push((n, run(Some((aim, p)))));
        }
    }
    let mut ok = [true; 5];
    for (n, r) in runs.iter().skip(1) {
        let g0 = (0..=STEPS).find(|&t| r[t].0 != base[t].0).map_or(-1, |t| t as i64);
        let l0 = (0..=STEPS).find(|&t| r[t].1 != base[t].1).map_or(-1, |t| t as i64);
        let want_l = if n.starts_with("east") { 32 } else { -1 };
        ok[0] &= g0 == 0;
        ok[1] &= l0 == want_l;
        println!("ZLIGHT_RUN|variant={n}|global_root_first_diff_step={g0}|target_local_first_diff_step={l0}|predicted_local={want_l}|json=0");
    }
    let mut pre: Vec<Vec<[u8; 32]>> = runs.iter().map(|(_, r)| r[..32].iter().map(|x| x.1).collect()).collect();
    pre.sort();
    pre.dedup();
    let mut at32: Vec<[u8; 32]> = runs.iter().map(|(_, r)| r[32].1).collect();
    at32.sort();
    at32.dedup();
    let mut r0: Vec<[u8; 32]> = runs.iter().map(|(_, r)| r[0].0).collect();
    r0.sort();
    r0.dedup();
    ok[2] = pre.len() == 1;
    ok[3] = at32.len() == 4;
    ok[4] = r0.len() == 7;
    println!("ZLIGHT_LOCAL|steps=0..31|distinct_target_view_sequences={}|bits_learned_before_arrival={}|json=0", pre.len(), if pre.len() == 1 { 0 } else { -1 });
    println!("ZLIGHT_LOCAL|step=32|distinct_target_views={}|json=0", at32.len());
    println!("ZLIGHT_GLOBAL|step=0|distinct_global_roots={}|baseline_root_step0={}|json=0", r0.len(), hex(&base[0].0));
    let v = |b: bool| if b { "PASS" } else { "FAIL" };
    println!(
        "ZLIGHT_RESULT|P1={}|P2={}|P3={}|P4={}|P5={}|overall={}|json=0",
        v(ok[0]), v(ok[1]), v(ok[2]), v(ok[3]), v(ok[4]),
        v(ok.iter().all(|&b| b))
    );
}
