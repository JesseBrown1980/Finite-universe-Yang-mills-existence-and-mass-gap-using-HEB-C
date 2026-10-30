//! zteleport: the iterated-teleportation hierarchy T_N for the zbell models (see PREREG.md).
//! Rust 1.81, std only, integer and exact-rational arithmetic, json=0.

/// CHSH numerator for one outcome: max over the four odd-minus arrangements of |sum +-c(s,t)|.
fn chsh_num(c: &[[i64; 2]; 2]) -> i64 {
    let v = [c[0][0], c[0][1], c[1][0], c[1][1]];
    (0..4)
        .map(|k| {
            let s: i64 = v.iter().enumerate().map(|(i, &x)| if i == k { -x } else { x }).sum();
            s.abs()
        })
        .max()
        .unwrap_or(0)
}

/// Per-outcome tallies: count n[s][t] and correlation sum c[s][t] (sum of (-1)^(a XOR b)).
#[derive(Clone, Default)]
struct Tally {
    n: [[i64; 2]; 2],
    c: [[i64; 2]; 2],
}

/// From tallies over all outcomes: (sum of CHSH numerators, total count, counts independent of (s,t)).
fn hierarchy_s(t: &[Tally]) -> (i64, i64, bool) {
    let mut num = 0;
    let mut total = 0;
    let mut equal = true;
    for x in t {
        if x.n[0][0] == 0 && x.n[0][1] == 0 && x.n[1][0] == 0 && x.n[1][1] == 0 {
            continue;
        }
        equal &= x.n[0][0] == x.n[0][1] && x.n[0][0] == x.n[1][0] && x.n[0][0] == x.n[1][1];
        num += chsh_num(&x.c);
        total += x.n[0][0];
    }
    (num, total, equal)
}

fn sgn(bit: u64) -> i64 {
    if bit == 0 {
        1
    } else {
        -1
    }
}

// ---------- Q: quantum reference with integer statevectors ----------
fn bell(mu: usize, u: usize, v: usize) -> i64 {
    match (mu, u, v) {
        (0, 0, 0) | (0, 1, 1) => 1,
        (1, 0, 0) => 1,
        (1, 1, 1) => -1,
        (2, 0, 1) | (2, 1, 0) => 1,
        (3, 0, 1) => 1,
        (3, 1, 0) => -1,
        _ => 0,
    }
}

