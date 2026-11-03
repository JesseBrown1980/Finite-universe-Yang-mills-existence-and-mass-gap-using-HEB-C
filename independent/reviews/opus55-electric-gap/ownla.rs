// Second seat's own build of E on the periodic 2x2 S3 torus and its own modular linear algebra.
// Integer only. Nothing here reads the builder's code. json=0.
use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::io::Write;

// ---------------------------------------------------------------- S3 from two generators, by closure
struct Grp {
    el: Vec<[u8; 3]>,
    mul: Vec<Vec<u8>>,
    inv: Vec<u8>,
    trans: Vec<u8>,
    three: Vec<u8>,
}

fn compose(a: [u8; 3], b: [u8; 3]) -> [u8; 3] {
    [a[b[0] as usize], a[b[1] as usize], a[b[2] as usize]]
}

fn make_group() -> Grp {
    let id = [0u8, 1, 2];
    let gens = [[1u8, 0, 2], [1u8, 2, 0]];
    let mut el = vec![id];
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
    let idx = |p: [u8; 3]| el.iter().position(|q| *q == p).unwrap() as u8;
    let mul: Vec<Vec<u8>> = (0..6)
        .map(|a| (0..6).map(|b| idx(compose(el[a], el[b]))).collect())
        .collect();
    let inv: Vec<u8> = (0..6)
        .map(|a| (0..6u8).find(|b| mul[a][*b as usize] == 0).unwrap())
        .collect();
    let fixed = |p: [u8; 3]| (0..3).filter(|i| p[*i] as usize == *i).count();
    let trans: Vec<u8> = (0..6u8).filter(|a| fixed(el[*a as usize]) == 1).collect();
    let three: Vec<u8> = (0..6u8).filter(|a| fixed(el[*a as usize]) == 0).collect();
    assert_eq!(trans.len(), 3);
    assert_eq!(three.len(), 2);
    Grp { el, mul, inv, trans, three }
}

// ---------------------------------------------------------------- the torus, sites v = x + Lx*y
struct Tor {
    lx: usize,
    ly: usize,
    nl: usize,
    nv: usize,
    src: Vec<usize>,
    dst: Vec<usize>,
}

fn make_torus(lx: usize, ly: usize) -> Tor {
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
    Tor { lx, ly, nl, nv, src, dst }
}

fn digits(code: u32, nl: usize) -> Vec<u8> {
    let mut d = vec![0u8; nl];
    let mut c = code;
    for x in d.iter_mut() {
        *x = (c % 6) as u8;
        c /= 6;
    }
    d
}

fn encode(d: &[u8]) -> u32 {
    let mut c = 0u32;
    for k in (0..d.len()).rev() {
        c = c * 6 + d[k] as u32;
    }
    c
}

