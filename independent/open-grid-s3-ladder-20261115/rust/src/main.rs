//! S3 Kogut-Susskind rule of this repository on an open a x b grid of plaquettes, in the gauge-fixed
//! space (one group element per independent loop, reduced by the global conjugation).
//!
//! The two lowest levels are located by fixed-point subspace iteration (an estimate only) and then
//! certified by inertia counts of W*(H - x) computed with outward-rounded integer intervals: a count is
//! reported only when every pivot interval excludes zero. Integers only; no floating point.
//!
//! usage: open_grid A B RNUM [THREADS] [RDEN]
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

// ---------------------------------------------------------------- interval arithmetic, outward rounded

#[derive(Clone, Copy)]
struct Iv {
    lo: i64,
    hi: i64,
}

fn shr_floor(p: i128) -> Option<i64> {
    i64::try_from(p >> FP).ok()
}

fn shr_ceil(p: i128) -> Option<i64> {
    i64::try_from(-((-p) >> FP)).ok()
}

fn iv_mul(a: Iv, b: Iv) -> Option<Iv> {
    let c = [
        i128::from(a.lo) * i128::from(b.lo),
        i128::from(a.lo) * i128::from(b.hi),
        i128::from(a.hi) * i128::from(b.lo),
        i128::from(a.hi) * i128::from(b.hi),
    ];
    let lo = c.iter().copied().min()?;
    let hi = c.iter().copied().max()?;
    Some(Iv { lo: shr_floor(lo)?, hi: shr_ceil(hi)? })
}

fn iv_sub(a: Iv, b: Iv) -> Option<Iv> {
    Some(Iv { lo: a.lo.checked_sub(b.hi)?, hi: a.hi.checked_sub(b.lo)? })
}

/// a / d for an interval d that excludes zero.
fn iv_div(a: Iv, d: Iv) -> Option<Iv> {
    if d.lo <= 0 && d.hi >= 0 {
        return None;
    }
    let fl = |n: i64, q: i64| -> i128 { (i128::from(n) << FP).div_euclid(i128::from(q)) };
    let floor = |n: i64, q: i64| -> i128 {
        if q > 0 {
            fl(n, q)
        } else {
            (-(i128::from(n) << FP)).div_euclid(-i128::from(q))
        }
    };
    let ceil = |n: i64, q: i64| -> i128 {
        if q > 0 {
            -((-(i128::from(n) << FP)).div_euclid(i128::from(q)))
        } else {
            -((i128::from(n) << FP).div_euclid(-i128::from(q)))
        }
    };
    let pairs = [(a.lo, d.lo), (a.lo, d.hi), (a.hi, d.lo), (a.hi, d.hi)];
    let lo = pairs.iter().map(|&(n, q)| floor(n, q)).min()?;
    let hi = pairs.iter().map(|&(n, q)| ceil(n, q)).max()?;
    Some(Iv { lo: i64::try_from(lo).ok()?, hi: i64::try_from(hi).ok()? })
}

