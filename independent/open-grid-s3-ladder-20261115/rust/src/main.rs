//! S3 Kogut-Susskind rule of this repository on an open a x b grid of plaquettes, in the gauge-fixed
//! space (one group element per independent loop, reduced by the global conjugation).
//!
//! The two lowest levels are located by fixed-point subspace iteration (an estimate only) and then
//! certified by counts from an approximate fixed-point factorisation of W*(H - x) whose residual is bounded
//! rigorously with outward-rounded integer intervals. Integers only; no floating point.
//!
//! usage: open_grid A B RNUM [THREADS] [RDEN] [sparse [SWEEPS] | cheb [ROUNDS [DEGREE]]]
//! With RDEN given the matrix is RDEN*(electric) + RNUM*(magnetic), that is RDEN times the model at
//! r = RNUM/RDEN; the reported levels are those of the scaled matrix.

use std::collections::{HashMap, VecDeque};
use std::env;
use std::thread;

const FP: u32 = 36; // interval fixed point: value = mantissa / 2^36
const UNITS: i128 = 1_000_000_000; // reported energies in units of 1e-9
const PERMS: [[usize; 3]; 6] = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]];

struct Group {
    mul: [[usize; 6]; 6],
    inv: [usize; 6],
    trans: Vec<usize>,
    chi: [i64; 6],
}

impl Group {
    fn new() -> Self {
        let mut mul = [[0usize; 6]; 6];
        for a in 0..6 {
            for (b, pb) in PERMS.iter().enumerate() {
                let c = [PERMS[a][pb[0]], PERMS[a][pb[1]], PERMS[a][pb[2]]];
                mul[a][b] = PERMS.iter().position(|p| *p == c).unwrap_or(0);
            }
        }
        let mut inv = [0usize; 6];
        for a in 0..6 {
            inv[a] = (0..6).find(|&b| mul[a][b] == 0).unwrap_or(0);
        }
        let trans = (1..6).filter(|&i| mul[i][i] == 0).collect();
        let mut chi = [0i64; 6];
        for a in 0..6 {
            chi[a] = (0..3).filter(|&j| PERMS[a][j] == j).count() as i64 - 1;
        }
        Group { mul, inv, trans, chi }
    }
    fn conj(&self, g: usize, a: usize) -> usize {
        self.mul[self.mul[g][a]][self.inv[g]]
    }
}

struct Grid {
    nv: usize,
    links: Vec<(usize, usize)>,
    plaq: Vec<[usize; 4]>,
    tree: Vec<(usize, usize, usize, bool)>,
    kept: Vec<usize>,
}

impl Grid {
    fn new(a: usize, b: usize) -> Self {
        let vid = |x: usize, y: usize| x * (b + 1) + y;
        let nv = (a + 1) * (b + 1);
        let mut links = Vec::new();
        let mut hx = HashMap::new();
        let mut vy = HashMap::new();
        for x in 0..a {
            for y in 0..=b {
                hx.insert((x, y), links.len());
                links.push((vid(x, y), vid(x + 1, y)));
            }
        }
        for x in 0..=a {
            for y in 0..b {
                vy.insert((x, y), links.len());
                links.push((vid(x, y), vid(x, y + 1)));
            }
        }
        let mut plaq = Vec::new();
        for x in 0..a {
            for y in 0..b {
                plaq.push([hx[&(x, y)], vy[&(x + 1, y)], hx[&(x, y + 1)], vy[&(x, y)]]);
            }
        }
        let mut adj: Vec<Vec<(usize, usize, bool)>> = vec![Vec::new(); nv];
        for (k, &(u, v)) in links.iter().enumerate() {
            adj[u].push((v, k, true));
            adj[v].push((u, k, false));
        }
        let mut tree = Vec::new();
        let mut seen = vec![false; nv];
        seen[0] = true;
        let mut dq = VecDeque::from([0usize]);
        while let Some(u) = dq.pop_front() {
            for &(v, k, fwd) in &adj[u] {
                if !seen[v] {
                    seen[v] = true;
                    tree.push((u, v, k, fwd));
                    dq.push_back(v);
                }
            }
        }
        let mut in_tree = vec![false; links.len()];
        for t in &tree {
            in_tree[t.2] = true;
        }
        let kept = (0..links.len()).filter(|&k| !in_tree[k]).collect();
        Grid { nv, links, plaq, tree, kept }
    }

    fn canonical(&self, g: &Group, u: &[usize]) -> u64 {
        let mut h = vec![0usize; self.nv];
        for &(a, b, k, fwd) in &self.tree {
            h[b] = if fwd { g.mul[h[a]][u[k]] } else { g.mul[h[a]][g.inv[u[k]]] };
        }
        let key: Vec<usize> = self
            .kept
            .iter()
            .map(|&k| g.mul[g.mul[h[self.links[k].0]][u[k]]][g.inv[h[self.links[k].1]]])
            .collect();
        (0..6).map(|c| key.iter().fold(0u64, |acc, &x| acc * 6 + g.conj(c, x) as u64)).min().unwrap_or(0)
    }