fn build(out: &str, lx: usize, ly: usize) {
    let g = make_group();
    let t = make_torus(lx, ly);
    let nl = t.nl;
    let total = 6u32.pow(nl as u32) as usize;
    // Orbits of G^V on G^links, depth first with the two generators at each vertex.
    let gens = [g.trans[0], g.three[0]];
    let mut orbit = vec![u32::MAX; total];
    let mut reps: Vec<u32> = Vec::new();
    let mut sizes: Vec<u64> = Vec::new();
    let mut stack: Vec<u32> = Vec::new();
    for start in 0..total as u32 {
        if orbit[start as usize] != u32::MAX {
            continue;
        }
        let id = reps.len() as u32;
        reps.push(start);
        orbit[start as usize] = id;
        stack.push(start);
        let mut size = 1u64;
        while let Some(c) = stack.pop() {
            let d = digits(c, nl);
            for v in 0..t.nv {
                for &h in gens.iter() {
                    let mut e = d.clone();
                    for l in 0..nl {
                        if t.src[l] == v {
                            e[l] = g.mul[h as usize][e[l] as usize];
                        }
                        if t.dst[l] == v {
                            e[l] = g.mul[e[l] as usize][g.inv[h as usize] as usize];
                        }
                    }
                    let n = encode(&e);
                    if orbit[n as usize] == u32::MAX {
                        orbit[n as usize] = id;
                        size += 1;
                        stack.push(n);
                    }
                }
            }
        }
        sizes.push(size);
    }
    let n = reps.len();
    let size_sum: u64 = sizes.iter().sum();
    let mut seen = sizes.clone();
    seen.sort();
    seen.dedup();
    println!(
        "OWN_ORBITS|configs={}|orbits={}|size_sum={}|sizes_seen={:?}|json=0",
        total, n, size_sum, seen
    );
    let w: Vec<u64> = sizes
        .iter()
        .map(|s| {
            let unit = 6u64.pow(t.nv as u32 - 1);
            assert_eq!(s % unit, 0);
            s / unit
        })
        .collect();
    // E in orbit-function form: (E f)(i) = 24 f(i) - sum_{link,t} f(orbit of t on link applied to the rep of i).
    let mut rows: Vec<BTreeMap<u32, i64>> = vec![BTreeMap::new(); n];
    let mut right: Vec<BTreeMap<u32, i64>> = vec![BTreeMap::new(); n];
    for i in 0..n {
        let d = digits(reps[i], nl);
        *rows[i].entry(i as u32).or_insert(0) += 3 * nl as i64;
        *right[i].entry(i as u32).or_insert(0) += 3 * nl as i64;
        for l in 0..nl {
            for &tt in g.trans.iter() {
                let mut e = d.clone();
                e[l] = g.mul[tt as usize][d[l] as usize];
                *rows[i].entry(orbit[encode(&e) as usize]).or_insert(0) -= 1;
                let mut f = d.clone();
                f[l] = g.mul[d[l] as usize][tt as usize];
                *right[i].entry(orbit[encode(&f) as usize]).or_insert(0) -= 1;
            }
        }
        rows[i].retain(|_, v| *v != 0);
        right[i].retain(|_, v| *v != 0);
    }
    let same_right = rows.iter().zip(right.iter()).filter(|(a, b)| a == b).count();
    println!("OWN_LEFT_RIGHT|rows_equal={}/{}|json=0", same_right, n);
    // The operator is well defined on orbits: every member of an orbit has the same target counts as its rep.
    let mut bad = 0u64;
    for c in 0..total as u32 {
        let i = orbit[c as usize] as usize;
        let d = digits(c, nl);
        let mut row: BTreeMap<u32, i64> = BTreeMap::new();
        *row.entry(i as u32).or_insert(0) += 3 * nl as i64;
        for l in 0..nl {
            for &tt in g.trans.iter() {
                let mut e = d.clone();
                e[l] = g.mul[tt as usize][d[l] as usize];
                *row.entry(orbit[encode(&e) as usize]).or_insert(0) -= 1;
            }
        }
        row.retain(|_, v| *v != 0);
        if row != rows[i] {
            bad += 1;
        }
    }
    println!(
        "OWN_WELL_DEFINED|configs_checked={}|configs_differing_from_rep={}|json=0",
        total, bad
    );
    let nnz: usize = rows.iter().map(|r| r.len()).sum();
    let diag24 = (0..n).filter(|&i| rows[i].get(&(i as u32)) == Some(&(3 * nl as i64))).count();
    let zero_sum = rows.iter().filter(|r| r.values().sum::<i64>() == 0).count();
    let mut balance = 0u64;
    let mut pairs = 0u64;
    for i in 0..n {
        for (&j, &v) in rows[i].iter() {
            pairs += 1;
            let back = *rows[j as usize].get(&(i as u32)).unwrap_or(&0);
            if (w[i] as i64) * v != (w[j as usize] as i64) * back {
                balance += 1;
            }
        }
    }
    println!(
        "OWN_E|dim={}|nnz={}|diag_24_rows={}|zero_sum_rows={}|detailed_balance_failures={}/{}|weight_sum={}|json=0",
        n,
        nnz,
        diag24,
        zero_sum,
        balance,
        pairs,
        w.iter().sum::<u64>()
    );
    // BFS diameter on the graph of E.
    let adj: Vec<Vec<u32>> = (0..n)
        .map(|i| rows[i].keys().filter(|&&j| j as usize != i).cloned().collect())
        .collect();
    let mut diam = 0;
    let mut connected = true;
    for s in 0..n {
        let mut dist = vec![-1i32; n];
        dist[s] = 0;
        let mut q = std::collections::VecDeque::new();
        q.push_back(s);
        while let Some(u) = q.pop_front() {
            for &v in &adj[u] {
                if dist[v as usize] < 0 {
                    dist[v as usize] = dist[u] + 1;
                    q.push_back(v as usize);
                }
            }
        }
        for &d in &dist {
            if d < 0 {
                connected = false;
            }
            if d > diam {
                diam = d;
            }
        }
    }
    let min_off = rows
        .iter()
        .enumerate()
        .flat_map(|(i, r)| r.iter().filter(move |(j, _)| **j as usize != i).map(|(_, v)| -*v))
        .min()
        .unwrap();
    println!(
        "OWN_GRAPH|diameter={}|connected={}|min_offdiag_magnitude={}|json=0",
        diam, connected, min_off
    );
    // The magnetic diagonal, by my own plaquette walk: U_x(v) U_y(v+x) U_x(v+y)^-1 U_y(v)^-1.
    let chi = |a: u8| -> i64 {
        let fx = (0..3).filter(|i| g.el[a as usize][*i] as usize == *i).count() as i64;
        fx - 1
    };
    let mut mag = vec![0i64; n];
    for i in 0..n {
        let d = digits(reps[i], nl);
        let mut total_m = 0i64;
        for y in 0..t.ly {
            for x in 0..t.lx {
                let v = x + t.lx * y;
                let vx = (x + 1) % t.lx + t.lx * y;
                let vy = x + t.lx * ((y + 1) % t.ly);
                let m = |a: u8, b: u8| g.mul[a as usize][b as usize];
                let hol = m(
                    m(m(d[2 * v], d[2 * vx + 1]), g.inv[d[2 * vy] as usize]),
                    g.inv[d[2 * v + 1] as usize],
                );
                total_m += 2 - chi(hol);
            }
        }
        mag[i] = total_m;
    }
    // Translations act on links and hence on orbits.
    let mut tx = vec![0u32; n];
    let mut ty = vec![0u32; n];
    for i in 0..n {
        let d = digits(reps[i], nl);
        let mut ex = d.clone();
        let mut ey = d.clone();
        for y in 0..t.ly {
            for x in 0..t.lx {
                let v = x + t.lx * y;
                let vx = (x + 1) % t.lx + t.lx * y;
                let vy = x + t.lx * ((y + 1) % t.ly);
                for dir in 0..2 {
                    ex[2 * v + dir] = d[2 * vx + dir];
                    ey[2 * v + dir] = d[2 * vy + dir];
                }
            }
        }
        tx[i] = orbit[encode(&ex) as usize];
        ty[i] = orbit[encode(&ey) as usize];
    }
    // The sign S of each orbit: the product of link signs.
    let sign: Vec<i64> = (0..n)
        .map(|i| {
            let d = digits(reps[i], nl);
            let tr = d.iter().filter(|a| g.trans.contains(a)).count();
            if tr % 2 == 0 {
                1
            } else {
                -1
            }
        })
        .collect();
    let mut f = fs::File::create(format!("{}/E.txt", out)).unwrap();
    writeln!(f, "{}", n).unwrap();
    for (i, row) in rows.iter().enumerate() {
        for (j, v) in row.iter() {
            writeln!(f, "{} {} {}", i, j, v).unwrap();
        }
    }
    let mut f = fs::File::create(format!("{}/orbits.txt", out)).unwrap();
    for i in 0..n {
        writeln!(f, "{} {} {} {} {} {}", reps[i], w[i], mag[i], tx[i], ty[i], sign[i]).unwrap();
    }
    let mut f = fs::File::create(format!("{}/orbit_of_config.bin", out)).unwrap();
    let mut bytes = Vec::with_capacity(total * 2);
    for o in orbit.iter() {
        bytes.extend_from_slice(&(*o as u16).to_le_bytes());
    }
    f.write_all(&bytes).unwrap();
    let mut f = fs::File::create(format!("{}/group.txt", out)).unwrap();
    for a in 0..6 {
        writeln!(f, "{} {} {} {}", a, g.el[a][0], g.el[a][1], g.el[a][2]).unwrap();
    }
}