fn quantum(n: usize) -> (bool, i64) {
    let q = 2 * (n + 1);
    let psi: Vec<usize> = (0..1usize << q).filter(|&i| (0..=n).all(|k| (i >> (2 * k)) & 1 == (i >> (2 * k + 1)) & 1)).collect();
    let psi_norm = psi.len() as i64; // all amplitudes 1
    let mut ok = true;
    let mut n_mu = 0i64;
    for m in 0..(1usize << (2 * n)) {
        let mut phi = [[0i64; 2]; 2];
        for &i in &psi {
            let mut w = 1i64;
            for k in 1..=n {
                let mu = (m >> (2 * (k - 1))) & 3;
                w *= bell(mu, (i >> (2 * k - 1)) & 1, (i >> (2 * k)) & 1);
                if w == 0 {
                    break;
                }
            }
            phi[i & 1][(i >> (q - 1)) & 1] += w;
        }
        let f = [phi[0][0], phi[0][1], phi[1][0], phi[1][1]]; // index 2a + b
        let den: i64 = f.iter().map(|x| x * x).sum();
        // p(mu) = den / (psi_norm * 2^n) must equal 4^-n
        let p_ok = den * (1i64 << (2 * n)) == psi_norm * (1i64 << n);
        // single-qubit matrices on basis index; sx, sz real; J = [[0,-1],[1,0]] (sy = iJ)
        let sx = |a: usize, b: usize| i64::from(a != b);
        let sz = |a: usize, b: usize| if a == b { sgn(a as u64) } else { 0 };
        let jm = |a: usize, b: usize| match (a, b) {
            (0, 1) => -1,
            (1, 0) => 1,
            _ => 0,
        };
        let expv = |m1: &dyn Fn(usize, usize) -> i64, m2: &dyn Fn(usize, usize) -> i64| {
            let mut e = 0i64;
            for a in 0..2 {
                for b in 0..2 {
                    for c in 0..2 {
                        for d in 0..2 {
                            e += f[2 * a + b] * m1(a, c) * m2(b, d) * f[2 * c + d];
                        }
                    }
                }
            }
            e
        };
        let id = |a: usize, b: usize| i64::from(a == b);
        let txx = expv(&sx, &sx);
        let tzz = expv(&sz, &sz);
        let tyy = -expv(&jm, &jm);
        let off = [expv(&sx, &sz), expv(&sz, &sx)];
        let marg = [expv(&sx, &id), expv(&sz, &id), expv(&id, &sx), expv(&id, &sz)];
        let diag_unit = [txx, tyy, tzz].iter().all(|&t| t == den || t == -den);
        // D = T_mu * T_0^-1 with T_0 = diag(1,-1,1); a Pauli frame has det(D) = +1
        let d = [txx / den.max(1), -tyy / den.max(1), tzz / den.max(1)];
        let frame = diag_unit && d[0] * d[1] * d[2] == 1;
        let s2_is_8 = diag_unit; // S^2 = 4(t1^2 + t2^2) = 8 when all |t_i| = 1
        let clean = off.iter().all(|&x| x == 0) && marg.iter().all(|&x| x == 0);
        let good = p_ok && frame && s2_is_8 && clean;
        ok &= good;
        n_mu += 1;
        if n <= 1 || !good {
            println!(
                "ZTQ|N={n}|mu={m}|norm={den}|p_ok={}|T=diag({},{},{})/{den}|pauli_frame={}|S2_eq_8={}|marginals_zero={}|json=0",
                i64::from(p_ok), txx, tyy, tzz, i64::from(frame), i64::from(s2_is_8), i64::from(clean)
            );
        }
    }
    (ok, n_mu)
}

// ---------- PRW: PR boxes composed by deterministic local wirings ----------
#[derive(Clone, Copy)]
struct Wiring {
    x0: u64,
    f: [u64; 2],
    g: [usize; 4],
}

fn wirings() -> Vec<Wiring> {
    let mut w = Vec::with_capacity(2048);
    for x0 in 0..2u64 {
        for fi in 0..4u64 {
            for gi in 0..256usize {
                w.push(Wiring { x0, f: [fi & 1, (fi >> 1) & 1], g: [gi & 3, (gi >> 2) & 3, (gi >> 4) & 3, (gi >> 6) & 3] });
            }
        }
    }
    w
}

/// N = 1: box1 (A: s -> a_L = r1; B: x0 -> b1 = r1 ^ s*x0), box2 (A: f(b1) -> a2 = r2; B: t -> b_R = r2 ^ f(b1)*t).
fn prw1(w: &Wiring) -> (i64, i64, bool) {
    let mut t = vec![Tally::default(); 4];
    for s in 0..2u64 {
        for tt in 0..2u64 {
            for r1 in 0..2u64 {
                for r2 in 0..2u64 {
                    let b1 = r1 ^ (s & w.x0);
                    let in2 = w.f[b1 as usize];
                    let br = r2 ^ (in2 & tt);
                    let mu = w.g[(b1 * 2 + r2) as usize];
                    t[mu].n[s as usize][tt as usize] += 1;
                    t[mu].c[s as usize][tt as usize] += sgn(r1 ^ br);
                }
            }
        }
    }
    hierarchy_s(&t)
}

/// N = 2: three boxes, two stations.
fn prw2(w1: &Wiring, w2: &Wiring) -> (i64, i64, bool) {
    let mut t = vec![Tally::default(); 16];
    for s in 0..2u64 {
        for tt in 0..2u64 {
            for r in 0..8u64 {
                let (r1, r2, r3) = (r & 1, (r >> 1) & 1, (r >> 2) & 1);
                let b1 = r1 ^ (s & w1.x0);
                let in2a = w1.f[b1 as usize];
                let b2 = r2 ^ (in2a & w2.x0);
                let in3a = w2.f[b2 as usize];
                let br = r3 ^ (in3a & tt);
                let mu = w1.g[(b1 * 2 + r2) as usize] * 4 + w2.g[(b2 * 2 + r3) as usize];
                t[mu].n[s as usize][tt as usize] += 1;
                t[mu].c[s as usize][tt as usize] += sgn(r1 ^ br);
            }
        }
    }
    hierarchy_s(&t)
}

