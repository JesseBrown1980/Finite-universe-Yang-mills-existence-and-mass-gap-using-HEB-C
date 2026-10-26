//! Symbolic fill of the LDL^T factor under different elimination orderings,
//! measured BEFORE any exact (interval) arithmetic is attempted.
//!
//! Reads a matrix in the exchange format (only its sparsity pattern is used;
//! the pattern is symmetric because the operator is W-self-adjoint) and, for
//! each ordering, reports
//!   bandwidth, envelope (profile) size,
//!   nnz(L) from exact symbolic Cholesky (elimination tree with structure
//!   unions: struct(L_j) = adj(j)_{>j}  U  (union over children c of
//!   struct(L_c) minus j)), stopping with "> CAP" once the running total
//!   exceeds the cap.
//! Orderings: natural (as stored) and reverse Cuthill-McKee (BFS from a
//! pseudo-peripheral start, neighbours by increasing degree, reversed).
//! Integer-only, Rust 1.81.
//! usage: fillest MATRIX [CAP=300000000]      json=0
#![deny(clippy::float_arithmetic)]

use std::collections::VecDeque;

fn load_pattern(path: &str) -> Result<Vec<Vec<u32>>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("read {path}: {e}"))?;
    let mut it = text.split_ascii_whitespace();
    let n: usize = it.next().ok_or("empty")?.parse().map_err(|_| "bad n")?;
    for _ in 0..2 * n {
        it.next().ok_or("truncated")?;
    }
    let mut adj: Vec<Vec<u32>> = vec![Vec::new(); n];
    loop {
        let (Some(a), Some(b), Some(_z)) = (it.next(), it.next(), it.next()) else { break };
        let i: usize = a.parse().map_err(|_| "bad i")?;
        let j: usize = b.parse().map_err(|_| "bad j")?;
        if i != j && i < n && j < n {
            adj[i].push(u32::try_from(j).unwrap_or(0));
            adj[j].push(u32::try_from(i).unwrap_or(0));
        }
    }
    for a in adj.iter_mut() {
        a.sort_unstable();
        a.dedup();
    }
    Ok(adj)
}

fn bfs_levels(adj: &[Vec<u32>], start: usize) -> (Vec<usize>, usize) {
    let n = adj.len();
    let mut dist = vec![usize::MAX; n];
    let mut q = VecDeque::from([start]);
    dist[start] = 0;
    let mut last = start;
    while let Some(v) = q.pop_front() {
        last = v;
        for &w in &adj[v] {
            let w = w as usize;
            if dist[w] == usize::MAX {
                dist[w] = dist[v] + 1;
                q.push_back(w);
            }
        }
    }
    (dist, last)
}

fn rcm(adj: &[Vec<u32>]) -> Vec<usize> {
    let n = adj.len();
    let mut order = Vec::with_capacity(n);
    let mut seen = vec![false; n];
    let deg = |v: usize| adj[v].len();
    let mut starts: Vec<usize> = (0..n).collect();
    starts.sort_by_key(|&v| deg(v));
    for &s0 in &starts {
        if seen[s0] {
            continue;
        }
        // pseudo-peripheral start: two BFS sweeps
        let (_, far) = bfs_levels(adj, s0);
        let (_, s) = bfs_levels(adj, far);
        let s = if seen[s] { s0 } else { s };
        let mut q = VecDeque::from([s]);
        seen[s] = true;
        while let Some(v) = q.pop_front() {
            order.push(v);
            let mut nb: Vec<usize> = adj[v].iter().map(|&w| w as usize).filter(|&w| !seen[w]).collect();
            nb.sort_by_key(|&w| deg(w));
            for w in nb {
                if !seen[w] {
                    seen[w] = true;
                    q.push_back(w);
                }
            }
        }
    }
    order.reverse();
    order
}

/// (bandwidth, envelope, nnz(L) or None if > cap)
fn analyse(adj: &[Vec<u32>], order: &[usize], cap: u64) -> (usize, u64, Option<u64>) {
    let n = adj.len();
    let mut pos = vec![0usize; n];
    for (k, &v) in order.iter().enumerate() {
        pos[v] = k;
    }
    let mut band = 0usize;
    let mut env = 0u64;
    for (k, &v) in order.iter().enumerate() {
        let mut first = k;
        for &w in &adj[v] {
            let pw = pos[w as usize];
            band = band.max(pw.abs_diff(k));
            first = first.min(pw);
        }
        env += (k - first) as u64;
    }
    // symbolic Cholesky with structure unions along the elimination tree
    let mut pending: Vec<Vec<u32>> = vec![Vec::new(); n]; // merged child structures waiting at their parent
    let mut total = 0u64;
    for k in 0..n {
        let v = order[k];
        let mut s: Vec<u32> = adj[v].iter().map(|&w| u32::try_from(pos[w as usize]).unwrap_or(0)).filter(|&p| p as usize > k).collect();
        let ch = std::mem::take(&mut pending[k]);
        s.extend(ch.into_iter().filter(|&p| p as usize > k));
        s.sort_unstable();
        s.dedup();
        total += s.len() as u64;
        if total > cap {
            return (band, env, None);
        }
        if let Some(&parent) = s.first() {
            let p = parent as usize;
            let mut merged = std::mem::take(&mut pending[p]);
            merged.extend(s.iter().copied());
            merged.sort_unstable();
            merged.dedup();
            pending[p] = merged;
        }
    }
    (band, env, Some(total))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 2 {
        eprintln!("usage: fillest MATRIX [CAP]");
        std::process::exit(1);
    }
    let cap: u64 = a.get(2).and_then(|s| s.parse().ok()).unwrap_or(300_000_000);
    let t0 = std::time::Instant::now();
    let adj = match load_pattern(&a[1]) {
        Ok(x) => x,
        Err(e) => {
            println!("FILLEST|error={e}|json=0");
            std::process::exit(1);
        }
    };
    let n = adj.len();
    let nnz_a: u64 = adj.iter().map(|r| r.len() as u64).sum::<u64>() / 2;
    let name = a[1].rsplit('/').next().unwrap_or("");
    let natural: Vec<usize> = (0..n).collect();
    let rc = rcm(&adj);
    for (label, ord) in [("natural", &natural), ("rcm", &rc)] {
        let (band, env, l) = analyse(&adj, ord, cap);
        println!(
            "FILLEST|matrix={name}|n={n}|nnz_A_offdiag_upper={nnz_a}|ordering={label}|bandwidth={band}|envelope={env}|nnz_L={}|cap={cap}|ms={}|json=0",
            l.map_or(format!(">{cap}"), |x| x.to_string()),
            t0.elapsed().as_millis()
        );
    }
}