// ---------------------------------------------------------------- Montgomery arithmetic mod an odd p < 2^62
#[derive(Clone, Copy)]
struct Mt {
    p: u64,
    ni: u64,
    r2: u64,
}

impl Mt {
    fn new(p: u64) -> Mt {
        assert!(p % 2 == 1 && p < (1u64 << 62));
        let mut inv = 1u64;
        for _ in 0..6 {
            inv = inv.wrapping_mul(2u64.wrapping_sub(p.wrapping_mul(inv)));
        }
        assert_eq!(p.wrapping_mul(inv), 1);
        let r = ((1u128 << 64) % p as u128) as u64;
        let r2 = ((r as u128 * r as u128) % p as u128) as u64;
        Mt { p, ni: inv.wrapping_neg(), r2 }
    }
    #[inline(always)]
    fn redc(&self, t: u128) -> u64 {
        let m = (t as u64).wrapping_mul(self.ni);
        let u = ((t + (m as u128) * (self.p as u128)) >> 64) as u64;
        if u >= self.p {
            u - self.p
        } else {
            u
        }
    }
    #[inline(always)]
    fn mul(&self, a: u64, b: u64) -> u64 {
        self.redc(a as u128 * b as u128)
    }
    #[inline(always)]
    fn add(&self, a: u64, b: u64) -> u64 {
        let s = a + b;
        if s >= self.p {
            s - self.p
        } else {
            s
        }
    }
    #[inline(always)]
    fn sub(&self, a: u64, b: u64) -> u64 {
        if a >= b {
            a - b
        } else {
            a + self.p - b
        }
    }
    fn to(&self, a: i64) -> u64 {
        let v = a.rem_euclid(self.p as i64) as u64;
        self.mul(v, self.r2)
    }
    fn one(&self) -> u64 {
        self.to(1)
    }
    fn pow(&self, mut a: u64, mut e: u64) -> u64 {
        let mut r = self.one();
        while e > 0 {
            if e & 1 == 1 {
                r = self.mul(r, a);
            }
            a = self.mul(a, a);
            e >>= 1;
        }
        r
    }
    fn inv(&self, a: u64) -> u64 {
        self.pow(a, self.p - 2)
    }
}