fn pr0() -> (i64, i64, bool) {
    let mut t = vec![Tally::default(); 1];
    for s in 0..2u64 {
        for tt in 0..2u64 {
            for r in 0..2u64 {
                t[0].n[s as usize][tt as usize] += 1;
                t[0].c[s as usize][tt as usize] += sgn(r ^ (r ^ (s & tt)));
            }
        }
    }
    hierarchy_s(&t)
}

// ---------- ZPR, ZT, LH ----------
fn zpr(n: usize) -> (i64, i64, bool, bool) {
    let mut t = vec![Tally::default(); 1 << (2 * n)];
    let mut ones = [[0i64; 2]; 2];
    for (m, tm) in t.iter_mut().enumerate() {
        for s in 0..2u64 {
            for tt in 0..2u64 {
                for a in 0..2u64 {
                    let b = a ^ (s & tt) ^ ((m as u64).count_ones() as u64 & 1);
                    tm.n[s as usize][tt as usize] += 1;
                    tm.c[s as usize][tt as usize] += sgn(a ^ b);
                    ones[s as usize][tt as usize] += a as i64;
                }
            }
        }
    }
    let ns = ones[0][0] == ones[0][1] && ones[1][0] == ones[1][1];
    let (num, tot, eq) = hierarchy_s(&t);
    (num, tot, eq, ns)
}

fn zt(n: usize) -> (i64, i64, bool) {
    let mut t = vec![Tally::default(); 1 << (2 * n)];
    for (m, tm) in t.iter_mut().enumerate() {
        let flip_all = (m as u64).count_ones() as u64 & 1;
        for s in 0..2u64 {
            for tt in 0..2u64 {
                for l in 0..486u64 {
                    let a = l & 1;
                    let flip = if s & tt == 1 { l >= 72 } else { l < 72 };
                    let b = a ^ u64::from(flip) ^ flip_all;
                    tm.n[s as usize][tt as usize] += 1;
                    tm.c[s as usize][tt as usize] += sgn(a ^ b);
                }
            }
        }
    }
    hierarchy_s(&t)
}

