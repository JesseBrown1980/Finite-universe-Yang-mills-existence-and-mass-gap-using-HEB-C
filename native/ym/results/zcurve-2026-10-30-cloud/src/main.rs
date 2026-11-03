//! zcurve: test B, straight r versus curved j. Integer only, json=0. See PREREG.md.

fn pow3(k: usize) -> usize {
    3usize.pow(k as u32)
}

fn digit(x: usize, k: usize) -> usize {
    (x / pow3(k)) % 3
}

fn rot(x: usize, k: usize, d: usize) -> usize {
    x - digit(x, k) * pow3(k) + ((digit(x, k) + d) % 3) * pow3(k)
}

/// Level-k operator a*I + b*R_k + c*R_k^2 as a dense M x M integer matrix (row = output).
fn level_op(m: usize, k: usize, w: [i64; 3]) -> Vec<i64> {
    let mut a = vec![0i64; m * m];
    for x in 0..m {
        for (d, &wd) in w.iter().enumerate() {
            a[rot(x, k, d) * m + x] += wd;
        }
    }
    a
}

fn mul(a: &[i64], b: &[i64], m: usize) -> Vec<i64> {
    let mut c = vec![0i64; m * m];
    for i in 0..m {
        for l in 0..m {
            let e = a[i * m + l];
            if e != 0 {
                for j in 0..m {
                    c[i * m + j] += e * b[l * m + j];
                }
            }
        }
    }
    c
}

fn symmetric(a: &[i64], m: usize) -> bool {
    (0..m).all(|i| (0..m).all(|j| a[i * m + j] == a[j * m + i]))
}

fn rank_mod3(a: &[i64], m: usize) -> usize {
    let mut g: Vec<i64> = a.iter().map(|&v| v.rem_euclid(3)).collect();
    let mut r = 0;
    for c in 0..m {
        let Some(p) = (r..m).find(|&i| g[i * m + c] != 0) else { continue };
        for j in 0..m {
            g.swap(r * m + j, p * m + j);
        }
        let inv = g[r * m + c]; // 1 or 2, each its own inverse mod 3
        for j in 0..m {
            g[r * m + j] = (g[r * m + j] * inv) % 3;
        }
        for i in 0..m {
            let f = g[i * m + c];
            if i != r && f != 0 {
                for j in 0..m {
                    g[i * m + j] = (g[i * m + j] - f * g[r * m + j]).rem_euclid(3);
                }
            }
        }
        r += 1;
    }
    r
}

fn det3(a: &[i64]) -> i64 {
    a[0] * (a[4] * a[8] - a[5] * a[7]) - a[1] * (a[3] * a[8] - a[5] * a[6]) + a[2] * (a[3] * a[7] - a[4] * a[6])
}

/// Reach times from a under the cascade of level operators (support of nonzero entries).
fn reach(ops: &[Vec<i64>], m: usize, a: usize) -> Vec<i64> {
    let mut t = vec![-1i64; m];
    let mut v = vec![false; m];
    v[a] = true;
    t[a] = 0;
    for (s, op) in ops.iter().enumerate() {
        let mut w = vec![false; m];
        for (x, &on) in v.iter().enumerate() {
            if on {
                for (y, wy) in w.iter_mut().enumerate() {
                    if op[y * m + x] != 0 {
                        *wy = true;
                    }
                }
            }
        }
        v = w;
        for (x, &on) in v.iter().enumerate() {
            if on && t[x] < 0 {
                t[x] = s as i64 + 1;
            }
        }
    }
    t
}

fn distinct_columns(a: &[i64], m: usize) -> usize {
    let mut cols: Vec<Vec<i64>> = (0..m).map(|j| (0..m).map(|i| a[i * m + j]).collect()).collect();
    cols.sort();
    cols.dedup();
    cols.len()
}

fn main() {
    let v = |b: bool| if b { "PASS" } else { "FAIL" };
    let (rw, jsym, jcur) = ([0, 1, 1], [1, 1, 1], [1, 1, -1]);
    let (j1, c1) = (level_op(3, 0, jsym), level_op(3, 0, jcur));
    let (d_sym, d_cur) = (det3(&j1), det3(&c1));
    let single = d_sym == 0 && d_cur == 4 && d_cur.rem_euclid(3) == 1;
    println!("ZCURVE_SINGLE|det_J={d_sym}|det_j={d_cur}|det_j_mod3={}|result={}|json=0", d_cur.rem_euclid(3), v(single));
    let mut all = single;
    for n in [3usize, 4, 5] {
        let m = pow3(n);
        let mut p1 = true;
        let (mut big_j, mut small_j) = (Vec::new(), Vec::new());
        for k in 0..n {
            let (r, jj, cj) = (level_op(m, k, rw), level_op(m, k, jsym), level_op(m, k, jcur));
            p1 &= symmetric(&r, m) && symmetric(&jj, m) && !symmetric(&cj, m);
            big_j.push(jj);
            small_j.push(cj);
        }
        let mut p2 = true;
        for a in 0..m {
            p2 &= reach(&big_j, m, a) == reach(&small_j, m, a);
        }
        let prod = |ops: &[Vec<i64>]| ops.iter().skip(1).fold(ops[0].clone(), |acc, o| mul(&acc, o, m));
        let (jall_sym, jall_cur) = (prod(&big_j), prod(&small_j));
        let neg = jall_cur.iter().filter(|&&e| e == -1).count();
        let want_neg = (9usize.pow(n as u32) - pow3(n)) / 2;
        let p3 = jall_cur.iter().all(|&e| e == 1 || e == -1) && jall_cur.iter().any(|&e| e != 1) && neg == want_neg;
        let (rk_sym, rk_cur) = (rank_mod3(&jall_sym, m), rank_mod3(&jall_cur, m));
        let p4 = rk_sym == 1 && rk_cur == m;
        let (dc_sym, dc_cur) = (distinct_columns(&jall_sym, m), distinct_columns(&jall_cur, m));
        let p5 = dc_sym == 1 && dc_cur == m;
        println!("ZCURVE|N={n}|M={m}|neg_entries={neg}|predicted_neg={want_neg}|rank3_Jall={rk_sym}|rank3_jall={rk_cur}|distinct_out_Jall={dc_sym}|distinct_out_jall={dc_cur}|json=0");
        println!("ZCURVE_RESULT|N={n}|P1={}|P2={}|P3={}|P4={}|P5={}|json=0", v(p1), v(p2), v(p3), v(p4), v(p5));
        all &= p1 && p2 && p3 && p4 && p5;
    }
    println!("ZCURVE_OVERALL|{}|json=0", v(all));
}