// ---------------------------------------------------------------- deterministic Miller-Rabin for u64
fn mulmod(a: u64, b: u64, m: u64) -> u64 {
    ((a as u128 * b as u128) % m as u128) as u64
}
fn powmod(mut a: u64, mut e: u64, m: u64) -> u64 {
    let mut r = 1u64;
    a %= m;
    while e > 0 {
        if e & 1 == 1 {
            r = mulmod(r, a, m);
        }
        a = mulmod(a, a, m);
        e >>= 1;
    }
    r
}
fn is_prime(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    for p in [2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        if n % p == 0 {
            return n == p;
        }
    }
    let mut d = n - 1;
    let mut s = 0;
    while d % 2 == 0 {
        d /= 2;
        s += 1;
    }
    'w: for a in [2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        let mut x = powmod(a, d, n);
        if x == 1 || x == n - 1 {
            continue;
        }
        for _ in 0..s - 1 {
            x = mulmod(x, x, n);
            if x == n - 1 {
                continue 'w;
            }
        }
        return false;
    }
    true
}
fn primes_from(top: u64, count: usize) -> Vec<u64> {
    let mut out = Vec::new();
    let mut c = top | 1;
    while out.len() < count {
        if is_prime(c) {
            out.push(c);
        }
        c -= 2;
    }
    out
}

// ---------------------------------------------------------------- matrices
struct Sparse {
    n: usize,
    e: Vec<(usize, usize, i64)>,
}

fn read_sparse(path: &str) -> Sparse {
    let text = fs::read_to_string(path).unwrap();
    let mut it = text.split_ascii_whitespace().map(|x| x.parse::<i64>().unwrap());
    let n = it.next().unwrap() as usize;
    let mut e = Vec::new();
    while let Some(i) = it.next() {
        let j = it.next().unwrap();
        let v = it.next().unwrap();
        e.push((i as usize, j as usize, v));
    }
    Sparse { n, e }
}

