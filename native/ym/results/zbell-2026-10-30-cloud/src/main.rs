//! zbell: Bell/CHSH test of the z layer. Integer only, json=0. See PREREG.md and ADDENDUM.md.
use sha2::{Digest, Sha256};

const N: i64 = 486;

/// Outcome of one side for (a, b, lambda); a model is a pair of such functions.
type Side = fn(usize, usize, i64) -> i64;

fn par(l: i64) -> i64 {
    if l % 2 == 0 {
        1
    } else {
        -1
    }
}

fn hbit(tag: &str, s: usize, l: i64) -> i64 {
    let d = Sha256::digest(format!("{tag}|{s}|{l}").as_bytes());
    if d[0] & 1 == 0 {
        1
    } else {
        -1
    }
}

fn lh_a(a: usize, _b: usize, l: i64) -> i64 {
    hbit("A", a, l)
}
fn lh_b(_a: usize, b: usize, l: i64) -> i64 {
    hbit("B", b, l)
}
fn zpr_a(_a: usize, _b: usize, l: i64) -> i64 {
    par(l)
}
fn zpr_b(a: usize, b: usize, l: i64) -> i64 {
    if a * b == 1 {
        -par(l)
    } else {
        par(l)
    }
}
fn zt_b(a: usize, b: usize, l: i64) -> i64 {
    if a * b == 1 || l < 72 {
        -par(l)
    } else {
        par(l)
    }
}
fn zt2_b(a: usize, b: usize, l: i64) -> i64 {
    let flip = if a * b == 1 { l >= 72 } else { l < 72 };
    if flip {
        -par(l)
    } else {
        par(l)
    }
}
fn leak_a(_a: usize, b: usize, l: i64) -> i64 {
    if b == 0 {
        par(l)
    } else {
        1
    }
}

/// (S*n, A=+1 counts [a][b], B=+1 counts [a][b])
fn chsh(fa: Side, fb: Side) -> (i64, [[i64; 2]; 2], [[i64; 2]; 2]) {
    let (mut e, mut ca, mut cb) = ([[0i64; 2]; 2], [[0i64; 2]; 2], [[0i64; 2]; 2]);
    for a in 0..2 {
        for b in 0..2 {
            for l in 0..N {
                let (x, y) = (fa(a, b, l), fb(a, b, l));
                e[a][b] += x * y;
                ca[a][b] += i64::from(x == 1);
                cb[a][b] += i64::from(y == 1);
            }
        }
    }
    (e[0][0] + e[0][1] + e[1][0] - e[1][1], ca, cb)
}

/// No-signalling: A's count depends only on a, B's only on b.
fn nosig(ca: &[[i64; 2]; 2], cb: &[[i64; 2]; 2]) -> bool {
    ca[0][0] == ca[0][1] && ca[1][0] == ca[1][1] && cb[0][0] == cb[1][0] && cb[0][1] == cb[1][1]
}

fn main() {
    let v = |b: bool| if b { "PASS" } else { "FAIL" };
    let quantum = |s: i64| s * s <= 8 * N * N;
    // P1: all 16 deterministic local strategies
    let mut p1 = true;
    let mut seen = Vec::new();
    for m in 0..16u32 {
        let s = |i: u32| if (m >> i) & 1 == 0 { 1i64 } else { -1 };
        let (a0, a1, b0, b1) = (s(0), s(1), s(2), s(3));
        let sv = a0 * b0 + a0 * b1 + a1 * b0 - a1 * b1;
        p1 &= sv.abs() == 2;
        seen.push(sv);
    }
    println!("ZBELL_LDET|strategies=16|S_values={:?}|max_abs_S=2|json=0", seen);
    let mut all = p1;
    let row = |name: &str, fa: Side, fb: Side| {
        let (s, ca, cb) = chsh(fa, fb);
        let ns = nosig(&ca, &cb);
        println!(
            "ZBELL_MODEL|model={name}|S_times_n={s}|local_bound=972|quantum_ok={}|no_signalling={}|A_plus={:?}|B_plus={:?}|json=0",
            i64::from(quantum(s)), i64::from(ns), ca, cb
        );
        (s, ns, ca)
    };
    let (s2, n2, _) = row("L-hash", lh_a, lh_b);
    let (s3, n3, ca3) = row("Z-PR", zpr_a, zpr_b);
    let (s4, n4, _) = row("Z-T", zpr_a, zt_b);
    let (s4c, n4c, _) = row("Z-T2", zpr_a, zt2_b);
    let (_, n5, ca5) = row("Leak", leak_a, zpr_b);
    let p2 = s2.abs() <= 2 * N && n2;
    let p3 = s3 == 4 * N && n3 && ca3.iter().flatten().all(|&c| c == 243);
    let p4 = s4 == 1368 && n4 && quantum(s4);
    let p4b = s4 == 1512 && !quantum(s4) && n4;
    let p4c = s4c == 1368 && s4c > 2 * N && quantum(s4c) && n4c;
    let p5 = !n5 && ca5[0][0] == 243 && ca5[0][1] == 486;
    println!(
        "ZBELL_RESULT|P1={}|P2={}|P3={}|P4={}|P5={}|json=0",
        v(p1), v(p2), v(p3), v(p4), v(p5)
    );
    println!("ZBELL_ADDENDUM|P4b={}|P4c={}|json=0", v(p4b), v(p4c));
    all &= p2 && p3 && p4 && p5;
    println!("ZBELL_OVERALL_REGISTERED|{}|json=0", v(all));
}