    fn magnetic(&self, g: &Group, u: &[usize]) -> i64 {
        self.plaq
            .iter()
            .map(|p| 2 - g.chi[g.mul[g.mul[g.mul[u[p[0]]][u[p[1]]]][g.inv[u[p[2]]]]][g.inv[u[p[3]]]]])
            .sum()
    }
}

struct Model {
    w: Vec<i64>,
    rows: Vec<Vec<(usize, i64)>>, // H in the orbit basis, row i: (j, value)
}

fn build(grid: &Grid, g: &Group, r: i64, e: i64) -> Model {
    let p = grid.kept.len();
    let raw = 6u64.pow(p as u32);
    let decode = |mut code: u64| -> Vec<usize> {
        let mut key = vec![0usize; p];
        for slot in key.iter_mut().rev() {
            *slot = (code % 6) as usize;
            code /= 6;
        }
        key
    };
    let orbit_min = |key: &[usize]| -> (u64, i64) {
        let mut images: Vec<u64> =
            (0..6).map(|c| key.iter().fold(0u64, |acc, &x| acc * 6 + g.conj(c, x) as u64)).collect();
        images.sort_unstable();
        images.dedup();
        (images[0], images.len() as i64)
    };
    let mut index: HashMap<u64, usize> = HashMap::new();
    let mut reps: Vec<u64> = Vec::new();
    let mut w: Vec<i64> = Vec::new();
    for code in 0..raw {
        let (m, size) = orbit_min(&decode(code));
        if m == code {
            index.insert(code, reps.len());
            reps.push(code);
            w.push(size);
        }
    }
    let nl = grid.links.len();
    let mut rows = Vec::with_capacity(reps.len());
    for (i, &code) in reps.iter().enumerate() {
        let key = decode(code);
        let mut u = vec![0usize; nl];
        for (slot, &k) in grid.kept.iter().enumerate() {
            u[k] = key[slot];
        }
        let mut row: HashMap<usize, i64> = HashMap::new();
        row.insert(i, e * 3 * nl as i64 + r * grid.magnetic(g, &u));
        for k in 0..nl {
            let old = u[k];
            for &t in &g.trans {
                u[k] = g.mul[t][old];
                let j = index[&grid.canonical(g, &u)];
                *row.entry(j).or_insert(0) -= e;
            }
            u[k] = old;
        }
        let mut v: Vec<(usize, i64)> = row.into_iter().collect();
        v.sort_unstable();
        rows.push(v);
    }
    Model { w, rows }
}

fn detailed_balance(m: &Model) -> bool {
    m.rows.iter().enumerate().all(|(i, row)| {
        row.iter().all(|&(j, v)| {
            let back = m.rows[j].iter().find(|e| e.0 == i).map_or(0, |e| e.1);
            m.w[i] * v == m.w[j] * back
        })
    })
}

// ---------------------------------------------------------------- certified counts
//
// For a shift x the matrix A = W*(H - x) is factored approximately in fixed point, P A P^T ~ L D L^T, with
// diagonal pivoting. The residual E = P A P^T - L D L^T is then bounded entry by entry with outward-rounded
// integers (one product chain per entry, so the widths do not compound), and eps is an upper bound of its
// largest absolute row sum, hence of its spectral norm. L is unit lower triangular, so by Sylvester's law the
// number of negative entries of D is the number of negative eigenvalues of A - E, and because W >= 1,
//     #levels of H below x - eps  <=  neg(D)  <=  #levels of H below x + eps.

fn shr_floor(p: i128) -> i128 {
    p >> FP
}

fn shr_ceil(p: i128) -> i128 {
    -((-p) >> FP)
}

struct Count {
    neg: usize,
    eps: i128, // in units of 1e-9, rounded up
}