fn mix(mut z: u64) -> u64 {
    z = z.wrapping_add(0x9E37_79B9_7F4A_7C15);
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

fn lh(n: usize) -> (i64, i64, bool, i64) {
    let mut t = vec![Tally::default(); 1 << (2 * n)];
    for l in 0..486u64 {
        let mut m = 0usize;
        for k in 0..n {
            m |= ((mix(1000 + 7 * k as u64 + (l << 8)) & 3) as usize) << (2 * k);
        }
        for s in 0..2u64 {
            for tt in 0..2u64 {
                let a = mix(1 + 2 * s + (l << 8)) & 1;
                let b = mix(5 + 2 * tt + (l << 8)) & 1;
                t[m].n[s as usize][tt as usize] += 1;
                t[m].c[s as usize][tt as usize] += sgn(a ^ b);
            }
        }
    }
    // worst per-outcome S_mu * n_mu against 2 * n_mu
    let worst = t.iter().filter(|x| x.n[0][0] > 0).map(|x| chsh_num(&x.c) - 2 * x.n[0][0]).max().unwrap_or(-1);
    let (num, tot, eq) = hierarchy_s(&t);
    (num, tot, eq, worst)
}

fn main() {
    let pf = |b: bool| if b { "PASS" } else { "FAIL" };
    // H1
    let mut h1 = true;
    for n in 0..=4 {
        let (ok, k) = quantum(n);
        println!("ZTQSUM|N={n}|outcomes={k}|all_conditions={}|S_N_squared=8|json=0", i64::from(ok));
        h1 &= ok;
    }
    // H2
    let w = wirings();
    let (n0, t0, e0) = pr0();
    let mut best1 = (0i64, 1i64, true, 0usize);
    for (i, wi) in w.iter().enumerate() {
        let (num, tot, eq) = prw1(wi);
        if num * best1.1 > best1.0 * tot {
            best1 = (num, tot, eq, i);
        }
    }
    let mut best2 = (0i64, 1i64, true, 0usize, 0usize);
    let mut all_eq2 = true;
    for (i, a) in w.iter().enumerate() {
        for (j, b) in w.iter().enumerate() {
            let (num, tot, eq) = prw2(a, b);
            all_eq2 &= eq;
            if num * best2.1 > best2.0 * tot {
                best2 = (num, tot, eq, i, j);
            }
        }
    }
    println!("ZTPRW|N=0|S_num={n0}|S_den={t0}|counts_equal={}|json=0", i64::from(e0));
    println!("ZTPRW|N=1|wirings=2048|best_S_num={}|best_S_den={}|best_wiring={}|json=0", best1.0, best1.1, best1.3);
    println!(
        "ZTPRW|N=2|wiring_pairs=4194304|best_S_num={}|best_S_den={}|best_pair={},{}|outcome_probs_setting_independent={}|json=0",
        best2.0, best2.1, best2.3, best2.4, i64::from(all_eq2)
    );
    let h2 = n0 == 4 * t0 && best1.0 == 2 * best1.1 && best2.0 == 2 * best2.1;
    // H3, H4, H5
    let (mut h3, mut h4, mut h5) = (true, true, true);
    let (mut zpr_v, mut zt_v, mut lh_v) = (Vec::new(), Vec::new(), Vec::new());
    for n in 0..=4 {
        let (num, tot, eq, ns) = zpr(n);
        let p_ok = tot == (1i64 << (2 * n)) * 2;
        println!("ZTZPR|N={n}|S_num={num}|S_den={tot}|p_uniform={}|no_signalling={}|json=0", i64::from(p_ok && eq), i64::from(ns));
        h3 &= num == 4 * tot && p_ok && eq && ns;
        zpr_v.push((n, num, tot));
        let (num, tot, _) = zt(n);
        println!("ZTZT|N={n}|S_num={num}|S_den={tot}|S_times_486={}|json=0", num * 486 / tot);
        h4 &= num * 486 == 1368 * tot;
        zt_v.push((n, num, tot));
        let (num, tot, _, worst) = lh(n);
        println!("ZTLH|N={n}|S_num={num}|S_den={tot}|worst_Smu_minus_2_times_n={worst}|json=0");
        h5 &= worst <= 0 && num <= 2 * tot;
        lh_v.push((n, num, tot));
    }
    // H6, computed: first N whose S differs from 2*sqrt(2) (S^2 != 8, exact), and stability of S across N
    let h6 = |name: &str, v: &[(usize, i64, i64)]| {
        let first = v.iter().find(|&&(_, a, b)| a * a != 8 * b * b).map_or(-1, |&(n, _, _)| n as i64);
        let stable = v.windows(2).all(|p| p[0].1 * p[1].2 == p[1].1 * p[0].2);
        let changes: Vec<String> = v.windows(2).filter(|p| p[0].1 * p[1].2 != p[1].1 * p[0].2).map(|p| p[1].0.to_string()).collect();
        println!(
            "ZTH6|model={name}|first_N_with_S2_ne_8={first}|S_same_at_every_N={}|N_where_S_changes={}|json=0",
            i64::from(stable),
            if changes.is_empty() { "none".to_string() } else { changes.join(",") }
        );
    };
    h6("ZPR", &zpr_v);
    h6("ZT", &zt_v);
    h6("LH", &lh_v);
    h6("PRW", &[(0, n0, t0), (1, best1.0, best1.1), (2, best2.0, best2.1)]);
    println!("ZTRESULT|H1={}|H2={}|H3={}|H4={}|H5={}|json=0", pf(h1), pf(h2), pf(h3), pf(h4), pf(h5));
}
