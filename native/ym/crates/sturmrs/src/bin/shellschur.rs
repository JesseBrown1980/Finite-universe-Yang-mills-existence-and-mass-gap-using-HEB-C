//! shellschur: inertia count by a magnetic-shell Schur decomposition.
//!
//! B = W(1000*(JE*E + JB*M) - t*W) (same convention as sturmrs, t in milli-units).
//! Split the states into a core C and the rest H, where every H row is strictly
//! diagonally dominant inside H: B_hh > sum_{j in H, j != h} |B_hj|. Then B_HH is
//! symmetric positive definite and, by Haynsworth's inertia additivity,
//!     neg(B) = neg(S),   S = B_CC - B_CH B_HH^{-1} B_HC.
//! The core is: every row that fails Gershgorin dominance in the full matrix,
//! plus (optionally) every state with magnetic number <= SHELL_MAX.
//!
//! Y = B_HH^{-1} B_HC is enclosed column by column with interval Gauss-Seidel
//! in scaled integers (scale F = 10^FDIG). The starting box is Varah's bound
//! ||y||_inf <= ||b||_inf / min_h (B_hh - sum_{j in H} |B_hj|); each sweep maps
//! a box containing the true solution to a box containing it (outward floor and
//! ceiling division), intersected with the previous box. S*F is then enclosed
//! entrywise, the two enclosures of S_ab and S_ba are intersected, and the
//! inertia of the small dense interval matrix S is counted with the same
//! outward-rounded LDL^T rule as sturmrs (pivot only when the pivot interval
//! excludes zero; ambiguous otherwise).
//! Integer-only: i128 with checked arithmetic, BigInt for the dense elimination.
//! usage: shellschur MATRIX JE JB TN [SHELL_MAX=-1] [FDIG=9] [TOL=1000] [MAXSWEEP=400]
//! GitRAM split: SHELLSCHUR_COLS=a:b (compute core columns a..b-1, print SCOL
//! lines), then SHELLSCHUR_MERGE=f1,f2,... (read them, finish the inertia).
//! json=0
#![forbid(unsafe_code)]
#![deny(clippy::float_arithmetic, clippy::float_cmp, clippy::cast_precision_loss)]

use num_bigint::BigInt;
use num_integer::Integer;
use num_traits::{Signed, Zero};
use std::time::Instant;

type Iv = (BigInt, BigInt);

fn cdiv(a: &BigInt, b: &BigInt) -> BigInt {
    -((-a).div_floor(b))
}

/// Enclosure of x*y/d (copy of the sturmrs rule).
fn quotient(x: &Iv, y: &Iv, d: &Iv) -> Result<Iv, String> {
    if !d.0.is_positive() && !d.1.is_negative() {
        return Err("pivot interval contains zero".into());
    }
    let p = [&x.0 * &y.0, &x.0 * &y.1, &x.1 * &y.0, &x.1 * &y.1];
    let mut lo = p.iter().min().cloned().unwrap_or_default();
    let mut hi = p.iter().max().cloned().unwrap_or_default();
    let (mut dlo, mut dhi) = (d.0.clone(), d.1.clone());
    if dhi.is_negative() {
        let (l, h) = (-hi, -lo);
        lo = l;
        hi = h;
        let (a, b) = (-dhi, -dlo);
        dlo = a;
        dhi = b;
    }
    Ok(if !lo.is_negative() {
        (lo.div_floor(&dhi), cdiv(&hi, &dlo))
    } else if !hi.is_positive() {
        (lo.div_floor(&dlo), cdiv(&hi, &dhi))
    } else {
        (lo.div_floor(&dlo), cdiv(&hi, &dlo))
    })
}

fn ck(o: Option<i128>) -> Result<i128, String> {
    o.ok_or_else(|| "i128 overflow".to_string())
}

/// [lo,hi] * c for an integer c, exact.
fn imul(lo: i128, hi: i128, c: i128) -> Result<(i128, i128), String> {
    let (a, b) = (ck(lo.checked_mul(c))?, ck(hi.checked_mul(c))?);
    Ok(if a <= b { (a, b) } else { (b, a) })
}

fn floor_div(a: i128, d: i128) -> i128 {
    Integer::div_floor(&a, &d)
}

fn ceil_div(a: i128, d: i128) -> i128 {
    -Integer::div_floor(&(-a), &d)
}

struct Op {
    n: usize,
    mag: Vec<i128>,
    diag: Vec<i128>,
    adj: Vec<Vec<(u32, i128)>>, // symmetric off-diagonal entries of B
}

