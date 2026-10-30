//! zlevel: is j instant per level while r travels? Integer only, json=0. See PREREG.md.

fn pow3(k: usize) -> usize {
    3usize.pow(k as u32)
}

/// Digit k of x in base 3.
fn digit(x: usize, k: usize) -> usize {
    (x / pow3(k)) % 3
}

/// x with digit k rotated by d (cyclic, no carry).
fn rot(x: usize, k: usize, d: usize) -> usize {
    x - digit(x, k) * pow3(k) + ((digit(x, k) + d) % 3) * pow3(k)
}

fn high_digit(a: usize, b: usize, n: usize) -> usize {
    (0..n).rev().find(|&k| digit(a, k) != digit(b, k)).unwrap()
}

/// One application of an operator given by its neighbour list, on a 0/1 support.
fn apply(v: &[bool], nb: impl Fn(usize) -> Vec<usize>) -> Vec<bool> {
    let mut w = vec![false; v.len()];
    for (x, &on) in v.iter().enumerate() {
        if on {
            for y in nb(x) {
                w[y] = true;
            }
        }
    }
    w
}

/// Reach time from a to every cell under a step sequence; 0 for a itself, -1 if never.
fn reach(m: usize, a: usize, steps: usize, step: impl Fn(&[bool], usize) -> Vec<bool>) -> Vec<i64> {
    let mut t = vec![-1i64; m];
    let mut v = vec![false; m];
    v[a] = true;
    t[a] = 0;
    for s in 1..=steps {
        v = step(&v, s);
        for (x, &on) in v.iter().enumerate() {
            if on && t[x] < 0 {
                t[x] = s as i64;
            }
        }
    }
    t
}

fn main() {
    let mut all = true;
    for n in [3usize, 4, 5] {
        let m = pow3(n);
        let jk = |x: usize, k: usize| vec![x, rot(x, k, 1), rot(x, k, 2)];
        // P1: product J_0 J_1 ... J_(n-1), exact integer entries
        let mut p = vec![0u64; m * m];
        for i in 0..m {
            p[i * m + i] = 1;
        }
        for k in 0..n {
            let mut q = vec![0u64; m * m];
            for i in 0..m {
                for j in 0..m {
                    let e = p[i * m + j];
                    if e != 0 {
                        for y in jk(j, k) {
                            q[i * m + y] += e;
                        }
                    }
                }
            }
            p = q;
        }
        let p1 = p.iter().all(|&e| e == 1);
        // P2, P3, P4, P5, P6 over every ordered pair
        let (mut p2, mut p3, mut p4) = (true, true, true);
        let (mut zmax, mut rmax) = (0i64, 0i64);
        let (mut sib1, mut sib2, mut sib_other) = (0u64, 0u64, 0u64);
        let mut kmax = vec![0i64; n];
        let mut kmin = vec![i64::MAX; n];
        let (mut z_slower, mut z_faster, mut z_slower_h0) = (0u64, 0u64, 0u64);
        for a in 0..m {
            let ring = reach(m, a, (m - 1) / 2, |v, _| apply(v, |x| vec![x, (x + 1) % m, (x + m - 1) % m]));
            let z = reach(m, a, n, |v, s| apply(v, |x| jk(x, s - 1)));
            let tri = reach(m, a, 1, |v, _| apply(v, |x| vec![x, rot(x, 0, 1), rot(x, 0, 2)]));
            for b in 0..m {
                if b == a {
                    continue;
                }
                let h = high_digit(a, b, n);
                let d = a.abs_diff(b);
                let ringd = d.min(m - d) as i64;
                p2 &= z[b] == h as i64 + 1;
                p3 &= ring[b] == ringd;
                zmax = zmax.max(z[b]);
                rmax = rmax.max(ring[b]);
                kmax[h] = kmax[h].max(ring[b]);
                kmin[h] = kmin[h].min(ring[b]);
                if h == 0 {
                    p4 &= tri[b] == 1 && z[b] == 1;
                    match ring[b] {
                        1 => sib1 += 1,
                        2 => sib2 += 1,
                        _ => sib_other += 1,
                    }
                }
                match z[b].cmp(&ring[b]) {
                    std::cmp::Ordering::Greater => {
                        z_slower += 1;
                        if h == 0 {
                            z_slower_h0 += 1;
                        }
                    }
                    std::cmp::Ordering::Less => z_faster += 1,
                    std::cmp::Ordering::Equal => {}
                }
            }
        }
        p2 &= zmax == n as i64;
        p3 &= rmax == ((m - 1) / 2) as i64;
        let mm = m as u64;
        p4 &= sib1 == 4 * mm / 3 && sib2 == 2 * mm / 3 && sib_other == 0;
        let mut p5 = true;
        for k in 0..n {
            let want = if k + 1 < n { pow3(k + 1) - 1 } else { (m - 1) / 2 } as i64;
            p5 &= kmax[k] == want && kmin[k] == 1;
            println!("ZLEVEL_LEVEL|N={n}|h={k}|z_time={}|ring_r_min={}|ring_r_max={}|predicted_max={want}|json=0", k + 1, kmin[k], kmax[k]);
        }
        let p6 = z_slower > 0 && z_slower_h0 == 0 && z_faster > 0;
        println!("ZLEVEL_PAIRS|N={n}|M={m}|ordered_pairs={}|z_max={zmax}|ring_r_max={rmax}|siblings_ring1={sib1}|siblings_ring2={sib2}|z_slower_than_r={z_slower}|z_faster_than_r={z_faster}|equal={}|json=0",
            m * (m - 1), (m * (m - 1)) as u64 - z_slower - z_faster);
        let v = |b: bool| if b { "PASS" } else { "FAIL" };
        println!("ZLEVEL_RESULT|N={n}|P1={}|P2={}|P3={}|P4={}|P5={}|P6={}|json=0", v(p1), v(p2), v(p3), v(p4), v(p5), v(p6));
        all &= p1 && p2 && p3 && p4 && p5 && p6;
    }
    println!("ZLEVEL_OVERALL|{}|json=0", if all { "PASS" } else { "FAIL" });
}