fn count_levels(m: &Model, num: i128, threads: usize) -> Result<Count, &'static str> {
    let n = m.w.len();
    let x_fp = (num << FP).div_euclid(UNITS);
    let mut a0: Vec<Vec<i64>> = vec![vec![0i64; n]; n];
    for (i, row) in m.rows.iter().enumerate() {
        for &(j, v) in row {
            let mut e = (i128::from(m.w[i]) * i128::from(v)) << FP;
            if i == j {
                e -= i128::from(m.w[i]) * x_fp;
            }
            a0[i][j] = i64::try_from(e).map_err(|_| "entry_overflow")?;
        }
    }
    let mut a = a0.clone();
    let mut perm: Vec<usize> = (0..n).collect();
    let mut neg = 0usize;
    for k in 0..n {
        let p = (k..n).max_by_key(|&q| a[q][q].unsigned_abs()).unwrap_or(k);
        if p != k {
            a.swap(k, p);
            for row in a.iter_mut() {
                row.swap(k, p);
            }
            perm.swap(k, p);
        }
        let d = a[k][k];
        if d == 0 {
            return Err("zero_pivot");
        }
        if d < 0 {
            neg += 1;
        }
        if k + 1 == n {
            break;
        }
        let col: Vec<i64> = (k + 1..n).map(|i| a[i][k]).collect();
        let mut l = Vec::with_capacity(col.len());
        for &c in &col {
            l.push(i64::try_from((i128::from(c) << FP) / i128::from(d)).map_err(|_| "multiplier_overflow")?);
        }
        let (_, tail) = a.split_at_mut(k + 1);
        let chunk = tail.len().div_ceil(threads.max(1)).max(1);
        let ok = thread::scope(|s| {
            let handles: Vec<_> = tail
                .chunks_mut(chunk)
                .enumerate()
                .map(|(ci, rows)| {
                    let (l, col) = (&l, &col);
                    s.spawn(move || {
                        for (ri, row) in rows.iter_mut().enumerate() {
                            let li = l[ci * chunk + ri];
                            row[k] = li;
                            if li == 0 {
                                continue;
                            }
                            for (j, &cj) in col.iter().enumerate() {
                                let prod = (i128::from(li) * i128::from(cj)) >> FP;
                                let Ok(next) = i64::try_from(i128::from(row[k + 1 + j]) - prod) else { return false };
                                row[k + 1 + j] = next;
                            }
                        }
                        true
                    })
                })
                .collect();
            handles.into_iter().all(|h| h.join().unwrap_or(false))
        });
        if !ok {
            return Err("update_overflow");
        }
    }
    // residual bound: for i >= j, R_ij = A0[perm i][perm j] - sum_{k<j} L_ik D_k L_jk - L_ij D_j   (L_jj = 1)
    let rows_idx: Vec<usize> = (0..n).collect();
    let chunk = n.div_ceil(threads.max(1)).max(1);
    let (a, a0, perm) = (&a, &a0, &perm);
    let partial: Vec<Vec<i128>> = thread::scope(|s| {
        let handles: Vec<_> = rows_idx
            .chunks(chunk)
            .map(|rows| {
                s.spawn(move || {
                    let mut sums = vec![0i128; n];
                    for &i in rows {
                        for j in 0..=i {
                            let (mut lo, mut hi) = (0i128, 0i128);
                            for k in 0..j {
                                let t = i128::from(a[i][k]) * i128::from(a[k][k]);
                                let (t_lo, t_hi) = (shr_floor(t), shr_ceil(t));
                                let ljk = i128::from(a[j][k]);
                                let (u, v) = (t_lo * ljk, t_hi * ljk);
                                lo += shr_floor(u.min(v));
                                hi += shr_ceil(u.max(v));
                            }
                            if i == j {
                                lo += i128::from(a[j][j]);
                                hi += i128::from(a[j][j]);
                            } else {
                                let t = i128::from(a[i][j]) * i128::from(a[j][j]);
                                lo += shr_floor(t);
                                hi += shr_ceil(t);
                            }
                            let orig = i128::from(a0[perm[i]][perm[j]]);
                            let r = (orig - lo).abs().max((orig - hi).abs());
                            sums[i] += r;
                            if i != j {
                                sums[j] += r;
                            }
                        }
                    }
                    sums
                })
            })
            .collect();
        handles.into_iter().map(|h| h.join().unwrap_or_default()).collect()
    });
    if partial.iter().any(|v| v.len() != n) {
        return Err("residual_thread_failed");
    }
    let worst = (0..n).map(|i| partial.iter().map(|v| v[i]).sum::<i128>()).max().unwrap_or(0);
    // + the difference between x and its fixed-point value (below 2^-FP), times W <= 6
    let eps = -((-((worst + 6) * UNITS)) >> FP) + 1;
    Ok(Count { neg, eps })
}

/// Bracket of the k-th level by bisection on certified counts, from lo (fewer than k levels below) to hi.
fn bisect(m: &Model, k: usize, lo: i128, hi: i128, threads: usize) -> Result<(i128, i128), &'static str> {
    let (mut lo, mut hi) = (lo, hi);
    let c = count_levels(m, lo, threads)?;
    if c.neg >= k {
        return Err("lower_end_not_below_the_level");
    }
    lo -= c.eps;
    let c = count_levels(m, hi, threads)?;
    if c.neg < k {
        return Err("upper_end_not_above_the_level");
    }
    hi += c.eps;
    for _ in 0..80 {
        if hi - lo <= 2000 {
            break;
        }
        let mid = (lo + hi) / 2;
        let c = count_levels(m, mid, threads)?;
        let (next_lo, next_hi) = if c.neg >= k { (lo, mid + c.eps) } else { (mid - c.eps, hi) };
        if next_hi - next_lo >= hi - lo {
            break; // the residual bound is as wide as the bracket: no further progress
        }
        lo = next_lo;
        hi = next_hi;
    }
    Ok((lo, hi))
}