fn load(path: &str, je: i128, jb: i128, tn: i128) -> Result<Op, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
    let mut it = text.split_ascii_whitespace().map(|s| s.parse::<i128>().map_err(|_| format!("bad token {s}")));
    let mut next = || it.next().ok_or_else(|| "truncated matrix".to_string())?;
    let n = usize::try_from(next()?).map_err(|_| "bad n")?;
    let w: Vec<i128> = (0..n).map(|_| next()).collect::<Result<_, _>>()?;
    let mag: Vec<i128> = (0..n).map(|_| next()).collect::<Result<_, _>>()?;
    if w.iter().any(|&v| v <= 0) {
        return Err("non-positive weight".into());
    }
    let mut diag: Vec<i128> = (0..n).map(|k| 1000 * jb * mag[k] * w[k] - tn * w[k]).collect();
    let mut adj: Vec<Vec<(u32, i128)>> = vec![Vec::new(); n];
    // HEB-C copy: triples are consumed as a stream (no token vector), so 2x5
    // sectors fit in runner memory; the entries and their order are unchanged.
    while let Ok(t0) = next() {
        let (t1, t2) = match (next(), next()) {
            (Ok(a), Ok(b)) => (a, b),
            _ => return Err("malformed triples".into()),
        };
        let (i, j) = (usize::try_from(t0).map_err(|_| "bad i")?, usize::try_from(t1).map_err(|_| "bad j")?);
        if i > j || j >= n {
            return Err("bad entry".into());
        }
        let v = 1000 * je * w[i] * t2;
        if i == j {
            diag[i] += v;
        } else if v != 0 {
            adj[i].push((u32::try_from(j).map_err(|_| "n too large")?, v));
            adj[j].push((u32::try_from(i).map_err(|_| "n too large")?, v));
        }
    }
    Ok(Op { n, mag, diag, adj })
}

fn dense_inertia(mut s: Vec<Vec<Iv>>) -> (usize, usize, usize, bool) {
    let m = s.len();
    let mut alive = vec![true; m];
    let (mut neg, mut pos) = (0usize, 0usize);
    for step in 0..m {
        // sign-definite pivot with the largest lower bound of |d|, scanning live rows
        let mut best: Option<(usize, BigInt)> = None;
        for k in 0..m {
            if !alive[k] {
                continue;
            }
            let d = &s[k][k];
            let mag = if d.0.is_positive() {
                d.0.clone()
            } else if d.1.is_negative() {
                -d.1.clone()
            } else {
                continue;
            };
            if best.as_ref().map_or(true, |(_, b)| mag > *b) {
                best = Some((k, mag));
            }
        }
        let Some((k, _)) = best else { return (neg, pos, step, false) };
        alive[k] = false;
        let d = s[k][k].clone();
        if d.1.is_negative() {
            neg += 1;
        } else {
            pos += 1;
        }
        let live: Vec<usize> = (0..m).filter(|&i| alive[i]).collect();
        for (x, &i) in live.iter().enumerate() {
            for &j in &live[x..] {
                let Ok(c) = quotient(&s[i][k], &s[k][j], &d) else { return (neg, pos, step, false) };
                let o = s[i][j].clone();
                let v: Iv = (o.0 - &c.1, o.1 - &c.0);
                s[i][j] = v.clone();
                s[j][i] = v;
            }
        }
    }
    (neg, pos, m, true)
}

