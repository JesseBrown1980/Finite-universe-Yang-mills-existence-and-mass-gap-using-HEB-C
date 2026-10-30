//! ymwser: exact strong-coupling series of the S3 spatial Wilson loops on the open ROWS x COLS strip.
//! <W(C_A)> = sum_k c_{A,k} r^k for W = chi_std(U_C), C_A the 1 x A rectangle on rows 0..1, columns 0..A,
//! by Rayleigh-Schrodinger perturbation theory in H0 = E (electric), V = M (magnetic), with exact rationals:
//!   E psi_n = -M psi_{n-1} + sum_{k=1..n} E_k psi_{n-k},  E_k = <psi_0|M|psi_{k-1}> / <psi_0|psi_0>,
//!   <psi_0|psi_n> = 0 (n >= 1), psi_0 = constant (the unique E = 0 state).
//! <W> = <psi|W|psi> / <psi|psi> expanded to order ORDER (every <psi_j|W|psi_{k-j}> term and the norm).
//! The singular system is solved as (S + w w^T) x = W b, S = W E symmetric, by exact elimination.
//! METHOD 0 = gauge-orbit basis under global conjugation with Gauss weights;
//! METHOD 1 = full gauge-fixed configuration basis (6^free states, unit weights, no orbit reduction).
//! usage: ymwser ROWS COLS METHOD ORDER        json=0
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use num_bigint::BigInt;
use num_integer::Integer;
use num_traits::{One, Signed, Zero};
use std::collections::{BTreeMap, HashMap};
use torusl::{G, TRANS};

#[derive(Clone, PartialEq, Debug)]
struct R {
    n: BigInt,
    d: BigInt,
}

impl R {
    fn new(n: BigInt, d: BigInt) -> R {
        let g = n.gcd(&d);
        let (mut n, mut d) = if g.is_zero() { (n, d) } else { (n / &g, d / &g) };
        if d.is_negative() {
            n = -n;
            d = -d;
        }
        R { n, d }
    }
    fn int(v: i64) -> R {
        R { n: BigInt::from(v), d: BigInt::one() }
    }
    fn zero() -> R {
        R::int(0)
    }
    fn add(&self, o: &R) -> R {
        R::new(&self.n * &o.d + &o.n * &self.d, &self.d * &o.d)
    }
    fn sub(&self, o: &R) -> R {
        R::new(&self.n * &o.d - &o.n * &self.d, &self.d * &o.d)
    }
    fn mul(&self, o: &R) -> R {
        R::new(&self.n * &o.n, &self.d * &o.d)
    }
    fn div(&self, o: &R) -> R {
        R::new(&self.n * &o.d, &self.d * &o.n)
    }
    fn is_zero(&self) -> bool {
        self.n.is_zero()
    }
    fn show(&self) -> String {
        format!("{}/{}", self.n, self.d)
    }
}

fn chi_std(a: u8) -> i64 {
    match a {
        0 => 2,
        3 | 4 => -1,
        _ => 0,
    }
}

struct Strip {
    edges: Vec<(usize, usize)>,
    hid: Vec<usize>,
    vid: Vec<usize>,
    cols: usize,
    tree: Vec<usize>,
    free: Vec<usize>,
    plaq: Vec<[usize; 4]>,
    sites: usize,
}

fn strip(rows: usize, cols: usize) -> Strip {
    let site = |x: usize, y: usize| y * cols + x;
    let (mut edges, mut hid, mut vid) = (Vec::new(), vec![usize::MAX; rows * cols], vec![usize::MAX; rows * cols]);
    for y in 0..rows {
        for x in 0..cols - 1 {
            hid[site(x, y)] = edges.len();
            edges.push((site(x, y), site(x + 1, y)));
        }
    }
    for y in 0..rows - 1 {
        for x in 0..cols {
            vid[site(x, y)] = edges.len();
            edges.push((site(x, y), site(x, y + 1)));
        }
    }
    let mut tree: Vec<usize> = (0..rows - 1).map(|y| vid[site(0, y)]).collect();
    for y in 0..rows {
        for x in 0..cols - 1 {
            tree.push(hid[site(x, y)]);
        }
    }
    let mut free = Vec::new();
    let mut plaq = Vec::new();
    for y in 0..rows - 1 {
        for x in 1..cols {
            free.push(vid[site(x, y)]);
        }
        for x in 0..cols - 1 {
            plaq.push([hid[site(x, y)], vid[site(x + 1, y)], hid[site(x, y + 1)], vid[site(x, y)]]);
        }
    }
    Strip { edges, hid, vid, cols, tree, free, plaq, sites: rows * cols }
}

struct Sys<'a> {
    g: &'a G,
    s: &'a Strip,
}