/// Bracket of the k-th level around an estimate: two counts when the estimate is good.
fn around(m: &Model, k: usize, est: i128, threads: usize) -> Option<(i128, i128)> {
    let mut delta: i128 = 1000;
    while delta <= 100_000_000 {
        let below = count_levels(m, est - delta, threads).ok()?;
        let above = count_levels(m, est + delta, threads).ok()?;
        if below.neg < k && above.neg >= k {
            return Some((est - delta - below.eps, est + delta + above.eps));
        }
        delta *= 10;
    }
    None
}

// ---------------------------------------------------------------- estimate by fixed-point subspace iteration

const EP: u32 = 40;

fn apply(m: &Model, v: &[i128]) -> Vec<i128> {
    m.rows.iter().map(|row| row.iter().map(|&(j, h)| i128::from(h) * v[j]).sum()).collect()
}

fn dot(m: &Model, a: &[i128], b: &[i128]) -> i128 {
    a.iter().zip(b).zip(&m.w).map(|((x, y), w)| ((x * y) >> EP) * i128::from(*w)).sum()
}

fn rescale(v: &mut [i128]) {
    let top = v.iter().map(|x| x.abs()).max().unwrap_or(1).max(1);
    for x in v.iter_mut() {
        *x = (*x << EP) / top;
    }
}

/// Three vectors after shifted subspace iteration in fixed point (the first converges to the ground vector).
fn iterate(m: &Model, ceiling: i128, sweeps: usize) -> Vec<Vec<i128>> {
    let n = m.w.len();
    let mut vs: Vec<Vec<i128>> = (0..3usize)
        .map(|s| (0..n).map(|i| (((i * 7919 + s * 104_729 + 1) % 1009) as i128 + 1 - 504 * (s as i128).min(1)) << (EP - 10)).collect())
        .collect();
    for _ in 0..sweeps {
        for s in 0..3 {
            let hv = apply(m, &vs[s]);
            let mut next: Vec<i128> = vs[s].iter().zip(&hv).map(|(x, h)| ceiling * x - h).collect();
            rescale(&mut next);
            for prev in vs.iter().take(s) {
                let c_num = dot(m, &next, prev);
                let c_den = dot(m, prev, prev).max(1);
                for (x, y) in next.iter_mut().zip(prev) {
                    *x -= (c_num * y) / c_den;
                }
            }
            rescale(&mut next);
            vs[s] = next;
        }
    }
    vs
}

/// Rayleigh estimates of the two lowest levels, in units of 1e-9. An estimate, certified afterwards.
fn estimate(m: &Model, ceiling: i128, sweeps: usize) -> (i128, i128) {
    let vs = iterate(m, ceiling, sweeps);
    let ray = |v: &[i128]| -> i128 {
        let hv = apply(m, v);
        (dot(m, v, &hv) * UNITS) / dot(m, v, v).max(1)
    };
    (ray(&vs[0]), ray(&vs[1]))
}

// ---------------------------------------------------------------- sparse mode (no dense matrix)
//
// What is certified here, with O(nonzeros) work and exact integers:
//   E0: the off-diagonal entries of H are <= 0, so for any positive vector v (Collatz-Wielandt)
//         min_i (Hv)_i / v_i  <=  E0  <=  max_i (Hv)_i / v_i.
//   E1 from above: by min-max, E1 <= the larger Ritz value of any two-dimensional subspace; the Ritz
//         problem is solved exactly for two integer vectors (256-bit products).
// A certified lower end for E1 needs a full count of levels and is not produced in this mode.

/// Sign of a*b - c*d for i128 inputs, by 256-bit products.
fn cmp_products(a: i128, b: i128, c: i128, d: i128) -> std::cmp::Ordering {
    fn wide(x: u128, y: u128) -> (u128, u128) {
        let (x1, x0) = (x >> 64, x & u128::from(u64::MAX));
        let (y1, y0) = (y >> 64, y & u128::from(u64::MAX));
        let (p00, p01, p10, p11) = (x0 * y0, x0 * y1, x1 * y0, x1 * y1);
        let mid = (p00 >> 64) + (p01 & u128::from(u64::MAX)) + (p10 & u128::from(u64::MAX));
        let lo = (p00 & u128::from(u64::MAX)) | (mid << 64);
        let hi = p11 + (p01 >> 64) + (p10 >> 64) + (mid >> 64);
        (hi, lo)
    }
    let signed = |x: i128, y: i128| -> (bool, (u128, u128)) {
        ((x < 0) != (y < 0) && x != 0 && y != 0, wide(x.unsigned_abs(), y.unsigned_abs()))
    };
    let (n1, m1) = signed(a, b);
    let (n2, m2) = signed(c, d);
    match (n1, n2) {
        (false, false) => m1.cmp(&m2),
        (true, true) => m2.cmp(&m1),
        (false, true) => {
            if m1 == (0, 0) && m2 == (0, 0) {
                std::cmp::Ordering::Equal
            } else {
                std::cmp::Ordering::Greater
            }
        }
        (true, false) => {
            if m1 == (0, 0) && m2 == (0, 0) {
                std::cmp::Ordering::Equal
            } else {
                std::cmp::Ordering::Less
            }
        }
    }
}