/// Number of levels below x = num/UNITS, or None when a pivot interval contains zero or a value overflows.
fn count_below(m: &Model, num: i128, threads: usize) -> Result<usize, &'static str> {
    let n = m.w.len();
    let x_lo = (num << FP).div_euclid(UNITS);
    let x_hi = -((-(num << FP)).div_euclid(UNITS));
    // lower triangle of A = W*(H - x), row i holds columns 0..=i
    let mut a: Vec<Vec<Iv>> = (0..n).map(|i| vec![Iv { lo: 0, hi: 0 }; i + 1]).collect();
    for (i, row) in m.rows.iter().enumerate() {
        for &(j, v) in row {
            if j <= i {
                let e = i128::from(m.w[i]) * i128::from(v);
                let (mut lo, mut hi) = (e << FP, e << FP);
                if i == j {
                    lo -= i128::from(m.w[i]) * x_hi;
                    hi -= i128::from(m.w[i]) * x_lo;
                }
                a[i][j] = Iv { lo: i64::try_from(lo).map_err(|_| "entry_overflow")?, hi: i64::try_from(hi).map_err(|_| "entry_overflow")? };
            }
        }
    }
    let mut negative = 0usize;
    for k in 0..n {
        let d = a[k][k];
        if d.hi < 0 {
            negative += 1;
        } else if d.lo <= 0 {
            return Err("pivot_interval_contains_zero");
        }
        if k + 1 == n {
            break;
        }
        let col: Vec<Iv> = (k + 1..n).map(|i| a[i][k]).collect();
        let mut l = Vec::with_capacity(col.len());
        for &c in &col {
            l.push(iv_div(c, d).ok_or("multiplier_overflow")?);
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
                            let i = ci * chunk + ri; // row index relative to k+1
                            let li = l[i];
                            if li.lo == 0 && li.hi == 0 {
                                continue;
                            }
                            for j in 0..=i {
                                let cj = col[j];
                                if cj.lo == 0 && cj.hi == 0 {
                                    continue;
                                }
                                let Some(prod) = iv_mul(li, cj) else { return false };
                                let Some(next) = iv_sub(row[k + 1 + j], prod) else { return false };
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
    Ok(negative)
}

fn count_nudged(m: &Model, num: i128, threads: usize) -> Option<(usize, i128)> {
    let found = (0..4).find_map(|s| count_below(m, num + s, threads).ok().map(|c| (c, num + s)));
    if found.is_none() {
        let why = count_below(m, num, threads).err().unwrap_or("none");
        println!("GRID_COUNT_UNCERTIFIED|x={num}|reason={why}|json=0");
    }
    found
}

/// Bracket of the k-th level by bisection on certified counts; None when a count cannot be certified.
fn bisect(m: &Model, k: usize, lo: i128, hi: i128, threads: usize) -> Option<(i128, i128)> {
    let (mut lo, mut hi) = (lo, hi);
    if count_nudged(m, lo, threads)?.0 >= k || count_nudged(m, hi, threads)?.0 < k {
        return None;
    }
    while hi - lo > 2000 {
        let c = count_nudged(m, (lo + hi) / 2, threads)?;
        if c.0 >= k {
            hi = c.1;
        } else {
            lo = c.1;
        }
    }
    Some((lo, hi))
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

/// Rayleigh estimates of the two lowest levels, in units of 1e-9. An estimate, certified afterwards.
fn estimate(m: &Model, ceiling: i128, sweeps: usize) -> (i128, i128) {
    let n = m.w.len();
    let mut vs: Vec<Vec<i128>> = (0..3usize)
        .map(|s| (0..n).map(|i| (((i * 7919 + s * 104_729 + 1) % 1009) as i128 - 504 * (s as i128).min(1)) << (EP - 10)).collect())
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
    let ray = |v: &[i128]| -> i128 {
        let hv = apply(m, v);
        (dot(m, v, &hv) * UNITS) / dot(m, v, v).max(1)
    };
    (ray(&vs[0]), ray(&vs[1]))
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
    let (e0, e1) = estimate(&model, ceiling, 1500);
    println!("GRID_ESTIMATE|E0_estimate={e0}|E1_estimate={e1}|units=1e-9|status=ESTIMATE_ONLY|json=0");
    let mut delta: i128 = 1000;
    while delta <= 100_000_000 {
        let c = [
            count_nudged(&model, e0 - delta, threads),
            count_nudged(&model, e0 + delta, threads),
            count_nudged(&model, e1 - delta, threads),
            count_nudged(&model, e1 + delta, threads),
        ];
        if let [Some(c0), Some(c1), Some(c2), Some(c3)] = c {
            if c0.0 == 0 && c1.0 == 1 && c2.0 == 1 && c3.0 >= 2 {
                println!(
                    "GRID_LEVELS|a={a}|b={b}|r={r}|rden={rden}|scaled_by_rden=1|gauge_orbits={n}|units=1e-9|E0_lo={}|E0_hi={}|E1_lo={}|E1_hi={}|gap_lo={}|gap_hi={}|levels_below_E1_hi={}|method=interval_inertia_counts|json=0",
                    c0.1, c1.1, c2.1, c3.1, c2.1 - c1.1, c3.1 - c0.1, c3.0
                );
                return;
            }
            println!("GRID_COUNTS|delta={delta}|counts={},{},{},{}|status=bracket_not_separated|json=0", c0.0, c1.0, c2.0, c3.0);
        } else {
            println!("GRID_COUNTS|delta={delta}|status=a_pivot_interval_contains_zero|json=0");
        }
        delta *= 10;
    }
    // The estimate did not separate the levels (near-degenerate excited levels): bisect on certified counts.
    let top = ceiling * UNITS;
    let b0 = bisect(&model, 1, -UNITS, top, threads);
    let b1 = b0.and_then(|x| bisect(&model, 2, x.0, top, threads));
    if let (Some(x), Some(y)) = (b0, b1) {
        println!(
            "GRID_LEVELS|a={a}|b={b}|r={r}|rden={rden}|scaled_by_rden=1|gauge_orbits={n}|units=1e-9|E0_lo={}|E0_hi={}|E1_lo={}|E1_hi={}|gap_lo={}|gap_hi={}|method=interval_inertia_bisection|json=0",
            x.0, x.1, y.0, y.1, y.0 - x.1, y.1 - x.0
        );
        return;
    }
    println!("GRID_LEVELS|a={a}|b={b}|r={r}|status=NOT_CERTIFIED|json=0");
    std::process::exit(1);
}