impl Sys<'_> {
    fn raw(&self, q: &[u8]) -> Vec<u8> {
        let mut l = vec![0u8; self.s.edges.len()];
        for (i, &e) in self.s.free.iter().enumerate() {
            l[e] = q[i];
        }
        l
    }
    fn fix(&self, l: &[u8]) -> Vec<u8> {
        let mut h = vec![0u8; self.s.sites];
        for &e in &self.s.tree {
            let (t, hd) = self.s.edges[e];
            h[hd] = self.g.m(h[t], l[e]);
        }
        self.s.free.iter().map(|&e| self.g.m(self.g.m(h[self.s.edges[e].0], l[e]), self.g.i(h[self.s.edges[e].1]))).collect()
    }
    fn magnetic(&self, l: &[u8]) -> i64 {
        self.s.plaq.iter().map(|p| 2 - chi_std(self.g.m(self.g.m(self.g.m(l[p[0]], l[p[1]]), self.g.i(l[p[2]])), self.g.i(l[p[3]])))).sum()
    }
    fn wilson(&self, l: &[u8], x0: usize, x1: usize) -> i64 {
        let s = self.s;
        let mut u = 0u8;
        for x in x0..x1 {
            u = self.g.m(u, l[s.hid[x]]);
        }
        u = self.g.m(u, l[s.vid[x1]]);
        for x in (x0..x1).rev() {
            u = self.g.m(u, self.g.i(l[s.hid[s.cols + x]]));
        }
        u = self.g.m(u, self.g.i(l[s.vid[x0]]));
        chi_std(u)
    }
}

fn code(q: &[u8]) -> u64 {
    q.iter().rev().fold(0u64, |a, &v| a * 6 + u64::from(v))
}

/// basis states (representative configurations), weights, electric matrix rows E[i] = {j: E_ij}
type Basis = (Vec<Vec<u8>>, Vec<i64>, Vec<BTreeMap<usize, i64>>);

fn basis(sys: &Sys, orbit: bool) -> Basis {
    let g = sys.g;
    let nf = sys.s.free.len();
    let total = 6u64.pow(nf as u32);
    let decode = |c: u64| -> Vec<u8> { (0..nf).map(|i| ((c / 6u64.pow(i as u32)) % 6) as u8).collect() };
    let conj = |q: &[u8]| -> Vec<u64> { (0..6u8).map(|c| code(&q.iter().map(|&x| g.m(g.m(c, x), g.i(c))).collect::<Vec<u8>>())).collect() };
    let mut reps = Vec::new();
    let mut w = Vec::new();
    for c in 0..total {
        let q = decode(c);
        if orbit {
            let cs = conj(&q);
            if cs.iter().min() == Some(&c) {
                let mut s = cs.clone();
                s.sort_unstable();
                s.dedup();
                w.push(s.len() as i64);
                reps.push(q);
            }
        } else {
            w.push(1);
            reps.push(q);
        }
    }
    let index: HashMap<u64, usize> = reps.iter().enumerate().map(|(i, q)| (code(q), i)).collect();
    let key = |q: &[u8]| -> u64 {
        if orbit {
            conj(q).into_iter().min().unwrap_or(0)
        } else {
            code(q)
        }
    };
    let links = sys.s.edges.len();
    let e: Vec<BTreeMap<usize, i64>> = reps
        .iter()
        .enumerate()
        .map(|(i, q)| {
            let raw = sys.raw(q);
            let mut row = BTreeMap::new();
            row.insert(i, 3 * links as i64);
            for l in 0..links {
                for &t in &TRANS {
                    let mut u = raw.clone();
                    u[l] = g.m(t, u[l]);
                    *row.entry(index[&key(&sys.fix(&u))]).or_insert(0) -= 1;
                }
            }
            row.retain(|_, v| *v != 0);
            row
        })
        .collect();
    (reps, w, e)
}

/// exact inverse of an integer matrix by Gauss-Jordan over the rationals
fn inverse(a: &[Vec<i64>]) -> Option<Vec<Vec<R>>> {
    let n = a.len();
    let mut m: Vec<Vec<R>> = a.iter().map(|r| r.iter().map(|&v| R::int(v)).collect()).collect();
    let mut inv: Vec<Vec<R>> = (0..n).map(|i| (0..n).map(|j| R::int(i64::from(i == j))).collect()).collect();
    for c in 0..n {
        let p = (c..n).find(|&r| !m[r][c].is_zero())?;
        m.swap(c, p);
        inv.swap(c, p);
        let pv = m[c][c].clone();
        for j in 0..n {
            m[c][j] = m[c][j].div(&pv);
            inv[c][j] = inv[c][j].div(&pv);
        }
        for r in 0..n {
            if r != c && !m[r][c].is_zero() {
                let f = m[r][c].clone();
                for j in 0..n {
                    let (a1, b1) = (m[c][j].mul(&f), inv[c][j].mul(&f));
                    m[r][j] = m[r][j].sub(&a1);
                    inv[r][j] = inv[r][j].sub(&b1);
                }
            }
        }
    }
    Some(inv)
}