struct SparseOut {
    e0_lo: i128,
    e0_hi: i128,
    e1_estimate: i128,
    e1_upper: i128,
}

fn sparse_levels(m: &Model, ceiling: i128, sweeps: usize) -> Result<SparseOut, &'static str> {
    let vs = iterate(m, ceiling, sweeps);
    let max_diag = m.rows.iter().enumerate().map(|(i, r)| r.iter().find(|e| e.0 == i).map_or(0, |e| e.1.abs())).max().unwrap_or(1);
    certify_pair(&|v: &[i128]| apply(m, v), &m.w, max_diag, ceiling, &vs[0], &vs[1])
}

/// The two certificates for a pair of vectors: E0 two-sided from v0 > 0, E1 from above from span(v0, v1).
fn certify_pair<F: Fn(&[i128]) -> Vec<i128>>(
    apply: &F,
    w: &[i64],
    max_diag: i64,
    ceiling: i128,
    v0: &[i128],
    v1: &[i128],
) -> Result<SparseOut, &'static str> {
    let n = w.len();
    if v0.iter().any(|&x| x <= 0) {
        return Err("ground_vector_not_positive");
    }
    let hv = apply(v0);
    let mut e0_lo = i128::MAX;
    let mut e0_hi = i128::MIN;
    for (h, v) in hv.iter().zip(v0) {
        let num = h.checked_mul(UNITS).ok_or("ratio_overflow")?;
        e0_lo = e0_lo.min(num.div_euclid(*v));
        e0_hi = e0_hi.max(-((-num).div_euclid(*v)));
    }
    let e1_estimate = (dot_w(w, v1, &apply(v1)) * UNITS) / dot_w(w, v1, v1).max(1);
    // exact Ritz problem on two reduced integer vectors
    let head = 128 - (n as u128 * 6 * max_diag.max(1) as u128).leading_zeros(); // bits of n*W*H
    let bits = ((92u32.saturating_sub(head)) / 2).min(EP); // entries a_kl below 2^92 so that a*UNITS fits
    let reduce = |v: &[i128]| -> Vec<i128> { v.iter().map(|x| x >> (EP - bits)).collect() };
    let u = [reduce(v0), reduce(v1)];
    let hu = [apply(&u[0]), apply(&u[1])];
    let form = |x: &Vec<i128>, y: &Vec<i128>| -> i128 { x.iter().zip(y).zip(w).map(|((p, q), w)| p * q * i128::from(*w)).sum() };
    let a = [[form(&u[0], &hu[0]), form(&u[0], &hu[1])], [form(&u[1], &hu[0]), form(&u[1], &hu[1])]];
    let b = [[form(&u[0], &u[0]), form(&u[0], &u[1])], [form(&u[1], &u[0]), form(&u[1], &u[1])]];
    if a[0][1] != a[1][0] {
        return Err("ritz_form_not_symmetric");
    }
    // larger Ritz value < t/UNITS  <=>  A*UNITS - t*B is negative definite
    let below = |t: i128| -> bool {
        let m11 = a[0][0] * UNITS - t * b[0][0];
        let m22 = a[1][1] * UNITS - t * b[1][1];
        let m12 = a[0][1] * UNITS - t * b[0][1];
        m11 < 0 && m22 < 0 && cmp_products(m11, m22, m12, m12) == std::cmp::Ordering::Greater
    };
    let (mut lo, mut hi) = (e0_lo, ceiling * UNITS);
    if !below(hi) {
        return Err("ritz_upper_range");
    }
    while hi - lo > 1 {
        let mid = lo + (hi - lo) / 2;
        if below(mid) {
            hi = mid;
        } else {
            lo = mid;
        }
    }
    Ok(SparseOut { e0_lo, e0_hi, e1_estimate, e1_upper: hi })
}

// ---------------------------------------------------------------- large grids: compact matrix, Chebyshev filter
//
// Every row of H has its diagonal and exactly 3*links moves of weight -e (repeats allowed), so the matrix is
// held as one u32 column per move. The vectors come from Chebyshev-filtered subspace iteration; whatever the
// vectors are, the two certificates of the sparse mode (Collatz-Wielandt for E0, exact Ritz for E1 from
// above) hold for them, so the filter changes the tightness of the result and never its validity.

struct Big {
    w: Vec<i64>,
    diag: Vec<i64>,
    cols: Vec<u32>,
    stride: usize,
    e: i64,
}

fn canonical_fast(grid: &Grid, g: &Group, conj: &[[u8; 6]; 6], u: &[usize], h: &mut [usize]) -> u64 {
    h[0] = 0;
    for &(a, b, k, fwd) in &grid.tree {
        h[b] = if fwd { g.mul[h[a]][u[k]] } else { g.mul[h[a]][g.inv[u[k]]] };
    }
    let mut images = [0u64; 6];
    for &k in &grid.kept {
        let x = g.mul[g.mul[h[grid.links[k].0]][u[k]]][g.inv[h[grid.links[k].1]]];
        for (c, im) in images.iter_mut().enumerate() {
            *im = *im * 6 + u64::from(conj[c][x]);
        }
    }
    images.iter().copied().min().unwrap_or(0)
}

