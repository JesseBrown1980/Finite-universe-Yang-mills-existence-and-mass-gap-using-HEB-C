// The real electric matrix on a torus with few free links, by my own gauge fixing. Integer only, json=0.
// P(E) = 0 is checked on one basis vector per translation orbit, since T commutes with E and T P(E) e_b = P(E) e_{T b}.
// Prefix traces use the same symmetry: (q(E))_{bb} is the same along a translation orbit.
use std::collections::{BTreeMap, HashMap};
use std::env;
use std::sync::atomic::{AtomicUsize, Ordering};

fn compose(a: [u8; 3], b: [u8; 3]) -> [u8; 3] {
    [a[b[0] as usize], a[b[1] as usize], a[b[2] as usize]]
}

fn main() {
    let a: Vec<String> = env::args().collect();
    let lx: usize = a[1].parse().unwrap();
    let ly: usize = a[2].parse().unwrap();
    let roots: Vec<i128> = a[3].split(',').map(|x| x.parse().unwrap()).collect();
    let threads: usize = a[4].parse().unwrap();

    // S3 by closure.
    let gens = [[1u8, 0, 2], [1u8, 2, 0]];
    let mut el = vec![[0u8, 1, 2]];
    let mut k = 0;
    while k < el.len() {
        for g in gens.iter() {
            let n = compose(*g, el[k]);
            if !el.contains(&n) {
                el.push(n);
            }
        }
        k += 1;
    }
    assert_eq!(el.len(), 6);
    let idx = |p: [u8; 3]| el.iter().position(|q| *q == p).unwrap();
    let mul: Vec<Vec<usize>> = (0..6)
        .map(|x| (0..6).map(|y| idx(compose(el[x], el[y]))).collect())
        .collect();
    let inv: Vec<usize> = (0..6).map(|x| (0..6).find(|y| mul[x][*y] == 0).unwrap()).collect();
    let fixed = |x: usize| (0..3).filter(|i| el[x][*i] as usize == *i).count();
    let trans: Vec<usize> = (0..6).filter(|x| fixed(*x) == 1).collect();

    // Torus: sites v = x + Lx*y, links 2v (+x), 2v+1 (+y).
    let nv = lx * ly;
    let nl = 2 * nv;
    let mut src = vec![0; nl];
    let mut dst = vec![0; nl];
    for y in 0..ly {
        for x in 0..lx {
            let v = x + lx * y;
            src[2 * v] = v;
            dst[2 * v] = (x + 1) % lx + lx * y;
            src[2 * v + 1] = v;
            dst[2 * v + 1] = x + lx * ((y + 1) % ly);
        }
    }
    // Spanning tree by a walk from site 0, skipping self loops.
    let mut seen = vec![false; nv];
    seen[0] = true;
    let mut tree: Vec<usize> = Vec::new();
    let mut order: Vec<usize> = vec![0];
    let mut head = 0;
    while head < order.len() {
        let u = order[head];
        head += 1;
        for l in 0..nl {
            if src[l] == u && !seen[dst[l]] {
                seen[dst[l]] = true;
                tree.push(l);
                order.push(dst[l]);
            } else if dst[l] == u && !seen[src[l]] {
                seen[src[l]] = true;
                tree.push(l);
                order.push(src[l]);
            }
        }
    }
    assert!(seen.iter().all(|s| *s));
    assert_eq!(tree.len(), nv - 1);
    let free: Vec<usize> = (0..nl).filter(|l| !tree.contains(l)).collect();
    let f = free.len();
    assert_eq!(f, nl - nv + 1);

    let code_of = |q: &[usize]| -> usize {
        let mut c = 0usize;
        for &x in q.iter().rev() {
            c = c * 6 + x;
        }
        c
    };
    let canonical = |q: &[usize]| -> usize {
        let mut best = usize::MAX;
        for g in 0..6 {
            let conj: Vec<usize> = q.iter().map(|&x| mul[mul[g][x]][inv[g]]).collect();
            let c = code_of(&conj);
            if c < best {
                best = c;
            }
        }
        best
    };
    // Gauge fix: frames from the tree walk, then the free tuple.
    let fix = |u: &[usize]| -> Vec<usize> {
        let mut frame: Vec<Option<usize>> = vec![None; nv];
        frame[0] = Some(0);
        for _ in 0..nv {
            for &l in &tree {
                match (frame[src[l]], frame[dst[l]]) {
                    (Some(fa), None) => frame[dst[l]] = Some(mul[fa][u[l]]),
                    (None, Some(fb)) => frame[src[l]] = Some(mul[fb][inv[u[l]]]),
                    _ => {}
                }
            }
        }
        free.iter()
            .map(|&l| mul[mul[frame[src[l]].unwrap()][u[l]]][inv[frame[dst[l]].unwrap()]])
            .collect()
    };

    // Orbits of simultaneous conjugation on the 6^f free tuples.
    let total = 6usize.pow(f as u32);
    let mut weights_by_code: BTreeMap<usize, u64> = BTreeMap::new();
    let mut q = vec![0usize; f];
    for code in 0..total {
        let mut c = code;
        for x in q.iter_mut() {
            *x = c % 6;
            c /= 6;
        }
        *weights_by_code.entry(canonical(&q)).or_insert(0) += 1;
    }
    let keys: Vec<usize> = weights_by_code.keys().cloned().collect();
    let w: Vec<u64> = weights_by_code.values().cloned().collect();
    let n = keys.len();
    let pos: HashMap<usize, usize> = keys.iter().enumerate().map(|(i, k)| (*k, i)).collect();
    let burnside = (6u128.pow(f as u32) + 3 * 2u128.pow(f as u32) + 2 * 3u128.pow(f as u32)) / 6;
    let rep_config = |key: usize| -> Vec<usize> {
        let mut u = vec![0usize; nl];
        let mut c = key;
        for &l in &free {
            u[l] = c % 6;
            c /= 6;
        }
        u
    };
    let mut rows: Vec<BTreeMap<u32, i64>> = vec![BTreeMap::new(); n];
    for i in 0..n {
        let u = rep_config(keys[i]);
        *rows[i].entry(i as u32).or_insert(0) += 3 * nl as i64;
        for l in 0..nl {
            for &t in &trans {
                let mut e = u.clone();
                e[l] = mul[t][u[l]];
                let j = pos[&canonical(&fix(&e))];
                *rows[i].entry(j as u32).or_insert(0) -= 1;
            }
        }
        rows[i].retain(|_, v| *v != 0);
    }
    let nnz: usize = rows.iter().map(|r| r.len()).sum();
    let mut bal = 0u64;
    for i in 0..n {
        for (&j, &v) in rows[i].iter() {
            if (w[i] as i64) * v != (w[j as usize] as i64) * *rows[j as usize].get(&(i as u32)).unwrap_or(&0) {
                bal += 1;
            }
        }
    }
    let zero_sum = rows.iter().filter(|r| r.values().sum::<i64>() == 0).count();
    println!(
        "OWN_REAL_BUILD|L={}x{}|links={}|free={}|dim={}|burnside={}|nnz={}|zero_sum_rows={}|balance_failures={}|weight_sum={}|json=0",
        lx, ly, nl, f, n, burnside, nnz, zero_sum, bal, w.iter().sum::<u64>()
    );

    // Translations.
    let translate = |i: usize, dx: usize, dy: usize| -> usize {
        let u = rep_config(keys[i]);
        let mut e = u.clone();
        for y in 0..ly {
            for x in 0..lx {
                let v = x + lx * y;
                let t = (x + dx) % lx + lx * ((y + dy) % ly);
                e[2 * v] = u[2 * t];
                e[2 * v + 1] = u[2 * t + 1];
            }
        }
        pos[&canonical(&fix(&e))]
    };
    let tx: Vec<usize> = (0..n).map(|i| translate(i, 1, 0)).collect();
    let ty: Vec<usize> = (0..n).map(|i| translate(i, 0, 1)).collect();
    let mut commute_bad = 0u64;
    for i in 0..n {
        for (&j, &v) in rows[i].iter() {
            if *rows[tx[i]].get(&(tx[j as usize] as u32)).unwrap_or(&0) != v
                || *rows[ty[i]].get(&(ty[j as usize] as u32)).unwrap_or(&0) != v
            {
                commute_bad += 1;
            }
        }
    }
    let mut seen_orbit = vec![false; n];
    let mut reps: Vec<(usize, u64)> = Vec::new();
    for i in 0..n {
        if seen_orbit[i] {
            continue;
        }
        let mut stack = vec![i];
        seen_orbit[i] = true;
        let mut size = 0u64;
        while let Some(x) = stack.pop() {
            size += 1;
            for y in [tx[x], ty[x]] {
                if !seen_orbit[y] {
                    seen_orbit[y] = true;
                    stack.push(y);
                }
            }
        }
        reps.push((i, size));
    }
    println!(
        "OWN_REAL_TRANSLATION|commute_failures={}|translation_orbits={}|size_sum={}|json=0",
        commute_bad,
        reps.len(),
        reps.iter().map(|r| r.1).sum::<u64>()
    );

    // CSR.
    let mut start = vec![0usize; n + 1];
    let mut col: Vec<u32> = Vec::with_capacity(nnz);
    let mut val: Vec<i64> = Vec::with_capacity(nnz);
    for i in 0..n {
        for (&j, &v) in rows[i].iter() {
            col.push(j);
            val.push(v);
        }
        start[i + 1] = col.len();
    }
    let next = AtomicUsize::new(0);
    let mut results: Vec<(Vec<i128>, u64, i128)> = Vec::new();
    std::thread::scope(|s| {
        let mut handles = Vec::new();
        for _ in 0..threads {
            let (start, col, val, reps, roots, next) = (&start, &col, &val, &reps, &roots, &next);
            handles.push(s.spawn(move || {
                let mut traces = vec![0i128; roots.len() + 1];
                let mut nonzero = 0u64;
                let mut max_abs = 0i128;
                let mut v = vec![0i128; n];
                let mut w_vec = vec![0i128; n];
                loop {
                    let k = next.fetch_add(1, Ordering::Relaxed);
                    if k >= reps.len() {
                        break;
                    }
                    let (b, size) = reps[k];
                    for x in v.iter_mut() {
                        *x = 0;
                    }
                    v[b] = 1;
                    traces[0] += size as i128;
                    for (r, &c) in roots.iter().enumerate() {
                        for i in 0..n {
                            let mut acc = 0i128;
                            for p in start[i]..start[i + 1] {
                                acc = acc
                                    .checked_add((val[p] as i128).checked_mul(v[col[p] as usize]).unwrap())
                                    .unwrap();
                            }
                            acc = acc.checked_sub(c.checked_mul(v[i]).unwrap()).unwrap();
                            w_vec[i] = acc;
                            if acc > max_abs {
                                max_abs = acc;
                            } else if -acc > max_abs {
                                max_abs = -acc;
                            }
                        }
                        std::mem::swap(&mut v, &mut w_vec);
                        traces[r + 1] = traces[r + 1].checked_add((size as i128).checked_mul(v[b]).unwrap()).unwrap();
                    }
                    if v.iter().any(|x| *x != 0) {
                        nonzero += 1;
                    }
                }
                (traces, nonzero, max_abs)
            }));
        }
        for h in handles {
            results.push(h.join().unwrap());
        }
    });
    let mut traces = vec![0i128; roots.len() + 1];
    let mut nonzero = 0u64;
    let mut max_abs = 0i128;
    for (t, nz, m) in results {
        for i in 0..traces.len() {
            traces[i] = traces[i].checked_add(t[i]).unwrap();
        }
        nonzero += nz;
        if m > max_abs {
            max_abs = m;
        }
    }
    println!(
        "OWN_REAL_ANNIHILATE|L={}x{}|roots={}|vectors_checked={}|one_per_translation_orbit=1|columns_nonzero={}|largest_abs_entry={}|prefix_traces={}|json=0",
        lx,
        ly,
        a[3],
        reps.len(),
        nonzero,
        max_abs,
        traces.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")
    );
}