fn dense_shift(s: &Sparse, mt: &Mt, c: i64) -> Vec<u64> {
    let n = s.n;
    let mut a = vec![0u64; n * n];
    for &(i, j, v) in &s.e {
        a[i * n + j] = mt.add(a[i * n + j], mt.to(v));
    }
    let cm = mt.to(c);
    for i in 0..n {
        a[i * n + i] = mt.sub(a[i * n + i], cm);
    }
    a
}

fn rank(a: &mut [u64], n: usize, mt: &Mt) -> usize {
    let mut r = 0;
    for col in 0..n {
        let mut piv = n;
        for i in r..n {
            if a[i * n + col] != 0 {
                piv = i;
                break;
            }
        }
        if piv == n {
            continue;
        }
        if piv != r {
            for j in col..n {
                a.swap(piv * n + j, r * n + j);
            }
        }
        let inv = mt.inv(a[r * n + col]);
        let (head, tail) = a.split_at_mut((r + 1) * n);
        let pr = &head[r * n..r * n + n];
        for i in 0..n - r - 1 {
            let row = &mut tail[i * n..(i + 1) * n];
            if row[col] == 0 {
                continue;
            }
            let f = mt.mul(row[col], inv);
            row[col] = 0;
            for j in col + 1..n {
                if pr[j] != 0 {
                    row[j] = mt.sub(row[j], mt.mul(f, pr[j]));
                }
            }
        }
        r += 1;
    }
    r
}

// Characteristic polynomial by Hessenberg reduction, coefficients low degree first, monic.
fn charpoly(s: &Sparse, mt: &Mt) -> Vec<u64> {
    let n = s.n;
    let mut h = dense_shift(s, mt, 0);
    for m in 1..n.saturating_sub(1) {
        let mut piv = n;
        for i in m..n {
            if h[i * n + m - 1] != 0 {
                piv = i;
                break;
            }
        }
        if piv == n {
            continue;
        }
        if piv != m {
            for j in 0..n {
                h.swap(piv * n + j, m * n + j);
            }
            for i in 0..n {
                h.swap(i * n + piv, i * n + m);
            }
        }
        let inv = mt.inv(h[m * n + m - 1]);
        for i in m + 1..n {
            if h[i * n + m - 1] == 0 {
                continue;
            }
            let u = mt.mul(h[i * n + m - 1], inv);
            h[i * n + m - 1] = 0;
            for j in m..n {
                let hm = h[m * n + j];
                if hm != 0 {
                    h[i * n + j] = mt.sub(h[i * n + j], mt.mul(u, hm));
                }
            }
            for r in 0..n {
                let hi = h[r * n + i];
                if hi != 0 {
                    h[r * n + m] = mt.add(h[r * n + m], mt.mul(u, hi));
                }
            }
        }
    }
    let one = mt.one();
    let mut polys: Vec<Vec<u64>> = Vec::with_capacity(n + 1);
    polys.push(vec![one]);
    for k in 1..=n {
        let prev = &polys[k - 1];
        let mut p = vec![0u64; k + 1];
        for d in 0..prev.len() {
            p[d + 1] = mt.add(p[d + 1], prev[d]);
            p[d] = mt.sub(p[d], mt.mul(h[(k - 1) * n + k - 1], prev[d]));
        }
        let mut prod = one;
        for i in 1..k {
            prod = mt.mul(prod, h[(k - i) * n + k - i - 1]);
            let term = mt.mul(h[(k - 1 - i) * n + k - 1], prod);
            if term == 0 {
                continue;
            }
            let q = &polys[k - 1 - i];
            for d in 0..q.len() {
                p[d] = mt.sub(p[d], mt.mul(term, q[d]));
            }
        }
        polys.push(p);
    }
    polys.pop().unwrap()
}

fn target_poly(table: &[(i64, u64)], mt: &Mt) -> Vec<u64> {
    let one = mt.one();
    let mut p = vec![one];
    for &(c, m) in table {
        let cm = mt.to(c);
        for _ in 0..m {
            let mut q = vec![0u64; p.len() + 1];
            for d in 0..p.len() {
                q[d + 1] = mt.add(q[d + 1], p[d]);
                q[d] = mt.sub(q[d], mt.mul(cm, p[d]));
            }
            p = q;
        }
    }
    p
}