fn build_big(grid: &Grid, g: &Group, r: i64, e: i64, threads: usize) -> Option<Big> {
    let p = grid.kept.len();
    let nl = grid.links.len();
    if p > 12 {
        return None;
    }
    let raw = 6u64.pow(p as u32);
    if raw >= u64::from(u32::MAX) {
        return None;
    }
    let mut conj = [[0u8; 6]; 6];
    for (c, row) in conj.iter_mut().enumerate() {
        for (x, slot) in row.iter_mut().enumerate() {
            *slot = g.conj(c, x) as u8;
        }
    }
    let mut rank = vec![u32::MAX; raw as usize];
    let mut reps: Vec<u32> = Vec::new();
    let mut w: Vec<i64> = Vec::new();
    for code in 0..raw {
        let mut digits = [0usize; 12];
        let mut c = code;
        for slot in (0..p).rev() {
            digits[slot] = (c % 6) as usize;
            c /= 6;
        }
        let mut images = [0u64; 6];
        for &d in &digits[..p] {
            for (c, im) in images.iter_mut().enumerate() {
                *im = *im * 6 + u64::from(conj[c][d]);
            }
        }
        images.sort_unstable();
        if images[0] == code {
            let size = 1 + images.windows(2).filter(|x| x[0] != x[1]).count();
            rank[code as usize] = reps.len() as u32;
            reps.push(code as u32);
            w.push(size as i64);
        }
    }
    let n = reps.len();
    let stride = 3 * nl;
    let mut cols = vec![0u32; n * stride];
    let mut diag = vec![0i64; n];
    let chunk = n.div_ceil(threads.max(1)).max(1);
    let (rank, conj) = (&rank, &conj);
    let ok = thread::scope(|s| {
        let handles: Vec<_> = cols
            .chunks_mut(chunk * stride)
            .zip(diag.chunks_mut(chunk))
            .zip(reps.chunks(chunk))
            .map(|((cols, diag), reps)| {
                s.spawn(move || {
                    let mut u = vec![0usize; nl];
                    let mut h = vec![0usize; grid.nv];
                    for (i, &code) in reps.iter().enumerate() {
                        let mut c = u64::from(code);
                        for &k in grid.kept.iter().rev() {
                            u[k] = (c % 6) as usize;
                            c /= 6;
                        }
                        diag[i] = e * 3 * nl as i64 + r * grid.magnetic(g, &u);
                        let mut at = i * stride;
                        for k in 0..nl {
                            let old = u[k];
                            for &t in &g.trans {
                                u[k] = g.mul[t][old];
                                let j = rank[canonical_fast(grid, g, conj, &u, &mut h) as usize];
                                if j == u32::MAX {
                                    return false;
                                }
                                cols[at] = j;
                                at += 1;
                            }
                            u[k] = old;
                        }
                    }
                    true
                })
            })
            .collect();
        handles.into_iter().all(|h| h.join().unwrap_or(false))
    });
    if !ok {
        return None;
    }
    Some(Big { w, diag, cols, stride, e })
}

fn apply_big(b: &Big, v: &[i128], threads: usize) -> Vec<i128> {
    let n = b.w.len();
    let mut out = vec![0i128; n];
    let chunk = n.div_ceil(threads.max(1)).max(1);
    thread::scope(|s| {
        for (ci, part) in out.chunks_mut(chunk).enumerate() {
            s.spawn(move || {
                for (ri, slot) in part.iter_mut().enumerate() {
                    let i = ci * chunk + ri;
                    let sum: i128 = b.cols[i * b.stride..(i + 1) * b.stride].iter().map(|&j| v[j as usize]).sum();
                    *slot = i128::from(b.diag[i]) * v[i] - i128::from(b.e) * sum;
                }
            });
        }
    });
    out
}

fn dot_w(w: &[i64], a: &[i128], b: &[i128]) -> i128 {
    a.iter().zip(b).zip(w).map(|((x, y), w)| ((x * y) >> EP) * i128::from(*w)).sum()
}

/// Scale two vectors by the same factor so that the first has its largest entry at 2^EP.
fn rescale_pair(lead: &mut [i128], other: &mut [i128]) {
    let top = lead.iter().map(|x| x.abs()).max().unwrap_or(1).max(1);
    for x in lead.iter_mut() {
        *x = (*x << EP) / top;
    }
    for x in other.iter_mut() {
        *x = (*x << EP) / top;
    }
}

