//! Diagonal-dominance core of B = W(1000(JE*E + JB*M) - t*W): the rows that a
//! Gershgorin test cannot certify positive at threshold t (milli-units).
//! Rows outside the core satisfy B_ii - sum_{j!=i} |B_ij| > 0. Reports the core
//! size, its induced nonzeros and its magnetic-shell histogram: the size of the
//! block a magnetic-shell Schur decomposition would have to factor exactly.
//! Integer-only (i128). usage: ddcore MATRIX JE JB TN        json=0
#![deny(clippy::float_arithmetic)]
use std::collections::BTreeMap;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 5 {
        eprintln!("usage: ddcore MATRIX JE JB TN");
        std::process::exit(1);
    }
    let p = |s: &str| s.parse::<i128>().unwrap_or(0);
    let (je, jb, tn) = (p(&a[2]), p(&a[3]), p(&a[4]));
    let text = std::fs::read_to_string(&a[1]).unwrap_or_default();
    let mut it = text.split_ascii_whitespace().map(|s| s.parse::<i128>().unwrap_or(0));
    let n = usize::try_from(it.next().unwrap_or(0)).unwrap_or(0);
    let w: Vec<i128> = (0..n).map(|_| it.next().unwrap_or(0)).collect();
    let mag: Vec<i128> = (0..n).map(|_| it.next().unwrap_or(0)).collect();
    let mut diag: Vec<i128> = (0..n).map(|k| 1000 * jb * mag[k] * w[k] - tn * w[k]).collect();
    let mut off = vec![0i128; n];
    let mut edges: Vec<(u32, u32)> = Vec::new();
    while let (Some(i), Some(j), Some(z)) = (it.next(), it.next(), it.next()) {
        let (i, j) = (usize::try_from(i).unwrap_or(0), usize::try_from(j).unwrap_or(0));
        let v = 1000 * je * w[i] * z;
        if i == j {
            diag[i] += v;
        } else if v != 0 {
            off[i] += v.abs();
            off[j] += v.abs();
            edges.push((u32::try_from(i).unwrap_or(0), u32::try_from(j).unwrap_or(0)));
        }
    }
    let core: Vec<bool> = (0..n).map(|k| diag[k] - off[k] <= 0).collect();
    let csize = core.iter().filter(|&&c| c).count();
    let cedges = edges.iter().filter(|&&(i, j)| core[i as usize] && core[j as usize]).count();
    let negdiag = (0..n).filter(|&k| diag[k] <= 0).count();
    // per shell: worst off/diag ratio over dominant rows, in ceil per-mille
    let mut ratio: BTreeMap<i128, i128> = BTreeMap::new();
    for k in 0..n {
        if !core[k] {
            let r = (1000 * off[k] + diag[k] - 1) / diag[k];
            let e = ratio.entry(mag[k]).or_insert(0);
            *e = (*e).max(r);
        }
    }
    let rs: Vec<String> = ratio.iter().map(|(m, r)| format!("{m}:{r}")).collect();
    let mut hist: BTreeMap<i128, (usize, usize)> = BTreeMap::new();
    for k in 0..n {
        let e = hist.entry(mag[k]).or_insert((0, 0));
        e.0 += 1;
        if core[k] {
            e.1 += 1;
        }
    }
    let h: Vec<String> = hist.iter().map(|(m, (t, c))| format!("{m}:{c}/{t}")).collect();
    let name = a[1].rsplit('/').next().unwrap_or("");
    println!("DDCORE|matrix={name}|n={n}|JE={je}|JB={jb}|t_milli={tn}|nonpositive_diagonal={negdiag}|core_rows={csize}|core_offdiag_edges={cedges}|shell_core/total={}|shell_max_offdiag_over_diag_permille_ceil={}|json=0", h.join(","), rs.join(","));
}