fn parse_table(s: &str) -> Vec<(i64, u64)> {
    s.split(',')
        .map(|kv| {
            let mut it = kv.split(':');
            (it.next().unwrap().parse().unwrap(), it.next().unwrap().parse().unwrap())
        })
        .collect()
}

fn main() {
    let a: Vec<String> = env::args().collect();
    match a[1].as_str() {
        "build" => build(&a[2], 2, 2),
        "buildl" => build(&a[2], a[3].parse().unwrap(), a[4].parse().unwrap()),
        "primes" => {
            let ps = primes_from(a[2].parse().unwrap(), a[3].parse().unwrap());
            for p in ps {
                println!("{}", p);
            }
        }
        // rank FILE TOP NPRIMES c1,c2,...
        "rank" => {
            let s = read_sparse(&a[2]);
            let ps = primes_from(a[3].parse().unwrap(), a[4].parse().unwrap());
            let cs: Vec<i64> = a[5].split(',').map(|x| x.parse().unwrap()).collect();
            for p in ps {
                let mt = Mt::new(p);
                let mut sum = 0usize;
                let mut text = Vec::new();
                for &c in &cs {
                    let mut m = dense_shift(&s, &mt, c);
                    let r = rank(&mut m, s.n, &mt);
                    let nu = s.n - r;
                    println!("OWN_RANK|file={}|p={}|c={}|rank={}|nullity={}|json=0", a[2], p, c, r, nu);
                    sum += nu;
                    if nu > 0 {
                        text.push(format!("{}:{}", c, nu));
                    }
                }
                println!(
                    "OWN_RANK_SUM|file={}|p={}|n={}|sum_nullity={}|table={}|json=0",
                    a[2],
                    p,
                    s.n,
                    sum,
                    text.join(",")
                );
            }
        }
        // charpoly FILE TOP NPRIMES TABLE
        "charpoly" => {
            let s = read_sparse(&a[2]);
            let ps = primes_from(a[3].parse().unwrap(), a[4].parse().unwrap());
            let table = parse_table(&a[5]);
            for p in ps {
                let mt = Mt::new(p);
                let cp = charpoly(&s, &mt);
                let tp = target_poly(&table, &mt);
                let same = cp == tp;
                println!(
                    "OWN_CHARPOLY|file={}|p={}|degree={}|equals_table_product={}|json=0",
                    a[2],
                    p,
                    cp.len() - 1,
                    same as u8
                );
                if !same {
                    std::process::exit(1);
                }
            }
        }
        // annihilate FILE c1,c2,...: exact P(E) on every basis vector in i128 with overflow checks.
        "annihilate" => {
            let s = read_sparse(&a[2]);
            let cs: Vec<i128> = a[3].split(',').map(|x| x.parse().unwrap()).collect();
            let n = s.n;
            let mut rows: Vec<Vec<(u32, i64)>> = vec![Vec::new(); n];
            for &(i, j, v) in &s.e {
                rows[i].push((j as u32, v));
            }
            let mut nonzero_columns = 0u64;
            let mut max_abs = 0i128;
            let mut prefix = vec![0i128; cs.len() + 1];
            for b in 0..n {
                let mut v = vec![0i128; n];
                v[b] = 1;
                prefix[0] += 1;
                for (k, &c) in cs.iter().enumerate() {
                    let mut w = vec![0i128; n];
                    for i in 0..n {
                        let mut acc = 0i128;
                        for &(j, x) in &rows[i] {
                            acc = acc.checked_add((x as i128).checked_mul(v[j as usize]).unwrap()).unwrap();
                        }
                        w[i] = acc.checked_sub(c.checked_mul(v[i]).unwrap()).unwrap();
                        if w[i].abs() > max_abs {
                            max_abs = w[i].abs();
                        }
                    }
                    v = w;
                    prefix[k + 1] += v[b];
                }
                if v.iter().any(|x| *x != 0) {
                    nonzero_columns += 1;
                }
            }
            println!(
                "OWN_ANNIHILATE|file={}|roots={}|basis_vectors={}|columns_nonzero={}|largest_abs_entry={}|prefix_traces={}|json=0",
                a[2],
                a[3],
                n,
                nonzero_columns,
                max_abs,
                prefix.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")
            );
        }
        _ => panic!("mode"),
    }
}