/// Three vectors after Chebyshev-filtered subspace iteration. The filter interval is [a, b] with b an upper
/// bound of the spectrum and a the Rayleigh value of the third vector, renewed every round.
fn cheb_vectors<F: Fn(&[i128]) -> Vec<i128>>(apply: &F, w: &[i64], ceiling: i128, rounds: usize, degree: usize) -> Vec<Vec<i128>> {
    const Q: i128 = 1024;
    let n = w.len();
    let mut vs: Vec<Vec<i128>> = (0..3usize)
        .map(|s| (0..n).map(|i| (((i * 7919 + s * 104_729 + 1) % 1009) as i128 + 1 - 504 * (s as i128).min(1)) << (EP - 10)).collect())
        .collect();
    let b_q = ceiling * Q;
    for _ in 0..rounds {
        let hv = apply(&vs[2]);
        let ray_q = (dot_w(w, &vs[2], &hv) * Q) / dot_w(w, &vs[2], &vs[2]).max(1);
        let a_q = (ray_q + 1).min(b_q - Q);
        let (sum, diff) = (a_q + b_q, b_q - a_q);
        for s in 0..3 {
            let mut prev = vs[s].clone();
            let hv = apply(&prev);
            let mut cur: Vec<i128> = prev.iter().zip(&hv).map(|(y, h)| (2 * Q * h - sum * y) / diff).collect();
            rescale_pair(&mut cur, &mut prev);
            for _ in 1..degree {
                let hv = apply(&cur);
                let mut next: Vec<i128> =
                    cur.iter().zip(&hv).zip(&prev).map(|((y, h), p)| (2 * (2 * Q * h - sum * y)) / diff - p).collect();
                rescale_pair(&mut next, &mut cur);
                prev = cur;
                cur = next;
            }
            for lower in vs.iter().take(s) {
                let c_num = dot_w(w, &cur, lower);
                let c_den = dot_w(w, lower, lower).max(1);
                for (x, y) in cur.iter_mut().zip(lower) {
                    *x -= (c_num * y) / c_den;
                }
            }
            rescale(&mut cur);
            vs[s] = cur;
        }
    }
    // two plain positive sweeps on the ground vector (ceiling - H has entries >= 0)
    for _ in 0..2 {
        let hv = apply(&vs[0]);
        let mut next: Vec<i128> = vs[0].iter().zip(&hv).map(|(x, h)| ceiling * x - h).collect();
        rescale(&mut next);
        vs[0] = next;
    }
    if vs[0].iter().all(|&x| x <= 0) {
        for x in vs[0].iter_mut() {
            *x = -*x;
        }
    }
    vs
}