fn run() -> Result<(), String> {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 5 {
        return Err("usage: shellschur MATRIX JE JB TN [SHELL_MAX=-1] [FDIG=9] [TOL=1000] [MAXSWEEP=400]".into());
    }
    let p = |k: usize, def: i128| a.get(k).and_then(|s| s.parse::<i128>().ok()).unwrap_or(def);
    let (je, jb, tn) = (p(2, 0), p(3, 0), p(4, 0));
    let shell_max = p(5, -1);
    let fdig = u32::try_from(p(6, 9)).map_err(|_| "bad FDIG")?;
    let tol = p(7, 1000);
    let maxsweep = usize::try_from(p(8, 400)).map_err(|_| "bad MAXSWEEP")?;
    let f: i128 = 10i128.pow(fdig);
    let t0 = Instant::now();
    let op = load(&a[1], je, jb, tn)?;
    let n = op.n;
    let full_off: Vec<i128> = op.adj.iter().map(|r| r.iter().map(|&(_, v)| v.abs()).sum()).collect();
    let core: Vec<bool> = (0..n).map(|k| op.diag[k] - full_off[k] <= 0 || op.mag[k] <= shell_max).collect();
    let cidx: Vec<usize> = (0..n).filter(|&k| core[k]).collect();
    let m = cidx.len();
    let mut cpos = vec![usize::MAX; n];
    for (q, &k) in cidx.iter().enumerate() {
        cpos[k] = q;
    }
    // dominance margins inside H (strict, positive) and contraction ratio
    let mut min_margin: Option<i128> = None;
    let mut worst_num = 0i128; // worst off_H/diag as a fraction num/den (per mille, ceil)
    for h in 0..n {
        if core[h] {
            continue;
        }
        let off_h: i128 = op.adj[h].iter().filter(|&&(j, _)| !core[j as usize]).map(|&(_, v)| v.abs()).sum();
        let mg = op.diag[h] - off_h;
        if mg <= 0 {
            return Err(format!("row {h} not dominant inside H"));
        }
        min_margin = Some(min_margin.map_or(mg, |x: i128| x.min(mg)));
        worst_num = worst_num.max(ceil_div(1000 * off_h, op.diag[h]));
    }
    let min_margin = min_margin.ok_or("H is empty")?;
    // Y columns by interval Gauss-Seidel; accumulate S*F enclosures
    let mut s_lo = vec![vec![0i128; m]; m];
    let mut s_hi = vec![vec![0i128; m]; m];
    let mut sweeps_max = 0usize;
    let mut width_max = 0i128;
    let mut lo = vec![0i128; n];
    let mut hi = vec![0i128; n];
    // GitRAM split: SHELLSCHUR_COLS=a:b computes only core columns a..b-1 and
    // prints them as SCOL lines; SHELLSCHUR_MERGE=f1,f2,... reads SCOL lines
    // (all columns, same matrix/coupling/threshold/core) instead of computing.
    let cols: Option<(usize, usize)> = std::env::var("SHELLSCHUR_COLS").ok().and_then(|v| {
        let (x, y) = v.split_once(':')?;
        Some((x.parse().ok()?, y.parse().ok()?))
    });
    let merge: Option<String> = std::env::var("SHELLSCHUR_MERGE").ok();
    // core fingerprint: a 64-bit polynomial digest of the ordered core indices, so
    // SCOL lines from a different core (same size) are rejected at merge time.
    // A consistency guard, not a cryptographic hash; matrix identity is checked
    // by SHA-256 at the backend level.
    let core_fp = cidx.iter().fold(0xcbf2_9ce4_8422_2325u64, |h, &k| (h ^ (k as u64)).wrapping_mul(0x0100_0000_01b3));
    let tag = format!("n={n}|JE={je}|JB={jb}|t_milli={tn}|shell_max={shell_max}|core={m}|core_fp={core_fp:016x}|F=10^{fdig}");
    if let Some(files) = &merge {
        // exactly one record for every (row, column) of the m x m core block
        let mut seen = vec![vec![false; m]; m];
        for path in files.split(',') {
            let text = std::fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
            for line in text.lines().filter(|l| l.starts_with("SCOL|")) {
                if !line.contains(&format!("|{tag}|")) {
                    return Err(format!("SCOL line from a different run in {path}"));
                }
                let fld = |k: &str| -> Result<i128, String> {
                    line.split('|').find_map(|kv| kv.strip_prefix(k)).and_then(|v| v.parse().ok()).ok_or_else(|| format!("missing {k}"))
                };
                let (cb, ca) = (usize::try_from(fld("cb=")?).map_err(|_| "cb")?, usize::try_from(fld("ca=")?).map_err(|_| "ca")?);
                if cb >= m || ca >= m {
                    return Err("SCOL index out of range".into());
                }
                s_lo[ca][cb] = fld("lo=")?;
                s_hi[ca][cb] = fld("hi=")?;
                if seen[ca][cb] {
                    return Err(format!("duplicate SCOL record ca={ca} cb={cb}"));
                }
                seen[ca][cb] = true;
                sweeps_max = sweeps_max.max(usize::try_from(fld("sweeps=")?).unwrap_or(0));
                width_max = width_max.max(fld("ywidth=")?);
            }
        }
        if seen.iter().any(|row| row.iter().any(|x| !x)) {
            return Err("merge is missing SCOL records (every core entry is required)".into());
        }
    }
    for (cb, &c) in cidx.iter().enumerate() {
        if merge.is_some() || cols.is_some_and(|(x, y)| cb < x || cb >= y) {
            continue;
        }
        // b = B_{H,c}
        let mut b = vec![0i128; 0];
        b.resize(n, 0);
        let mut bmax = 0i128;
        for &(h, v) in &op.adj[c] {
            if !core[h as usize] {
                b[h as usize] = v;
                bmax = bmax.max(v.abs());
            }
        }
        let beta = ceil_div(ck(bmax.checked_mul(f))?, min_margin);
        for h in 0..n {
            if core[h] {
                lo[h] = 0;
                hi[h] = 0;
            } else {
                lo[h] = -beta;
                hi[h] = beta;
            }
        }
        let mut sweeps = 0usize;
        let mut width = 2 * beta;
        while sweeps < maxsweep && width > tol {
            sweeps += 1;
            width = 0;
            for h in 0..n {
                if core[h] {
                    continue;
                }
                // y_h = (b_h*F - sum_{j in H} B_hj y_j) / B_hh
                let base = ck(b[h].checked_mul(f))?;
                let (mut nlo, mut nhi) = (base, base);
                for &(j, v) in &op.adj[h] {
                    let j = j as usize;
                    if core[j] {
                        continue;
                    }
                    let (pl, ph) = imul(lo[j], hi[j], -v)?;
                    nlo = ck(nlo.checked_add(pl))?;
                    nhi = ck(nhi.checked_add(ph))?;
                }
                let d = op.diag[h];
                let (ylo, yhi) = (floor_div(nlo, d).max(lo[h]), ceil_div(nhi, d).min(hi[h]));
                if ylo > yhi {
                    return Err("empty enclosure (arithmetic inconsistency)".into());
                }
                lo[h] = ylo;
                hi[h] = yhi;
                width = width.max(yhi - ylo);
            }
        }
        sweeps_max = sweeps_max.max(sweeps);
        width_max = width_max.max(width);
        // S_{a,c}*F = B_ac*F - sum_h B_ah * y_h      for every core a
        for (ca, &ar) in cidx.iter().enumerate() {
            let mut bac = if ar == c { op.diag[c] } else { 0 };
            let (mut acc_lo, mut acc_hi) = (0i128, 0i128);
            for &(h, v) in &op.adj[ar] {
                let h = h as usize;
                if core[h] {
                    if h == c {
                        bac = v;
                    }
                    continue;
                }
                let (pl, ph) = imul(lo[h], hi[h], v)?;
                acc_lo = ck(acc_lo.checked_add(pl))?;
                acc_hi = ck(acc_hi.checked_add(ph))?;
            }
            let bf = ck(bac.checked_mul(f))?;
            s_lo[ca][cb] = bf - acc_hi;
            s_hi[ca][cb] = bf - acc_lo;
            if cols.is_some() {
                println!("SCOL|{tag}|cb={cb}|ca={ca}|lo={}|hi={}|sweeps={sweeps}|ywidth={width}|json=0", s_lo[ca][cb], s_hi[ca][cb]);
            }
        }
    }
    if let Some((x, y)) = cols {
        println!("SHELL_SCHUR_COLS|{tag}|cols={x}:{}|gs_sweeps_max={sweeps_max}|y_width_max={width_max}|ms={}|json=0", y.min(m), t0.elapsed().as_millis());
        return Ok(());
    }
    // symmetrize by intersecting the two valid enclosures
    let mut s: Vec<Vec<Iv>> = vec![vec![(BigInt::zero(), BigInt::zero()); m]; m];
    for i in 0..m {
        for j in 0..m {
            let l = s_lo[i][j].max(s_lo[j][i]);
            let h = s_hi[i][j].min(s_hi[j][i]);
            if l > h {
                return Err("S enclosures disjoint (inconsistency)".into());
            }
            s[i][j] = (BigInt::from(l), BigInt::from(h));
        }
    }
    let (neg, pos, steps, ok) = dense_inertia(s);
    let name = a[1].rsplit('/').next().unwrap_or("");
    let core_edges: usize = cidx.iter().map(|&k| op.adj[k].iter().filter(|&&(j, _)| core[j as usize]).count()).sum::<usize>() / 2;
    println!(
        "SHELL_SCHUR|matrix={name}|n={n}|JE={je}|JB={jb}|t_milli={tn}|shell_max={shell_max}|core={m}|core_edges={core_edges}|H={}|H_min_margin={min_margin}|H_max_offdiag_over_diag_permille_ceil={worst_num}|F=10^{fdig}|gs_sweeps_max={sweeps_max}|y_width_max={width_max}|negative={neg}|positive_core={pos}|positive_H={}|eliminated={steps}|ambiguous={}|result={}|ms={}|json=0",
        n - m,
        n - m,
        if ok { 0 } else { m - steps },
        if ok { "PASS" } else { "AMBIGUOUS" },
        t0.elapsed().as_millis()
    );
    if !ok {
        std::process::exit(2);
    }
    Ok(())
}

fn main() {
    if let Err(e) = run() {
        println!("SHELL_SCHUR|result=FAIL|reason={e}|json=0");
        std::process::exit(1);
    }
}