fn main() {
    let args: Vec<usize> = std::env::args().skip(1).filter_map(|a| a.parse().ok()).collect();
    if args.len() != 4 || !(2..=3).contains(&args[0]) || !(2..=4).contains(&args[1]) || args[2] > 1 || !(1..=6).contains(&args[3]) {
        eprintln!("usage: ymwser ROWS COLS METHOD ORDER");
        std::process::exit(1);
    }
    let (rows, cols, orbit, order) = (args[0], args[1], args[2] == 0, args[3]);
    let g = G::new();
    let s = strip(rows, cols);
    let sys = Sys { g: &g, s: &s };
    let (reps, w, e) = basis(&sys, orbit);
    let n = reps.len();
    // W-self-adjointness of E
    let mut adjoint = true;
    for i in 0..n {
        for (&j, &v) in &e[i] {
            adjoint &= w[i] * v == w[j] * e[j].get(&i).copied().unwrap_or(0);
        }
    }
    // A = W E + w w^T
    let mut a = vec![vec![0i64; n]; n];
    for i in 0..n {
        for (&j, &v) in &e[i] {
            a[i][j] += w[i] * v;
        }
        for j in 0..n {
            a[i][j] += w[i] * w[j];
        }
    }
    let Some(ainv) = inverse(&a) else {
        println!("WSERIES|result=FAIL|reason=singular|json=0");
        std::process::exit(2);
    };
    let mag: Vec<R> = reps.iter().map(|q| R::int(sys.magnetic(&sys.raw(q)))).collect();
    let dot = |x: &[R], y: &[R]| -> R { (0..n).fold(R::zero(), |acc, i| acc.add(&x[i].mul(&y[i]).mul(&R::int(w[i])))) };
    let n0 = R::int(w.iter().sum());
    let mut psi: Vec<Vec<R>> = vec![vec![R::int(1); n]];
    let mut ek: Vec<R> = vec![R::zero()];
    for k in 1..=order {
        // E_k = <psi0|M|psi_{k-1}> / <psi0|psi0>
        let mp: Vec<R> = (0..n).map(|i| mag[i].mul(&psi[k - 1][i])).collect();
        ek.push(dot(&psi[0], &mp).div(&n0));
        // b = -M psi_{k-1} + sum_j E_j psi_{k-j}
        let mut b: Vec<R> = mp.iter().map(|v| R::zero().sub(v)).collect();
        for j in 1..=k {
            for (bi, pv) in b.iter_mut().zip(psi[k - j].iter()) {
                *bi = bi.add(&ek[j].mul(pv));
            }
        }
        // x = A^{-1} (W b)
        let wb: Vec<R> = (0..n).map(|i| b[i].mul(&R::int(w[i]))).collect();
        let x: Vec<R> = (0..n).map(|i| (0..n).fold(R::zero(), |acc, j| acc.add(&ainv[i][j].mul(&wb[j])))).collect();
        psi.push(x);
    }
    let ortho = (1..=order).all(|k| dot(&psi[0], &psi[k]).is_zero());
    println!(
        "WSERIES_BASIS|rows={rows}|cols={cols}|method={}|states={n}|e_w_self_adjoint={}|orthogonality={}|order={order}|json=0",
        if orbit { "A_orbit" } else { "B_config" },
        if adjoint { "PASS" } else { "FAIL" },
        if ortho { "PASS" } else { "FAIL" }
    );
    let energies: Vec<String> = ek.iter().skip(1).map(R::show).collect();
    println!("WSERIES_ENERGY|E_k={}|json=0", energies.join(","));
    // norm series D_k = sum_j <psi_j|psi_{k-j}>
    let dser: Vec<R> = (0..=order).map(|k| (0..=k).fold(R::zero(), |acc, j| acc.add(&dot(&psi[j], &psi[k - j])))).collect();
    for x1 in 1..cols {
        let wv: Vec<R> = reps.iter().map(|q| R::int(sys.wilson(&sys.raw(q), 0, x1))).collect();
        let nser: Vec<R> = (0..=order)
            .map(|k| {
                (0..=k).fold(R::zero(), |acc, j| {
                    let wy: Vec<R> = (0..n).map(|i| wv[i].mul(&psi[k - j][i])).collect();
                    acc.add(&dot(&psi[j], &wy))
                })
            })
            .collect();
        // c = N / D as power series
        let mut c: Vec<R> = Vec::new();
        for k in 0..=order {
            let mut v = nser[k].clone();
            for j in 1..=k {
                v = v.sub(&dser[j].mul(&c[k - j]));
            }
            c.push(v.div(&dser[0]));
        }
        let cs: Vec<String> = c.iter().map(R::show).collect();
        println!("WSERIES|loop=1x{x1}|method={}|c_k={}|json=0", if orbit { "A_orbit" } else { "B_config" }, cs.join(","));
    }
}