#[allow(clippy::too_many_arguments)]
fn run_big(a: usize, b: usize, r: i64, rden: i64, threads: usize, rounds: usize, degree: usize, grid: &Grid, g: &Group) -> bool {
    let p = a * b;
    let Some(big) = build_big(grid, g, r, rden, threads) else {
        println!("SPARSE_REFUSE|reason=compact_build_failed_or_grid_too_large|json=0");
        return false;
    };
    let n = big.w.len();
    let formula = (6u64.pow(p as u32) + 2 * 3u64.pow(p as u32) + 3 * 2u64.pow(p as u32)) / 6;
    let size_sum: i64 = big.w.iter().sum();
    let applyf = |v: &[i128]| apply_big(&big, v, threads);
    // W-symmetry probe with two exact integer vectors: <x, H y>_W = <H x, y>_W
    let x: Vec<i128> = (0..n).map(|i| ((i * 7919 + 1) % 1009) as i128 + 1).collect();
    let y: Vec<i128> = (0..n).map(|i| ((i * 104_729 + 5) % 997) as i128 + 1).collect();
    let (hx, hy) = (applyf(&x), applyf(&y));
    let left: i128 = x.iter().zip(&hy).zip(&big.w).map(|((p, q), w)| p * q * i128::from(*w)).sum();
    let right: i128 = hx.iter().zip(&y).zip(&big.w).map(|((p, q), w)| p * q * i128::from(*w)).sum();
    let checks = n as u64 == formula && size_sum as u64 == 6u64.pow(p as u32) && left == right;
    println!(
        "GRID_SPACE|a={a}|b={b}|plaquettes={p}|links={}|raw_link_states=6^{}|gauge_orbits={n}|r={r}|rden={rden}|matrix=compact_one_column_per_move|orbit_formula_and_weighted_symmetry_probe={}|json=0",
        grid.links.len(),
        grid.links.len(),
        i32::from(checks)
    );
    if !checks {
        return false;
    }
    let ceiling = 6 * grid.links.len() as i128 * i128::from(rden) + 3 * i128::from(r) * p as i128 + 1;
    let vs = cheb_vectors(&applyf, &big.w, ceiling, rounds, degree);
    let max_diag = big.diag.iter().map(|d| d.abs()).max().unwrap_or(1);
    match certify_pair(&applyf, &big.w, max_diag, ceiling, &vs[0], &vs[1]) {
        Ok(o) => {
            println!(
                "SPARSE_LEVELS|a={a}|b={b}|r={r}|rden={rden}|scaled_by_rden=1|gauge_orbits={n}|units=1e-9|vectors=chebyshev_filtered_subspace|rounds={rounds}|degree={degree}|E0_lo={}|E0_hi={}|E0_method=Collatz_Wielandt_exact|E1_estimate={}|E1_upper={}|E1_upper_method=exact_two_vector_Ritz|E1_lower=NOT_CERTIFIED|gap_estimate={}|gap_upper={}|json=0",
                o.e0_lo, o.e0_hi, o.e1_estimate, o.e1_upper, o.e1_estimate - (o.e0_lo + o.e0_hi) / 2, o.e1_upper - o.e0_lo
            );
            true
        }
        Err(why) => {
            println!("SPARSE_REFUSE|reason={why}|json=0");
            false
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 4 {
        println!("GRID_REFUSE|reason=usage_open_grid_A_B_RNUM_[THREADS]_[RDEN]|json=0");
        std::process::exit(2);
    }
    let parse = |s: &String| s.parse::<i64>().unwrap_or(0);
    let (a, b, r) = (parse(&args[1]) as usize, parse(&args[2]) as usize, parse(&args[3]));
    let threads = args.get(4).map_or(4, |s| s.parse::<usize>().unwrap_or(4));
    let g = Group::new();
    let grid = Grid::new(a, b);
    let p = a * b;
    let rden = args.get(5).map_or(1, |s| s.parse::<i64>().unwrap_or(1)).max(1);
    if args.get(6).is_some_and(|x| x == "cheb") {
        let rounds = args.get(7).map_or(15, |x| x.parse::<usize>().unwrap_or(15));
        let degree = args.get(8).map_or(20, |x| x.parse::<usize>().unwrap_or(20)).max(2) / 2 * 2;
        if !run_big(a, b, r, rden, threads, rounds, degree, &grid, &g) {
            std::process::exit(1);
        }
        return;
    }
    let model = build(&grid, &g, r, rden);
    let n = model.w.len();
    let formula = (6u64.pow(p as u32) + 2 * 3u64.pow(p as u32) + 3 * 2u64.pow(p as u32)) / 6;
    let size_sum: i64 = model.w.iter().sum();
    let checks = n as u64 == formula && size_sum as u64 == 6u64.pow(p as u32) && detailed_balance(&model);
    println!(
        "GRID_SPACE|a={a}|b={b}|plaquettes={p}|links={}|raw_link_states=6^{}|gauge_orbits={n}|r={r}|rden={rden}|orbit_formula_and_detailed_balance={}|json=0",
        grid.links.len(),
        grid.links.len(),
        i32::from(checks)
    );
    if !checks {
        std::process::exit(1);
    }
    let ceiling = 6 * grid.links.len() as i128 * i128::from(rden) + 3 * i128::from(r) * p as i128 + 1;
    if args.get(6).is_some_and(|x| x == "sparse") {
        let sweeps = args.get(7).map_or(600, |x| x.parse::<usize>().unwrap_or(600));
        match sparse_levels(&model, ceiling, sweeps) {
            Ok(o) => println!(
                "SPARSE_LEVELS|a={a}|b={b}|r={r}|rden={rden}|scaled_by_rden=1|gauge_orbits={n}|units=1e-9|sweeps={sweeps}|E0_lo={}|E0_hi={}|E0_method=Collatz_Wielandt_exact|E1_estimate={}|E1_upper={}|E1_upper_method=exact_two_vector_Ritz|E1_lower=NOT_CERTIFIED|gap_estimate={}|gap_upper={}|json=0",
                o.e0_lo, o.e0_hi, o.e1_estimate, o.e1_upper, o.e1_estimate - (o.e0_lo + o.e0_hi) / 2, o.e1_upper - o.e0_lo
            ),
            Err(why) => {
                println!("SPARSE_REFUSE|reason={why}|json=0");
                std::process::exit(1);
            }
        }
        return;
    }
    let (e0, e1) = estimate(&model, ceiling, 1500);
    println!("GRID_ESTIMATE|E0_estimate={e0}|E1_estimate={e1}|units=1e-9|status=ESTIMATE_ONLY|json=0");
    let top = ceiling * UNITS;
    let b0 = around(&model, 1, e0, threads).map_or_else(|| bisect(&model, 1, -UNITS, top, threads), Ok);
    let b1 = around(&model, 2, e1, threads).map_or_else(|| bisect(&model, 2, -UNITS, top, threads), Ok);
    match (b0, b1) {
        (Ok(x), Ok(y)) => {
            println!(
                "GRID_LEVELS|a={a}|b={b}|r={r}|rden={rden}|scaled_by_rden=1|gauge_orbits={n}|units=1e-9|E0_lo={}|E0_hi={}|E1_lo={}|E1_hi={}|gap_lo={}|gap_hi={}|method=approximate_factor_with_certified_residual_bound|json=0",
                x.0, x.1, y.0, y.1, y.0 - x.1, y.1 - x.0
            );
            return;
        }
        (x, y) => {
            println!(
                "GRID_UNCERTIFIED|level1={}|level2={}|json=0",
                x.err().unwrap_or("ok"),
                y.err().unwrap_or("ok")
            );
        }
    }
    println!("GRID_LEVELS|a={a}|b={b}|r={r}|status=NOT_CERTIFIED|json=0");
    std::process::exit(1);
}
